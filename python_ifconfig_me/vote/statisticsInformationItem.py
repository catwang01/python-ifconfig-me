from python_ifconfig_me.ipretriever.IPRetriever import IPObject, IPRetriever


from dataclasses import dataclass, field
from typing import Any, List


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
