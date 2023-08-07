import pytest

from downloader.site_saver import TelegraphProvider, dataProvider, defaultProvider, textProvider, urlProvider


def test_data_provider() -> None:
    with pytest.raises(TypeError):
        dataProvider("fail")


def test_text_provider() -> None:
    provider = textProvider("i need to return")
    assert provider.provide() == "i need to return"


def test_default_provider() -> None:
    provider = defaultProvider()
    print(provider.provide())
    assert provider.provide() != ""


def test_url_provider() -> None:
    with pytest.raises(TypeError):
        urlProvider(None)


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
    provider = TelegraphProvider(textProvider(file_content))
    parsed = provider.provide()[0]
    assert parsed.url == url
    assert parsed.metadata["videos"] == videos
    assert parsed.metadata["nude"] == nude
    assert parsed.metadata["nonNude"] == nonNude


def test_telegraph_provider_multiple() -> None:
    test_file = """
    INTERESTING (2 video) https://telegra.ph/an-03-10
        Nude: 2 non-nude: 4
        Total video: 2

    INTERESTING https://telegra.ph/a-07-22-7 (15.58s)
        Nude: 0 (0 new) non-nude: 10 (10 new)
        Total video: 2

    """
    provider = TelegraphProvider(textProvider(test_file))
    parsed = provider.provide()
    assert len(parsed) == 2
    assert parsed[0].url == "https://telegra.ph/an-03-10"
    assert parsed[1].url == "https://telegra.ph/a-07-22-7"
