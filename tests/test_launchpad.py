#! /usr/bin/env python
# -*- coding: utf-8 -*-
# S.D.G

"""
Test launchpad connector
"""

# Imports
import json
import phabricator
import lugito
from lugito.connectors import launchpad

# Setup ###############################################################

lugito.config.CONFIG = {
    'phabricator': {
        'host': 'http://127.0.0.1:9091/api/',
        'token': 'api-nojs2ip33hmp4zn6u6cf72w7d6yh',
        'hooks': {
            'diffhook': 'vglzi6t4gsumnilv27r27no7rs3vgs75',
            'commithook': 'znkyfflbcia5gviqx5ybad7s6uyfywxi',
            },
        },
    'connectors': {
        'irc': {
            'host': 'irc.freenode.net',
            'port': '6697',
            'username': 'someusername',
            'password': 'somepassword',
            'channel': '#somechannel',
        },
    'launchpad': {
        'application': 'lugito',
        'staging': 'production',
        'version': 'devel',
        'supported_versions': ['Cosmic', 'Bionic', 'Xenial', 'Trusty'],
        'package_names': {
            'rDEFAULTSETTINGS': 'lubuntu-default-settings',
            'rART': 'lubuntu-artwork',
            'rCALASETTINGS': 'calamares-settings-ubuntu',
            'rQTERMINALPACKAGING': 'qterminal',
            'rLXQTCONFIGPACKAGING': 'lxqt-config',
            'rNMTRAYPACKAGING': 'nm-tray',
            },
        },
    },
}


# Tests ###############################################################


def test_init():
    """Test initialising LPConnector"""

    obj = launchpad()

    assert(obj.application == "lugito")
    assert(obj.staging == "production")
    assert(obj.version == "devel")
    assert(obj.supported_vers == ["Cosmic", "Bionic", "Xenial", "Trusty"])
    assert(obj.package_names == {
        'rDEFAULTSETTINGS': 'lubuntu-default-settings',
        'rART': 'lubuntu-artwork',
        'rCALASETTINGS': 'calamares-settings-ubuntu',
        'rQTERMINALPACKAGING': 'qterminal',
        'rLXQTCONFIGPACKAGING': 'lxqt-config',
        'rNMTRAYPACKAGING': 'nm-tray',
    })


def test_get_package_name():
    """Test get package name"""

    obj = launchpad()

    assert(obj.get_package_name('rART') == 'lubuntu-artwork')
    assert(obj.get_package_name('rT') is None)


def test_get_package_name():
    """Test getting package name"""

    obj = launchpad()

    assert(obj.get_package_name('rNMTRAYPACKAGING') == 'nm-tray')
    assert(obj.get_package_name('rNMTRKAGING') is None)


def test_get_bugs_list():
    """Test getting buglist"""

    obj = launchpad()

    assert(obj.get_bugs_list("lp: #1234") == ['1234'])
    assert(obj.get_bugs_list("#1234") == [])
