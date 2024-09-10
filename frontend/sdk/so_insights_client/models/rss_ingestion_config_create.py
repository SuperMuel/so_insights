from typing import Any, Dict, Type, TypeVar

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

    def to_dict(self) -> Dict[str, Any]:
        title = self.title

        rss_feed_url = self.rss_feed_url

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "title": title,
                "rss_feed_url": rss_feed_url,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        title = d.pop("title")

        rss_feed_url = d.pop("rss_feed_url")

        rss_ingestion_config_create = cls(
            title=title,
            rss_feed_url=rss_feed_url,
        )

        return rss_ingestion_config_create
