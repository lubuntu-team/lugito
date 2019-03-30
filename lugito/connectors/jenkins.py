#! /usr/bin/env python
# -*- coding: utf-8 -*-
# S.D.G
"""
:mod:`lugito.connectors.jenkins`
======================================

Define a jenkins connector class

.. currentmodule:: lugito.connectors.jenkins
"""

# Imports
import re
import logging
import phabricator
import lugito
import requests
from string import Template


class launchpad(object):

    def __init__(self, log_level=logging.DEBUG):

        # Launchpad info
        # Read the configuration out of the .lugitorc file
        self.package_names =\
            lugito.config.CONFIG['phabricator']['package_names']

        # Phabricator info
        self.phab = phabricator.Phabricator(
            host=lugito.config.CONFIG['phabricator']['host'],
            token=lugito.config.CONFIG['phabricator']['token'],
        )

        # Jenkins info
        self.jenkins_site = lugito.config.CONFIG['jenkins']['site']
        self.jenkins_trigger_url = lugito.config.CONFIG['jenkins']\
            ['template_url']

        self.phab_host = lugito.config.CONFIG['phabricator']['host'].replace(
            'api/', '')

        self.logger = logging.getLogger('lugito.connector.jenkins')

        # Add log level
        ch = logging.StreamHandler()

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)

        self.logger.addHandler(ch)
        self.logger.setLevel(log_level)


    def get_package_name(self, name):
        """Need to check"""

        if name in self.package_names:
            return self.package_names[name]

        self.logger.debug('{} is an unsupported repository'.format(
            name))


    def send(self, *args, **kwargs):
        """Send the commit message"""

        if len(args) == 1:
            package_name = args
        elif len(kwargs) == 1:
            package_name = kwargs['package_name']

        # Get the package name we'll be triggering; this assumes the repo
        # name always matches the package name
        package_name = self.get_package_name(package_name)

        if package_name:
            package_url = self.jenkins_trigger_url.replace(
                "PACKAGE", package_name)
            r = requests.post("{}/git/notifyCommit?url={}".format(
                self.jenkins_site, package_url), data="")

            self.logger.debug("Sent to Jenkins: {} {}".format(
                r.status_code, r.reason))


    def listen(self):
        pass
