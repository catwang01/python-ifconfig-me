[TOC]

## What this package does

This is a simple python library used to detect the current public ip.

## How this package works

The idea behind this library is pretty simple: majority voting among multiple public ip detection services.

AAs of now the following services are configured to be used for detention:

- https://checkip.amazonaws.com
- https://icanhazip.com
- https://ifconfig.co/ip
- https://ifconfig.me/ip
- https://ipecho.net/plain
- https://ipinfo.io/ip
- https://httpbin.org/ip
- https://api.ipify.org

## Installation

```bash
pip install python-ifconfig-me
```

## Basic usage - Use as a tool

Show help messages:

```python
$ ifconfig-me -h
```

Show the current public ip:

```python
$ ifconfig-me
```

Show statistics use the to determine the public ip.

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

## Advanced usage - Use as a library

```python
import asyncio
from python_ifconfig_me import getIPsAsync

asyncio.run(getIPsAsync())
```