#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_keychain_manager
----------------------------------

Tests for `keychain_manager` module.
"""

import unittest
import os

from keychain_manager import KeychainManager


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

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
