from .alpha_i_update import audit_alpha_i_update
from .berger_anisotropy_compatibility import audit_berger_anisotropy_compatibility
from .ckm_value_update import audit_ckm_value_update
from .closure_report import build_berger_frame_weighting_report, berger_frame_weighting_report_to_markdown
from .denominator_update import audit_denominator_update
from .equal_frame_weighting import audit_equal_frame_weighting
from .frame_average_normalization import audit_frame_average_normalization
from .full_completion_update import audit_full_completion_update
from .g2_update import audit_g2_update
from .gauge_action_attachment_update import audit_gauge_action_attachment_update
from .gauge_trace_frame_average_attachment import audit_gauge_trace_frame_average_attachment
from .source_search import search_berger_frame_weighting_sources
from .universal_quantum_update import audit_universal_quantum_update


COMMAND_BUILDERS = {
    "berger-frame-weighting-search": search_berger_frame_weighting_sources,
    "equal-frame-weighting": audit_equal_frame_weighting,
    "frame-average-normalization": audit_frame_average_normalization,
    "berger-anisotropy-compatibility": audit_berger_anisotropy_compatibility,
    "gauge-trace-frame-average-attachment-v4-2": audit_gauge_trace_frame_average_attachment,
    "gauge-denominator-update-v4-2": audit_denominator_update,
    "universal-quantum-update-v4-2": audit_universal_quantum_update,
    "gauge-action-attachment-update-v4-2": audit_gauge_action_attachment_update,
    "alpha-i-update-v4-2": audit_alpha_i_update,
    "g2-update-v4-2": audit_g2_update,
    "ckm-value-update-v4-2": audit_ckm_value_update,
    "full-completion-update-v4-2": audit_full_completion_update,
    "berger-frame-weighting-report": build_berger_frame_weighting_report,
}

__all__ = ["COMMAND_BUILDERS", "berger_frame_weighting_report_to_markdown"]
