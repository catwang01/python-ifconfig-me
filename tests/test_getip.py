from typing import List
from unittest.mock import patch

import pytest

from python_ifconfig_me import GetIPsOptions, getIPsAsync
from python_ifconfig_me.ipretriever.IPRetriever import IPObject, IPRetriever
from python_ifconfig_me.ipretriever.simpleTextIPRetriever import \
    SimpleTextIPRetriever
from python_ifconfig_me.vote.votingStrategy import (VotingResult,
                                                    VotingStatisticsItem)


@pytest.fixture
def retriever1():
    return SimpleTextIPRetriever("example.com")


@pytest.fixture
def retriever2():
    return SimpleTextIPRetriever("example2.com")


@pytest.fixture
def retriever3():
    return SimpleTextIPRetriever("example3.com")


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
async def test_getIPs_default(mock_get, retriever1):
    ip = "127.0.0.1"
    mock_get.return_value = MockResponse(ip, 200)

    ipRetrievers: List[IPRetriever] = [retriever1]
    result = await getIPsAsync(ipRetrievers=ipRetrievers)

    assert result == VotingResult(ip=ip, statistics=[])


@pytest.mark.parametrize(
    "retrievers",
    [
        [SimpleTextIPRetriever("example.com")],
        [SimpleTextIPRetriever("example.com"), SimpleTextIPRetriever("example2.com")],
    ],
)
@pytest.mark.asyncio
@patch("aiohttp.ClientSession.get")
async def test_getIPs_return_statistics(mock_get, retrievers):
    ip = "127.0.0.1"
    mock_get.return_value = MockResponse(ip, 200)

    options = GetIPsOptions(return_statistics=True)
    result = await getIPsAsync(options=options, ipRetrievers=retrievers)

    assert result == VotingResult(
        ip=ip,
        statistics=[
            VotingStatisticsItem(
                ipObject=IPObject(ip), weight=len(retrievers), retrievers=retrievers
            )
        ],
    )


@pytest.mark.asyncio
@patch("aiohttp.ClientSession.get")
async def test_getIPs_most_common_ip_will_be_returned(mock_get, retriever1, retriever2):
    ip = "127.0.0.1"
    ip2 = "127.0.0.2"

    def side_effect(url, **kwargs):
        if url == retriever1.url:
            return MockResponse(ip, 200)
        elif url == retriever2.url:
            return MockResponse(ip2, 200)
        else:
            raise ValueError(f"Unexpected url: {url}")

    mock_get.side_effect = side_effect
    retrievers: List[IPRetriever] = [
        retriever1,
        retriever2,
        retriever2,
    ]
    options = GetIPsOptions(return_statistics=True)
    result = await getIPsAsync(options=options, ipRetrievers=retrievers)

    assert result == VotingResult(
        ip=ip2,
        statistics=[
            VotingStatisticsItem(
                ipObject=IPObject(ip2), weight=2, retrievers=[retriever2, retriever2]
            ),
            VotingStatisticsItem(
                ipObject=IPObject(ip), weight=1, retrievers=[retriever1]
            ),
        ],
    )


@pytest.mark.asyncio
@patch("aiohttp.ClientSession.get")
async def test_getIPs_most_common_ip_only_return_ipv6(mock_get, retriever1, retriever2):
    ipv4 = "127.0.0.1"
    ipv6 = "2001:0db8:85a3:0000:0000:8a2e:0370:7334"

    def side_effect(url, **kwargs):
        if url == retriever1.url:
            return MockResponse(ipv4, 200)
        elif url == retriever2.url:
            return MockResponse(ipv6, 200)
        else:
            raise ValueError(f"Unexpected url: {url}")

    mock_get.side_effect = side_effect
    retrievers: List[IPRetriever] = [retriever1, retriever1, retriever2]
    options = GetIPsOptions(return_statistics=True, ipv6=True)
    result = await getIPsAsync(options=options, ipRetrievers=retrievers)

    assert result == VotingResult(
        ip=ipv6,
        statistics=[
            VotingStatisticsItem(
                ipObject=IPObject(ipv6), weight=1, retrievers=[retriever2]
            )
        ],
    )


