import json
import os
import sqlite3
from collections.abc import Callable
from datetime import datetime

from database.database_worker import DatabaseWorder
from utils.basic_structures import TelegraphUrl

TEST_DB_FILE_PATH = os.path.join("server", "tests", "tmp.db")


def prepare_database(func: Callable) -> Callable:
    def inner() -> None:
        if os.path.exists(TEST_DB_FILE_PATH):
            os.remove(TEST_DB_FILE_PATH)
        DatabaseWorder(TEST_DB_FILE_PATH)
        func()
        os.remove(TEST_DB_FILE_PATH)

    return inner


def insert_tags(fucn: Callable) -> Callable:
    def inner() -> None:
        worker = DatabaseWorder(TEST_DB_FILE_PATH)
        worker.insert("tag1")
        worker.insert("tag2")
        worker.insert("tag3")
        worker.insert("tag3")
        worker.insert("tag3")
        fucn()

    return inner


def insert_url(fucn: Callable) -> Callable:
    def inner() -> None:
        worker = DatabaseWorder(TEST_DB_FILE_PATH)
        url = TelegraphUrl(
            "https://telegra.ph/an-03-10", {"videos": 2, "nude": 2, "nonNude": 4}
        )
        worker.insert(url, "path")
        worker.insert(url, "path")
        worker.insert(url, "path")
        fucn(url)

    return inner


@prepare_database
def test_base_file_creation() -> None:
    assert os.path.exists(TEST_DB_FILE_PATH)


@prepare_database
def test_base_initialization() -> None:
    con = sqlite3.connect(TEST_DB_FILE_PATH)
    sql_query = """SELECT name FROM sqlite_master
                          WHERE type='table';"""
    tables = con.cursor().execute(sql_query).fetchall()

    assert ("pages",) in tables
    assert ("tags",) in tables
    assert ("pages_tags",) in tables


@prepare_database
@insert_tags
def test_tag_insertion() -> None:
    con = sqlite3.connect(TEST_DB_FILE_PATH)
    sql_query = """SELECT tag FROM tags"""
    tags = con.cursor().execute(sql_query).fetchall()
    assert ("tag1",) in tags
    assert ("tag2",) in tags
    assert ("tag3",) in tags


@prepare_database
@insert_tags
def test_unique_tags() -> None:
    con = sqlite3.connect(TEST_DB_FILE_PATH)
    sql_query = """SELECT tag FROM tags"""
    tags = con.cursor().execute(sql_query).fetchall()
    assert len(tags) == 3


@prepare_database
@insert_url
def test_telegraph_url_insertion(url: TelegraphUrl) -> None:
    con = sqlite3.connect(TEST_DB_FILE_PATH)
    sql_query = (
        """SELECT page_name, page_path, page_type, metadata, created from pages"""
    )
    page_name, page_path, page_type, metadata, created = (
        con.cursor().execute(sql_query).fetchone()
    )
    assert page_name == url.get_name()
    assert page_path == "path"
    assert page_type == url.page_type
    assert json.loads(metadata) == url.metadata
    # ignore seconds -- [:-3]
    assert created[:-3] == datetime.utcnow().strftime("%Y-%m-%d %H:%M")


@prepare_database
@insert_url
def test_unique_url(url: TelegraphUrl) -> None:
    con = sqlite3.connect(TEST_DB_FILE_PATH)
    sql_query = (
        """SELECT page_name, page_path, page_type, metadata, created from pages"""
    )
    pages = con.cursor().execute(sql_query).fetchall()
    assert len(pages) == 1


@prepare_database
@insert_tags
@insert_url
def test_tag_to_page_addition(url: TelegraphUrl) -> None:
    worker = DatabaseWorder(TEST_DB_FILE_PATH)
    worker.insert(url.get_name(), "tag1")
    worker.insert(url.get_name(), "tag1")

    con = sqlite3.connect(TEST_DB_FILE_PATH)
    sql_query = """SELECT tag FROM pages_tags WHERE page_name = (?)"""
    tags = con.cursor().execute(sql_query, (url.get_name(),)).fetchall()
    assert ("tag1",) in tags
