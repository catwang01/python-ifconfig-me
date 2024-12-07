import logging

import pytest

from python_ifconfig_me.cli import CommandLineArgs
from python_ifconfig_me.cli import get_args


def test_default_parameters():
    result = get_args([])
    expected = CommandLineArgs(
        show_statistics=False,
        ipv4=False,
        ipv6=False,
        prefer_ipv6=False,
        logLevel=logging.ERROR,
    )
    assert result == expected

@pytest.mark.parametrize(
    "logLevelStr, expectedLogLevel", [
        ("DEBUG", logging.DEBUG),
        ("debug", logging.DEBUG),
        ("11", 11)
    ]
)
def test_loglevel_parsing(logLevelStr: str, expectedLogLevel: int):
    result = get_args(["--logLevel", logLevelStr])
    expected = CommandLineArgs(
        show_statistics=False,
        ipv4=False,
        ipv6=False,
        prefer_ipv6=False,
        logLevel=expectedLogLevel
    )
    assert result == expected

def test_ipv4_ipv6_cannot_be_used_together():
    result = get_args(["--ipv4", "--ipv6"])
    assert result is None