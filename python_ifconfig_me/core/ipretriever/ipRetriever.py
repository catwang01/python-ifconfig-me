from dataclasses import dataclass
from typing import Optional, Protocol

import aiohttp

from python_ifconfig_me.core.ipObject import IPObject


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
