import logging
import aiohttp

from python_ifconfig_me.ipretriever.IPRetriever import IPObject, IPResultObject
from python_ifconfig_me.ipretriever.IPRetriever import IPRetriever
from python_ifconfig_me.ipretriever.IPRetriever import IPRetrieverContext

logger = logging.getLogger(__name__)


class SimpleTextIPRetriever(IPRetriever):

    def __init__(self, url: str) -> None:
        self.url = url

    async def getIPAsync(self, context: IPRetrieverContext) -> IPResultObject:
        session = context.session
        timeout = aiohttp.ClientTimeout(context.timeout)

        ip = None
        try:
            async with session.get(self.url, timeout=timeout) as response:
                if response.status == 200:
                    ip = (await response.text()).strip()
        except Exception as e:
            logger.warning(
                f"Run into error making API call to {self.url} due to error: {e}"
            )
        return IPResultObject(IPObject(ip), retriever=self)
