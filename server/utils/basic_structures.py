from abc import abstractclassmethod
from dataclasses import dataclass, field
from threading import Lock


@dataclass
class BasicUrl:
    url: str = None
    metadata: dict = field(default_factory=dict)
    page_type: str = "BasicUrl"

    @abstractclassmethod
    def get_name(self) -> str:
        pass


class TelegraphUrl(BasicUrl):
    metadata: dict = field(
        default_factory=lambda: {"videos": 0, "nude": 0, "nonNude": 0}
    )
    page_type: str = "TelegraphUrl"

    def get_name(self) -> str:
        return self.url[self.url.rfind("/") + 1 :]


class SafeCounter:
    def __init__(self, init_value: int = 0) -> None:
        self._value = init_value
        self._lock = Lock()

    def inc(self) -> None:
        with self._lock:
            self._value += 1

    def get(self) -> int:
        with self._lock:
            return self._value
