import os
from shutil import rmtree
from time import sleep
from typing import Any

import pytest
from flask.testing import FlaskClient

TEST_FILE = """
    INTERESTING (2 video) https://telegra.ph/an-03-10
        Nude: 2 non-nude: 4
        Total video: 2

    INTERESTING https://telegra.ph/a-07-22-7 (15.58s)
        Nude: 0 (0 new) non-nude: 10 (10 new)
        Total video: 2

    """
TEST_DB_PATH = os.path.join("server", "tests", "ta_db.db")
TEST_DATA_PATH = os.path.join("server", "tests", "ta_data")


@pytest.fixture(scope="session")
def setup() -> Any:
    from app import InnerApp

    inner_app = InnerApp(TEST_DB_PATH, TEST_DATA_PATH)
    app = inner_app.get_app()

    app.config.update(
        {
            "TESTING": True,
        }
    )
    yield app.test_client()
    inner_app._worker._con.close()
    if os.path.exists(TEST_DATA_PATH):
        rmtree(TEST_DATA_PATH)
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


@pytest.fixture(scope="session")
def insert_file(setup: FlaskClient) -> Any:
    response = setup.post(
        "/save",
        json={
            "crawler_type": "TelegraphProvider",
            "text": TEST_FILE,
        },
    )
    # wait untill download is finished
    while True:
        respone_temp = setup.get("/save/status")
        if len(respone_temp.json) == 0:
            break
        sleep(0.5)
    return response, setup


def test_save_bunch(insert_file: tuple) -> None:
    response, client = insert_file
    assert response.status_code == 200
    assert os.path.exists(os.path.join(TEST_DATA_PATH, "an-03-10"))
    assert os.path.exists(os.path.join(TEST_DATA_PATH, "a-07-22-7"))


def test_page_providing(insert_file: tuple) -> None:
    response, client = insert_file
    assert response.status_code == 200
    assert client.get("/site/an-03-10/html").status_code == 200
    assert client.get("/site/a-07-22-7/html").status_code == 200
    assert client.get("/site/an-03-10/quill.core.min.css").status_code == 200
    assert client.get("/site/a-07-22-7/quill.core.min.css").status_code == 200


def test_page_data_providing(insert_file: tuple) -> None:
    response, client = insert_file
    assert response.status_code == 200
    response = client.post(
        "/pages",
        json={
            "page": 0,
        },
    )
    assert {"an-03-10", "a-07-22-7"}.issubset({x["name"] for x in response.json})
    assert {"TelegraphUrl"}.issubset({x["page_type"] for x in response.json})


def test_unsupported_provider(insert_file: tuple) -> None:
    response, client = insert_file
    response = client.post(
        "/save",
        json={
            "crawler_type": "UUTelegraphProvider",
            "text": TEST_FILE,
        },
    )
    assert response.json == "Unsupported provider"


def test_get_app() -> None:
    from app import create_app

    app = create_app()
    app.config.update(
        {
            "TESTING": True,
        }
    )
    test = app.test_client()
    respone_temp = test.get("/save/status")
    assert respone_temp.status_code == 200
