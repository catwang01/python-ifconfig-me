from dataclasses import dataclass
from typing import Dict, List, Optional, Protocol, Tuple

from python_ifconfig_me.ipretriever.IPRetriever import IPResultObject
from python_ifconfig_me.vote.statisticsInformationItem import VotingStatisticsItem


@dataclass
class VotingResult:
    ip: str
    statistics: list[VotingStatisticsItem]


@dataclass
class VotingStrategyContext:
    prefer_ipv6: bool
    ipv4: bool
    ipv6: bool
    return_statistics: bool = False


class IVotingStrategy(Protocol):

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

        statisticsDict: Dict[Tuple[str, int], VotingStatisticsItem] = {}
        for candidate in candidates:
            ip = candidate.ipObject.ip
            if ip is None:
                continue
            priority = candidate.priority
            key = (ip, priority)
            if key not in statisticsDict:
                statisticsDict[key] = VotingStatisticsItem(
                    candidate.ipObject, priority=priority
                )
            else:
                statisticsDict[key].weight += 1
            retriever = candidate.getRetriever()
            if retriever is not None:
                statisticsDict[key].retrievers.append(retriever)

        statistics = list(statisticsDict.values())
        statistics = sorted(
            statistics,
            key=lambda x: x.getSortKey(prefer_ipv6=context.prefer_ipv6),
            reverse=True,
        )
        most_common_ip = statistics[0].ipObject.ip
        if most_common_ip is None:
            return None
        return VotingResult(
            ip=most_common_ip,
            statistics=statistics if context.return_statistics else [],
        )
