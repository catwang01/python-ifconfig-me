import asyncio
import json
import logging
from dataclasses import dataclass
from typing import List, Optional

import aiohttp

from python_ifconfig_me.ipretriever.callbackIPRetriever import CallbackIPRetriever
from python_ifconfig_me.ipretriever.IPRetriever import (
    IPResultObject,
    IPRetriever,
    IPRetrieverContext,
)
from python_ifconfig_me.ipretriever.simpleTextIPRetriever import SimpleTextIPRetriever
from python_ifconfig_me.vote.voteStrategy import (
    SimpleVoteStrategy,
    VoteResult,
    VoteStrategyContext,
)

logger = logging.getLogger(__name__)

GLOBAL_TIMEOUT = 5

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
    prefer_ipv6: bool = False
    prefer_ipv4: bool = True


async def retrieveIPsAsync(
    ipRetrievers: List[IPRetriever],
) -> List[IPResultObject]:
    async with aiohttp.ClientSession() as session:
        context = IPRetrieverContext(
            session=session,
            timeout=GLOBAL_TIMEOUT,
        )
        tasks = [ipRetriever.getIPAsync(context) for ipRetriever in ipRetrievers]
        results = await asyncio.gather(*tasks)

    return results


def getIPs(
    args: Optional[GetIPsOptions] = None,
    ipRetrievers: Optional[List[IPRetriever]] = None,
    voteStrategy: Optional[SimpleVoteStrategy] = None,
) -> Optional[VoteResult]:
    if args is None:
        args = GetIPsOptions()
    if ipRetrievers is None:
        ipRetrievers = DEFAULT_IP_RETRIEVERS
    ipResults = asyncio.run(retrieveIPsAsync(ipRetrievers))
    context = VoteStrategyContext(
        prefer_ipv4=args.prefer_ipv4, ipv4=args.ipv4, ipv6=args.ipv6
    )
    if voteStrategy is None:
        voteStrategy = SimpleVoteStrategy()
    votedResult = voteStrategy.vote(ipResults, context)
    return votedResult