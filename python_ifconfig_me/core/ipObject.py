from dataclasses import dataclass
from typing import Optional


@dataclass
class IPObject:
    ip: Optional[str] = None

    def isIPv6(self) -> bool:
        return self.ip is not None and ":" in self.ip

    def isIPv4(self) -> bool:
        return self.ip is not None and "." in self.ip
