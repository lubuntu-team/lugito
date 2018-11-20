#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
:mod:`lugito.lugito`
======================================

Defines a class to interact with Phabricator

.. currentmodule:: lugito.lugito
"""

import json
import hmac
import http
import logging
import phabricator
import lugito
from hashlib import sha256

PHAB_WEBHOOK_SIG = "X-Phabricator-Webhook-Signature"

COMMIT = "CMIT"
DIFF_REV = "DREV"
TASK = "TASK"


class Lugito(object):

    def __init__(self, log_level=logging.DEBUG):
        """
        Initialise
        """

        self.phab = phabricator.Phabricator(
            host=lugito.config.CONFIG['phabricator']['host'],
            token=lugito.config.CONFIG['phabricator']['token'],
        )
        self.HMAC = lugito.config.CONFIG['phabricator']['hooks']
        self.host = lugito.config.CONFIG['phabricator']['host']

        self.logger = logging.getLogger('lugito.lugito')

        # Add log level
        ch = logging.StreamHandler()

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)

        self.logger.addHandler(ch)
        self.logger.setLevel(log_level)

        for key, val in self.HMAC.items():
            self.HMAC[key] = bytes(u'%s' % val, 'utf-8')


    def validate_request(self, hmac_key, request):
        """
        Check a request originated from Phabricator.  This method must be called
        first to validate a request is from Phabricator before any other method
        can be called

        Parameters
        ----------

        hmac_key: str
           The dictionary key corresponding to the HMAC token for the specifid webhook

        request: flask request object
           The request object provided by the flask route decorator

        Returns
        -------

        result: boolean
           True if the request matches the specified HMAC key, False if not

        """

        hash_ = hmac.new(self.HMAC[hmac_key], request.data, sha256)

        # check if from phabricator
        if hash_.hexdigest() == request.headers[PHAB_WEBHOOK_SIG]:

            # Store the request and transaction
            self.request_data = json.loads(request.data)
            self.transaction = self.phab.transaction.search(objectIdentifier=
                self.request_data["object"]["phid"])["data"]


            self.logger.info('received phid: %s' %\
                self.request_data["object"]["phid"])
            return True
        return False


    def get_object_type(self):
        """
        Get object type from a request

        Parameters
        ----------

        request: flask request object
           The request object provided by the flask route decorator

        Returns
        -------

        object_type: str or None
            The object type from a request

        """
        object_type = self.request_data["object"]["type"]
        self.logger.debug('get_object_type: %s' % object_type)
        return object_type


    def get_author_fullname(self):
        """
        Get author fullname from a request

        Parameters
        ----------

        request: flask request object
           The request object provided by the flask route decorator

        Returns
        -------

        author_name: str or None
           The fullname if the author object exists.  If the object doesn't
           exist a blank string is returned.

        """

        try:
            # Find the author too.
            userlookup = self.transaction[0]["authorPHID"]
            who = dict(self.phab.phid.query(
                phids=[userlookup]))[userlookup]["fullName"]

            self.logger.debug('get_author_fullname: %s' % who)
            return who

        # If the object exists, no worries, let's just return a good response.
        except http.client.HTTPException:
            self.logger.info('get_author_fullname is None')
            return None


    def get_object_string(self, key): #pragma: no cover

        phid = self.request_data["object"]["phid"]
        return self.phab.phid.query(phids=[phid])[phid][key]


    def get_commit_message(self):
        """
        Get the commit message


        Returns
        -------

        commit_message: str or None
           The commit message for the request if the author object exists.
           If the object doesn't exist a blank string is returned.

        """
        fullName = self.get_object_string(self.request_data, "fullName")
        name = self.get_object_string(self.request_data, "name")

        commitmessage = fullName.replace(name + ": ", "")

        self.logger.debug('get_commit_message: %s' % commitmessage)
        return commitmessage


    def is_new_object(self):
        """
        Is the request from a newly created object


        Returns
        -------

        new_object: boolean
            True if a new searches else False

        """

        newtask = None
        modified = None
        for data in self.transaction:
            if modified:
                if (data["dateCreated"] == data["dateModified"])\
                    and (data["dateCreated"] == modified):
                        modified = data["dateCreated"]
                        newtask = True
                else:
                    newtask = False
                    break
            else:
                modified = data["dateCreated"]

        return newtask


    def is_comment(self, period=10):
        """
        Is the request from a new or edited comment object

        Parameters
        ----------

        request: flask request object
           The request object provided by the flask route decorator

        Returns
        -------

        is_new_comment: boolean
            True if the request is from a new comment

        is_edited_comment: boolean
            True if the request is from an edtied comment

        comment_id: string or None
            The id of the comment to use as an HTML anchor or None if no comment
            is referenced

        """

        is_new_comment = False
        is_edited_comment = False
        comment_id = None
        for task in self.transaction:
            dataepoch = self.request_data["action"]["epoch"]
            datemodified = task["dateModified"]

            # All comments within period seconds of the request are fair game.
            if (dataepoch - period) <= datemodified <= (dataepoch + period) and\
                    task["comments"] != []:

                comment_id = task["id"]

                if datemodified != task["dateCreated"]:
                    is_new_comment = False
                    is_edited_comment = True
                else:
                    is_new_comment = True
                    is_edited_comment = False
                break

        return (is_new_comment, is_edited_comment, comment_id)
