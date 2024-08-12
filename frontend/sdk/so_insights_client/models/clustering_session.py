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
        metadata (ClusteringSessionMetadata):
        articles_count (int): Number of articles on which the clustering was performed, including noise.
        clusters_count (int):
        noise_articles_ids (List[str]):
        noise_articles_count (int):
        clustered_articles_count (int): Number of articles in clusters, excluding noise.
        field_id (Union[None, Unset, str]): MongoDB document ObjectID
        session_start (Union[Unset, datetime.datetime]):
        session_end (Union[None, Unset, datetime.datetime]):
    """

    workspace_id: str
    data_start: datetime.datetime
    data_end: datetime.datetime
    metadata: "ClusteringSessionMetadata"
    articles_count: int
    clusters_count: int
    noise_articles_ids: List[str]
    noise_articles_count: int
    clustered_articles_count: int
    field_id: Union[None, Unset, str] = UNSET
    session_start: Union[Unset, datetime.datetime] = UNSET
    session_end: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        workspace_id = self.workspace_id

        data_start = self.data_start.isoformat()

        data_end = self.data_end.isoformat()

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

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "workspace_id": workspace_id,
                "data_start": data_start,
                "data_end": data_end,
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

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.clustering_session_metadata import ClusteringSessionMetadata

        d = src_dict.copy()
        workspace_id = d.pop("workspace_id")

        data_start = isoparse(d.pop("data_start"))

        data_end = isoparse(d.pop("data_end"))

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

        clustering_session = cls(
            workspace_id=workspace_id,
            data_start=data_start,
            data_end=data_end,
            metadata=metadata,
            articles_count=articles_count,
            clusters_count=clusters_count,
            noise_articles_ids=noise_articles_ids,
            noise_articles_count=noise_articles_count,
            clustered_articles_count=clustered_articles_count,
            field_id=field_id,
            session_start=session_start,
            session_end=session_end,
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
