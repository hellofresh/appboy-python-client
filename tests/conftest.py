from __future__ import absolute_import
import pytest

from braze.client import BrazeClient


@pytest.fixture
def braze_client():
    return BrazeClient(api_key='API_KEY')
