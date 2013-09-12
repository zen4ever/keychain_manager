#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import locale


class KeychainManager(object):

    def __init__(self, name):
        self.name = name

    def create(self):
        self.call(['security', 'create-keychain', '-p', '', self.name])

    def delete(self):
        self.call(['security', 'delete-keychain', self.filename])

    def exists(self):
        return self.name in self.check_output(['security', 'list-keychains'])

    def export_identities(self, p12_file_path):
        self.call([
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
            for fname in self.keychain_files():
                if self.name in fname:
                    self._filename = fname
        return self._filename

    def import_apple_cert(self, apple_cert_file_path):
        return self.check_output(['security', 'import', apple_cert_file_path, '-k', self.filename])

    def import_rsa_key(self, rsa_file_path):
        return self.check_output([
            'security',
            'import',
            rsa_file_path,
            '-P',
            '',
            '-k',
            self.filename
        ])

    @classmethod
    def call(self, command):
        subprocess.call(command)

    @classmethod
    def check_output(self, command):
        if hasattr(subprocess, 'check_output'):
            output = subprocess.check_output(command)
        else:
            output = subprocess.Popen(command, stdout=subprocess.PIPE).communicate()[0]
        encoding = locale.getdefaultlocale()[1]
        return output.decode(encoding)

    @classmethod
    def generate_rsa_key(self, rsa_file_path, keysize=2048):
        return self.check_output(['openssl', 'genrsa', '-out', rsa_file_path, str(keysize)])

    @classmethod
    def generate_cert_request(self, email, country, rsa_file_path, cert_file_path):
        self.call([
            'openssl',
            'req',
            '-new',
            '-key',
            rsa_file_path,
            '-out',
            cert_file_path,
            '-subj',
            '/%s, CN=CERT_NAME, C=%s' % (email, country)
        ])

    @classmethod
    def convert_p12_to_pem(self, p12_file_path, pem_file_path):
        self.call([
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
    def keychain_files(self):
        return [
            fname.strip('" ')
            for fname in self.check_output(['security', 'list-keychains']).split('\n') if fname]
