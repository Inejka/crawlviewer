from abc import abstractclassmethod
from dataclasses import dataclass, field
from datetime import date
from threading import Lock


@dataclass
class BasicUrl:
    url: str = None
    metadata: dict = field(default_factory=dict)
    page_type: str =field(default="BasicUrl", init=False)

    @abstractclassmethod
    def get_name(self) -> str:
        pass


class TelegraphUrl(BasicUrl):
    metadata: dict = field(
        default_factory=lambda: {"videos": 0, "nude": 0, "nonNude": 0}
    )
    page_type = "TelegraphUrl"

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


@dataclass
class PageEntry:
    name: str
    save_path: str
    page_type: str
    metadata: dict
    created: date
