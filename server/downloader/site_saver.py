import os
import re
from abc import ABC, abstractclassmethod
from threading import BoundedSemaphore, Thread

from database.database_worker import DatabaseWorder
from utils.basic_structures import BasicUrl, SafeCounter, TelegraphUrl


class DataProvider(ABC):
    def __init__(self, file_path: str) -> None:
        self._file_path = file_path

    @abstractclassmethod
    def provide() -> str:
        pass


class TextProvider(DataProvider):
    def provide(self) -> str:
        return self._file_path


class DefaultProvider(DataProvider):
    def __init__(self) -> None:
        super().__init__("/tmp/run/log.txt")

    def provide(self) -> str:
        with open(self._file_path, encoding="utf-8") as file:
            return file.read()


class UrlProvider(ABC):
    def __init__(self, provider: DataProvider) -> None:
        self._provider = provider

    @abstractclassmethod
    def provide(self) -> list[BasicUrl]:
        pass


class TelegraphProvider(UrlProvider):
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
                newEntry.metadata["nonNude"] = int(
                    re.findall(r"\d+", line[line.find("non-nude") :])[0]
                )
            if "Total video" in line:
                newEntry.metadata["videos"] = int(re.findall(r"\d+", line)[0])

        if newEntry is not None:
            to_return.append(newEntry)

        return to_return


class SiteSaver(Thread):
    def __init__(
        self,
        db_worker: DatabaseWorder,
        url_provider: UrlProvider,
        max_parrarel_downloads: int = 3,
        download_folder: str = os.path.join("server", "data"),
    ) -> None:
        super().__init__()
        self._db_worker = db_worker
        self._url_provider = url_provider
        self._download_folder = download_folder
        self._started_threads = SafeCounter()
        self._finished_threads = SafeCounter()
        self._parrarel_downloads_counter = BoundedSemaphore(max_parrarel_downloads)

        if not os.path.exists(download_folder):
            os.mkdir(download_folder)

    def run(self) -> None:
        urls = self._url_provider.provide()
        download_class = self._get_downloader(urls)
        threads = []
        # TODO insert only unique
        for url in urls:
            if not self._db_worker.has_row_with_name(url.get_name()):
                self._parrarel_downloads_counter.acquire()
                th = download_class(
                    self._download_folder,
                    self._finished_threads,
                    self._parrarel_downloads_counter,
                    url,
                )
                self._started_threads.inc()
                self._db_worker.insert(
                    url, os.path.join(self._download_folder, url.get_name())
                )
                th.start()
                threads.append(th)
        for thread in threads:
            thread.join()

    class _DownloaderThread(Thread):
        def __init__(
            self,
            download_folder: str,
            finished_counter: SafeCounter,
            to_release: BoundedSemaphore,
            url: BasicUrl,
        ) -> None:
            super().__init__()
            self._download_folder = download_folder
            self._finished_counter = finished_counter
            self._to_release = to_release
            self._url = url

        def run(self) -> None:
            self._download()
            self._finished_counter.inc()
            self._to_release.release()

        @abstractclassmethod
        def _download(self) -> None:
            pass

    class _DownloaderTelegraph(_DownloaderThread):
        def _download(self) -> None:
            params = f"{os.path.join(self._download_folder, self._url.get_name())} -q {self._url.url}"
            os.system("wget -r -k -l 2 -p -E -nc -nd -P " + params)

    def _get_downloader(self, urls: list[UrlProvider]) -> _DownloaderThread:
        match urls[0]:
            case TelegraphUrl():
                return self._DownloaderTelegraph
        raise RuntimeError("Dowloader was not implemented")
