from dataclasses import dataclass
import json
import asyncio
from typing import Callable, Optional
import aiohttp
from collections import Counter
import argparse

async def make_async_api_call(session: aiohttp.ClientSession, 
                              api_url: str, 
                              callback: Callable[[str], Optional[str]]) -> Optional[str]:
    try:
        async with session.get(api_url, timeout=1) as response:
            if response.status == 200:
                return callback(await response.text())
    except Exception as e:
        print(f"Run into error making API call to {api_url}: {e}")
    return None

@dataclass
class GetIpArgs:
    show_statistics: bool = None

async def get_ip_async(args: GetIpArgs) -> Optional[str]:
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
        if args.show_statistics:
            print("statistics: ", counter)
        most_common_result = counter[0][0]
        return most_common_result
    return None

def get_ip(args) -> Optional[str]:
    return asyncio.run(get_ip_async(args))

def get_args() -> GetIpArgs:
    parser = argparse.ArgumentParser()
    parser.add_argument("--show-statistics", action='store_true', default=False)
    args = parser.parse_args(namespace=GetIpArgs())
    return args

def main():
    args = get_args()
    try:
        ip = get_ip(args)
        print(f"{ip}")
    except Exception as e:
        print("No successful API call with status code 200.")

if __name__ == "__main__":
    main()