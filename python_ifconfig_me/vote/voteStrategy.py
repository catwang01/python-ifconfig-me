from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional

from python_ifconfig_me.vote.statisticsInformationItem import StatisticsInformationItem
from python_ifconfig_me.ipretriever.IPRetriever import IPResultObject


@dataclass
class VotingResult:
    ip: str
    statistics: list[StatisticsInformationItem]


@dataclass
class VotingStrategyContext:
    prefer_ipv4: bool
    ipv4: bool
    ipv6: bool


class IVotingStrategy(metaclass=ABCMeta):

    @abstractmethod
    def vote(
        self, results: List[IPResultObject], context: VotingStrategyContext
    ) -> Optional[VotingResult]:
        pass


class SimpleVotingStrategy(IVotingStrategy):

    def vote(
        self, results: List[IPResultObject], context: VotingStrategyContext
    ) -> Optional[VotingResult]:
        ipv4_list = []
        ipv6_list = []
        for result in results:
            if result.ipObject.isIPv4():
                ipv4_list.append(result)
            elif result.ipObject.isIPv6():
                ipv6_list.append(result)

        candidates: list[IPResultObject]
        if context.ipv6:
            candidates = ipv6_list
        elif context.ipv4:
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
                statisticsDict[ip] = StatisticsInformationItem(candidate.ipObject)
            else:
                statisticsDict[ip].weight += 1
            retriever = candidate.getRetriever()
            if retriever is not None:
                statisticsDict[ip].retrievers.append(retriever)
        statistics = list(statisticsDict.values())
        statistics = sorted(
            statistics,
            key=lambda x: x.getSortKey(context.prefer_ipv4),
            reverse=True,
        )
        return VotingResult(ip=most_common_ip, statistics=statistics)
