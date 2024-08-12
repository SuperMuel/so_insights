from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.cluster_evaluation import ClusterEvaluation


T = TypeVar("T", bound="Cluster")


@_attrs_define
class Cluster:
    """
    Attributes:
        workspace_id (str):  Example: 5eb7cf5a86d9755df3a6c593.
        session_id (str):  Example: 5eb7cf5a86d9755df3a6c593.
        articles_count (int): Number of articles in the cluster.
        articles_ids (List[str]): IDs of articles in the cluster, sorted by their distance to the cluster center
        field_id (Union[None, Unset, str]): MongoDB document ObjectID
        title (Union[None, Unset, str]): AI generated title of the cluster
        summary (Union[None, Unset, str]): AI generated summary of the cluster
        overview_generation_error (Union[None, Unset, str]): Error message if the overview generation failed
        evaluation (Union['ClusterEvaluation', None, Unset]):
    """

    workspace_id: str
    session_id: str
    articles_count: int
    articles_ids: List[str]
    field_id: Union[None, Unset, str] = UNSET
    title: Union[None, Unset, str] = UNSET
    summary: Union[None, Unset, str] = UNSET
    overview_generation_error: Union[None, Unset, str] = UNSET
    evaluation: Union["ClusterEvaluation", None, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.cluster_evaluation import ClusterEvaluation

        workspace_id = self.workspace_id

        session_id = self.session_id

        articles_count = self.articles_count

        articles_ids = self.articles_ids

        field_id: Union[None, Unset, str]
        if isinstance(self.field_id, Unset):
            field_id = UNSET
        else:
            field_id = self.field_id

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

        evaluation: Union[Dict[str, Any], None, Unset]
        if isinstance(self.evaluation, Unset):
            evaluation = UNSET
        elif isinstance(self.evaluation, ClusterEvaluation):
            evaluation = self.evaluation.to_dict()
        else:
            evaluation = self.evaluation

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "workspace_id": workspace_id,
                "session_id": session_id,
                "articles_count": articles_count,
                "articles_ids": articles_ids,
            }
        )
        if field_id is not UNSET:
            field_dict["_id"] = field_id
        if title is not UNSET:
            field_dict["title"] = title
        if summary is not UNSET:
            field_dict["summary"] = summary
        if overview_generation_error is not UNSET:
            field_dict["overview_generation_error"] = overview_generation_error
        if evaluation is not UNSET:
            field_dict["evaluation"] = evaluation

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.cluster_evaluation import ClusterEvaluation

        d = src_dict.copy()
        workspace_id = d.pop("workspace_id")

        session_id = d.pop("session_id")

        articles_count = d.pop("articles_count")

        articles_ids = cast(List[str], d.pop("articles_ids"))

        def _parse_field_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        field_id = _parse_field_id(d.pop("_id", UNSET))

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

        cluster = cls(
            workspace_id=workspace_id,
            session_id=session_id,
            articles_count=articles_count,
            articles_ids=articles_ids,
            field_id=field_id,
            title=title,
            summary=summary,
            overview_generation_error=overview_generation_error,
            evaluation=evaluation,
        )

        cluster.additional_properties = d
        return cluster

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
