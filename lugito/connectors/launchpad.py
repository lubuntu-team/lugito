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
import re
import logging
import phabricator
import lugito
from string import Template
from launchpadlib.launchpad import Launchpad as lp


BUG_MESSAGE = Template(
        "This bug has been marked as fixed in the Git repository: $link\n"
        "The commit message is the following: $commit_message\n\n"
        "(Note: I am only a bot. If this message was received in error, "
        "please contact my owners on the Lubuntu Team.)")

RE_COMMIT_MSG = re.compile(r"lp:\s+\#\d+(?:,\s*\#\d+)*")


class launchpad(object):

    def __init__(self, log_level=logging.DEBUG):

        # Launchpad info
        # Read the configuration out of the .lugitorc file
        self.application = lugito.config.CONFIG['connectors']\
            ['launchpad']['application']
        self.staging = lugito.config.CONFIG['connectors']\
            ['launchpad']['staging']
        self.version = lugito.config.CONFIG['connectors']\
            ['launchpad']['version']
        self.supported_vers =\
            lugito.config.CONFIG['connectors']\
            ['launchpad']['supported_versions']
        self.package_names =\
            lugito.config.CONFIG['phabricator']['package_names']


        # Phabricator info
        self.phab = phabricator.Phabricator(
            host=lugito.config.CONFIG['phabricator']['host'],
            token=lugito.config.CONFIG['phabricator']['token'],
        )

        self.phab_host = lugito.config.CONFIG['phabricator']['host'].replace(
            'api/', '')

        self.logger = logging.getLogger('lugito.connector.launchpad')

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
        self.lp = lp.login_with(
            self.application,
            self.staging,
            self.version)

    def get_package_name(self, name):
        """Need to check"""

        if name in self.package_names:
            return self.package_names[name]

        self.logger.debug('{} is an unsupported repository'.format(
            name))

        return None

    def get_bugs_list(self, link):
        """Get bugs list using a link"""

        regex_search = RE_COMMIT_MSG.search(link.lower())
        if not regex_search:
            self.logger.debug('{} not a commit message'.format(link))
            return []

        return regex_search.group(0).strip("lp: ").replace("#", "").split(", ")


    def send(self, *args, **kwargs):
        """Send the commit message"""

        if len(args) == 2:
            package_name, commit_msg = args

        elif len(kwargs) == 2:
            commit_msg = kwargs['commit_msg']
            package_name = kwargs['package_name']

        # else
        # raise exception

        package_name = self.get_package_name(package_name)
        bug_list = self.get_bugs_list(commit_msg)

        if package_name and bug_list:

            for bug in bug_list:
                goodtask = None
                bug = self.lp.load("/bugs/" + str(bug).strip())

                for task in bug.bug_tasks:
                    for rel in self.supported_vers:
                        if package_name + " (Ubuntu " + rel + ")" in task.bug_target_display_name:
                            goodtask = task
                            break

                    if not goodtask:
                        if package_name + " (Ubuntu)" in task.bug_target_display_name:
                            goodtask = task

                if goodtask:
                    message = BUG_MESSAGE.substitute(
                        link=self.phab_host + package_name,
                        commit_message=commit_msg,
                    )
                    bug.newMessage(content=message)
                    goodtask.status = "Fix Committed"
                    goodtask.lp_save()


    def listen(self):
        pass
