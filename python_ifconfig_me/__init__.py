import asyncio
import json
import logging
from dataclasses import dataclass
from typing import List, Optional, TypedDict, Unpack

import aiohttp

from python_ifconfig_me.ipretriever.callbackIPRetriever import CallbackIPRetriever
from python_ifconfig_me.ipretriever.IPRetriever import (
    IPResultObject,
    IPRetriever,
    IPRetrieverContext,
)
from python_ifconfig_me.ipretriever.simpleTextIPRetriever import SimpleTextIPRetriever
from python_ifconfig_me.vote.votingStrategy import (
    SimpleVotingStrategy,
    VotingResult,
    VotingStrategyContext,
)

logger = logging.getLogger(__name__)

DEFAULT_IP_RETRIEVERS: List[IPRetriever] = []


def populateDefaultIPList(ipRetrievers: List[IPRetriever]) -> None:
    URLS = [
        "https://ifconfig.me/ip",
        "https://checkip.amazonaws.com",
        "https://icanhazip.com",
        "https://ifconfig.co/ip",
        "https://ipecho.net/plain",
        "https://ipinfo.io/ip",
    ]
    for url in URLS:
        ipRetrievers.append(SimpleTextIPRetriever(url))
    ipRetrievers.append(
        CallbackIPRetriever(
            "https://httpbin.org/ip",
            lambda text: json.loads(text).get("origin").strip(),
        )
    )
    ipRetrievers.append(
        CallbackIPRetriever(
            "https://api.ipify.org/?format=json",
            lambda text: json.loads(text).get("ip").strip(),
        )
    )


populateDefaultIPList(DEFAULT_IP_RETRIEVERS)


@dataclass
class GetIPsOptions:
    return_statistics: bool = False
    ipv6: bool = False
    ipv4: bool = False
    prefer_ipv4: bool = True
    timeout: int = 5


class RetrieveIPsAsyncKwargs(TypedDict):
    timeout: int


async def retrieveIPsAsync(
    ipRetrievers: List[IPRetriever],
    **kwargs: Unpack[RetrieveIPsAsyncKwargs],
) -> List[IPResultObject]:
    timeout = kwargs.get("timeout", 5)
    context = IPRetrieverContext(session=aiohttp.ClientSession(), timeout=timeout)
    async with context.session:
        tasks = [ipRetriever.getIPAsync(context) for ipRetriever in ipRetrievers]
        results = await asyncio.gather(*tasks)

    return results


async def getIPsAsync(
    options: Optional[GetIPsOptions] = None,
    ipRetrievers: Optional[List[IPRetriever]] = None,
    votingStrategy: Optional[SimpleVotingStrategy] = None,
) -> Optional[VotingResult]:
    if options is None:
        options = GetIPsOptions()
    if ipRetrievers is None:
        ipRetrievers = DEFAULT_IP_RETRIEVERS
    ipResults = await retrieveIPsAsync(ipRetrievers, timeout=options.timeout)
    context = VotingStrategyContext(
        prefer_ipv4=options.prefer_ipv4,
        ipv4=options.ipv4,
        ipv6=options.ipv6,
        return_statistics=options.return_statistics,
    )
    if votingStrategy is None:
        votingStrategy = SimpleVotingStrategy()
    votingResult = votingStrategy.vote(ipResults, context)
    return votingResult
