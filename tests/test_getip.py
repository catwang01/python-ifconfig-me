from unittest import mock
from unittest.mock import Mock, patch

import pytest

from python_ifconfig_me import getIPsAsync

class MockResponse:
    def __init__(self, text, status):
        self._text = text
        self.status = status

    async def text(self):
        return self._text

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def __aenter__(self):
        return self

@pytest.mark.asyncio
@patch("aiohttp.ClientSession.get")
async def test_getIPs_default(mock_get):
    mock_get.return_value = MockResponse("127.0.0.1", 200)

    result = await getIPsAsync()

    assert result is not None
    assert result.ip == "127.0.0.1"