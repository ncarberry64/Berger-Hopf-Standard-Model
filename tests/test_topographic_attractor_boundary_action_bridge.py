from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm_topographic_attractor_bridge import (  # noqa: E402
    ENVIRONMENTAL_MASS_SHIFT_CANDIDATE_ONLY,
    STOCHASTIC_ATTRACTOR_DRESSING_STRUCTURAL_CANDIDATE,
    TOPOGRAPHIC_ATTRACTOR_BRIDGE_STRUCTURAL_CANDIDATE,
    attractor_susceptibility_proxy,
    audit_payload,
    brownian_dressing_factor,
    environmental_shift_candidate,
    export_topographic_attractor_bridge_outputs,
    generation_count_status_object,
    geometric_inertia_proxy,
    lepton_eta_8alpha_9pi,
    mode_norm_N,
    q_from_kj,
    threshold_gate,
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_mode_norm_and_brownian_reference_values() -> None:
    assert q_from_kj(0, 0) == 0
    assert q_from_kj(5, 2) == 1
    assert q_from_kj(9, 3) == 3

    assert mode_norm_N(0, 0) == 0
    assert mode_norm_N(5, 2) == 5
    assert mode_norm_N(9, 3) == 18

    assert brownian_dressing_factor(0.123, 0, 0) == 1.0
    assert brownian_dressing_factor(0.1, 9, 3) < brownian_dressing_factor(0.1, 5, 2)


def test_eta_formula_and_susceptibility_ordering() -> None:
    alpha = 1.0 / 137.035999084
    assert math.isclose(lepton_eta_8alpha_9pi(alpha), 8.0 * alpha / (9.0 * math.pi))

    tau_sus = attractor_susceptibility_proxy(0, 0)
    mu_sus = attractor_susceptibility_proxy(5, 2)
    e_sus = attractor_susceptibility_proxy(9, 3)
    assert tau_sus > mu_sus > e_sus

    assert geometric_inertia_proxy(9, 3, "lepton") > geometric_inertia_proxy(5, 2, "lepton")
    assert geometric_inertia_proxy(6, 0, "up") > geometric_inertia_proxy(6, 0, "lepton")


def test_environmental_shift_is_threshold_gated() -> None:
    assert threshold_gate(0.0, threshold=2.0, power=2.0) == 0.0
    assert environmental_shift_candidate(1.0, susceptibility=0.5, gate=0.0) == 0.0
    assert threshold_gate(10.0, threshold=1.0, power=2.0) > threshold_gate(
        1.0, threshold=10.0, power=2.0
    )


def test_generation_count_remains_candidate_not_proven() -> None:
    status = generation_count_status_object()
    assert status.ledger_generation_count == 3
    assert status.derived is False
    assert status.status in {
        "GENERATION_COUNT_GLOBAL_CURVATURE_STRUCTURAL_CANDIDATE",
        "GENERATION_COUNT_LEDGER_ASSUMPTION",
        "GENERATION_COUNT_OPEN",
    }


def test_payload_claim_flags_and_statuses_are_conservative() -> None:
    payload = audit_payload()

    assert payload["topographic_attractor_bridge_status"] == TOPOGRAPHIC_ATTRACTOR_BRIDGE_STRUCTURAL_CANDIDATE
    assert payload["stochastic_dressing_status"] == STOCHASTIC_ATTRACTOR_DRESSING_STRUCTURAL_CANDIDATE
    assert payload["environmental_mass_shift_status"] == ENVIRONMENTAL_MASS_SHIFT_CANDIDATE_ONLY
    assert payload["does_bridge_identify_A_q"] is True
    assert payload["does_bridge_identify_A_j"] is False
    assert payload["does_bridge_derive_exponential_dressing"] is False
    assert payload["does_bridge_derive_lepton_8_9"] is False
    assert payload["does_bridge_change_official_predictions"] is False
    assert payload["ordinary_environmental_mass_drift_claim"] is False
    assert payload["lab_mass_variation_claim"] is False
    assert payload["time_dependent_constants_official_claim"] is False
    assert payload["full_SM_derivation_claim"] is False
    assert payload["SM_replacement_claim"] is False
    assert payload["ordinary_FTL_neutrino_claim"] is False
    assert payload["forbidden_claims_absent"] is True
    assert payload["safe_to_merge_as_candidate_only"] is True
    assert payload["missing_assumptions"]


def test_frozen_sanity_remains_unchanged() -> None:
    sanity = audit_payload()["frozen_sanity"]

    assert sanity["BHSM_BARE_V1_unchanged"] is True
    assert sanity["BHSM_DRESSED_V1_CANDIDATE_unchanged"] is True
    assert sanity["dressed_branch_changes_only_c_over_t"] is True
    assert sanity["u_over_t_unchanged"] is True
    assert sanity["ckm_sin_theta_13_unchanged"] is True
    assert sanity["a_unchanged"] is True
    assert sanity["S_unchanged"] is True


def test_export_writes_valid_candidate_reports_without_touching_frozen_files() -> None:
    frozen_paths = [
        ROOT / "docs" / "frozen_predictions.md",
        ROOT / "docs" / "frozen_predictions.json",
    ]
    before = {path: _sha(path) for path in frozen_paths}

    export_topographic_attractor_bridge_outputs(ROOT)

    after = {path: _sha(path) for path in frozen_paths}
    assert before == after

    report_paths = [
        ROOT / "theory" / "topographic_attractor_boundary_action_bridge.md",
        ROOT / "theory" / "stochastic_attractor_dressing_candidate.md",
        ROOT / "theory" / "geometric_inertia_susceptibility_candidate.md",
        ROOT / "theory" / "generation_count_global_curvature_candidate.md",
        ROOT / "theory" / "environmental_mass_shift_safety_note.md",
        ROOT / "theory" / "Aq_Aj_topographic_connection_candidate.md",
        ROOT / "theory" / "lepton_attractor_hierarchy_candidate.md",
        ROOT / "theory" / "quark_attractor_hierarchy_candidate.md",
        ROOT / "audits" / "topographic_attractor_boundary_action_bridge_audit.md",
        ROOT / "audits" / "topographic_attractor_boundary_action_bridge_audit.json",
    ]
    for path in report_paths:
        assert path.exists()

    parsed = json.loads(
        (ROOT / "audits" / "topographic_attractor_boundary_action_bridge_audit.json").read_text()
    )
    assert parsed["official_outputs_modified"] is False
    assert parsed["frozen_predictions_modified"] is False
    assert parsed["does_bridge_derive_lepton_8_9"] is False


def test_reports_do_not_contain_forbidden_overclaims() -> None:
    export_topographic_attractor_bridge_outputs(ROOT)
    forbidden = [
        "bhsm is proven",
        "bhsm is confirmed",
        "replaces the standard model",
        "ordinary faster-than-light neutrino",
        "ordinary environmental mass drift is claimed",
        "full standard model derivation",
        "lepton 8/9 is derived",
    ]
    paths = [
        ROOT / "theory" / "topographic_attractor_boundary_action_bridge.md",
        ROOT / "audits" / "topographic_attractor_boundary_action_bridge_audit.md",
        ROOT / "theory" / "environmental_mass_shift_safety_note.md",
    ]
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in paths)
    for phrase in forbidden:
        assert phrase not in text
