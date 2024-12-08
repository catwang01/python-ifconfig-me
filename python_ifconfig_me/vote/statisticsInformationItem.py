from python_ifconfig_me.ipretriever.IPRetriever import IPObject, IPRetriever


from dataclasses import dataclass, field
from typing import Any, List, TypedDict, Unpack


class GetSortKeyKwargs(TypedDict):
    prefer_ipv6: bool


@dataclass
class VotingStatisticsItem:
    ipObject: IPObject
    weight: int = 1
    priority: int = 0
    retrievers: List[IPRetriever] = field(default_factory=list)

    def getSortKey(self, **kwargs: Unpack[GetSortKeyKwargs]) -> Any:
        prefer_ipv6 = kwargs.get("prefer_ipv6", False)
        ip = self.ipObject.ip
        is_ipv6 = int(self.ipObject.isIPv6())
        return (
            self.priority,
            self.weight,
            (is_ipv6 * (1 if prefer_ipv6 else -1)),
            ip,
        )
