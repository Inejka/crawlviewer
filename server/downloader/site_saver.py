import re
from abc import ABC, abstractclassmethod

from utils.basic_structures import BasicUrl, TelegraphUrl


class dataProvider(ABC):
    def __init__(self, file_path: str) -> None:
        self._file_path = file_path

    @abstractclassmethod
    def provide() -> str:
        pass


class textProvider(dataProvider):
    def provide(self) -> str:
        return self._file_path


class defaultProvider(dataProvider):
    def __init__(self) -> None:
        super().__init__("/tmp/run/log.txt")

    def provide(self) -> str:
        with open(self._file_path, encoding="utf-8") as file:
            return file.read()


class urlProvider(ABC):
    def __init__(self, provider: dataProvider) -> None:
        self._provider = provider

    @abstractclassmethod
    def provide(self) -> list[BasicUrl]:
        pass


class TelegraphProvider(urlProvider):
    def provide(self) -> list[TelegraphUrl]:
        to_return = []
        newEntry = None
        for line in self._provider.provide().split("\n"):
            if len(line) == 0:
                if newEntry is not None:
                    to_return.append(newEntry)
                    newEntry = None
                continue
            if "INTERESTING" in line:
                newEntry = TelegraphUrl()
                for word in line.split(" "):
                    if "http" in word:
                        newEntry.url = word
                        break
            if "Nude" in line:
                newEntry.metadata["nude"] = int(re.findall(r"\d+", line)[0])
                newEntry.metadata["nonNude"] = int(re.findall(r"\d+", line[line.find("non-nude"):])[0])
            if "Total video" in line:
                newEntry.metadata["videos"] = int(re.findall(r"\d+", line)[0])

        if newEntry is not None:
            to_return.append(newEntry)

        return to_return
