import json
from typing import List

from python_ifconfig_me.core.ipretriever.simpleTextIPRetriever import (
    SimpleTextIPRetriever,
)
from python_ifconfig_me.core.ipretriever.ipRetriever import IPRetriever
from python_ifconfig_me.core.ipretriever.callbackIPRetriever import CallbackIPRetriever


DEFAULT_IP_RETRIEVERS: List[IPRetriever] = []


def populateDefaultIPList(ipRetrievers: List[IPRetriever]) -> None:
    URLS = [
        "https://ifconfig.me/ip",
        "https://checkip.amazonaws.com",
        "https://icanhazip.com",
        "https://ifconfig.co/ip",
        "https://ipecho.net/plain",
        "https://ipinfo.io/ip",
    ]
    for url in URLS:
        ipRetrievers.append(SimpleTextIPRetriever(url))
    ipRetrievers.append(
        CallbackIPRetriever(
            "https://httpbin.org/ip",
            lambda text: json.loads(text).get("origin").strip(),
        )
    )
    ipRetrievers.append(
        CallbackIPRetriever(
            "https://api.ipify.org/?format=json",
            lambda text: json.loads(text).get("ip").strip(),
        )
    )


populateDefaultIPList(DEFAULT_IP_RETRIEVERS)
