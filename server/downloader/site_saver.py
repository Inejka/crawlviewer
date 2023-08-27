import os
import re
from abc import ABC, abstractclassmethod
from multiprocessing.pool import ThreadPool
from threading import Thread

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
            if len(line.strip()) == 0:
                if newEntry is not None:
                    to_return.append(newEntry)
                    newEntry = None
                continue
            if "INTERESTING" in line and "http" in line:
                newEntry = TelegraphUrl()
                for word in line.split(" "):
                    if "http" in word:
                        newEntry.url = word
                        break
                continue
            if "Nude" in line:
                newEntry.metadata["nude"] = int(re.findall(r"\d+", line)[0])
                newEntry.metadata["nonNude"] = int(
                    re.findall(r"\d+", line[line.find("non-nude") :])[0]
                )
                continue
            if "Total video" in line:
                newEntry.metadata["videos"] = int(re.findall(r"\d+", line)[0])
                continue

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
        self._finished_threads = SafeCounter()
        self._max_parrarel_downloads = max_parrarel_downloads
        self._total_pages_to_save = 0

        if not os.path.exists(download_folder):
            os.mkdir(download_folder)

    def run(self) -> None:
        urls = self._url_provider.provide()
        self._total_pages_to_save = len(urls)

        def process_urls(url: BasicUrl) -> None:
            if not process_urls.db_worker.has_row_with_name(url.get_name()):
                th = process_urls.download_class(
                    process_urls.download_folder,
                    process_urls.finished_threads,
                    url,
                )
                process_urls.db_worker.insert(
                    url, os.path.join(process_urls.download_folder, url.get_name())
                )
                th.run()
            else:
                process_urls.finished_threads.inc()

        process_urls.download_class = self._get_downloader(urls)
        process_urls.db_worker = self._db_worker
        process_urls.finished_threads = self._finished_threads
        process_urls.download_folder = self._download_folder
        with ThreadPool(self._max_parrarel_downloads) as pool:
            pool.map(process_urls, urls)

    def get_total_pages_to_save(self) -> int:
        return self._total_pages_to_save

    def get_finished_downloads(self) -> int:
        return self._finished_threads.get()

    class _DownloaderThread:
        def __init__(
            self,
            download_folder: str,
            finished_counter: SafeCounter,
            url: BasicUrl,
        ) -> None:
            self._download_folder = download_folder
            self._finished_counter = finished_counter
            self._url = url

        def run(self) -> None:
            self._download()
            self._finished_counter.inc()

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
