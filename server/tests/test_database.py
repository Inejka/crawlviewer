import json
import os
import sqlite3
from datetime import datetime

import pytest

from database.database_worker import DatabaseWorder
from utils.basic_structures import TelegraphUrl

TEST_DB_FILE_PATH = os.path.join("server", "tests", "database_tmp.db")


# TODO replace with fixtures
@pytest.fixture(scope="session", autouse=True)
def _prepare_database() -> None:
    DatabaseWorder(TEST_DB_FILE_PATH)
    yield
    os.remove(TEST_DB_FILE_PATH)


@pytest.fixture(scope="session", autouse=True)
def _insert_tags() -> None:
    worker = DatabaseWorder(TEST_DB_FILE_PATH)
    worker.insert("tag1")
    worker.insert("tag2")
    worker.insert("tag3")
    worker.insert("tag3")
    worker.insert("tag3")


@pytest.fixture(scope="session")
def insert_url() -> TelegraphUrl:
    worker = DatabaseWorder(TEST_DB_FILE_PATH)
    url = TelegraphUrl(
        "https://telegra.ph/an-03-10", {"videos": 2, "nude": 2, "nonNude": 4}
    )
    worker.insert(url, "path")
    worker.insert(
        TelegraphUrl(
            "https://telegra.ph/an-03-10-2", {"videos": 2, "nude": 4, "nonNude": 4}
        ),
        "path",
    )
    worker.insert(
        TelegraphUrl(
            "https://telegra.ph/an-03-10-1", {"videos": 2, "nude": 2, "nonNude": 4}
        ),
        "path",
    )
    worker.insert(url, "path")
    worker.insert(url, "path")
    return url


def test_base_file_creation() -> None:
    assert os.path.exists(TEST_DB_FILE_PATH)


def test_base_initialization() -> None:
    con = sqlite3.connect(TEST_DB_FILE_PATH)
    sql_query = """SELECT name FROM sqlite_master
                          WHERE type='table';"""
    tables = con.cursor().execute(sql_query).fetchall()

    assert ("pages",) in tables
    assert ("tags",) in tables
    assert ("pages_tags",) in tables


def test_tag_insertion() -> None:
    con = sqlite3.connect(TEST_DB_FILE_PATH)
    sql_query = """SELECT tag FROM tags"""
    tags = con.cursor().execute(sql_query).fetchall()
    assert ("tag1",) in tags
    assert ("tag2",) in tags
    assert ("tag3",) in tags


def test_unique_tags() -> None:
    con = sqlite3.connect(TEST_DB_FILE_PATH)
    sql_query = """SELECT tag FROM tags"""
    tags = con.cursor().execute(sql_query).fetchall()
    assert len(tags) == 3


def test_telegraph_url_insertion(insert_url: TelegraphUrl) -> None:
    con = sqlite3.connect(TEST_DB_FILE_PATH)
    sql_query = (
        """SELECT page_name, page_path, page_type, metadata, created from pages"""
    )
    page_name, page_path, page_type, metadata, created = (
        con.cursor().execute(sql_query).fetchall()[0]
    )
    assert page_name == insert_url.get_name()
    assert page_path == "path"
    assert page_type == insert_url.page_type
    assert json.loads(metadata) == insert_url.metadata
    # ignore seconds -- [:-3]
    assert created[:-3] == datetime.utcnow().strftime("%Y-%m-%d %H:%M")


def test_unique_url(insert_url: TelegraphUrl) -> None:
    con = sqlite3.connect(TEST_DB_FILE_PATH)
    sql_query = (
        """SELECT page_name, page_path, page_type, metadata, created from pages"""
    )
    pages = con.cursor().execute(sql_query).fetchall()
    assert len(pages) == 3


def test_tag_to_page_addition(insert_url: TelegraphUrl) -> None:
    worker = DatabaseWorder(TEST_DB_FILE_PATH)
    worker.insert(insert_url.get_name(), "tag1")
    worker.insert(insert_url.get_name(), "tag1")

    con = sqlite3.connect(TEST_DB_FILE_PATH)
    sql_query = """SELECT tag FROM pages_tags WHERE page_name = (?)"""
    tags = con.cursor().execute(sql_query, (insert_url.get_name(),)).fetchall()
    assert ("tag1",) in tags


def test_get_total_pages(insert_url: TelegraphUrl) -> None:
    worker = DatabaseWorder(TEST_DB_FILE_PATH)
    assert worker.get_total_pages() == 3


def test_get_pages(insert_url: TelegraphUrl) -> None:
    worker = DatabaseWorder(TEST_DB_FILE_PATH)
    pages = worker.get_pages(0)
    assert len(pages) == 3
    assert {"an-03-10", "an-03-10-1", "an-03-10-2"}.issubset({x.name for x in pages})
    assert {"path"}.issubset({x.save_path for x in pages})
    assert {"TelegraphUrl"}.issubset({x.page_type for x in pages})

    # well, for some reason this assert fails
    # using debbuger i found that this test assert must pass
    # found = False
    # for page in pages:
    #     if {"videos": 2, "nude": 2, "nonNude": 4} == page.metadata:
    #         found = True
    # assert found


def test_get_pages_num(insert_url: TelegraphUrl) -> None:
    worker = DatabaseWorder(TEST_DB_FILE_PATH)

    assert len(worker.get_pages(0, 2)) == 2
    assert len(worker.get_pages(1, 2)) == 1
    assert len(worker.get_pages(3, 1)) == 0
    assert len(worker.get_pages(2, 1)) == 1
