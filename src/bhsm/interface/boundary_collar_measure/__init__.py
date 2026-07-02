from .alpha_i_update import audit_alpha_i_update
from .boundary_collar_measure_source import audit_boundary_collar_measure_source
from .boundary_frame_averaging import audit_boundary_frame_averaging
from .ckm_value_update import audit_ckm_value_update
from .closure_report import build_boundary_collar_measure_report, boundary_collar_measure_report_to_markdown
from .full_completion_update import audit_full_completion_update
from .g2_update import audit_g2_update
from .gauge_action_attachment_update import audit_gauge_action_attachment_update
from .gauge_denominator_source import audit_gauge_denominator_source
from .gauge_trace_frame_average_attachment import audit_gauge_trace_frame_average_attachment
from .source_search import search_boundary_collar_measure_sources
from .three_boundary_frame_directions import audit_three_boundary_frame_directions
from .unit_s3_volume_normalization import audit_unit_s3_volume_normalization
from .universal_gauge_quantum_update import audit_universal_gauge_quantum_update


COMMAND_BUILDERS = {
    "boundary-collar-measure-search": search_boundary_collar_measure_sources,
    "boundary-collar-measure-source": audit_boundary_collar_measure_source,
    "unit-s3-volume-normalization": audit_unit_s3_volume_normalization,
    "three-boundary-frame-directions": audit_three_boundary_frame_directions,
    "boundary-frame-averaging-v4-1": audit_boundary_frame_averaging,
    "gauge-trace-frame-average-attachment": audit_gauge_trace_frame_average_attachment,
    "gauge-denominator-source-v4-1": audit_gauge_denominator_source,
    "universal-gauge-quantum-update": audit_universal_gauge_quantum_update,
    "gauge-action-attachment-update": audit_gauge_action_attachment_update,
    "alpha-i-update-v4-1": audit_alpha_i_update,
    "g2-update-v4-1": audit_g2_update,
    "ckm-value-update-v4-1": audit_ckm_value_update,
    "full-completion-update-v4-1": audit_full_completion_update,
    "boundary-collar-measure-report": build_boundary_collar_measure_report,
}

__all__ = ["COMMAND_BUILDERS", "boundary_collar_measure_report_to_markdown"]
