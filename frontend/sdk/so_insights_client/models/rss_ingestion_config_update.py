from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="RssIngestionConfigUpdate")


@_attrs_define
class RssIngestionConfigUpdate:
    """
    Attributes:
        title (Union[None, Unset, str]):
        rss_feed_url (Union[None, Unset, str]):
    """

    title: Union[None, Unset, str] = UNSET
    rss_feed_url: Union[None, Unset, str] = UNSET

    def to_dict(self) -> dict[str, Any]:
        title: Union[None, Unset, str]
        if isinstance(self.title, Unset):
            title = UNSET
        else:
            title = self.title

        rss_feed_url: Union[None, Unset, str]
        if isinstance(self.rss_feed_url, Unset):
            rss_feed_url = UNSET
        else:
            rss_feed_url = self.rss_feed_url

        field_dict: dict[str, Any] = {}
        field_dict.update({})
        if title is not UNSET:
            field_dict["title"] = title
        if rss_feed_url is not UNSET:
            field_dict["rss_feed_url"] = rss_feed_url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()

        def _parse_title(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        title = _parse_title(d.pop("title", UNSET))

        def _parse_rss_feed_url(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        rss_feed_url = _parse_rss_feed_url(d.pop("rss_feed_url", UNSET))

        rss_ingestion_config_update = cls(
            title=title,
            rss_feed_url=rss_feed_url,
        )

        return rss_ingestion_config_update
