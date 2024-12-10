import logging

from python_ifconfig_me.ipretriever.callbackIPRetriever import CallbackIPRetriever

logger = logging.getLogger(__name__)


class SimpleTextIPRetriever(CallbackIPRetriever):

    def __init__(self, url: str, priority: int = 0) -> None:
        self.url = url
        self.priority = priority
        super().__init__(url, lambda text: text, priority)
