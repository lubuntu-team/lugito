#! /usr/bin/env python
# -*- coding: utf-8 -*-
# S.D.G

"""
:mod:`lugito.config`
======================================

Module to manage lugito configuration

.. currentmodule:: lugito.config
"""

# Imports
import os
import logging
import configparser

DEFAULT_CONFIG_FILE = os.path.join(
    os.getcwd(), '.lugitorc')

logger = logging.getLogger('lugito.config')

# Add log level
ch = logging.StreamHandler()

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.DEBUG)

CONFIG = {}


def update_config(config_file=DEFAULT_CONFIG_FILE):
    """
    Update the system config from a config file

    Parameters
    ----------

    config_file: str
       The path of the lugito config file

    Returns
    -------

    config: dictionary
       A dictionary of config parameters

    """
    config = configparser.ConfigParser()
    config.read(config_file)

    # Make some basic assertions for minimum functionality
    if 'phabricator' not in config:
        raise ValueError('phabricator section missing from config file: %s' %\
            config_file)

    if 'host' not in config['phabricator']:
        raise ValueError('host value missing from phabricator section in'\
            ' config file: %s' % config_file)

    if 'token' not in config['phabricator']:
        raise ValueError('token value missing from phabricator section in'\
            ' config file: %s' % config_file)

    CONFIG['phabricator'] = {}
    CONFIG['phabricator']['host'] = config['phabricator']['host']
    CONFIG['phabricator']['token'] = config['phabricator']['token']

    CONFIG['phabricator']['hooks'] = {}
    CONFIG['phabricator']['package_names'] = {}

    # Iterate through hooks for HMAC keys
    if 'phabricator.hooks' in config:
        for key, value in config['phabricator.hooks'].items():
            CONFIG['phabricator']['hooks'][key] = value

    if 'phabricator.package_names' in config:
        for key, value in config['phabricator.package_names'].items():
            CONFIG['phabricator']['package_names'][key] = value

    CONFIG['connectors'] = {}

    # Iterate through available connectors
    for key in config.keys():

        # Is a connector section
        if ('connector.' in key) and (key.count('.') == 1) :
            connector = key.split('.')[1]

            if 'connectors' not in CONFIG:
                CONFIG['connectors'] = {}

            if connector not in CONFIG['connectors']:
                CONFIG['connectors'][connector] = {}

            for param, value in config[key].items():

                # Check for multiple values for a parameter
                if value.find('\n') >= 0:
                    value = value[1:].split('\n')

                CONFIG['connectors'][connector][param] = value

        # Is a connector sub-section
        elif ('connector.' in key) and (key.count('.') > 1) :
            sections = key.split('.')
            connector = sections[1]
            subsection = sections[-1]

            if 'connectors' not in CONFIG:
                CONFIG['connectors'] = {}

            if connector not in CONFIG['connectors']:
                CONFIG['connectors'][connector] = {}

            CONFIG['connectors'][connector][subsection] = {}

            for param, value in config[key].items():

                # Check for multiple values for a parameter
                if value.find('\n') >= 0:
                    value = value[1:].split('\n')

                # configparser reads the parameters as lower case
                # convert all but first character to upper case
                param = 'r{}'.format(param[1:].upper())
                CONFIG['connectors'][connector][subsection][param] = value


try:
    update_config()
except ValueError:
    # The config file is not present
    logging.warning('Default config file: %s not found' % DEFAULT_CONFIG_FILE)
