import json
import asyncio
import aiohttp
from collections import Counter
import argparse

async def make_async_api_call(session, api_url, callback):
    try:
        async with session.get(api_url, timeout=1) as response:
            if response.status == 200:
                return callback(await response.text())
    except Exception as e:
        print(f"Error making API call: {e}")
    return None

async def get_async_ips(args):
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
        counter = Counter(results)
        if args.show_statistics:
            print("statistics: ", counter)
        most_common_result = counter.most_common(1)[0][0]
        print(f"{most_common_result}")
    else:
        print("No successful API call with status code 200.")

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--show-statistics", action='store_true', default=False)
    args = parser.parse_args()
    return args

def main():
    args = get_args()
    # Run the asynchronous function
    asyncio.run(get_async_ips(args))
