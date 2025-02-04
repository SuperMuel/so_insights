import datetime
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ..models.analysis_run_create_analysis_type import AnalysisRunCreateAnalysisType

if TYPE_CHECKING:
    from ..models.clustering_analysis_params import ClusteringAnalysisParams
    from ..models.report_analysis_params import ReportAnalysisParams


T = TypeVar("T", bound="AnalysisRunCreate")


@_attrs_define
class AnalysisRunCreate:
    """
    Attributes:
        data_start (datetime.datetime):
        data_end (datetime.datetime):
        analysis_type (AnalysisRunCreateAnalysisType):
        params (Union['ClusteringAnalysisParams', 'ReportAnalysisParams']):
    """

    data_start: datetime.datetime
    data_end: datetime.datetime
    analysis_type: AnalysisRunCreateAnalysisType
    params: Union["ClusteringAnalysisParams", "ReportAnalysisParams"]

    def to_dict(self) -> dict[str, Any]:
        from ..models.clustering_analysis_params import ClusteringAnalysisParams

        data_start = self.data_start.isoformat()

        data_end = self.data_end.isoformat()

        analysis_type = self.analysis_type.value

        params: dict[str, Any]
        if isinstance(self.params, ClusteringAnalysisParams):
            params = self.params.to_dict()
        else:
            params = self.params.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "data_start": data_start,
                "data_end": data_end,
                "analysis_type": analysis_type,
                "params": params,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.clustering_analysis_params import ClusteringAnalysisParams
        from ..models.report_analysis_params import ReportAnalysisParams

        d = src_dict.copy()
        data_start = isoparse(d.pop("data_start"))

        data_end = isoparse(d.pop("data_end"))

        analysis_type = AnalysisRunCreateAnalysisType(d.pop("analysis_type"))

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

        analysis_run_create = cls(
            data_start=data_start,
            data_end=data_end,
            analysis_type=analysis_type,
            params=params,
        )

        return analysis_run_create
