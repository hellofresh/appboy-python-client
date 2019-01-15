from __future__ import absolute_import

from braze.client import BrazeClient
import pytest


@pytest.fixture
def braze_client():
    return BrazeClient(api_key="API_KEY")
