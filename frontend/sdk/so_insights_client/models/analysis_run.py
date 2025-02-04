import datetime
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.analysis_run_analysis_type import AnalysisRunAnalysisType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.analysis_result import AnalysisResult
    from ..models.clustering_analysis_params import ClusteringAnalysisParams
    from ..models.report_analysis_params import ReportAnalysisParams


T = TypeVar("T", bound="AnalysisRun")


@_attrs_define
class AnalysisRun:
    """
    Attributes:
        workspace_id (str):  Example: 5eb7cf5a86d9755df3a6c593.
        analysis_type (AnalysisRunAnalysisType): Type of analysis performed in this run (e.g., 'clustering', 'report')
        data_start (datetime.datetime): Start date of the data range used for analysis
        data_end (datetime.datetime): End date of the data range used for analysis
        params (Union['ClusteringAnalysisParams', 'ReportAnalysisParams']):
        field_id (Union[None, Unset, str]): MongoDB document ObjectID
        created_at (Union[Unset, datetime.datetime]): Timestamp when the run was created
        status (Union[Unset, Any]): Current status of the analysis run Default: 'pending'.
        error (Union[None, Unset, str]): Error message if the run failed
        session_start (Union[None, Unset, datetime.datetime]): Timestamp when the session started
        session_end (Union[None, Unset, datetime.datetime]): Timestamp when the session ended
        result (Union['AnalysisResult', None, Unset]): Result of the analysis
    """

    workspace_id: str
    analysis_type: AnalysisRunAnalysisType
    data_start: datetime.datetime
    data_end: datetime.datetime
    params: Union["ClusteringAnalysisParams", "ReportAnalysisParams"]
    field_id: Union[None, Unset, str] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    status: Union[Unset, Any] = "pending"
    error: Union[None, Unset, str] = UNSET
    session_start: Union[None, Unset, datetime.datetime] = UNSET
    session_end: Union[None, Unset, datetime.datetime] = UNSET
    result: Union["AnalysisResult", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.analysis_result import AnalysisResult
        from ..models.clustering_analysis_params import ClusteringAnalysisParams

        workspace_id = self.workspace_id

        analysis_type = self.analysis_type.value

        data_start = self.data_start.isoformat()

        data_end = self.data_end.isoformat()

        params: dict[str, Any]
        if isinstance(self.params, ClusteringAnalysisParams):
            params = self.params.to_dict()
        else:
            params = self.params.to_dict()

        field_id: Union[None, Unset, str]
        if isinstance(self.field_id, Unset):
            field_id = UNSET
        else:
            field_id = self.field_id

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        status = self.status

        error: Union[None, Unset, str]
        if isinstance(self.error, Unset):
            error = UNSET
        else:
            error = self.error

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

        result: Union[None, Unset, dict[str, Any]]
        if isinstance(self.result, Unset):
            result = UNSET
        elif isinstance(self.result, AnalysisResult):
            result = self.result.to_dict()
        else:
            result = self.result

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "workspace_id": workspace_id,
                "analysis_type": analysis_type,
                "data_start": data_start,
                "data_end": data_end,
                "params": params,
            }
        )
        if field_id is not UNSET:
            field_dict["_id"] = field_id
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if status is not UNSET:
            field_dict["status"] = status
        if error is not UNSET:
            field_dict["error"] = error
        if session_start is not UNSET:
            field_dict["session_start"] = session_start
        if session_end is not UNSET:
            field_dict["session_end"] = session_end
        if result is not UNSET:
            field_dict["result"] = result

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.analysis_result import AnalysisResult
        from ..models.clustering_analysis_params import ClusteringAnalysisParams
        from ..models.report_analysis_params import ReportAnalysisParams

        d = src_dict.copy()
        workspace_id = d.pop("workspace_id")

        analysis_type = AnalysisRunAnalysisType(d.pop("analysis_type"))

        data_start = isoparse(d.pop("data_start"))

        data_end = isoparse(d.pop("data_end"))

        def _parse_params(data: object) -> Union["ClusteringAnalysisParams", "ReportAnalysisParams"]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                params_type_0 = ClusteringAnalysisParams.from_dict(data)

                return params_type_0
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            params_type_1 = ReportAnalysisParams.from_dict(data)

            return params_type_1

        params = _parse_params(d.pop("params"))

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

        status = d.pop("status", UNSET)

        def _parse_error(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        error = _parse_error(d.pop("error", UNSET))

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

        def _parse_result(data: object) -> Union["AnalysisResult", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                result_type_0 = AnalysisResult.from_dict(data)

                return result_type_0
            except:  # noqa: E722
                pass
            return cast(Union["AnalysisResult", None, Unset], data)

        result = _parse_result(d.pop("result", UNSET))

        analysis_run = cls(
            workspace_id=workspace_id,
            analysis_type=analysis_type,
            data_start=data_start,
            data_end=data_end,
            params=params,
            field_id=field_id,
            created_at=created_at,
            status=status,
            error=error,
            session_start=session_start,
            session_end=session_end,
            result=result,
        )

        analysis_run.additional_properties = d
        return analysis_run

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
