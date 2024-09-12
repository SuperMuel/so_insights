import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.status import Status
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.clustering_session_metadata import ClusteringSessionMetadata


T = TypeVar("T", bound="ClusteringSession")


@_attrs_define
class ClusteringSession:
    """Represents a session of grouping similar articles together.

    A ClusteringSession is like a large-scale organization effort. It takes all the
    articles collected within a certain time frame and groups them based on their
    similarities. This helps in identifying trends, recurring themes, or related
    pieces of information across many articles.

    The session keeps track of various statistics about the clustering process,
    such as how many groups were formed, how many articles were processed, and
    how relevant or useful these groups are estimated to be.

        Attributes:
            workspace_id (str):  Example: 5eb7cf5a86d9755df3a6c593.
            data_start (datetime.datetime): Start date of the data range used for clustering
            data_end (datetime.datetime): End date of the data range used for clustering
            nb_days (int): Number of days in the data range
            field_id (Union[None, Unset, str]): MongoDB document ObjectID
            created_at (Union[Unset, datetime.datetime]): Timestamp when the session was created
            session_start (Union[None, Unset, datetime.datetime]): Timestamp when the clustering session started
            session_end (Union[None, Unset, datetime.datetime]): Timestamp when the clustering session ended
            status (Union[Unset, Status]):  Default: Status.PENDING.
            error (Union[None, Unset, str]): Error message if the session failed
            metadata (Union[Unset, ClusteringSessionMetadata]): Additional metadata about the clustering session
            articles_count (Union[None, Unset, int]): Number of articles processed in this session
            clusters_count (Union[None, Unset, int]): Total number of clusters formed
            relevant_clusters_count (Union[None, Unset, int]): Number of clusters deemed highly relevant
            somewhat_relevant_clusters_count (Union[None, Unset, int]): Number of clusters deemed somewhat relevant
            irrelevant_clusters_count (Union[None, Unset, int]): Number of clusters deemed not relevant
            noise_articles_ids (Union[List[str], None, Unset]): IDs of articles classified as noise
            noise_articles_count (Union[None, Unset, int]): Number of articles classified as noise
            clustered_articles_count (Union[None, Unset, int]): Number of articles successfully clustered
            summary (Union[None, Unset, str]): Overall summary of the clusteres deemed relevant
    """

    workspace_id: str
    data_start: datetime.datetime
    data_end: datetime.datetime
    nb_days: int
    field_id: Union[None, Unset, str] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    session_start: Union[None, Unset, datetime.datetime] = UNSET
    session_end: Union[None, Unset, datetime.datetime] = UNSET
    status: Union[Unset, Status] = Status.PENDING
    error: Union[None, Unset, str] = UNSET
    metadata: Union[Unset, "ClusteringSessionMetadata"] = UNSET
    articles_count: Union[None, Unset, int] = UNSET
    clusters_count: Union[None, Unset, int] = UNSET
    relevant_clusters_count: Union[None, Unset, int] = UNSET
    somewhat_relevant_clusters_count: Union[None, Unset, int] = UNSET
    irrelevant_clusters_count: Union[None, Unset, int] = UNSET
    noise_articles_ids: Union[List[str], None, Unset] = UNSET
    noise_articles_count: Union[None, Unset, int] = UNSET
    clustered_articles_count: Union[None, Unset, int] = UNSET
    summary: Union[None, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        workspace_id = self.workspace_id

        data_start = self.data_start.isoformat()

        data_end = self.data_end.isoformat()

        nb_days = self.nb_days

        field_id: Union[None, Unset, str]
        if isinstance(self.field_id, Unset):
            field_id = UNSET
        else:
            field_id = self.field_id

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        session_start: Union[None, Unset, str]
        if isinstance(self.session_start, Unset):
            session_start = UNSET
        elif isinstance(self.session_start, datetime.datetime):
            session_start = self.session_start.isoformat()
        else:
            session_start = self.session_start

        session_end: Union[None, Unset, str]
        if isinstance(self.session_end, Unset):
            session_end = UNSET
        elif isinstance(self.session_end, datetime.datetime):
            session_end = self.session_end.isoformat()
        else:
            session_end = self.session_end

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        error: Union[None, Unset, str]
        if isinstance(self.error, Unset):
            error = UNSET
        else:
            error = self.error

        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        articles_count: Union[None, Unset, int]
        if isinstance(self.articles_count, Unset):
            articles_count = UNSET
        else:
            articles_count = self.articles_count

        clusters_count: Union[None, Unset, int]
        if isinstance(self.clusters_count, Unset):
            clusters_count = UNSET
        else:
            clusters_count = self.clusters_count

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

        noise_articles_ids: Union[List[str], None, Unset]
        if isinstance(self.noise_articles_ids, Unset):
            noise_articles_ids = UNSET
        elif isinstance(self.noise_articles_ids, list):
            noise_articles_ids = self.noise_articles_ids

        else:
            noise_articles_ids = self.noise_articles_ids

        noise_articles_count: Union[None, Unset, int]
        if isinstance(self.noise_articles_count, Unset):
            noise_articles_count = UNSET
        else:
            noise_articles_count = self.noise_articles_count

        clustered_articles_count: Union[None, Unset, int]
        if isinstance(self.clustered_articles_count, Unset):
            clustered_articles_count = UNSET
        else:
            clustered_articles_count = self.clustered_articles_count

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
            }
        )
        if field_id is not UNSET:
            field_dict["_id"] = field_id
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if session_start is not UNSET:
            field_dict["session_start"] = session_start
        if session_end is not UNSET:
            field_dict["session_end"] = session_end
        if status is not UNSET:
            field_dict["status"] = status
        if error is not UNSET:
            field_dict["error"] = error
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if articles_count is not UNSET:
            field_dict["articles_count"] = articles_count
        if clusters_count is not UNSET:
            field_dict["clusters_count"] = clusters_count
        if relevant_clusters_count is not UNSET:
            field_dict["relevant_clusters_count"] = relevant_clusters_count
        if somewhat_relevant_clusters_count is not UNSET:
            field_dict["somewhat_relevant_clusters_count"] = somewhat_relevant_clusters_count
        if irrelevant_clusters_count is not UNSET:
            field_dict["irrelevant_clusters_count"] = irrelevant_clusters_count
        if noise_articles_ids is not UNSET:
            field_dict["noise_articles_ids"] = noise_articles_ids
        if noise_articles_count is not UNSET:
            field_dict["noise_articles_count"] = noise_articles_count
        if clustered_articles_count is not UNSET:
            field_dict["clustered_articles_count"] = clustered_articles_count
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

        def _parse_field_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        field_id = _parse_field_id(d.pop("_id", UNSET))

        _created_at = d.pop("created_at", UNSET)
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        def _parse_session_start(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                session_start_type_0 = isoparse(data)

                return session_start_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        session_start = _parse_session_start(d.pop("session_start", UNSET))

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

        _status = d.pop("status", UNSET)
        status: Union[Unset, Status]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = Status(_status)

        def _parse_error(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        error = _parse_error(d.pop("error", UNSET))

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, ClusteringSessionMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = ClusteringSessionMetadata.from_dict(_metadata)

        def _parse_articles_count(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        articles_count = _parse_articles_count(d.pop("articles_count", UNSET))

        def _parse_clusters_count(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        clusters_count = _parse_clusters_count(d.pop("clusters_count", UNSET))

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

        def _parse_noise_articles_ids(data: object) -> Union[List[str], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                noise_articles_ids_type_0 = cast(List[str], data)

                return noise_articles_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List[str], None, Unset], data)

        noise_articles_ids = _parse_noise_articles_ids(d.pop("noise_articles_ids", UNSET))

        def _parse_noise_articles_count(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        noise_articles_count = _parse_noise_articles_count(d.pop("noise_articles_count", UNSET))

        def _parse_clustered_articles_count(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        clustered_articles_count = _parse_clustered_articles_count(d.pop("clustered_articles_count", UNSET))

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
            field_id=field_id,
            created_at=created_at,
            session_start=session_start,
            session_end=session_end,
            status=status,
            error=error,
            metadata=metadata,
            articles_count=articles_count,
            clusters_count=clusters_count,
            relevant_clusters_count=relevant_clusters_count,
            somewhat_relevant_clusters_count=somewhat_relevant_clusters_count,
            irrelevant_clusters_count=irrelevant_clusters_count,
            noise_articles_ids=noise_articles_ids,
            noise_articles_count=noise_articles_count,
            clustered_articles_count=clustered_articles_count,
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
