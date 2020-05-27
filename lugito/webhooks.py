#! /usr/bin/env python
# -*- coding: utf-8 -*-
# S.D.G

"""

:mod:`lugito.webhooks`
======================================

Lugito webhooks

.. currentmodule:: lugito.webhooks
"""

# Imports
import logging
import threading
from flask import Flask, request
from time import sleep
from lugito import Lugito
from lugito.connectors import irc, launchpad, jenkins

# Constants
GLOBAL_LOG_LEVEL = logging.DEBUG

# Instantiate Lugito and connectors
lugito = Lugito(GLOBAL_LOG_LEVEL)
WEBSITE = lugito.host.replace('/api/', '')

# Connectors
irc_con = irc()
launchpad_con = launchpad()
jenkins_con = jenkins()

# Logging
logger = logging.getLogger('lugito.webhooks')

# Add log level
ch = logging.StreamHandler()

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

logger.addHandler(ch)
logger.setLevel(GLOBAL_LOG_LEVEL)

# Flask
app = Flask('lugito')


@app.route("/commithook", methods=["POST"])
def commithook():
    """Commit hook"""

    if lugito.validate_request('commithook', request):

        author = lugito.get_author_fullname()

        # Without the author we can't continue
        if author is None:
            return 'Ok'

        object_type = lugito.request_data["object"]["type"]

        if object_type == "CMIT":
            logger.debug("Object is a commit.")

            commit_msg = lugito.get_object_string("fullName").replace(
                lugito.get_object_string("name") + ": ", "")
            pkg_name = lugito.get_object_string("name")


            launchpad_con.send(pkg_name, commit_msg)


    return 'Ok'


@app.route("/irc", methods=["POST"])
def _main():
    """Main route"""

    if lugito.validate_request('irc', request):

        author = lugito.get_author_fullname()

        # Without the author we can't continue
        if author is None:
            return 'Ok'

        logger.debug("Object exists, checking to see if it's a task, diff "\
            "or a commit.")

        newtask = lugito.is_new_object()
        is_new_comment, is_edited, comment_id = lugito.is_comment()
        object_type = lugito.request_data["object"]["type"]

        body = ""
        link = ""
        objectstr = lugito.get_object_string("fullName")

        send_msg = True
        # Determine what event produced the webhook call
        if (object_type == "TASK") and newtask:
            logger.debug("Object is a new task.")
            body = "just created this task"
            link = lugito.get_object_string("uri")

        elif (object_type == "TASK") and (not newtask):
            logger.debug("Object is NOT a new task.")

            # Is it a new or edited comment
            if is_new_comment and (not is_edited):
                logger.debug("Object is a new comment.")
                body = "commented on the task"

            elif (not is_new_comment) and is_edited:
                logger.debug("Object is an edited comment.")
                body = "edited a message on the task"

            if is_new_comment or is_edited:
                link = lugito.get_object_string("uri")
                link += "#" + str(comment_id)
                logger.info(link)

            else:
                logger.debug("The object has already been processed")
                send_msg = False

        elif (object_type == "DREV") and newtask:
            logger.debug("Object is a new diff.")
            body = "just created this diff"
            link = lugito.get_object_string("uri")

        elif (object_type == "DREV") and (not newtask):
            logger.debug("Object is NOT a new diff.")

            # Is it a new or edited comment
            if is_new_comment and (not is_edited):
                logger.debug("Object is a new comment.")
                body = "commented on the diff"

            elif (not is_new_comment) and is_edited:
                logger.debug("Object is an edited comment.")
                body = "edited a message on the diff"

            if is_new_comment or is_edited:
                link = lugito.get_object_string("uri")
                link += "#" + str(comment_id)
                logger.info(link)

            else:
                logger.debug("The object has already been processed")
                send_msg = False

        elif object_type == "CMIT":
            logger.debug("Object is a commit.")
            body = "committed"
            link = WEBSITE + "/" + lugito.get_object_string("name")
            logger.info(link)

        if send_msg:
            irc_con.send(objectstr, author, body, link)

    return 'Ok'


@app.route("/jenkins", methods=["POST"])
def jenkinstrigger():
    """Jenkins trigger"""

    if lugito.validate_request('jenkins', request):

        author = lugito.get_author_fullname()

        # Without the author we can't continue
        if author is None:
            return 'Ok'

        object_type = lugito.request_data["object"]["type"]
        pkg_name = lugito.get_repository_name()

        if object_type == "CMIT":
            logger.debug("Object is a commit.")

            jenkins_con.send(package_name=pkg_name)


    return 'Ok'


def processjenkinsircnotify(request):
    """Process the request given so it can be daemonized"""

    sleep(10)

    # Get the status of the most recent build to the given project
    proj, status, link = jenkins_con.receive(request)

    if status:
        irc_con.send("Lubuntu CI", proj, status, link)


@app.route("/jenkinsnag", methods=["POST"])
def jenkinsircnotify():
    """Jenkins IRC notifications"""

    print("Processing request")
    send_notification = threading.Thread(
            target=processjenkinsircnotify, args=[request.data])
    send_notification.setDaemon(True)
    send_notification.start()

    return 'Ok'


def run():
    irc_con.connect()
    launchpad_con.connect()
    t = threading.Thread(target=irc_con.listen)
    t.daemon = True
    t.start()
    app.run(host="0.0.0.0", port=5000)
