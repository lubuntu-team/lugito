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
import json
import jenkinsapi.custom_exceptions
from jenkinsapi.jenkins import Jenkins
from string import Template


class jenkins(object):

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
        self.jenkins_site = lugito.config.CONFIG['connectors']['jenkins']\
            ['site']
        self.jenkins_trigger_url = lugito.config.CONFIG['connectors']\
            ['jenkins']['template_url']

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
        package_name = self.get_package_name(package_name.lower())

        if package_name:
            package_url = self.jenkins_trigger_url.replace(
                "PACKAGE", package_name)
            r = requests.post("{}/git/notifyCommit?url={}".format(
                self.jenkins_site, package_url), data="")

            self.logger.debug("Sent to Jenkins: {} {}".format(
                r.status_code, r.reason))


    def auth_jenkins(self):
        """Authenticate with the Jenkins server"""

        site = lugito.config.CONFIG["connectors"]["jenkins"]["site"]
        user = lugito.config.CONFIG["connectors"]["jenkins"]["user"]
        key = lugito.config.CONFIG["connectors"]["jenkins"]["api_key"]

        server = Jenkins(site, username=user, password=key)

        return server


    def receive(self, proj_name):
        """Receive the project name and return the status of the last build"""

        proj_name = json.loads(proj_name)["PROJECT"]

        status = None

        # Authenticate with the server
        jenkins = self.auth_jenkins()

        # Check if the project name matches a valid one on the server
        # If it does, grab the job info, if it doesn't, stop
        proj = None
        for job in jenkins.get_jobs():
            if job[0] == proj_name:
                proj = job

        if not proj:
            return status

        # Return the status of the last completed build
        try:
            status = proj[1].get_last_completed_build().get_status()
            url = proj[1].get_last_completed_build().get_build_url()
            return proj[0], status, url
        except jenkinsapi.custom_exceptions.NoBuildData:
            return None


    def listen(self):
        pass
