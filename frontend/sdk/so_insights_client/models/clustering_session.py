import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.clustering_session_metadata import ClusteringSessionMetadata


T = TypeVar("T", bound="ClusteringSession")


@_attrs_define
class ClusteringSession:
    """
    Attributes:
        workspace_id (str):  Example: 5eb7cf5a86d9755df3a6c593.
        data_start (datetime.datetime):
        data_end (datetime.datetime):
        nb_days (int):
        metadata (ClusteringSessionMetadata):
        articles_count (int): Number of articles on which the clustering was performed, including noise.
        clusters_count (int):
        noise_articles_ids (List[str]):
        noise_articles_count (int):
        clustered_articles_count (int): Number of articles in clusters, excluding noise.
        field_id (Union[None, Unset, str]): MongoDB document ObjectID
        session_start (Union[Unset, datetime.datetime]):
        session_end (Union[None, Unset, datetime.datetime]):
        relevant_clusters_count (Union[None, Unset, int]):
        somewhat_relevant_clusters_count (Union[None, Unset, int]):
        irrelevant_clusters_count (Union[None, Unset, int]):
        summary (Union[None, Unset, str]):
    """

    workspace_id: str
    data_start: datetime.datetime
    data_end: datetime.datetime
    nb_days: int
    metadata: "ClusteringSessionMetadata"
    articles_count: int
    clusters_count: int
    noise_articles_ids: List[str]
    noise_articles_count: int
    clustered_articles_count: int
    field_id: Union[None, Unset, str] = UNSET
    session_start: Union[Unset, datetime.datetime] = UNSET
    session_end: Union[None, Unset, datetime.datetime] = UNSET
    relevant_clusters_count: Union[None, Unset, int] = UNSET
    somewhat_relevant_clusters_count: Union[None, Unset, int] = UNSET
    irrelevant_clusters_count: Union[None, Unset, int] = UNSET
    summary: Union[None, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        workspace_id = self.workspace_id

        data_start = self.data_start.isoformat()

        data_end = self.data_end.isoformat()

        nb_days = self.nb_days

        metadata = self.metadata.to_dict()

        articles_count = self.articles_count

        clusters_count = self.clusters_count

        noise_articles_ids = self.noise_articles_ids

        noise_articles_count = self.noise_articles_count

        clustered_articles_count = self.clustered_articles_count

        field_id: Union[None, Unset, str]
        if isinstance(self.field_id, Unset):
            field_id = UNSET
        else:
            field_id = self.field_id

        session_start: Union[Unset, str] = UNSET
        if not isinstance(self.session_start, Unset):
            session_start = self.session_start.isoformat()

        session_end: Union[None, Unset, str]
        if isinstance(self.session_end, Unset):
            session_end = UNSET
        elif isinstance(self.session_end, datetime.datetime):
            session_end = self.session_end.isoformat()
        else:
            session_end = self.session_end

        relevant_clusters_count: Union[None, Unset, int]
        if isinstance(self.relevant_clusters_count, Unset):
            relevant_clusters_count = UNSET
        else:
            relevant_clusters_count = self.relevant_clusters_count

        somewhat_relevant_clusters_count: Union[None, Unset, int]
        if isinstance(self.somewhat_relevant_clusters_count, Unset):
            somewhat_relevant_clusters_count = UNSET
        else:
            somewhat_relevant_clusters_count = self.somewhat_relevant_clusters_count

        irrelevant_clusters_count: Union[None, Unset, int]
        if isinstance(self.irrelevant_clusters_count, Unset):
            irrelevant_clusters_count = UNSET
        else:
            irrelevant_clusters_count = self.irrelevant_clusters_count

        summary: Union[None, Unset, str]
        if isinstance(self.summary, Unset):
            summary = UNSET
        else:
            summary = self.summary

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "workspace_id": workspace_id,
                "data_start": data_start,
                "data_end": data_end,
                "nb_days": nb_days,
                "metadata": metadata,
                "articles_count": articles_count,
                "clusters_count": clusters_count,
                "noise_articles_ids": noise_articles_ids,
                "noise_articles_count": noise_articles_count,
                "clustered_articles_count": clustered_articles_count,
            }
        )
        if field_id is not UNSET:
            field_dict["_id"] = field_id
        if session_start is not UNSET:
            field_dict["session_start"] = session_start
        if session_end is not UNSET:
            field_dict["session_end"] = session_end
        if relevant_clusters_count is not UNSET:
            field_dict["relevant_clusters_count"] = relevant_clusters_count
        if somewhat_relevant_clusters_count is not UNSET:
            field_dict["somewhat_relevant_clusters_count"] = somewhat_relevant_clusters_count
        if irrelevant_clusters_count is not UNSET:
            field_dict["irrelevant_clusters_count"] = irrelevant_clusters_count
        if summary is not UNSET:
            field_dict["summary"] = summary

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.clustering_session_metadata import ClusteringSessionMetadata

        d = src_dict.copy()
        workspace_id = d.pop("workspace_id")

        data_start = isoparse(d.pop("data_start"))

        data_end = isoparse(d.pop("data_end"))

        nb_days = d.pop("nb_days")

        metadata = ClusteringSessionMetadata.from_dict(d.pop("metadata"))

        articles_count = d.pop("articles_count")

        clusters_count = d.pop("clusters_count")

        noise_articles_ids = cast(List[str], d.pop("noise_articles_ids"))

        noise_articles_count = d.pop("noise_articles_count")

        clustered_articles_count = d.pop("clustered_articles_count")

        def _parse_field_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        field_id = _parse_field_id(d.pop("_id", UNSET))

        _session_start = d.pop("session_start", UNSET)
        session_start: Union[Unset, datetime.datetime]
        if isinstance(_session_start, Unset):
            session_start = UNSET
        else:
            session_start = isoparse(_session_start)

        def _parse_session_end(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                session_end_type_0 = isoparse(data)

                return session_end_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        session_end = _parse_session_end(d.pop("session_end", UNSET))

        def _parse_relevant_clusters_count(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        relevant_clusters_count = _parse_relevant_clusters_count(d.pop("relevant_clusters_count", UNSET))

        def _parse_somewhat_relevant_clusters_count(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        somewhat_relevant_clusters_count = _parse_somewhat_relevant_clusters_count(
            d.pop("somewhat_relevant_clusters_count", UNSET)
        )

        def _parse_irrelevant_clusters_count(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        irrelevant_clusters_count = _parse_irrelevant_clusters_count(d.pop("irrelevant_clusters_count", UNSET))

        def _parse_summary(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        summary = _parse_summary(d.pop("summary", UNSET))

        clustering_session = cls(
            workspace_id=workspace_id,
            data_start=data_start,
            data_end=data_end,
            nb_days=nb_days,
            metadata=metadata,
            articles_count=articles_count,
            clusters_count=clusters_count,
            noise_articles_ids=noise_articles_ids,
            noise_articles_count=noise_articles_count,
            clustered_articles_count=clustered_articles_count,
            field_id=field_id,
            session_start=session_start,
            session_end=session_end,
            relevant_clusters_count=relevant_clusters_count,
            somewhat_relevant_clusters_count=somewhat_relevant_clusters_count,
            irrelevant_clusters_count=irrelevant_clusters_count,
            summary=summary,
        )

        clustering_session.additional_properties = d
        return clustering_session

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
