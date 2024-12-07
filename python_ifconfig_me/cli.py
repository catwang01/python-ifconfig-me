import argparse
import json
import logging
import sys
from dataclasses import dataclass, is_dataclass
from json import JSONEncoder
from typing import Optional

from python_ifconfig_me import GetIPsOptions, getIPs
from python_ifconfig_me.ipretriever.callbackIPRetriever import CallbackIPRetriever
from python_ifconfig_me.ipretriever.IPRetriever import IPResultObject
from python_ifconfig_me.ipretriever.simpleTextIPRetriever import SimpleTextIPRetriever
from python_ifconfig_me.utils import parse_loglevel

logger = logging.getLogger(__name__)


class CustomJSONEncoder(JSONEncoder):

    def default(self, obj):
        if is_dataclass(obj) or isinstance(
            obj, (IPResultObject, SimpleTextIPRetriever, CallbackIPRetriever)
        ):
            return {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}
        return super().default(obj)


@dataclass
class CommandLineArgs:
    logLevel: int = logging.ERROR
    show_statistics: bool = False
    ipv6: bool = False
    ipv4: bool = False
    prefer_ipv6: bool = False


def get_args(raw_args) -> Optional[CommandLineArgs]:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--loglevel",
        "--logLevel",
        "--log-level",
        dest="logLevel",
        type=parse_loglevel,
        default=logging.ERROR,
        help="Logging level, can be either string or positive int. Valid string: [DEBUG, INFO, WARNING, ERROR, CRITICAL]",
    )
    parser.add_argument("--show-statistics", action="store_true", default=False)
    parser.add_argument(
        "--ipv6",
        action="store_true",
        default=False,
        help="Return IPv6 address only. By default, either IPv4 or IPv6 will be returned.",
    )
    parser.add_argument(
        "--ipv4",
        action="store_true",
        default=False,
        help="Return IPv4 address only. By default, either IPv4 or IPv6 will be returned.",
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
    result = getIPs(getIPsArgs)
    if result is None:
        print("No successful API call with status code 200.")
    else:
        if args.show_statistics:
            print(json.dumps(result, cls=CustomJSONEncoder, indent=2))
        print(f"{result.ip}")


if __name__ == "__main__":
    main()
