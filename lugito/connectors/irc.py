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
from time import sleep


class IRCConnector(object):

    def __init__(self, log_level=logging.DEBUG):

        # IRC info
        # Read the configuration out of the .arcconfig file
        self.host = phabricator.ARCRC['irc']['host']
        self.port = int(phabricator.ARCRC['irc']['port'])
        self.username = phabricator.ARCRC['irc']['username']
        self.password = phabricator.ARCRC['irc']['password']
        self.channel = phabricator.ARCRC['irc']['channel']

        # Phabricator info
        self.phab = phabricator.Phabricator()
        self.phab_host = phabricator.ARCRC['config']['default'].replace(
            'api/', '')

        self.logger = logging.getLogger('lugito.connector.IRCConnector')

        # Add log level
        ch = logging.StreamHandler()

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)

        self.logger.addHandler(ch)
        self.logger.setLevel(log_level)


    def _send_raw(self, message):
        """Low level send"""

        self.conn.send(message.encode('utf-8'))


    def _socket_conn(self):
        self.conn = ssl.wrap_socket(
            socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        self.conn.connect((self.host, self.port))


    def connect(self):
        """Connect"""

        self._socket_conn()

        setup = False
        usersuffix = 0
        self.logger.info("Connecting to IRC.")

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
                sleep(5)
                self._send_raw("JOIN {}\r\n".format(self.channel))

            if "477" in response:
                sleep(5)
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

    def send_notice(self, message):
        self._send_raw("NOTICE {} :{}\r\n".format(self.channel, message))

    def send(self, objectstr, who, body, link):
        """Send a formatted message"""

        # e.g. [T31: Better IRC integration]
        message = "\x033[\x03\x0313" + objectstr + "\x03\x033]\x03 "
        # e.g. tsimonq2 (Simon Quigley)
        message = message + "\x0315" + who + "\x03 "
        # e.g. commented on the task:
        message = message + body + ": "
        # e.g. https://phab.lubuntu.me/T40#779
        message = message + "\x032" + link + "\x03"
        # Make sure we can debug this if it goes haywire
        self.logger.debug(message)
        # Sleep for a fifth of a second, so when we have a bunch of messages we have a buffer
        sleep(0.2)
        # Aaaaand, send it off!
        self.send_notice(message)

    def gettaskinfo(self, task):

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

            sendmessage +=  taskinfo["statusName"] + "\x03\x033]\x03 "

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
            self.send_notice("\x034Error: " + task.strip() + "is an invalid task reference.\x03")
            return None


    def bot(self, message, msgtype):

        if msgtype == "info":
            message = message.split(" :" + self.username + ": info")[1]

            for item in message.split():
                if item.startswith("T") or item.startwith("D"):
                    self.gettaskinfo(item.strip())

        elif msgtype == "link":

            for item in message.split(self.phab_host):
                if (item.split()[0].strip().startswith("T")) or \
                    (item.split()[0].strip().startswith("D")):

                    self.gettaskinfo(item.split()[0].strip())

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
