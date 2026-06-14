from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm_boundary_connection_holonomy import (  # noqa: E402
    BOUNDARY_CONNECTION_HOLONOMY_STRUCTURAL_CANDIDATE,
    CKM_H_MIX_DIM4_ANALOGY_ONLY,
    COEFFICIENT_ORIGIN_STRUCTURAL_CANDIDATE,
    LEPTON_8_9_CHANNEL_RULE_STRUCTURAL_CANDIDATE,
    NEUTRINO_LEAKAGE_CHANNEL_REFINED,
    PURE_FIBER_DOUBLE_BRANCH_ANALOGY_ONLY,
    audit_payload,
    check_mode_pair_constant_level,
    coefficient_origin_status,
    connection_candidate_status,
    cyclic_dimension_from_holonomy,
    export_boundary_connection_outputs,
    holonomy_integer_status,
    lepton_channel_consequence,
    mode_pair_checks,
    omega_down,
    omega_lepton,
    omega_linear,
    omega_up,
    q_from_kj,
)
from constants import ALPHA_INV_LOW_ENERGY  # noqa: E402


def _sha(path: str) -> str:
    return hashlib.sha256(ROOT.joinpath(path).read_bytes()).hexdigest()


def test_linear_holonomy_functions_recover_known_levels() -> None:
    assert q_from_kj(5, 2) == 1
    assert omega_linear(1, 2, -1, 2) == 3
    assert omega_lepton(q_from_kj(5, 2), 2) == 3
    assert omega_lepton(q_from_kj(9, 3), 3) == 3
    assert omega_up(q_from_kj(6, 0), 0) == 6
    assert omega_up(q_from_kj(10, 1), 1) == 6
    assert omega_down(q_from_kj(6, 3), 3) == 12
    assert omega_down(q_from_kj(8, 2), 2) == 12


def test_mode_pair_constant_level_and_holonomy_dimension() -> None:
    check = check_mode_pair_constant_level(((5, 2), (9, 3)), omega_lepton)
    assert check["constant"] is True
    assert check["level"] == 3
    all_checks = mode_pair_checks()
    assert all_checks["lepton"]["level"] == 3
    assert all_checks["up"]["level"] == 6
    assert all_checks["down"]["level"] == 12
    assert holonomy_integer_status(3)["integer"] is True
    assert cyclic_dimension_from_holonomy(3) == 3
    try:
        cyclic_dimension_from_holonomy(0)
    except ValueError:
        pass
    else:  # pragma: no cover
        raise AssertionError("zero holonomy level should be rejected")


def test_lepton_channel_consequence_arithmetic() -> None:
    alpha = 1.0 / ALPHA_INV_LOW_ENERGY
    consequence = lepton_channel_consequence(alpha)
    assert consequence["dim_H_l"] == 3
    assert consequence["active_fraction"] == 8 / 9
    assert math.isclose(consequence["eta_l"], 8 * alpha / (9 * math.pi))
    assert consequence["status"] == LEPTON_8_9_CHANNEL_RULE_STRUCTURAL_CANDIDATE
    assert consequence["derived"] is False


def test_candidate_and_coefficient_statuses_are_not_derived() -> None:
    assert connection_candidate_status("sector_projected").derived is False
    assert connection_candidate_status("hopf").status.endswith("STRUCTURAL_CANDIDATE")
    assert connection_candidate_status("topographic_surface").status.endswith("INTERPRETATION_ONLY")
    rule = coefficient_origin_status("down")
    assert rule.status == COEFFICIENT_ORIGIN_STRUCTURAL_CANDIDATE
    assert rule.a_q == 1
    assert rule.b_j == 4
    try:
        coefficient_origin_status("unknown")
    except ValueError:
        pass
    else:  # pragma: no cover
        raise AssertionError("unknown sector should be rejected")


