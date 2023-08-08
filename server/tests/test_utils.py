from threading import Thread

import pytest

from utils.basic_structures import SafeCounter, TelegraphUrl


@pytest.mark.parametrize(
    ("url", "name"),
    [
        ("https://telegra.ph/an-03-10", "an-03-10"),
        ("https://telegra.ph/a-07-22-7", "a-07-22-7"),
    ],
)
def test_telegraph_get_name(url: str, name: str) -> None:
    assert TelegraphUrl(url).get_name() == name


def test_safe_counter() -> None:
    counter = SafeCounter()
    threads = []

    def simple_func(counter: SafeCounter) -> None:
        counter.inc()

    for _ in range(10000):
        threads.append(Thread(target=simple_func, args=(counter,)))

    for i in threads:
        i.start()

    for i in threads:
        i.join()

    assert counter.get() == 10000
