from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.article_preview import ArticlePreview
    from ..models.cluster_evaluation import ClusterEvaluation


T = TypeVar("T", bound="ClusterWithArticles")


@_attrs_define
class ClusterWithArticles:
    """
    Attributes:
        id (str):
        workspace_id (str):
        session_id (str):
        articles_count (int):
        articles (list['ArticlePreview']):
        title (Union[None, Unset, str]):
        summary (Union[None, Unset, str]):
        overview_generation_error (Union[None, Unset, str]):
        evaluation (Union['ClusterEvaluation', None, Unset]):
        first_image (Union[None, Unset, str]):
    """

    id: str
    workspace_id: str
    session_id: str
    articles_count: int
    articles: list["ArticlePreview"]
    title: Union[None, Unset, str] = UNSET
    summary: Union[None, Unset, str] = UNSET
    overview_generation_error: Union[None, Unset, str] = UNSET
    evaluation: Union["ClusterEvaluation", None, Unset] = UNSET
    first_image: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.cluster_evaluation import ClusterEvaluation

        id = self.id

        workspace_id = self.workspace_id

        session_id = self.session_id

        articles_count = self.articles_count

        articles = []
        for articles_item_data in self.articles:
            articles_item = articles_item_data.to_dict()
            articles.append(articles_item)

        title: Union[None, Unset, str]
        if isinstance(self.title, Unset):
            title = UNSET
        else:
            title = self.title

        summary: Union[None, Unset, str]
        if isinstance(self.summary, Unset):
            summary = UNSET
        else:
            summary = self.summary

        overview_generation_error: Union[None, Unset, str]
        if isinstance(self.overview_generation_error, Unset):
            overview_generation_error = UNSET
        else:
            overview_generation_error = self.overview_generation_error

        evaluation: Union[None, Unset, dict[str, Any]]
        if isinstance(self.evaluation, Unset):
            evaluation = UNSET
        elif isinstance(self.evaluation, ClusterEvaluation):
            evaluation = self.evaluation.to_dict()
        else:
            evaluation = self.evaluation

        first_image: Union[None, Unset, str]
        if isinstance(self.first_image, Unset):
            first_image = UNSET
        else:
            first_image = self.first_image

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "workspace_id": workspace_id,
                "session_id": session_id,
                "articles_count": articles_count,
                "articles": articles,
            }
        )
        if title is not UNSET:
            field_dict["title"] = title
        if summary is not UNSET:
            field_dict["summary"] = summary
        if overview_generation_error is not UNSET:
            field_dict["overview_generation_error"] = overview_generation_error
        if evaluation is not UNSET:
            field_dict["evaluation"] = evaluation
        if first_image is not UNSET:
            field_dict["first_image"] = first_image

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.article_preview import ArticlePreview
        from ..models.cluster_evaluation import ClusterEvaluation

        d = src_dict.copy()
        id = d.pop("id")

        workspace_id = d.pop("workspace_id")

        session_id = d.pop("session_id")

        articles_count = d.pop("articles_count")

        articles = []
        _articles = d.pop("articles")
        for articles_item_data in _articles:
            articles_item = ArticlePreview.from_dict(articles_item_data)

            articles.append(articles_item)

        def _parse_title(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        title = _parse_title(d.pop("title", UNSET))

        def _parse_summary(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        summary = _parse_summary(d.pop("summary", UNSET))

        def _parse_overview_generation_error(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        overview_generation_error = _parse_overview_generation_error(d.pop("overview_generation_error", UNSET))

        def _parse_evaluation(data: object) -> Union["ClusterEvaluation", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                evaluation_type_0 = ClusterEvaluation.from_dict(data)

                return evaluation_type_0
            except:  # noqa: E722
                pass
            return cast(Union["ClusterEvaluation", None, Unset], data)

        evaluation = _parse_evaluation(d.pop("evaluation", UNSET))

        def _parse_first_image(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        first_image = _parse_first_image(d.pop("first_image", UNSET))

        cluster_with_articles = cls(
            id=id,
            workspace_id=workspace_id,
            session_id=session_id,
            articles_count=articles_count,
            articles=articles,
            title=title,
            summary=summary,
            overview_generation_error=overview_generation_error,
            evaluation=evaluation,
            first_image=first_image,
        )

        cluster_with_articles.additional_properties = d
        return cluster_with_articles

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
