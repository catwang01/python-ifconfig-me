# python-ifconfig-me

![](https://img.shields.io/github/actions/workflow/status/catwang01/python-ifconfig-me/python-package.yml)![](https://img.shields.io/github/license/catwang01/python-ifconfig-me)![](https://img.shields.io/github/last-commit/catwang01/python-ifconfig-me)![](https://img.shields.io/pypi/v/python-ifconfig-me)![](https://img.shields.io/codecov/c/github/catwang01/python-ifconfig-me)

## Project Overview

This is a simple Python library to detect the current public IP of your machine.

## Getting Started

### Prerequisites

Python version >= 3.9

### Installation

```bash
pip install python-ifconfig-me
```

## Usage

### Basic usage - Use as a tool

Show help messages:

```python
$ ifconfig-me -h
```

Show the current public ip:

```python
$ ifconfig-me
```

Show statistics used to determine the public IP.

```python
$ ifconfig-me --show-statistics
{
  "ip": "xxx.xxx.xxx.xxx",
  "statistics": [
    {
      "ipObject": {
        "ip": "xxx.xxx.xxx.xxx"
      },
      "weight": 4,
      "priority": 0,
      "retrievers": [
        {
          "url": "https://ifconfig.me/ip",
          "priority": 0
        },
        {
          "url": "https://ipecho.net/plain",
          "priority": 0
        },
        {
          "url": "https://ipinfo.io/ip",
          "priority": 0
        },
        {
          "url": "https://httpbin.org/ip",
          "priority": 0
        }
      ]
    },
    {
      "ipObject": {
        "ip": "xxx.xxx.xxx.xxx\n"
      },
      "weight": 3,
      "priority": 0,
      "retrievers": [
        {
          "url": "https://checkip.amazonaws.com",
          "priority": 0
        },
        {
          "url": "https://icanhazip.com",
          "priority": 0
        },
        {
          "url": "https://ifconfig.co/ip",
          "priority": 0
        }
      ]
    }
  ]
}
xxx.xxx.xxx.xxx
```

Force to return IPv4

```
$ ifconfig-me --ipv4
```

Force to return IPv6

```
$ ifconfig-me --ipv6
```

Prefer ipv4 over ipv6. By default, if an IPv4 address and IPv6 address are both detected and have the same weight (i.e. the same number of services detected them), the IPv4 address is returned. This option forces the IPv6 address to be returned in this case.

Note: This option only takes effect when both an IPv4 address and an IPv6 address have the same weight.

```
$ ifconfig-me --prefer-ipv6
```

Use `--logLevel` to set the log level. The default log level is `ERROR`.

### Advanced usage - Use as a library

#### getPublicIPAsync and getPulicIP

There are two versions of the getPublicIP function: synchronous and asynchronous.

Async version:

```python
import asyncio
from python_ifconfig_me import getPublicIPAsync

asyncio.run(getPublicIPAsync())
```

Sync version:

```python
from python_ifconfig_me import getPublicIP

public = getPublicIP()
```

The sync version is just a wrapper of the async version. If possible, use the async version because it is more efficient.

```python
import asyncio
from python_ifconfig_me import getPublicIPAsync, GetPublicIPOptions

options = GetPublicIPOptions(
    return_statistics=True
)
asyncio.run(getPublicIPAsync(options))
```

#### Use retrievers

You can pass retrievers to the `getPublicIPAsync/getPublicIP` function. A retriever follows the `IPRetriever` protocol.  You can implement your own retriever by inheriting the `IPRetriever` class.

```python
import asyncio
from python_ifconfig_me import getPublicIPAsync, GetPublicIPOptions
from python_ifconfig_me.core.ipretriever.simpleTextIPRetriever import SimpleTextIPRetriever

options = GetPublicIPOptions(
    return_statistics=True
)
retrievers = [
    SimpleTextIPRetriever("https://ifconfig.me/ip"),
]
asyncio.run(getPublicIPAsync(options, retrievers))
```

If you want to add your retriever to the default retrievers, you can use the `DEFAULT_IP_RETRIEVERS` variable.

```python
import asyncio
from python_ifconfig_me import getPublicIPAsync, GetPublicIPOptions
from python_ifconfig_me.core.ipretriever.simpleTextIPRetriever import SimpleTextIPRetriever
from python_ifconfig_me.core.ipretriever import DEFAULT_IP_RETRIEVERS

options = GetPublicIPOptions(
    return_statistics=True
)
retrievers = DEFAULT_IP_RETRIEVERS + [
    SimpleTextIPRetriever("https://ifconfig.me/ip"),
]
asyncio.run(getPublicIPAsync(options, retrievers))
```

## How this project works

The idea behind this library is pretty simple: majority voting among multiple third-party public ip detection services.

As of now, the following services are configured to be used for detention:

- https://checkip.amazonaws.com
- https://icanhazip.com
- https://ifconfig.co/ip
- https://ifconfig.me/ip
- https://ipecho.net/plain
- https://ipinfo.io/ip
- https://httpbin.org/ip
- https://api.ipify.org


## LICENSE

The project is licensed under the GPL license. For more information, please refer to the [LICENSE](./LICENSE) file.