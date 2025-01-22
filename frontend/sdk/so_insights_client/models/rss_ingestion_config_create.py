from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="RssIngestionConfigCreate")


@_attrs_define
class RssIngestionConfigCreate:
    """
    Attributes:
        title (str):
        rss_feed_url (str):
    """

    title: str
    rss_feed_url: str

    def to_dict(self) -> dict[str, Any]:
        title = self.title

        rss_feed_url = self.rss_feed_url

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "title": title,
                "rss_feed_url": rss_feed_url,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        title = d.pop("title")

        rss_feed_url = d.pop("rss_feed_url")

        rss_ingestion_config_create = cls(
            title=title,
            rss_feed_url=rss_feed_url,
        )

        return rss_ingestion_config_create