@pytest.mark.asyncio
@patch("aiohttp.ClientSession.get")
async def test_getIPs_most_common_ip_prefer_ipv4_works_when_both_have_the_same_weight(
    mock_get, retriever1, retriever2
):
    ipv4 = "127.0.0.1"
    ipv6 = "0001:0db8:85a3:0000:0000:8a2e:0370:7334"

    def side_effect(url, **kwargs):
        if url == retriever1.url:
            return MockResponse(ipv4, 200)
        elif url == retriever2.url:
            return MockResponse(ipv6, 200)
        else:
            raise ValueError(f"Unexpected url: {url}")

    mock_get.side_effect = side_effect
    retrievers: List[IPRetriever] = [retriever1, retriever2]
    options = GetIPsOptions(return_statistics=True)
    result = await getIPsAsync(options=options, ipRetrievers=retrievers)

    assert result == VotingResult(
        ip=ipv4,
        statistics=[
            VotingStatisticsItem(
                ipObject=IPObject(ipv4), weight=1, retrievers=[retriever1]
            ),
            VotingStatisticsItem(
                ipObject=IPObject(ipv6), weight=1, retrievers=[retriever2]
            ),
        ],
    )


@pytest.mark.asyncio
@patch("aiohttp.ClientSession.get")
async def test_getIPs_most_common_ip_prefer_ipv6_works_when_both_have_the_same_weight(
    mock_get, retriever1, retriever2
):
    ipv4 = "127.0.0.1"
    ipv6 = "2001:0db8:85a3:0000:0000:8a2e:0370:7334"

    def side_effect(url, **kwargs):
        if url == retriever1.url:
            return MockResponse(ipv4, 200)
        elif url == retriever2.url:
            return MockResponse(ipv6, 200)
        else:
            raise ValueError(f"Unexpected url: {url}")

    mock_get.side_effect = side_effect
    retrievers: List[IPRetriever] = [retriever1, retriever2]
    options = GetIPsOptions(return_statistics=True, prefer_ipv4=False)
    result = await getIPsAsync(options=options, ipRetrievers=retrievers)

    assert result == VotingResult(
        ip=ipv6,
        statistics=[
            VotingStatisticsItem(
                ipObject=IPObject(ipv6), weight=1, retrievers=[retriever2]
            ),
            VotingStatisticsItem(
                ipObject=IPObject(ipv4), weight=1, retrievers=[retriever1]
            ),
        ],
    )


@pytest.mark.asyncio
@patch("aiohttp.ClientSession.get")
async def test_getIPs_most_common_ip_prefer_ipv6_doesnt_work_when_dont_have_the_same_weight(
    mock_get, retriever1, retriever2
):
    ipv4 = "127.0.0.1"
    ipv6 = "2001:0db8:85a3:0000:0000:8a2e:0370:7334"

    def side_effect(url, **kwargs):
        if url == retriever1.url:
            return MockResponse(ipv4, 200)
        elif url == retriever2.url:
            return MockResponse(ipv6, 200)
        else:
            raise ValueError(f"Unexpected url: {url}")

    mock_get.side_effect = side_effect
    retrievers: List[IPRetriever] = [retriever1, retriever1, retriever2]
    options = GetIPsOptions(return_statistics=True, prefer_ipv4=False)
    result = await getIPsAsync(options=options, ipRetrievers=retrievers)

    assert result == VotingResult(
        ip=ipv4,
        statistics=[
            VotingStatisticsItem(
                ipObject=IPObject(ipv4), weight=2, retrievers=[retriever1, retriever1]
            ),
            VotingStatisticsItem(
                ipObject=IPObject(ipv6), weight=1, retrievers=[retriever2]
            ),
        ],
    )


@pytest.mark.asyncio
@patch("aiohttp.ClientSession.get")
async def test_getIPs_most_common_ip_failed_retriever_are_ignored(
    mock_get, retriever1,
):
    ipv4 = "127.0.0.1"

    # Simulate the case where the second retriever failed
    mock_get.side_effect = [MockResponse(ipv4, 200), MockResponse(ipv4, 404), MockResponse(ipv4, 200)]
    retrievers: List[IPRetriever] = [retriever1] * 3
    options = GetIPsOptions(return_statistics=True, prefer_ipv4=False)
    result = await getIPsAsync(options=options, ipRetrievers=retrievers)

    assert result == VotingResult(
        ip=ipv4,
        statistics=[
            VotingStatisticsItem(
                ipObject=IPObject(ipv4), weight=2, retrievers=[retriever1] * 2
            ),
        ],
    )