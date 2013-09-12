===============================
Keychain Manager
===============================

.. image:: https://badge.fury.io/py/keychain_manager.png
    :target: http://badge.fury.io/py/keychain_manager
    
.. image:: https://pypip.in/d/keychain_manager/badge.png
        :target: https://crate.io/packages/keychain_manager?version=latest

A Python api for Mac OS X Keychain.
It is a port of https://github.com/jprichardson/keychain_manager

* Free software: BSD license

Getting started
---------------

To install the package do:

    .. code-block:: bash

        pip install keychain-manager

Usage
-----

Example of generating Apple Push Certificate

    .. code-block:: python

        from keychain_manager import KeychainManager
        import os.path

        USER = 'youremail@example.com'
        # let's choose a keychain name, so we won't pollute the 'login' keychain
        KEYCHAIN = 'apple_push_keychain'
        # this is where the file aps_production_identity.cer will be downloaded
        YOUR_DOWNLOADS_DIR = '~/Downloads/'

        RSA_FILE = '/tmp/myrsa.key'
        KeychainManager.generate_rsa_key(RSA_FILE)

        CERT_FILE = '/tmp/CertificateSigningRequest.certSigningRequest'
        # 'US' is the country abbreviation.
        KeychainManager.generate_cert_request(USER, 'US', RSA_FILE, CERT_FILE)

        kcm = KeychainManager(KEYCHAIN)
        if kcm.exists():
            kcm.delete()
        kcm.create()

        kcm.import_rsa_key(RSA_FILE)

        #now from your browser, you'll have downloaded a file from Apple typically
        named: aps_production_identity.cer
        kcm.import_apple_cert(os.path.join(YOUR_DOWNLOADS_DIR, 'aps_production_identity.cer'))

        P12_FILE = '/tmp/push_prod.p12'
        kcm.export_identites(P12_FILE)

        PEM_FILE = '/tmp/push_prod.pem'
        KeychainManager.convert_p12_to_pem(P12_FILE, PEM_FILE)

        kcm.delete()

Tests
-----

Tests are running on the Mac OS X only, since we need to have actualy Keychain
Manager. Just clone the repo on your Mac computer and run::

    python setup.py test
