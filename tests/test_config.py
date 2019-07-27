#! /usr/bin/env python
# -*- coding: utf-8 -*-
# S.D.G

"""Test config values


:author: Ben Johnston

"""

# Imports
import os
import pytest
import lugito.config

TEST_FILE = os.path.join(
    os.path.dirname(__file__),
    '.lugitorc')


TEST_FILE_NO_PHAB = os.path.join(
    os.path.dirname(__file__),
    '.lugitorc_no_phab')


TEST_FILE_NO_HOST = os.path.join(
    os.path.dirname(__file__),
    '.lugitorc_no_host')


TEST_FILE_NO_TOKEN = os.path.join(
    os.path.dirname(__file__),
    '.lugitorc_no_token')


def test_loading_config_hooks():
    """Test loading config"""

    lugito.config.update_config(TEST_FILE)
    CONFIG = lugito.config.CONFIG

    assert(CONFIG['phabricator']['host'] == 'http://127.0.0.1:9091/api/')
    assert(CONFIG['phabricator']['token'] == 'api-nojs2ip33hmp4zn6u6cf72w7d6yh')

    # Hooks
    assert(CONFIG['phabricator']['hooks']['diffhook'] ==\
        'vglzi6t4gsumnilv27r27no7rs3vgs75')
    assert(CONFIG['phabricator']['hooks']['commithook'] ==\
        'znkyfflbcia5gviqx5ybad7s6uyfywxi')

    # Package names
    assert(CONFIG['phabricator']['package_names']['rdefaultsettings'] ==\
        'lubuntu-default-settings')
    assert(CONFIG['phabricator']['package_names']['rart'] ==\
        'lubuntu-artwork')
    assert(CONFIG['phabricator']['package_names']['rcalasettings'] ==\
        'calamares-settings-ubuntu')
    assert(CONFIG['phabricator']['package_names']['rqterminalpackaging'] ==\
        'qterminal')
    assert(CONFIG['phabricator']['package_names']['rlxqtconfigpackaging'] ==\
        'lxqt-config')
    assert(CONFIG['phabricator']['package_names']['rnmtraypackaging'] ==\
        'nm-tray')


def test_loading_config_connectors():
    """Test loading config connectors"""


    lugito.config.update_config(TEST_FILE)
    CONFIG = lugito.config.CONFIG

    # Connectors
    assert(CONFIG['connectors']['irc'] == {
        'host': 'irc.freenode.net',
        'port': '6697',
        'username': 'someusername',
        'password':'somepassword',
        'channel': '#somechannel',
    })

    if not (CONFIG['connectors']['launchpad'] == {
        'application': 'lugito',
        'staging': 'production',
        'version': 'devel',
        'supported_versions': ['Cosmic', 'Bionic', 'Xenial', 'Trusty'],
        }):
        import pdb;pdb.set_trace()




def test_load_config_no_phab():
    """Test loading config to load phabricator"""

    with pytest.raises(ValueError) as err:

        lugito.config.update_config(TEST_FILE_NO_PHAB)

        assert('phabricator section missing from config file' in str(err))


def test_load_config_no_host():
    """Test loading config to load phabricator"""

    with pytest.raises(ValueError) as err:
        lugito.config.update_config(TEST_FILE_NO_HOST)

        assert('host value missing from phabricator section config file' in str(err))


def test_load_config_no_token():
    """Test loading config to load phabricator"""

    with pytest.raises(ValueError) as err:

        lugito.config.update_config(TEST_FILE_NO_TOKEN)

        assert('host value missing from phabricator conffig file' in str(err))
