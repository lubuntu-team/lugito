#! /usr/bin/env python
# -*- coding: utf-8 -*-
# S.D.G

"""
:mod:`lugito.connectors.irc`
======================================

Define an irc connector class

.. currentmodule:: lugito.connectors.irc
"""

# Imports
import ssl
import http
import socket
import logging
import threading
import phabricator
import lugito
from time import sleep


class irc(object):

    def __init__(self, log_level=logging.DEBUG, sleep_delay=5):

        # IRC info
        # Read the configuration out of the .arcconfig file
        self.host = lugito.config.CONFIG['connectors']['irc']['host']
        self.port = int(lugito.config.CONFIG['connectors']['irc']['port'])
        self.username = lugito.config.CONFIG['connectors']['irc']['username']
        self.password = lugito.config.CONFIG['connectors']['irc']['password']
        self.channel = lugito.config.CONFIG['connectors']['irc']['channel']

        # Phabricator info
        self.phab = phabricator.Phabricator(
            host=lugito.config.CONFIG['phabricator']['host'],
            token=lugito.config.CONFIG['phabricator']['token'],)
        self.phab_host = self.phab.host.replace('api/', '')

        self.logger = logging.getLogger('lugito.connector.IRCConnector')

        # Add log level
        ch = logging.StreamHandler()

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)

        self.logger.addHandler(ch)
        self.logger.setLevel(log_level)

        self.sleep_delay = sleep_delay


    def _send_raw(self, message): # pragma: no cover
        """Low level send"""

        self.conn.send(message.encode('utf-8'))


    def _setup_connection(self):
        """Setup connection"""
        self.conn = ssl.wrap_socket(
            socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        self.conn.connect((self.host, self.port))


    def connect(self):
        """Connect"""

        self.logger.info("Connecting to IRC.")
        self._setup_connection()

        setup = False
        usersuffix = 0

        while not setup:
            response = self.conn.recv(512).decode("utf-8")
            self.logger.debug(response)

            if "No Ident response" in response:
                self._send_raw("NICK {}\r\n".format(self.username))
                self._send_raw("USER {} * * :{}\r\n".format(
                    self.username, self.username))
                self._send_raw("PRIVMSG nickserv :identify {} {}\r\n".format(
                    self.username, self.password))

            if "You are now identified" in response:
                sleep(self.sleep_delay)
                self._send_raw("JOIN {}\r\n".format(self.channel))

            if "477" in response:
                sleep(self.sleep_delay)
                self._send_raw("JOIN {}\r\n".format(self.channel))

            if "433" in response:
                usersuffix = usersuffix + 1
                self.username = self.username + str(usersuffix)
                self._send_raw("NICK {}\r\n".format(self.username))
                self._send_raw("USER {} * * :{}\r\n".format(
                    self.username, self.username))

            if "PING" in response:
                self._send_raw("PONG :{}\r\n".format(response.split(":")[1]))

            if "366" in response:
                setup = True

        self.logger.info("Successfully connected to the IRC server.")

    def send_notice(self, message): # pragma: no cover
        self._send_raw("NOTICE {} :{}\r\n".format(self.channel, message))

    def send(self, *args, **kwargs):
        """Send a formatted message"""

        if len(args) == 4:
            objectstr, who, body, link = args

        elif len(kwargs) == 4:
            objectstr = kwargs['objectstr']
            who = kwargs['who']
            body = kwargs['body']
            link = kwargs['link']

        # else
        # raise exception

        # e.g. [T31: Better IRC integration]
        message = "\x033[\x03\x0313" + objectstr + "\x03\x033]\x03 "
        # e.g. tsimonq2 (Simon Quigley)
        message += "\x0315" + who + "\x03 "
        # e.g. commented on the task:
        message += body + ": "
        # e.g. https://phab.lubuntu.me/T40#779
        message += "\x032" + link + "\x03"
        # Make sure we can debug this if it goes haywire
        self.logger.debug(message)
        # Sleep for a fifth of a second, so when we have a bunch of messages we have a buffer
        sleep(0.2)
        # Aaaaand, send it off!
        self.send_notice(message)

    def get_task_info(self, task):

        sendmessage = ""

        # Strip out anchor link
        # This will prevent invalid task / diff references
        anchor = None
        if '#' in task:
            task, anchor = task.split('#')

        try:
            # We only need the task number.
            if len(task.split("T")) > 1:
                taskinfo = self.phab.maniphest.info(
                    task_id=int(task.split("T")[1]))

            # or the diff number
            elif len(task.split("D")) > 1:
                taskinfo = self.phab.differential.query(
                    ids=[int(task.split("D")[1])])[0]
                taskinfo['priorityColor'] = None

            sendmessage += "\x033[\x03"

            # The color of the priority text should correspond to its value.
            color = taskinfo["priorityColor"]
            if color == "violet":
                sendmessage += "\x036Needs Triage"
            elif color == "pink":
                sendmessage += "\x035Unbreak Now!"
            elif color == "red":
                sendmessage += "\x034High"
            elif color == "orange":
                sendmessage += "\x037Medium"
            elif color == "yellow":
                sendmessage += "\x038Low"
            elif color == "sky":
                sendmessage += "\x037Wishlist"

            # Put the task status in the message.
            if color is not None:
                sendmessage += ", "

            sendmessage += taskinfo["statusName"] + "\x03\x033]\x03 "

            # Put the title in there as well.
            sendmessage += taskinfo["title"].strip() + ": "

            # And the link.
            sendmessage += "\x032" + taskinfo["uri"]

            # Add the anchor back if it was present
            if anchor is not None:
                sendmessage += '#{}'.format(anchor)

            sendmessage += '\x03'

            # Send it off!
            self.send_notice(sendmessage)

        # If someone wrote something like "Tblah", obviously that's not right.
        except ValueError:

            if anchor is not None:
                link = '{}#{}'.format(task.strip(), anchor)
            else:
                link = task.strip()

            self.send_notice("\x034Error: " + link +\
                " is an invalid task reference.\x03")


    def bot(self, message, msgtype):

        if msgtype == "info":
            message = message.split(" :" + self.username + ": info")[1]

            for item in message.split():
                if item.startswith("T") or item.startwith("D"):
                    self.get_task_info(item.strip())

        elif msgtype == "link":

            for item in message.split(self.phab_host):
                if (item.split()[0].strip().startswith("T")) or \
                    (item.split()[0].strip().startswith("D")):

                    self.get_task_info(item.split()[0].strip())

        else:
            self.sendnotice("\x034Error: unknown command.\x03")
            return None


    def listen(self):

        while True:
            ircmsg = self.conn.recv(512)

            if len(ircmsg) == 0:
                # logger.warn is deprecated, use .warning.
                self.logger.warning("Connection lost, reconnecting!")
                self.connect()
                continue

            ircmsg = ircmsg.decode("UTF-8").strip('\n\r')
            self.logger.debug(ircmsg)

            if ircmsg.find("PING :") != -1:
                self.conn.send(bytes("PONG :pingis\n", "UTF-8"))

            elif ircmsg.find(" :" + self.username + ": info") != -1:
                self.bot(ircmsg, "info")

            elif ircmsg.find("{}".format(self.phab_host)) != -1:
                self.bot(ircmsg, "link")
