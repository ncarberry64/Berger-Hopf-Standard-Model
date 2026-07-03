from .coframe_basis_selection import audit_coframe_basis_selection
from .closure_report import build_berger_hodge_component_report, berger_hodge_component_report_to_markdown
from .denominator_update import audit_denominator_update
from .downstream_update import audit_downstream_update
from .equal_coefficient_update import audit_equal_coefficient_update
from .frame_average_update import audit_frame_average_update
from .full_completion_update import audit_full_completion_update
from .gauge_attachment_update import audit_gauge_attachment_update
from .gauge_trace_hodge_expansion import audit_gauge_trace_hodge_expansion
from .hodge_component_map import audit_hodge_component_map
from .source_search import search_berger_hodge_component_sources

COMMAND_BUILDERS = {
    "berger-hodge-component-map-search": search_berger_hodge_component_sources,
    "berger-hodge-component-map": audit_hodge_component_map,
    "gauge-action-coframe-selection": audit_coframe_basis_selection,
    "gauge-trace-hodge-component-expansion": audit_gauge_trace_hodge_expansion,
    "equal-coefficient-update-v4-4": audit_equal_coefficient_update,
    "frame-average-update-v4-4": audit_frame_average_update,
    "gauge-attachment-update-v4-4": audit_gauge_attachment_update,
    "denominator-update-v4-4": audit_denominator_update,
    "downstream-update-v4-4": audit_downstream_update,
    "full-completion-update-v4-4": audit_full_completion_update,
    "berger-hodge-component-report": build_berger_hodge_component_report,
}
