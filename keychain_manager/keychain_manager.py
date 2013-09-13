#!/usr/bin/env python
# -*- coding: utf-8 -*-
import locale
import subprocess
import re

ERROR_RE = re.compile(r'^security: ')
KEYCHAIN_RE = re.compile(r'^keychain: \"(.+)\"')
ATTRIBUTES_RE = re.compile(r'\"(\w{4})\".+\=\"(.+)\"')
PASSWORD_RE = re.compile(r'^password: \"(.+)\"')

FLAG_MAP = dict([
    ('account', 'a'),
    ('creator', 'c'),
    ('type', 'C'),
    ('kind', 'D'),
    ('value', 'G'),
    ('comment', 'j'),
    ('password', 'w'),
    ('server', 's'),
    ('path', 'p'),
    ('port', 'P'),
    ('protocol', 'r'),
    ('service', 's'),
])


class KeychainException(Exception):
    pass


class KeychainManager(object):

    def __init__(self, name=None):
        self.name = name

    def create(self):
        if self.name:
            self._call(['security', 'create-keychain', '-p', '', self.name])
        else:
            raise KeychainException("Can't create a default keychain")

    def delete(self):
        if self.name:
            self._call(['security', 'delete-keychain', self.filename])
            self._filename = None
        else:
            raise KeychainException("Can't delete a default keychain")

    def lock(self):
        self._call(['security', 'lock-keychain', self.filename])

    def unlock(self, password):
        self._call(['security', 'unlock-keychain', '-p', password, self.filename])

    def exists(self):
        return self.filename

    def export_identities(self, p12_file_path):
        self._call([
            'security',
            'export',
            '-k',
            self.filename,
            '-t',
            'identities',
            '-f',
            'pkcs12',
            '-P',
            "",
            '-o',
            p12_file_path
        ])

    @property
    def filename(self):
        if not hasattr(self, '_filename') or not self._filename:
            self._filename = None
            if self.name:
                for fname in self.keychain_files():
                    if self.name in fname:
                        self._filename = fname
            else:
                self._filename = self.default_keychain()
        return self._filename

    def import_apple_cert(self, apple_cert_file_path):
        return self._check_output(['security', 'import', apple_cert_file_path, '-k', self.filename])

    def import_rsa_key(self, rsa_file_path):
        return self._check_output([
            'security',
            'import',
            rsa_file_path,
            '-P',
            '',
            '-k',
            self.filename
        ])

    def _flags_for_options(self, options):
        flags = [['-'+FLAG_MAP[key], value] for key, value in options.items()]
        return [item for sublist in flags for item in sublist] + [self.filename]

    def add_internet_password(self, account, server, password, **kwargs):
        options = dict(kwargs)
        options.update({
            'account': account,
            'server': server,
            'password': password,
        })

        self._call(
            [
                'security',
                'add-internet-password',
            ] + self._flags_for_options(options))

    def delete_internet_password(self, options):
        self._call(
            [
                'security',
                'delete-internet-password',
            ] + self._flags_for_options(options)
        )
        pass

    def find_internet_password(self, options):
        return self._password_from_output(self._check_output(
            [
                "security",
                "find-internet-password",
                "-g",
            ] + self._flags_for_options(options)))

    def add_generic_password(self, account, service, password, **kwargs):
        options = dict(kwargs)
        options.update({
            'account': account,
            'service': service,
            'password': password,
        })

        self._call(
            [
                'security',
                'add-generic-password',
            ] + self._flags_for_options(options))

    def delete_generic_password(self, options):
        self._call(
            [
                'security',
                'delete-generic-password',
            ] + self._flags_for_options(options)
        )
        pass

    def find_generic_password(self, options):
        return self._password_from_output(self._check_output(
            [
                "security",
                "find-generic-password",
                "-g",
            ] + self._flags_for_options(options)))

    @classmethod
    def _call(self, command):
        subprocess.call(command)

    @classmethod
    def _check_output(self, command):
        if hasattr(subprocess, 'check_output'):
            output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        else:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            output = process.communicate()[0]
            retcode = process.poll()
            if retcode:
                raise subprocess.CalledProcessError(retcode, command)
        encoding = locale.getdefaultlocale()[1]
        return output.decode(encoding)

    @classmethod
    def generate_rsa_key(self, rsa_file_path, keysize=2048):
        return self._check_output(['openssl', 'genrsa', '-out', rsa_file_path, str(keysize)])

    @classmethod
    def generate_cert_request(self, email, country, rsa_file_path, cert_file_path):
        self._call([
            'openssl',
            'req',
            '-new',
            '-key',
            rsa_file_path,
            '-out',
            cert_file_path,
            '-subj',
            '/CN=%s, C=%s' % (email, country)
        ])

    @classmethod
    def convert_p12_to_pem(self, p12_file_path, pem_file_path):
        self._call([
            'openssl',
            'pkcs12',
            '-passin',
            'pass:',
            '-nodes',
            '-in',
            p12_file_path,
            '-out',
            pem_file_path
        ])

    @classmethod
    def _keychains_from_output(self, output):
        return [fname.strip('" ') for fname in output.split('\n') if fname]

    @classmethod
    def _password_from_output(self, output):
        result = {}
        for line in output.split('\n'):
            m1 = KEYCHAIN_RE.match(line)
            if m1:
                result['keychain'] = m1.groups()[0]
            m2 = PASSWORD_RE.match(line)
            if m2:
                result['password'] = m2.groups()[0]
            m3 = ATTRIBUTES_RE.search(line)
            if m3:
                result[m3.groups()[0]] = m3.groups()[1]
        return result

    @classmethod
    def keychain_files(self):
        return self._keychains_from_output(self._check_output(['security', 'list-keychains']))

    @classmethod
    def default_keychain(self):
        return self._keychains_from_output(self._check_output(['security', 'default-keychain']))[0]

    @classmethod
    def login_keychain(self):
        return self._keychains_from_output(self._check_output(['security', 'login-keychain']))[0]
