import os
import shutil
import sqlite3

import pytest

from database.database_worker import DatabaseWorder
from downloader.site_saver import (
    DataProvider,
    SiteSaver,
    TelegraphProvider,
    TextProvider,
    UrlProvider,
)

TEST_FILE = """
    INTERESTING (2 video) https://telegra.ph/an-03-10
        Nude: 2 non-nude: 4
        Total video: 2

    INTERESTING https://telegra.ph/a-07-22-7 (15.58s)
        Nude: 0 (0 new) non-nude: 10 (10 new)
        Total video: 2"""

TEST_DB_FILE_PATH = os.path.join("server", "tests", "site_saver_tmp.db")
TEST_DATA_FOLDER_PATH = os.path.join("server", "tests", "site_saver_data")


@pytest.fixture(scope="session")
def prepare_database() -> SiteSaver:
    DatabaseWorder(TEST_DB_FILE_PATH)
    worker = DatabaseWorder(TEST_DB_FILE_PATH)
    url_provider = TelegraphProvider(TextProvider(TEST_FILE))
    saver = SiteSaver(worker, url_provider, download_folder=TEST_DATA_FOLDER_PATH)

    saver.start()
    saver.join()
    for _ in range(3):
        saver_tmp = SiteSaver(
            worker, url_provider, download_folder=TEST_DATA_FOLDER_PATH
        )

        saver_tmp.start()
        saver_tmp.join()
    yield saver
    worker._con.close()
    os.remove(TEST_DB_FILE_PATH)
    shutil.rmtree(TEST_DATA_FOLDER_PATH)


def test_data_provider() -> None:
    with pytest.raises(TypeError):
        DataProvider("fail")


def test_text_provider() -> None:
    provider = TextProvider("i need to return")
    assert provider.provide() == "i need to return"


def test_url_provider() -> None:
    with pytest.raises(TypeError):
        UrlProvider(None)


@pytest.mark.parametrize(
    ("file_content", "url", "videos", "nude", "nonNude"),
    [
        (
            """
    INTERESTING (2 video) https://telegra.ph/an-03-10
        Nude: 2 non-nude: 4
        Total video: 2
    """,
            "https://telegra.ph/an-03-10",
            2,
            2,
            4,
        ),
        (
            """
    INTERESTING https://telegra.ph/a-07-22-7 (15.58s)
        Nude: 0 (0 new) non-nude: 10 (10 new)
        Total video: 2

         """,
            "https://telegra.ph/a-07-22-7",
            2,
            0,
            10,
        ),
    ],
)
def test_telegraph_provider(
    file_content: str, url: str, videos: int, nude: int, nonNude: int
) -> None:
    provider = TelegraphProvider(TextProvider(file_content))
    parsed = provider.provide()[0]
    assert parsed.url == url
    assert parsed.metadata["videos"] == videos
    assert parsed.metadata["nude"] == nude
    assert parsed.metadata["nonNude"] == nonNude


def test_telegraph_provider_multiple() -> None:
    provider = TelegraphProvider(TextProvider(TEST_FILE))
    parsed = provider.provide()
    assert len(parsed) == 2
    assert parsed[0].url == "https://telegra.ph/an-03-10"
    assert parsed[1].url == "https://telegra.ph/a-07-22-7"


def test_telegraph_saver(prepare_database: SiteSaver) -> None:
    assert os.path.exists(os.path.join(TEST_DATA_FOLDER_PATH, "an-03-10"))
    assert os.path.exists(os.path.join(TEST_DATA_FOLDER_PATH, "a-07-22-7"))

    con = sqlite3.connect(TEST_DB_FILE_PATH)
    sql_query = (
        """SELECT page_name, page_path, page_type, metadata, created from pages"""
    )
    pages = con.cursor().execute(sql_query).fetchall()
    assert len(pages) == 2


def test_saver_stats(prepare_database: SiteSaver) -> None:
    assert prepare_database.get_finished_downloads() == 2
    assert prepare_database.get_total_pages_to_save() == 2
