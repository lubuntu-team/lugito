#! /usr/bin/env python
# -*- coding: utf-8 -*-
# S.D.G

"""
lugito tests
"""

# Imports
import os
import pytest
import phabricator
import json
import http
from lugito import Lugito
from unittest.mock import MagicMock

# Setup ###############################################################

TEST_DIR = os.path.dirname(__file__)

# Force phabricator to use the ./tests/.arcconfig file
TEST_CONFIG = os.path.join(TEST_DIR, '.arcconfig')

with open(TEST_CONFIG, 'r') as f:
    phabricator.ARCRC = json.load(f)

# Pre-prepared request
FAKE_REQUEST = os.path.join(TEST_DIR, 'request.json')

FAKE_REQ_DATA = os.path.join(TEST_DIR, 'fake_req_data.json')
FAKE_TRANSACTION = os.path.join(TEST_DIR, 'fake_transaction.json')
FAKE_TRANSACTION_NEW_OBJECT = os.path.join(
    TEST_DIR, 'fake_transaction_new_object.json')

FAKE_REQ_NEW_COMMENT = os.path.join(TEST_DIR, 'fake_req_data_new_comment.json')
FAKE_NEW_COMMENT = os.path.join(TEST_DIR, 'fake_transaction_new_comment.json')

FAKE_REQ_EDITED_COMMENT = os.path.join(TEST_DIR,
    'fake_req_data_edit_comment.json')
FAKE_EDITED_COMMENT = os.path.join(TEST_DIR,
    'fake_transaction_edit_comment.json')

# Tests ###############################################################

def test_init():
    """Test initialise lugito"""

    obj = Lugito()

    assert('http://127.0.0.1:9091/api/' in obj.phab.host)
    assert('api-nojs2ip33hmp4zn6u6cf72w7d6yh' in obj.phab.token)
    assert(obj.HMAC['diffhook'] == bytes(u'vglzi6t4gsumnilv27r27no7rs3vgs75',
        'utf-8'))
    assert(obj.HMAC['commithook'] == bytes(u'znkyfflbcia5gviqx5ybad7s6uyfywxi',
        'utf-8'))


def test_validate_HMAC():
    """Test validating HMAC"""

    obj = Lugito()

    request_mock = MagicMock()

    with open(FAKE_REQ_DATA, 'r') as f:
        request_mock.data = f.read().encode()

    request_mock.headers = {
        "X-Phabricator-Webhook-Signature":
        "a8f636f03ed4464ddb398ea873ffab409d941f87396f28fa9d22bb58cfbedc9f"
    }

    assert(obj.validate_HMAC('diffhook', request_mock))


def test_invalid_HMAC():
    """Test validating HMAC"""

    obj = Lugito()

    request_mock = MagicMock()

    with open(FAKE_REQ_DATA, 'r') as f:
        request_mock.data = f.read().encode()

    request_mock.headers = {
        "X-Phabricator-Webhook-Signature":
        "a8f6364464ddb398ea873ffab409d941f87396f28fa9d22bb58cfbedc9f"
    }

    assert(not obj.validate_HMAC('diffhook', request_mock))


def test_author_fullname():
    """Test get the author name"""

    obj = Lugito()

    with open(FAKE_REQ_DATA, 'r') as f:
        obj.request_data = json.load(f)

    with open(FAKE_TRANSACTION, 'r') as f:
        obj.transaction = json.load(f)

    obj.phab = MagicMock()
    obj.phab.phid.query = MagicMock(return_value={
        'PHID-USER-5cmhaqtkggymhvbyqdcv':{
            'fullName': 'AuthorName',
            },
        }
    )

    author_name = obj.get_author_fullname()
    assert(author_name == 'AuthorName')


def test_author_fullname_error():
    """Test unable to get the author name"""

    obj = Lugito()

    with open(FAKE_REQ_DATA, 'r') as f:
        obj.request_data = json.load(f)

    with open(FAKE_TRANSACTION, 'r') as f:
        obj.transaction = json.load(f)

    obj.phab = MagicMock()
    obj.phab.phid.query = MagicMock(side_effect=http.client.HTTPException)

    author_name = obj.get_author_fullname()
    assert(author_name is None)


def test_get_object_type():
    """Test get object type"""

    obj = Lugito()

    with open(FAKE_REQ_DATA, 'r') as f:
        obj.request_data = json.load(f)

    obj._transaction_search()

    assert(obj.get_object_type() == 'DREV')

def test_is_new_object_false():
    """Test is new task - false"""

    obj = Lugito()

    with open(FAKE_REQ_DATA, 'r') as f:
        obj.request_data = json.load(f)

    with open(FAKE_TRANSACTION, 'r') as f:
        obj.transaction = json.load(f)

    assert (not obj.is_new_object())

def test_is_new_object_true():
    """Test is new task - true"""

    obj = Lugito()

    with open(FAKE_REQ_DATA, 'r') as f:
        obj.request_data = json.load(f)

    with open(FAKE_TRANSACTION_NEW_OBJECT, 'r') as f:
        obj.transaction = json.load(f)

    assert (obj.is_new_object())


def test_is_new_comment():
    """Test checking for new  - using transaction search"""

    obj = Lugito()

    with open(FAKE_REQ_NEW_COMMENT, 'r') as f:
        obj.request_data = json.load(f)

    with open(FAKE_NEW_COMMENT, 'r') as f:
        obj.transaction = json.load(f)

    new_comment, edited, _id = obj.is_comment()

    assert(new_comment)
    assert(not edited)
    assert(_id == 133)


def test_is_edited_comment():
    """Test checking for edited comment"""

    obj = Lugito()

    with open(FAKE_REQ_EDITED_COMMENT, 'r') as f:
        obj.request_data = json.load(f)

    with open(FAKE_EDITED_COMMENT, 'r') as f:
        obj.transaction = json.load(f)

    new_comment, edited, _id = obj.is_comment()

    assert(not new_comment)
    assert(edited)
    assert(_id == 157)
