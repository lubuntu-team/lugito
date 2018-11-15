#! /usr/bin/env python
# -*- coding: utf-8 -*-
# S.D.G

"""
Test launchpad connector
"""

# Imports
import json
import phabricator
from lugito.connectors.launchpad import LPConnector

# Setup ###############################################################

TEST_DIR = os.path.dirname(__file__)

# Force phabricator to use the ./tests/.arcconfig file
TEST_CONFIG = os.path.join(TEST_DIR, '.arcconfig')

with open(TEST_CONFIG, 'r') as f:
    phabricator.ARCRC = json.load(f)

# Tests ###############################################################


def test_init()