def test_payload_statuses_and_schema() -> None:
    payload = audit_payload()
    assert payload["official_outputs_modified"] is False
    assert payload["frozen_predictions_modified"] is False
    assert payload["prs_opened"] is False
    assert payload["boundary_connection_status"] == BOUNDARY_CONNECTION_HOLONOMY_STRUCTURAL_CANDIDATE
    assert payload["coefficient_origin_status"] == COEFFICIENT_ORIGIN_STRUCTURAL_CANDIDATE
    assert payload["does_holonomy_produce_3_6_12"] is True
    assert payload["does_dim_H_equal_abs_Omega_follow"] is False
    assert payload["does_lepton_8_9_follow"] is False
    assert payload["pure_fiber_consequence_status"] == PURE_FIBER_DOUBLE_BRANCH_ANALOGY_ONLY
    assert payload["ckm_consequence_status"] == CKM_H_MIX_DIM4_ANALOGY_ONLY
    assert payload["neutrino_consequence_status"] == NEUTRINO_LEAKAGE_CHANNEL_REFINED
    assert payload["blockers_closed"] == ()
    assert payload["derived_components"] == ()
    assert payload["safe_to_merge_as_candidate_only"] is True


def test_official_outputs_and_frozen_files_unchanged_by_export() -> None:
    frozen_md = _sha("docs/frozen_predictions.md")
    frozen_json = _sha("docs/frozen_predictions.json")
    payload = export_boundary_connection_outputs(ROOT)
    assert _sha("docs/frozen_predictions.md") == frozen_md
    assert _sha("docs/frozen_predictions.json") == frozen_json
    sanity = payload["frozen_sanity"]
    assert sanity["BHSM_BARE_V1_unchanged"] is True
    assert sanity["BHSM_DRESSED_V1_CANDIDATE_unchanged"] is True
    assert sanity["dressed_branch_changes_only_c_over_t"] is True
    assert sanity["u_over_t_unchanged"] is True
    assert sanity["ckm_sin_theta_13_unchanged"] is True
    changed = [row for row in payload["official_branch_comparison"]["rows"] if row["changed"]]
    assert [row["quantity"] for row in changed] == ["c/t"]


def test_audit_json_validates() -> None:
    export_boundary_connection_outputs(ROOT)
    path = ROOT / "audits" / "boundary_connection_holonomy_construction_audit.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "official_outputs_modified",
        "frozen_predictions_modified",
        "prs_opened",
        "boundary_connection_status",
        "hopf_connection_status",
        "berger_axis_connection_status",
        "sector_projected_connection_status",
        "topographic_surface_connection_status",
        "electroweak_boundary_connection_status",
        "coefficient_origin_status",
        "does_holonomy_produce_3_6_12",
        "does_dim_H_equal_abs_Omega_follow",
        "does_lepton_8_9_follow",
        "pure_fiber_consequence_status",
        "ckm_consequence_status",
        "neutrino_consequence_status",
        "blockers_closed",
        "blockers_remaining",
        "missing_assumptions",
        "forbidden_claims_absent",
        "safe_to_merge_as_candidate_only",
    }
    assert required.issubset(data)
    assert data["forbidden_claims_absent"] is True


def test_no_forbidden_claims_in_new_reports() -> None:
    export_boundary_connection_outputs(ROOT)
    paths = [
        "theory/boundary_connection_holonomy_construction.md",
        "audits/boundary_connection_holonomy_construction_audit.md",
        "theory/topographic_surface_connection_candidate.md",
    ]
    text = "\n".join(ROOT.joinpath(path).read_text(encoding="utf-8").lower() for path in paths)
    forbidden = [
        "ordinary faster-than-light neutrino claim is made",
        "ordinary environmental mass-drift claim",
        "standard model replacement",
        "bhsm is proven",
        "bhsm is confirmed",
    ]
    for phrase in forbidden:
        assert phrase not in text
    assert "no ordinary superluminal neutrino claim is made" in text
    assert "no ordinary environmental mass drift claim is made" in text
