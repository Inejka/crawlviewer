import json
import os
import sqlite3
from abc import ABC, abstractclassmethod
from threading import Lock
from typing import Any, Optional

from utils.basic_structures import PageEntry, TelegraphUrl


class DatabaseWorder:
    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        self._is_initialized = os.path.exists(self._db_path)
        self._con = sqlite3.connect(self._db_path, check_same_thread=False)
        self._operation_lock = Lock()
        if not self._is_initialized:
            self.__initialize()

    def __initialize(self) -> None:
        cur = self._con.cursor()
        cur.execute(
            """CREATE TABLE pages
                    (page_name TEXT, page_path TEXT, page_type TEXT,
                        metadata JSON, created DATETIME)"""
        )
        cur.execute(
            """CREATE TABLE tags
                    (tag TEXT)"""
        )
        cur.execute(
            """CREATE TABLE pages_tags
                    (page_name TEXT, tag TEXT)"""
        )
        self._con.commit()

    def insert(self, *args: Any) -> None:
        with self._operation_lock:
            self._InsertQuerryFabric(args).execute()
            self._con.commit()

    def has_row_with_name(self, name: str) -> bool:
        return (
            self._con.cursor()
            .execute(
                "SELECT page_name FROM pages WHERE page_name=(?)",
                (name,),
            )
            .fetchone()
            is not None
        )

    def get_total_pages(self) -> int:
        return self._con.cursor().execute("SELECT COUNT(*) FROM pages;").fetchone()[0]

    def get_pages(self, page: int, pages_per_page: Optional[int] = None) -> list[PageEntry]:
        if pages_per_page is None:
            pages_per_page = 15
        content = (
            self._con.cursor()
            .execute(
                "SELECT page_name, page_type, metadata, created from pages LIMIT (?) OFFSET (?)",
                (pages_per_page, pages_per_page * page),
            )
            .fetchall()
        )
        return [PageEntry(*x) for x in content]

    class _InsertQuerry(ABC):
        def __init__(self, cur: sqlite3.Cursor, *args: Any) -> None:
            self._cur = cur

        @abstractclassmethod
        def execute(self) -> None:
            pass

        def _is_unique(self, field_name: str, table_name: str, value: str) -> bool:
            return (
                self._cur.execute(
                    f"SELECT {field_name} FROM {table_name} WHERE {field_name}=(?)",
                    (value,),
                ).fetchone()
                is None
            )

    class _InsertTagQuerry(_InsertQuerry):
        def __init__(self, cur: sqlite3.Cursor, tag: str) -> None:
            super().__init__(cur)
            self._tag = tag

        def execute(self) -> None:
            if self._is_unique("tag", "tags", self._tag):
                self._cur.execute("INSERT INTO tags VALUES (?)", (self._tag,))

    class _InsertTelegraphUrlQuerry(_InsertQuerry):
        def __init__(self, cur: sqlite3.Cursor, url: TelegraphUrl, path: str) -> None:
            super().__init__(cur)
            self._url = url
            self._path = path

        def execute(self) -> None:
            if self._is_unique("page_name", "pages", self._url.get_name()):
                """id INTEGER PRIMARY KEY, page_name TEXT, page_path TEXT, page_type TEXT,
                metadata JSON, created DATETIME)"""
                self._cur.execute(
                    "INSERT INTO pages VALUES(?,?,?,?, DATETIME('now'))",
                    (
                        self._url.get_name(),
                        self._path,
                        self._url.page_type,
                        json.dumps(self._url.metadata),
                    ),
                )

    class _InsertTagToPageQuerry(_InsertQuerry):
        def __init__(self, cur: sqlite3.Cursor, page_name: str, tag: str) -> None:
            super().__init__(cur)
            self._page_name = page_name
            self._tag = tag

        def execute(self) -> None:
            if (
                not self._is_unique("page_name", "pages", self._page_name)
                and not (self._is_unique("tag", "tags", self._tag))
                and (
                    self._cur.execute(
                        "SELECT * FROM pages_tags WHERE page_name=(?) AND tag = (?)",
                        (self._page_name, self._tag),
                    ).fetchone()
                    is None
                )
            ):
                self._cur.execute(
                    "INSERT INTO pages_tags VALUES(?,?)", (self._page_name, self._tag)
                )

    def _InsertQuerryFabric(self, *args: Any) -> _InsertQuerry:
        match args:
            case ((str() as tag,),):
                return self._InsertTagQuerry(self._con.cursor(), tag)
            case ((TelegraphUrl() as url, str() as path),):
                return self._InsertTelegraphUrlQuerry(self._con.cursor(), url, path)
            case ((str() as page_name, str() as tag),):
                return self._InsertTagToPageQuerry(self._con.cursor(), page_name, tag)
        raise RuntimeError("Unkown argument to insert")
