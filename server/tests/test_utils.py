import pytest

from utils.basic_structures import TelegraphUrl


@pytest.mark.parametrize(
    ("url", "name"),
    [
        ("https://telegra.ph/an-03-10", "an-03-10"),
        ("https://telegra.ph/a-07-22-7", "a-07-22-7"),
    ],
)
def test_telegraph_get_name(url: str, name: str) -> None:
    assert TelegraphUrl(url).get_name() == name
