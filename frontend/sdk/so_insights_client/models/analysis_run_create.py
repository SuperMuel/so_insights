import datetime
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ..models.analysis_type import AnalysisType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.agentic_analysis_params import AgenticAnalysisParams
    from ..models.clustering_analysis_params import ClusteringAnalysisParams


T = TypeVar("T", bound="AnalysisRunCreate")


@_attrs_define
class AnalysisRunCreate:
    """
    Attributes:
        data_start (datetime.datetime):
        data_end (datetime.datetime):
        analysis_type (AnalysisType):
        params (Union['AgenticAnalysisParams', 'ClusteringAnalysisParams', None, Unset]): Parameters for the analysis.
            If None, default parameters for the workspace will be used.
    """

    data_start: datetime.datetime
    data_end: datetime.datetime
    analysis_type: AnalysisType
    params: Union["AgenticAnalysisParams", "ClusteringAnalysisParams", None, Unset] = UNSET

    def to_dict(self) -> dict[str, Any]:
        from ..models.agentic_analysis_params import AgenticAnalysisParams
        from ..models.clustering_analysis_params import ClusteringAnalysisParams

        data_start = self.data_start.isoformat()

        data_end = self.data_end.isoformat()

        analysis_type = self.analysis_type.value

        params: Union[None, Unset, dict[str, Any]]
        if isinstance(self.params, Unset):
            params = UNSET
        elif isinstance(self.params, ClusteringAnalysisParams):
            params = self.params.to_dict()
        elif isinstance(self.params, AgenticAnalysisParams):
            params = self.params.to_dict()
        else:
            params = self.params

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "data_start": data_start,
                "data_end": data_end,
                "analysis_type": analysis_type,
            }
        )
        if params is not UNSET:
            field_dict["params"] = params

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.agentic_analysis_params import AgenticAnalysisParams
        from ..models.clustering_analysis_params import ClusteringAnalysisParams

        d = src_dict.copy()
        data_start = isoparse(d.pop("data_start"))

        data_end = isoparse(d.pop("data_end"))

        analysis_type = AnalysisType(d.pop("analysis_type"))

        def _parse_params(data: object) -> Union["AgenticAnalysisParams", "ClusteringAnalysisParams", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                params_type_0 = ClusteringAnalysisParams.from_dict(data)

                return params_type_0
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                params_type_1 = AgenticAnalysisParams.from_dict(data)

                return params_type_1
            except:  # noqa: E722
                pass
            return cast(Union["AgenticAnalysisParams", "ClusteringAnalysisParams", None, Unset], data)

        params = _parse_params(d.pop("params", UNSET))

        analysis_run_create = cls(
            data_start=data_start,
            data_end=data_end,
            analysis_type=analysis_type,
            params=params,
        )

        return analysis_run_create
