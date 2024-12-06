import argparse
from textwrap import indent
import asyncio
import json
import logging
import sys
from collections import Counter
from dataclasses import dataclass
from typing import Any, Optional

import aiohttp

logger = logging.getLogger(__name__)

GLOBAL_TIMEOUT = 5


@dataclass
class GetIPsOptions:
    return_statistics: bool = False
    ipv6: bool = False
    ipv4: bool = False
    prefer_ipv6: bool = False
    prefer_ipv4: bool = True


@dataclass
class CommandLineArgs:
    logLevel: int = logging.ERROR
    show_statistics: bool = False
    ipv6: bool = False
    ipv4: bool = False
    prefer_ipv6: bool = False


@dataclass
class StatisticsInformationItem:
    ip: str
    key: Any


@dataclass
class GetIPsResult:
    ip: str
    statistics: list[StatisticsInformationItem]


async def make_async_api_call(session, api_url, callback):
    try:
        async with session.get(api_url, timeout=GLOBAL_TIMEOUT) as response:
            if response.status == 200:
                text = await response.text()
                return callback(text)
            return None
    except Exception as e:
        logger.warning(f"Run into error making API call to {api_url} due to error {e}")
    return None


def is_ipv6(ip: str) -> bool:
    return ":" in ip


def is_ipv4(ip: str) -> bool:
    return "." in ip


async def get_async_ips(args: GetIPsOptions) -> Optional[GetIPsResult]:
    api_urls = {
        "https://ifconfig.me/ip": lambda text: text.strip(),
        "https://checkip.amazonaws.com": lambda text: text.strip(),
        "https://icanhazip.com": lambda text: text.strip(),
        "https://ifconfig.co/ip": lambda text: text.strip(),
        "https://ipecho.net/plain": lambda text: text.strip(),
        "https://ipinfo.io/ip": lambda text: text.strip(),
        "https://httpbin.org/ip": lambda text: json.loads(text).get("origin").strip(),
        "https://api.ipify.org/?format=json": lambda text: json.loads(text)
        .get("ip")
        .strip(),
    }

    async with aiohttp.ClientSession() as session:
        tasks = [
            make_async_api_call(session, api_url, callback)
            for api_url, callback in api_urls.items()
        ]
        results = await asyncio.gather(*tasks)

    ipv4_list = []
    ipv6_list = []
    for result in results:
        if result is not None:
            if is_ipv4(result):
                ipv4_list.append(result)
            elif is_ipv6(result):
                ipv6_list.append(result)

    candidates: list
    if args.ipv6:
        candidates = ipv6_list
    elif args.ipv4:
        candidates = ipv4_list
    else:
        candidates = ipv4_list + ipv6_list

    if not candidates:
        return None
    # Choose the most frequently occurring result
    counter = list(Counter(candidates).items())
    statistics = []
    for pair in counter:
        ip, frequency = pair
        key = (frequency, is_ipv6(ip) if args.prefer_ipv6 else is_ipv4(ip), ip)
        statistics.append(StatisticsInformationItem(ip, key))
    most_common_result = counter[0][0]
    return GetIPsResult(
        ip=most_common_result, statistics=statistics if args.return_statistics else []
    )


def get_ips(args: Optional[GetIPsOptions] = None) -> Optional[GetIPsResult]:
    if args is None:
        args = GetIPsOptions()
    return asyncio.run(get_async_ips(args))


# parse loglevel from string
def parse_loglevel(logLevelStr: str):
    try:
        return int(logLevelStr)
    except Exception:
        pass
    logLevelStrUpper = logLevelStr.upper()
    if hasattr(logging, logLevelStrUpper):
        return getattr(logging, logLevelStrUpper)
    raise ValueError(f"Can't parse the loglevel from str {logLevelStr!r}")


def get_args(raw_args) -> Optional[CommandLineArgs]:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--loglevel", "--logLevel", "--log-level",
        dest="logLevel",
        type=parse_loglevel,
        default=logging.ERROR,
        help="Logging level, can be either string or positive int. Valid string: [DEBUG, INFO, WARNING, ERROR, CRITICAL]",
    )
    parser.add_argument("--show-statistics", action="store_true", default=False)
    parser.add_argument(
        "--ipv6", action="store_true", default=False, help="Return IPv6 address only. By default, either IPv4 or IPv6 will be returned."
    )
    parser.add_argument(
        "--ipv4", action="store_true", default=False, help="Return IPv4 address only. By default, either IPv4 or IPv6 will be returned."
    )
    parser.add_argument(
        "--prefer-ipv6",
        action="store_true",
        default=False,
        help="Prefer IPv6 over IPv4. By default, prefer IPv4 over IPv6, which means choose IPv4 when the IPv4 and IPv6 have the same frequency. Note that, the preference only matters when a IPv4 and IPv6 have the same frequency. Use this flag to override the default behavior.",
    )
    args = parser.parse_args(raw_args, namespace=CommandLineArgs())
    if args.ipv4 and args.ipv6:
        print("--ipv4 and --ipv6 can't be used together")
        return None
    return args


def main():
    args = get_args(sys.argv[1:])
    if not args:
        return
    logger.setLevel(args.logLevel)
    getIPsArgs = GetIPsOptions(
        return_statistics=args.show_statistics,
        ipv6=args.ipv6,
        ipv4=args.ipv4,
        prefer_ipv6=args.prefer_ipv6,
    )
    try:
        result = get_ips(getIPsArgs)
        if result is None:
            print("Failed to detect any IP")
        else:
            if args.show_statistics:
                print("[")
                for item in result.statistics:
                    # convert dataclass into a dict
                    print(indent(json.dumps(item.__dict__, indent=2), " " * 2))
                print("]")
            print(f"{result.ip}")
    except Exception as e:
        print("No successful API call with status code 200.")


if __name__ == "__main__":
    main()
