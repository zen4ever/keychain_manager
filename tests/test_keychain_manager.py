#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_keychain_manager
----------------------------------

Tests for `keychain_manager` module.
"""

import unittest
import os
import subprocess

from keychain_manager import KeychainManager, KeychainException


OUTPUT = """
keychain: "/Users/username/Library/Keychains/login.keychain"
class: "inet"
attributes:
    0x00000007 <blob>="daw.apple.com (youremail@example.com)"
    0x00000008 <blob>=<NULL>
    "acct"<blob>="youremail@example.com"
    "atyp"<blob>="form"
    "cdat"<timedate>=0x32303133303931333030323533395A00  "20130913002539Z\000"
    "crtr"<uint32>=<NULL>
    "cusi"<sint32>=<NULL>
    "desc"<blob>="Web form password"
    "icmt"<blob>="default"
    "invi"<sint32>=<NULL>
    "mdat"<timedate>=0x32303133303931333034303130375A00  "20130913040107Z\000"
    "nega"<sint32>=<NULL>
    "path"<blob>=<NULL>
    "port"<uint32>=0x00000000
    "prot"<blob>=<NULL>
    "ptcl"<uint32>="htps"
    "scrp"<sint32>=<NULL>
    "sdmn"<blob>=<NULL>
    "srvr"<blob>="daw.apple.com"
    "type"<uint32>=<NULL>
password: "examplepass"
"""


class TestKeychain_manager(unittest.TestCase):

    def setUp(self):
        self.rsa_file_path = '/tmp/rsa.key'
        self.csr_file_path = '/tmp/cert.csr'

    def test_create_keychain(self):
        km = KeychainManager("some_keychain")
        km.create()
        self.assertTrue(km.exists())
        km.delete()
        self.assertFalse(km.exists())

    def test_filename_keychain(self):
        km = KeychainManager("some_keychain")
        self.assertFalse(km.exists())
        self.assertEqual(km.filename, None)
        km.create()
        self.assertNotEqual(km.filename, None)
        km.delete()
        self.assertFalse(km.exists())

    def test_import_rsa_key(self):
        KeychainManager.generate_rsa_key(self.rsa_file_path, 2048)
        km = KeychainManager("some_keychain")
        km.create()
        self.assertTrue('1 key imported' in km.import_rsa_key(self.rsa_file_path))
        km.delete()
        os.unlink(self.rsa_file_path)

    def test_csr_cert(self):
        KeychainManager.generate_rsa_key(self.rsa_file_path)
        self.assertTrue(os.path.exists(self.rsa_file_path))
        KeychainManager.generate_cert_request(
            'andrew@marpasoft.com',
            'US',
            self.rsa_file_path,
            self.csr_file_path
        )
        self.assertTrue(os.path.exists(self.rsa_file_path))
        self.assertTrue(os.path.exists(self.csr_file_path))
        os.unlink(self.rsa_file_path)
        os.unlink(self.csr_file_path)

    def test_keychain_files(self):
        files = KeychainManager.keychain_files()
        self.assertNotEqual(files, [])
        self.assertTrue('/Library/Keychains/System.keychain' in files)

    def test_default_keychain(self):
        self.assertNotEqual(KeychainManager.default_keychain(), "")

    def test_login_keychain(self):
        self.assertTrue("login" in KeychainManager.login_keychain())

    def test_default_keychain_manager(self):
        kcm = KeychainManager()
        self.assertTrue(kcm.exists())
        self.assertTrue("login" in kcm.filename)
        self.assertRaises(KeychainException, lambda: kcm.create())
        self.assertRaises(KeychainException, lambda: kcm.delete())

    def test_password_output(self):
        result = KeychainManager._password_from_output(OUTPUT)
        self.assertEqual(
            result,
            {
                'acct': 'youremail@example.com',
                'atyp': 'form',
                'desc': 'Web form password',
                'icmt': 'default',
                'keychain': '/Users/username/Library/Keychains/login.keychain',
                'password': 'examplepass',
                'ptcl': 'htps',
                'srvr': 'daw.apple.com',
            }
        )

    def test_password_management(self):
        kcm = KeychainManager('some_keychain')
        kcm.create()
        kcm.add_internet_password('youremail@example.com', 'www.example.com', 'testpass')
        result = kcm.find_internet_password({'server': 'www.example.com'})
        self.assertTrue('password' in result)
        kcm.delete_internet_password({'server': 'www.example.com'})
        self.assertRaises(
            subprocess.CalledProcessError,
            lambda: kcm.find_internet_password({'server': 'www.example.com'})
        )
        kcm.delete()

    def test_generic_password_management(self):
        kcm = KeychainManager('some_keychain')
        kcm.create()
        kcm.add_generic_password('youremail@example.com', 'someservice', 'testpass')
        result = kcm.find_generic_password({'service': 'someservice'})
        self.assertTrue('password' in result)
        kcm.delete_generic_password({'service': 'someservice'})
        self.assertRaises(
            subprocess.CalledProcessError,
            lambda: kcm.find_generic_password({'service': 'someservice'})
        )
        kcm.delete()

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
