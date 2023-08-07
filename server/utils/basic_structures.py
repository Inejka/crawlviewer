from dataclasses import dataclass, field


@dataclass
class BasicUrl:
    url: str = None
    metadata: dict = field(default_factory=dict)
    page_type: str = "BasicUrl"


class TelegraphUrl(BasicUrl):
    metadata: dict = field(
        default_factory=lambda: {"videos": 0, "nude": 0, "nonNude": 0}
    )
    page_type: str = "TelegraphUrl"

    def get_name(self) -> str:
        return self.url[self.url.rfind("/") + 1 :]
