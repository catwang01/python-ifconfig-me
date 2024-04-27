import argparse
import asyncio
import json
from collections import Counter
from dataclasses import dataclass
from typing import Optional

import aiohttp


@dataclass
class GetIPsArgs:
    return_statistics: bool=False

@dataclass
class GetIPsResult:
    ip: str
    statistics: list

@dataclass
class MainArgs:
    show_statistics: bool=False

async def make_async_api_call(session, api_url, callback):
    try:
        async with session.get(api_url, timeout=1) as response:
            if response.status == 200:
                return callback(await response.text())
    except Exception as e:
        print(f"Run into error making API call to {api_url}: {e}")
    return None

async def get_async_ips(args: GetIPsArgs) -> Optional[GetIPsResult]:
    api_urls = {
        'https://ifconfig.me/ip': lambda text: text,
        'https://httpbin.org/ip': lambda text: json.loads(text).get('origin'),
        'https://api.ipify.org/?format=json' : lambda text: json.loads(text).get('ip')
    }

    async with aiohttp.ClientSession() as session:
        tasks = [make_async_api_call(session, api_url, callback) for api_url, callback in api_urls.items()]
        results = await asyncio.gather(*tasks)

    results = [result for result in results if result is not None]
    # Choose the most frequently occurring result
    if results:
        counter = list(Counter(results).items())
        counter.sort(key=lambda x: (x[1], -len(x[0])), reverse=True)
        most_common_result = counter[0][0]
        statistics = counter if args.return_statistics else None
        return GetIPsResult(ip=most_common_result, statistics=statistics)
    return None

    
def get_ips(args: Optional[GetIPsArgs]=None) -> Optional[GetIPsResult]:
    if args is None:
        args = GetIPsArgs()
    return asyncio.run(get_async_ips(args))

def get_args() -> MainArgs:
    parser = argparse.ArgumentParser()
    parser.add_argument("--show-statistics", action='store_true', default=False)
    args = parser.parse_args(namespace=MainArgs())
    return args

def main():
    args = get_args()
    getIPsArgs = GetIPsArgs(return_statistics=args.show_statistics)
    try:
        result = get_ips(getIPsArgs)
        if result is None:
            print("Failed to detect any IP")
        else:
            if args.show_statistics:
                print(f"{result.statistics}")
            print(f"{result.ip}")
    except Exception as e:
        print("No successful API call with status code 200.")

if __name__ == "__main__":
    main()