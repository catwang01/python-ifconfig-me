import logging
from typing import Optional, TypeVar

T = TypeVar("T")


def nn(x: Optional[T]) -> T:
    assert x is not None, "Value is expected to be non-None"
    return x


def parse_loglevel(logLevelStr: str):
    try:
        return int(logLevelStr)
    except Exception:
        pass
    logLevelStrUpper = logLevelStr.upper()
    if hasattr(logging, logLevelStrUpper):
        return getattr(logging, logLevelStrUpper)
    raise ValueError(f"Can't parse the loglevel from str {logLevelStr!r}")
