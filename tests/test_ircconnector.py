#! /usr/bin/env python
# -*- coding: utf-8 -*-
# S.D.G

"""
Test IRC connector
"""

# Imports
import os
import json
import phabricator
import lugito
import pytest
from lugito.connectors import irc
# docEbrown - 20181120
# There is a bug in inspect.unwrap preventing the import of call directly
import unittest.mock
from unittest.mock import MagicMock, patch

# Setup ###############################################################

lugito.config.CONFIG = {
    'phabricator': {
        'host': 'http://127.0.0.1:9091/api/',
        'token': 'api-nojs2ip33hmp4zn6u6cf72w7d6yh',
        'hooks': {
            'diffhook': 'vglzi6t4gsumnilv27r27no7rs3vgs75',
            'commithook': 'znkyfflbcia5gviqx5ybad7s6uyfywxi',
            },
        },
    'connectors': {
        'irc': {
            'host': 'irc.freenode.net',
            'port': '6697',
            'username': 'someusername',
            'password': 'somepassword',
            'channel': '#somechannel',
        },
    'launchpad': {
        'application': 'lugito',
        'staging': 'production',
        'version': 'devel',
        'supported_versions': ['Cosmic', 'Bionic', 'Xenial', 'Trusty'],
        },
    },
}


# Tests ###############################################################

def test_init():
    """Test initialise irc connector"""

    obj = irc()

    assert('irc.freenode.net' == obj.host)
    assert(6697 == obj.port)
    assert('someusername' == obj.username)
    assert('somepassword' == obj.password)
    assert('#somechannel' == obj.channel)
    assert('http://127.0.0.1:9091/' == obj.phab_host)


@patch('phabricator.Phabricator')
def test_connect(phab_mock):
    """Test initial connection"""

    obj = irc()

    assert(phab_mock.is_called())


@patch('phabricator.Phabricator')
def test_send(phab_mock):
    """Test sending a message"""

    obj = irc()
    obj.send_notice = MagicMock()

    objectstr = "objectstr"
    who = "who"
    body = "body"
    link = "link"

    obj.send(objectstr, who, body, link)

    obj.send_notice.assert_called_with(
        '\x033[\x03\x0313objectstr\x03\x033]\x03 \x0315who\x03 body: \x032link\x03')


@patch('phabricator.Phabricator')
def test_send_kwargs(phab_mock):
    """Test sending a message - kwargs"""

    obj = irc()
    obj.send_notice = MagicMock()

    objectstr = "objectstr"
    who = "who"
    body = "body"
    link = "link"

    obj.send(objectstr=objectstr, who=who, body=body, link=link)

    obj.send_notice.assert_called_with(
        '\x033[\x03\x0313objectstr\x03\x033]\x03 \x0315who\x03 body: \x032link\x03')


def test_connect():
    """Test connect"""

    obj = irc(sleep_delay=0)

    obj._send_raw = MagicMock()
    obj._setup_connection = MagicMock()
    obj.conn = MagicMock()

    obj.conn.recv.side_effect = [
        b'No Ident response',
        b'You are now identified',
        b'477',
        b'433',
        b'PING: something',
        b'366',
    ]

    obj.connect()

    # No Ident response results
    assert(unittest.mock.call('NICK someusername1\r\n') in\
        obj._send_raw.call_args_list)
    assert(unittest.mock.call('USER someusername * * :someusername\r\n') in\
        obj._send_raw.call_args_list)
    assert(unittest.mock.call('PRIVMSG nickserv :identify someusername'\
        ' somepassword\r\n') in obj._send_raw.call_args_list)

    # Now identified / 477
    assert(unittest.mock.call('JOIN #somechannel\r\n') in\
        obj._send_raw.call_args_list)

    # 433
    assert(unittest.mock.call('NICK someusername1\r\n') in\
        obj._send_raw.call_args_list)
    assert(unittest.mock.call('USER someusername1 * * :someusername1\r\n') in\
        obj._send_raw.call_args_list)

    # Ping
    assert(unittest.mock.call('PONG : something\r\n') in\
        obj._send_raw.call_args_list)


# docEbrown - 20181120
# Address including anchors in reference
# https://phab.lubuntu.me/T88#3230
def test_get_task_info_with_anchor():
    """Test getting task info with anchor"""

    obj = irc()

    obj.send_notice = MagicMock()
    obj.phab = MagicMock()
    obj.phab.maniphest.info = MagicMock(
        return_value={
            'priorityColor': 'pink',
            'statusName': 'Open',
            'title': 'Fix shortcuts related to Super key',
            'uri': 'https://phab.lubuntu.me/T154'
        }
    )

    link_with_anchor = 'https://phab.lubuntu.me/T154#3228'
    obj.get_task_info(link_with_anchor)

    assert(unittest.mock.call(task_id=154) in\
        obj.phab.maniphest.info.call_args_list)
    assert(obj.send_notice.call_args == \
        unittest.mock.call('\x033[\x03\x035Unbreak Now!, Open\x03\x033]\x03 '
            'Fix shortcuts related to Super key: '\
            '\x032https://phab.lubuntu.me/T154#3228\x03'))


def test_get_diff_info_with_anchor():
    """Test getting diff info with anchor"""

    obj = irc()

    obj.send_notice = MagicMock()
    obj.phab = MagicMock()
    obj.phab.differential.query = MagicMock(
        return_value=[{
            'statusName': 'Closed',
            'title': 'Some diff title',
            'uri': 'https://phab.lubuntu.me/D24'
        },]
    )

    link_with_anchor = 'https://phab.lubuntu.me/D24#123'
    obj.get_task_info(link_with_anchor)

    assert(unittest.mock.call(ids=[24]) in\
        obj.phab.differential.query.call_args_list)
    assert(obj.send_notice.call_args == \
        unittest.mock.call('\x033[\x03Closed\x03\x033]\x03 '
            'Some diff title: '\
            '\x032https://phab.lubuntu.me/D24#123\x03'))

def test_get_task_info_with_error_anchor():
    """Test getting task info with anchor"""

    obj = irc()

    obj.send_notice = MagicMock()
    obj.phab = MagicMock()
    obj.phab.maniphest.info = MagicMock(side_effect=ValueError(''))

    link_with_anchor = 'https://phab.lubuntu.me/T154#3228'

    obj.get_task_info(link_with_anchor)

    assert(obj.send_notice.call_args ==
        unittest.mock.call('\x034Error: https://phab.lubuntu.me/T154#3228'\
            ' is an invalid task reference.\x03'))

def test_get_task_info_with_error_no_anchor():
    """Test getting task info with no anchor"""

    obj = irc()

    obj.send_notice = MagicMock()
    obj.phab = MagicMock()
    obj.phab.maniphest.info = MagicMock(side_effect=ValueError(''))

    link_with_anchor = 'https://phab.lubuntu.me/T154'

    obj.get_task_info(link_with_anchor)

    assert(obj.send_notice.call_args ==
        unittest.mock.call('\x034Error: https://phab.lubuntu.me/T154'\
            ' is an invalid task reference.\x03'))
