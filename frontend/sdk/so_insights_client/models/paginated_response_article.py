from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.article import Article


T = TypeVar("T", bound="PaginatedResponseArticle")


@_attrs_define
class PaginatedResponseArticle:
    """
    Attributes:
        total (int):
        page (int):
        per_page (int):
        items (list['Article']):
    """

    total: int
    page: int
    per_page: int
    items: list["Article"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        total = self.total

        page = self.page

        per_page = self.per_page

        items = []
        for items_item_data in self.items:
            items_item = items_item_data.to_dict()
            items.append(items_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "total": total,
                "page": page,
                "per_page": per_page,
                "items": items,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.article import Article

        d = src_dict.copy()
        total = d.pop("total")

        page = d.pop("page")

        per_page = d.pop("per_page")

        items = []
        _items = d.pop("items")
        for items_item_data in _items:
            items_item = Article.from_dict(items_item_data)

            items.append(items_item)

        paginated_response_article = cls(
            total=total,
            page=page,
            per_page=per_page,
            items=items,
        )

        paginated_response_article.additional_properties = d
        return paginated_response_article

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
