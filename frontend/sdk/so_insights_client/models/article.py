import datetime
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.region import Region
from ..models.search_provider import SearchProvider
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.article_evaluation import ArticleEvaluation
    from ..models.content_fetching_result import ContentFetchingResult


T = TypeVar("T", bound="Article")


@_attrs_define
class Article:
    """Represents a single piece of content collected during ingestion.

    An Article could be a news article, blog post, or any other text-based content
    retrieved from the web

        Attributes:
            workspace_id (str):  Example: 5eb7cf5a86d9755df3a6c593.
            title (str): Title of the article
            url (str): URL where the article was found
            date (datetime.datetime): Publication date of the article
            provider (SearchProvider):
            field_id (Union[None, Unset, str]): MongoDB document ObjectID
            body (Union[Unset, str]): Short excerpt or meta_description of the article Default: ''.
            found_at (Union[Unset, datetime.datetime]): Timestamp when the article was found
            region (Union[None, Region, Unset]): Geographic region associated with the article
            image (Union[None, Unset, str]): URL of the main image in the article
            source (Union[Unset, str]): Source of the article Default: ''.
            content (Union[None, Unset, str]): Full content of the article
            content_cleaning_error (Union[None, Unset, str]): Error message if the content could not be cleaned
            ingestion_run_id (Union[None, Unset, str]): ID of the ingestion run that found this article
            vector_indexed (Union[Unset, bool]): Whether this article has been indexed in the vector database Default:
                False.
            content_fetching_result (Union['ContentFetchingResult', None, Unset]): The result of fetching and cleaning the
                article content
            evaluation (Union['ArticleEvaluation', None, Unset]):
    """

    workspace_id: str
    title: str
    url: str
    date: datetime.datetime
    provider: SearchProvider
    field_id: Union[None, Unset, str] = UNSET
    body: Union[Unset, str] = ""
    found_at: Union[Unset, datetime.datetime] = UNSET
    region: Union[None, Region, Unset] = UNSET
    image: Union[None, Unset, str] = UNSET
    source: Union[Unset, str] = ""
    content: Union[None, Unset, str] = UNSET
    content_cleaning_error: Union[None, Unset, str] = UNSET
    ingestion_run_id: Union[None, Unset, str] = UNSET
    vector_indexed: Union[Unset, bool] = False
    content_fetching_result: Union["ContentFetchingResult", None, Unset] = UNSET
    evaluation: Union["ArticleEvaluation", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.article_evaluation import ArticleEvaluation
        from ..models.content_fetching_result import ContentFetchingResult

        workspace_id = self.workspace_id

        title = self.title

        url = self.url

        date = self.date.isoformat()

        provider = self.provider.value

        field_id: Union[None, Unset, str]
        if isinstance(self.field_id, Unset):
            field_id = UNSET
        else:
            field_id = self.field_id

        body = self.body

        found_at: Union[Unset, str] = UNSET
        if not isinstance(self.found_at, Unset):
            found_at = self.found_at.isoformat()

        region: Union[None, Unset, str]
        if isinstance(self.region, Unset):
            region = UNSET
        elif isinstance(self.region, Region):
            region = self.region.value
        else:
            region = self.region

        image: Union[None, Unset, str]
        if isinstance(self.image, Unset):
            image = UNSET
        else:
            image = self.image

        source = self.source

        content: Union[None, Unset, str]
        if isinstance(self.content, Unset):
            content = UNSET
        else:
            content = self.content

        content_cleaning_error: Union[None, Unset, str]
        if isinstance(self.content_cleaning_error, Unset):
            content_cleaning_error = UNSET
        else:
            content_cleaning_error = self.content_cleaning_error

        ingestion_run_id: Union[None, Unset, str]
        if isinstance(self.ingestion_run_id, Unset):
            ingestion_run_id = UNSET
        else:
            ingestion_run_id = self.ingestion_run_id

        vector_indexed = self.vector_indexed

        content_fetching_result: Union[None, Unset, dict[str, Any]]
        if isinstance(self.content_fetching_result, Unset):
            content_fetching_result = UNSET
        elif isinstance(self.content_fetching_result, ContentFetchingResult):
            content_fetching_result = self.content_fetching_result.to_dict()
        else:
            content_fetching_result = self.content_fetching_result

        evaluation: Union[None, Unset, dict[str, Any]]
        if isinstance(self.evaluation, Unset):
            evaluation = UNSET
        elif isinstance(self.evaluation, ArticleEvaluation):
            evaluation = self.evaluation.to_dict()
        else:
            evaluation = self.evaluation

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "workspace_id": workspace_id,
                "title": title,
                "url": url,
                "date": date,
                "provider": provider,
            }
        )
        if field_id is not UNSET:
            field_dict["_id"] = field_id
        if body is not UNSET:
            field_dict["body"] = body
        if found_at is not UNSET:
            field_dict["found_at"] = found_at
        if region is not UNSET:
            field_dict["region"] = region
        if image is not UNSET:
            field_dict["image"] = image
        if source is not UNSET:
            field_dict["source"] = source
        if content is not UNSET:
            field_dict["content"] = content
        if content_cleaning_error is not UNSET:
            field_dict["content_cleaning_error"] = content_cleaning_error
        if ingestion_run_id is not UNSET:
            field_dict["ingestion_run_id"] = ingestion_run_id
        if vector_indexed is not UNSET:
            field_dict["vector_indexed"] = vector_indexed
        if content_fetching_result is not UNSET:
            field_dict["content_fetching_result"] = content_fetching_result
        if evaluation is not UNSET:
            field_dict["evaluation"] = evaluation

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.article_evaluation import ArticleEvaluation
        from ..models.content_fetching_result import ContentFetchingResult

        d = src_dict.copy()
        workspace_id = d.pop("workspace_id")

        title = d.pop("title")

        url = d.pop("url")

        date = isoparse(d.pop("date"))

        provider = SearchProvider(d.pop("provider"))

        def _parse_field_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        field_id = _parse_field_id(d.pop("_id", UNSET))

        body = d.pop("body", UNSET)

        _found_at = d.pop("found_at", UNSET)
        found_at: Union[Unset, datetime.datetime]
        if isinstance(_found_at, Unset):
            found_at = UNSET
        else:
            found_at = isoparse(_found_at)

        def _parse_region(data: object) -> Union[None, Region, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                region_type_0 = Region(data)

                return region_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Region, Unset], data)

        region = _parse_region(d.pop("region", UNSET))

        def _parse_image(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        image = _parse_image(d.pop("image", UNSET))

        source = d.pop("source", UNSET)

        def _parse_content(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        content = _parse_content(d.pop("content", UNSET))

        def _parse_content_cleaning_error(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        content_cleaning_error = _parse_content_cleaning_error(d.pop("content_cleaning_error", UNSET))

        def _parse_ingestion_run_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        ingestion_run_id = _parse_ingestion_run_id(d.pop("ingestion_run_id", UNSET))

        vector_indexed = d.pop("vector_indexed", UNSET)

        def _parse_content_fetching_result(data: object) -> Union["ContentFetchingResult", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                content_fetching_result_type_0 = ContentFetchingResult.from_dict(data)

                return content_fetching_result_type_0
            except:  # noqa: E722
                pass
            return cast(Union["ContentFetchingResult", None, Unset], data)

        content_fetching_result = _parse_content_fetching_result(d.pop("content_fetching_result", UNSET))

        def _parse_evaluation(data: object) -> Union["ArticleEvaluation", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                evaluation_type_0 = ArticleEvaluation.from_dict(data)

                return evaluation_type_0
            except:  # noqa: E722
                pass
            return cast(Union["ArticleEvaluation", None, Unset], data)

        evaluation = _parse_evaluation(d.pop("evaluation", UNSET))

        article = cls(
            workspace_id=workspace_id,
            title=title,
            url=url,
            date=date,
            provider=provider,
            field_id=field_id,
            body=body,
            found_at=found_at,
            region=region,
            image=image,
            source=source,
            content=content,
            content_cleaning_error=content_cleaning_error,
            ingestion_run_id=ingestion_run_id,
            vector_indexed=vector_indexed,
            content_fetching_result=content_fetching_result,
            evaluation=evaluation,
        )

        article.additional_properties = d
        return article

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
