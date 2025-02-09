from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.article_preview import ArticlePreview


T = TypeVar("T", bound="TopicWithArticles")


@_attrs_define
class TopicWithArticles:
    """
    Attributes:
        articles_count (int):
        title (str):
        summary (str):
        articles (list['ArticlePreview']):
        summary_with_links (Union[None, Unset, str]):
        first_image (Union[None, Unset, str]):
    """

    articles_count: int
    title: str
    summary: str
    articles: list["ArticlePreview"]
    summary_with_links: Union[None, Unset, str] = UNSET
    first_image: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        articles_count = self.articles_count

        title = self.title

        summary = self.summary

        articles = []
        for articles_item_data in self.articles:
            articles_item = articles_item_data.to_dict()
            articles.append(articles_item)

        summary_with_links: Union[None, Unset, str]
        if isinstance(self.summary_with_links, Unset):
            summary_with_links = UNSET
        else:
            summary_with_links = self.summary_with_links

        first_image: Union[None, Unset, str]
        if isinstance(self.first_image, Unset):
            first_image = UNSET
        else:
            first_image = self.first_image

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "articles_count": articles_count,
                "title": title,
                "summary": summary,
                "articles": articles,
            }
        )
        if summary_with_links is not UNSET:
            field_dict["summary_with_links"] = summary_with_links
        if first_image is not UNSET:
            field_dict["first_image"] = first_image

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.article_preview import ArticlePreview

        d = src_dict.copy()
        articles_count = d.pop("articles_count")

        title = d.pop("title")

        summary = d.pop("summary")

        articles = []
        _articles = d.pop("articles")
        for articles_item_data in _articles:
            articles_item = ArticlePreview.from_dict(articles_item_data)

            articles.append(articles_item)

        def _parse_summary_with_links(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        summary_with_links = _parse_summary_with_links(d.pop("summary_with_links", UNSET))

        def _parse_first_image(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        first_image = _parse_first_image(d.pop("first_image", UNSET))

        topic_with_articles = cls(
            articles_count=articles_count,
            title=title,
            summary=summary,
            articles=articles,
            summary_with_links=summary_with_links,
            first_image=first_image,
        )

        topic_with_articles.additional_properties = d
        return topic_with_articles

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
