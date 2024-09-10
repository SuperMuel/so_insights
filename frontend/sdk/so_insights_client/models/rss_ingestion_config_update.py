from typing import Any, Dict, Type, TypeVar, Union, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="RssIngestionConfigUpdate")


@_attrs_define
class RssIngestionConfigUpdate:
    """
    Attributes:
        title (Union[None, str]):
        rss_feed_url (Union[None, str]):
    """

    title: Union[None, str]
    rss_feed_url: Union[None, str]

    def to_dict(self) -> Dict[str, Any]:
        title: Union[None, str]
        title = self.title

        rss_feed_url: Union[None, str]
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

        def _parse_title(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        title = _parse_title(d.pop("title"))

        def _parse_rss_feed_url(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        rss_feed_url = _parse_rss_feed_url(d.pop("rss_feed_url"))

        rss_ingestion_config_update = cls(
            title=title,
            rss_feed_url=rss_feed_url,
        )

        return rss_ingestion_config_update
