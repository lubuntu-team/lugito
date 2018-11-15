#! /usr/bin/env python
# -*- coding: utf-8 -*-
# S.D.G
"""
:mod:`lugito.connectors.launchpad`
======================================

Define a launchpad connector class

.. currentmodule:: lugito.connectors.launchpad
"""

# Imports
import logging
import phabricator
from launchpadlib.launchpad import Launchpad


class LPConnector(object):

    def __init__(self, log_level=logging.DEBUG):

        # Launchpad info
        # Read the configuration out of the .arcconfig file
        self.application = phabricator.ARCRC['launchpad']['application']
        self.staging = phabricator.ARCRC['launchpad']['staging']
        self.version = phabricator.ARCRC['launchpad']['version']
        self.supported_vers =\
            phabricator.ARCRC['launchpad']['supported_versions']

        # Phabricator info
        self.phab = phabricator.Phabricator()
        self.phab_host = phabricator.ARCRC['config']['default'].replace(
            'api/', '')

        self.logger = logging.getLogger('lugito.connector.LPConnector')

        # Add log level
        ch = logging.StreamHandler()

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)

        self.logger.addHandler(ch)
        self.logger.setLevel(log_level)


    def connect(self):
        """Connect"""

        self.logger.info("Connecting to Launchpad")


    def send(self, objectstr, who, body, link):
        pass


    def listen(self):
        pass


if __name__ == "__main__":

    obj = LPConnector()

