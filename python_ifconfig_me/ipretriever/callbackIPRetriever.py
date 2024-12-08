import logging

from python_ifconfig_me.ipretriever.IPRetriever import IPObject, IPResultObject
from python_ifconfig_me.ipretriever.IPRetriever import IPRetriever
from python_ifconfig_me.ipretriever.IPRetriever import IPRetrieverContext


import aiohttp

logger = logging.getLogger(__name__)


class CallbackIPRetriever(IPRetriever):

    def __init__(self, url: str, callback, priority: int = 0) -> None:
        self.url = url
        self.priority = priority
        self._callback = callback

    async def getIPAsync(self, context: IPRetrieverContext) -> IPResultObject:
        session = context.session
        timeout = aiohttp.ClientTimeout(context.timeout)

        ip = None
        try:
            async with session.get(self.url, timeout=timeout) as response:
                if response.status == 200:
                    text = await response.text()
                    ip = self._callback(text)
        except Exception as e:
            logger.warning(
                f"Run into error making API call to {self.url} due to error {e}"
            )
        return IPResultObject(IPObject(ip), retriever=self, priority=self.priority)
