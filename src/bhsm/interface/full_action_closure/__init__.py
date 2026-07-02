"""Offline interfaces for the BHSM v4.0 full-action closure audit."""

from .alpha_i_action_gate import audit_alpha_i_action_gate
from .boundary_frame_averaging import audit_boundary_frame_averaging
from .ckm_completion_gate import audit_ckm_completion_gate
from .closure_report import build_full_action_closure_report, full_action_closure_report_to_markdown
from .dimensionful_scale_bridge import audit_dimensionful_scale_bridge
from .full_completion_gate import audit_full_completion_gate
from .g2_action_gate import audit_g2_action_gate
from .gauge_action_coefficient_k import audit_gauge_action_coefficient_k
from .gauge_denominator_source import audit_gauge_denominator_source
from .neutral_scale_gate import audit_neutral_scale_gate
from .scalar_topographic_gate import audit_scalar_topographic_gate
from .sector_weight_action_attachment import audit_sector_weight_action_attachment
from .source_search import search_full_action_sources
from .status_snapshot import build_status_snapshot
from .theorem_blocker_dag import build_theorem_blocker_dag
from .unified_action_skeleton import build_unified_action_skeleton


COMMAND_BUILDERS = {
    "full-action-status-snapshot": build_status_snapshot,
    "full-theorem-blocker-dag": build_theorem_blocker_dag,
    "unified-action-skeleton": build_unified_action_skeleton,
    "boundary-frame-averaging": audit_boundary_frame_averaging,
    "gauge-denominator-source": audit_gauge_denominator_source,
    "sector-weight-action-attachment": audit_sector_weight_action_attachment,
    "gauge-action-coefficient-k": audit_gauge_action_coefficient_k,
    "alpha-i-action-gate": audit_alpha_i_action_gate,
    "g2-action-gate": audit_g2_action_gate,
    "ckm-completion-gate": audit_ckm_completion_gate,
    "neutral-scale-gate": audit_neutral_scale_gate,
    "scalar-topographic-gate": audit_scalar_topographic_gate,
    "dimensionful-scale-bridge": audit_dimensionful_scale_bridge,
    "full-bhsm-completion-gate": audit_full_completion_gate,
    "full-action-closure-report": build_full_action_closure_report,
}

__all__ = ["COMMAND_BUILDERS", "build_full_action_closure_report", "full_action_closure_report_to_markdown", "search_full_action_sources"]
