"""Predeclared scoring for the next BHSM completion target."""

from __future__ import annotations

from .common import CompletionPriorityRow


def _row(
    target_id: str,
    title: str,
    linked: tuple[str, ...],
    necessity: int,
    locality: int,
    no_empirical: int,
    leverage: int,
    feasibility: int,
    runtime_penalty: int,
    rationale: str,
) -> CompletionPriorityRow:
    score = necessity + locality + no_empirical + leverage + feasibility - runtime_penalty
    return CompletionPriorityRow(
        target_id, title, linked, necessity, locality, no_empirical, leverage,
        feasibility, runtime_penalty, score, rationale,
    )


def build_full_completion_priority_map() -> tuple[CompletionPriorityRow, ...]:
    """Score local targets without using observed residuals or fit quality."""

    rows = (
        _row("boundary_measure_collar_transport", "Boundary measure and collar transport normalization", ("FC-01", "FC-03", "FC-07", "FC-09", "FC-10", "FC-11", "FC-12"), 5, 5, 5, 5, 4, 0, "Existing action and collar artifacts prove shape/identity subblocks; the remaining normalization affects seven completion categories."),
        _row("complete_action_response_cone", "Complete action-derived response cone", ("FC-02", "FC-07", "FC-12"), 5, 4, 5, 4, 2, 0, "High mathematical leverage, but complete action and variation data are still absent."),
        _row("charged_stiffness_action", "Charged stiffness action normalization", ("FC-03", "FC-05", "FC-06"), 5, 4, 5, 4, 3, 0, "Local artifacts expose candidate branches, but no unique Hessian selector is yet present."),
        _row("gauge_action_normalization", "Gauge action normalization", ("FC-01", "FC-09", "FC-11"), 4, 3, 5, 4, 2, 0, "Important cross-sector normalization with open boundary trace and measure inputs."),
        _row("ckm_exponent_source", "CKM 1/16 exponent source", ("FC-06",), 4, 3, 5, 3, 2, 0, "A focused theorem gap, but it removes fewer shared dependencies."),
        _row("lepton_eta_origin", "Charged-lepton eta_l origin", ("FC-05", "FC-11"), 4, 3, 5, 3, 2, 0, "The stochastic path is partially derived but still depends on shared normalization."),
        _row("external_hep_runtime", "FeynRules/UFO/MadGraph runtime validation", ("FC-14",), 3, 5, 5, 2, 3, 5, "Well localized but explicitly depends on external licensed/runtime components."),
    )
    return tuple(sorted(rows, key=lambda row: (-row.total_score, row.target_id)))


def select_highest_leverage_target() -> CompletionPriorityRow:
    return build_full_completion_priority_map()[0]
