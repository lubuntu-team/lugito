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
from lugito import IRCConnector
from unittest.mock import MagicMock

# Setup ###############################################################

TEST_DIR = os.path.dirname(__file__)

# Force phabricator to use the ./tests/.arcconfig file
TEST_CONFIG = os.path.join(TEST_DIR, '.arcconfig')

with open(TEST_CONFIG, 'r') as f:
    phabricator.ARCRC = json.load(f)

# Tests ###############################################################

def test_init():
    """Test initialise irc connector"""

    obj = IRCConnector()

    assert('irc.freenode.net' == obj.host)
    assert(6697 == obj.port)
    assert('someusername' == obj.username)
    assert('somepassword' == obj.password)
    assert('#somechannel' == obj.channel)
    assert('http://127.0.0.1:9091/' == obj.phab_host)


def test_connect():
    """Test initial connection"""

    obj = IRCConnector()

    obj._socket_conn = MagicMock()

#    obj.conn.recv = MagicMock(side_effect=[

