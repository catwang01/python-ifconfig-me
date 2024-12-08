from python_ifconfig_me.ipretriever.IPRetriever import IPObject, IPRetriever


from dataclasses import dataclass, field
from typing import Any, List


@dataclass
class VotingStatisticsItem:
    ipObject: IPObject
    weight: int = 1
    retrievers: List[IPRetriever] = field(default_factory=list)

    def getSortKey(self, prefer_ipv6: bool) -> Any:
        ip = self.ipObject.ip
        is_ipv6 = int(self.ipObject.isIPv6())
        return (
            self.ipObject.priority,
            self.weight,
            (is_ipv6 * (1 if prefer_ipv6 else -1)),
            ip,
        )
