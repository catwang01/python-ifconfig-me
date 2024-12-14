from dataclasses import dataclass
from typing import Optional, Protocol

import aiohttp


@dataclass
class IPObject:
    ip: Optional[str] = None

    def isIPv6(self) -> bool:
        return self.ip is not None and ":" in self.ip

    def isIPv4(self) -> bool:
        return self.ip is not None and "." in self.ip


class IPResultObject:

    def __init__(
        self,
        ipObject: IPObject,
        priority: int = 0,
        retriever: Optional["IPRetriever"] = None,
    ) -> None:
        self.ipObject = ipObject
        self.retreiver = retriever
        self.priority = priority

    def getRetriever(self) -> Optional["IPRetriever"]:
        return self.retreiver


@dataclass
class IPRetrieverContext:
    session: aiohttp.ClientSession
    timeout: int


class IPRetriever(Protocol):

    async def getIPAsync(self, context: IPRetrieverContext) -> IPResultObject:
        pass
