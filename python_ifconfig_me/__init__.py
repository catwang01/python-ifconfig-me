import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import aiohttp

from python_ifconfig_me.ipretriever.IPRetriever import IPObject, IPResultObject
from python_ifconfig_me.ipretriever.callbackIPRetriever import CallbackIPRetriever
from python_ifconfig_me.ipretriever.IPRetriever import IPRetriever
from python_ifconfig_me.ipretriever.IPRetriever import IPRetrieverContext
from python_ifconfig_me.ipretriever.simpleTextIPRetriever import SimpleTextIPRetriever

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


@dataclass
class StatisticsInformationItem:
    ipObject: IPObject
    weight: int = 1
    retrievers: List[IPRetriever] = field(default_factory=list)

    def getSortKey(self, prefer_ipv6: bool) -> Any:
        ip = self.ipObject.ip
        return (
            self.ipObject.priority,
            self.weight,
            (self.ipObject.isIPv6() if prefer_ipv6 else self.ipObject.isIPv4()),
            ip,
        )


@dataclass
class GetIPsResult:
    ip: str
    statistics: list[StatisticsInformationItem]


async def get_async_ips(
    ipRetrievers: Optional[List[IPRetriever]] = None
) -> List[IPResultObject]:
    if ipRetrievers is None:
        ipRetrievers = DEFAULT_IP_RETRIEVERS
    async with aiohttp.ClientSession() as session:
        context = IPRetrieverContext(
            session=session,
            timeout=GLOBAL_TIMEOUT,
        )
        tasks = [ipRetriever.getIPAsync(context) for ipRetriever in ipRetrievers]
        results = await asyncio.gather(*tasks)

    return results


def find_most_common_ip(
    results: List[IPResultObject], args: GetIPsOptions
) -> Optional[GetIPsResult]:
    ipv4_list = []
    ipv6_list = []
    for result in results:
        if result.ipObject.isIPv4():
            ipv4_list.append(result)
        elif result.ipObject.isIPv6():
            ipv6_list.append(result)

    candidates: list[IPResultObject]
    if args.ipv6:
        candidates = ipv6_list
    elif args.ipv4:
        candidates = ipv4_list
    else:
        candidates = ipv4_list + ipv6_list

    if not candidates:
        return None

    statisticsDict: Dict[str, StatisticsInformationItem] = {}
    most_common_item: Optional[StatisticsInformationItem] = None
    for candidate in candidates:
        ip = candidate.ipObject.ip
        if ip is None:
            continue
        if (
            most_common_item is None
            or most_common_item.weight < statisticsDict[ip].weight
        ):
            most_common_ip = ip
        if ip not in statisticsDict:
            statisticsDict[ip] = StatisticsInformationItem(candidate.ipObject, 1)
        else:
            statisticsDict[ip].weight += 1
        retriever = candidate.getRetriever()
        if retriever is not None:
            statisticsDict[ip].retrievers.append(retriever)
    statistics = list(statisticsDict.values())
    statistics = sorted(
        statistics, key=lambda x: x.getSortKey(args.prefer_ipv4), reverse=True
    )
    return GetIPsResult(ip=most_common_ip, statistics=statistics)


def get_ips(args: Optional[GetIPsOptions] = None) -> Optional[GetIPsResult]:
    if args is None:
        args = GetIPsOptions()
    ipResults = asyncio.run(get_async_ips())
    return find_most_common_ip(ipResults, args)
