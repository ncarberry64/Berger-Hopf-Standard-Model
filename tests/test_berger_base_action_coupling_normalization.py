from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm_berger_base_action_coupling import (  # noqa: E402
    A_J_ACTION_COUPLING_PARTIAL,
    A_REP_TRUE_CONNECTION_PARTIAL,
    BASE_CURVATURE_NORMALIZATION_CONVENTION_DEPENDENT,
    BERGER_BASE_ACTION_COUPLING_PARTIAL,
    O_j,
    O_q,
    audit_payload,
    base_curvature_flux_status,
    berger_metric_symbolic,
    color_coframe_operator,
    colored_lower_projector,
    export_berger_base_action_coupling_outputs,
    horizontal_coframe_dimension,
    hopf_connection_Aq,
    hopf_curvature_Fq,
    lower_weak_projector,
    mode_pair_omega_values,
    omega_from_Arep,
    q_from_kj,
    representation_boundary_connection_terms,
    sigma_1_symbolic,
    sigma_2_symbolic,
    sigma_3_symbolic,
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_symbolic_hopf_berger_and_coframe_objects_exist() -> None:
    assert "sigma_1" in sigma_1_symbolic()
    assert "sigma_2" in sigma_2_symbolic()
    assert "sigma_3" in sigma_3_symbolic()
    assert hopf_connection_Aq() == "A_q = sigma_3/(2*pi)"
    assert "dA_Hopf" in hopf_curvature_Fq()
    assert "g_Berger" in berger_metric_symbolic("R", "r")
    assert horizontal_coframe_dimension() == 2


def test_exact_q_and_projector_values() -> None:
    assert q_from_kj(5, 2) == 1
    assert q_from_kj(9, 3) == 3
    assert q_from_kj(6, 0) == 6
    assert q_from_kj(10, 1) == 8
    assert q_from_kj(6, 3) == 0
    assert q_from_kj(8, 2) == 4

    assert color_coframe_operator(Fraction(1, 3)) == 1
    assert lower_weak_projector(Fraction(-1, 2)) == 1
    assert colored_lower_projector(Fraction(1, 3), Fraction(-1, 2)) == 1

    assert O_q(Fraction(0), Fraction(1)) == -1
    assert O_q(Fraction(1, 3), Fraction(0)) == 1
    assert O_j(Fraction(0), Fraction(-1, 2)) == 2
    assert O_j(Fraction(1, 3), Fraction(1, 2)) == -2
    assert O_j(Fraction(1, 3), Fraction(-1, 2)) == 4


def test_Arep_terms_and_mode_pair_values_are_exact() -> None:
    lepton = representation_boundary_connection_terms(0, 1, Fraction(-1, 2))
    up = representation_boundary_connection_terms(Fraction(1, 3), 0, Fraction(1, 2))
    down = representation_boundary_connection_terms(Fraction(1, 3), 0, Fraction(-1, 2))

    assert (lepton.O_q, lepton.O_j) == (Fraction(-1), Fraction(2))
    assert (up.O_q, up.O_j) == (Fraction(1), Fraction(-2))
    assert (down.O_q, down.O_j) == (Fraction(1), Fraction(4))
    assert "D_boundary_rep" in lepton.term

    assert mode_pair_omega_values("charged_lepton") == (Fraction(3), Fraction(3))
    assert mode_pair_omega_values("up") == (Fraction(6), Fraction(6))
    assert mode_pair_omega_values("down") == (Fraction(12), Fraction(12))
    assert omega_from_Arep(1, 2, 0, 1, Fraction(-1, 2)) == 3


def test_base_curvature_normalization_is_explicit_but_not_global() -> None:
    status = base_curvature_flux_status()
    assert status["status"] == BASE_CURVATURE_NORMALIZATION_CONVENTION_DEPENDENT
    assert status["flux_unit"] == Fraction(1)
    assert status["globally_fixed"] is False


def test_payload_statuses_are_partial_not_overclaimed() -> None:
    payload = audit_payload()

    assert payload["berger_base_action_coupling_status"] == BERGER_BASE_ACTION_COUPLING_PARTIAL
    assert payload["A_j_action_coupling_status"] == A_J_ACTION_COUPLING_PARTIAL
    assert payload["A_rep_true_connection_status"] == A_REP_TRUE_CONNECTION_PARTIAL
    assert payload["does_A_j_have_action_coupling"] is True
    assert payload["does_A_j_normalization_become_global"] is False
    assert payload["does_Arep_act_on_boundary_tensor_bundle"] is True
    assert payload["does_Arep_reproduce_omega_l_u_d"] is True
    assert payload["does_this_close_boundary_connection"] is False
    assert payload["does_this_promote_lepton_8_9"] is False
    assert payload["normalization_ambiguities"]
    assert payload["missing_assumptions"] == payload["blockers_remaining"]
    assert payload["forbidden_claims_absent"] is True


def test_frozen_sanity_remains_unchanged() -> None:
    sanity = audit_payload()["frozen_sanity"]

    assert sanity["BHSM_BARE_V1_unchanged"] is True
    assert sanity["BHSM_DRESSED_V1_CANDIDATE_unchanged"] is True
    assert sanity["dressed_branch_changes_only_c_over_t"] is True
    assert sanity["u_over_t_unchanged"] is True
    assert sanity["ckm_sin_theta_13_unchanged"] is True
    assert sanity["a_unchanged"] is True
    assert sanity["S_unchanged"] is True


def test_export_writes_reports_without_touching_frozen_predictions() -> None:
    frozen_paths = [
        ROOT / "docs" / "frozen_predictions.md",
        ROOT / "docs" / "frozen_predictions.json",
    ]
    before = {path: _sha(path) for path in frozen_paths}

    export_berger_base_action_coupling_outputs(ROOT)

    after = {path: _sha(path) for path in frozen_paths}
    assert before == after

    report_paths = [
        ROOT / "theory" / "berger_base_action_coupling_normalization.md",
        ROOT / "theory" / "boundary_minimal_coupling_candidate.md",
        ROOT / "theory" / "berger_casimir_decomposition_candidate.md",
        ROOT / "theory" / "base_curvature_cern_normalization.md",
        ROOT / "theory" / "horizontal_coframe_coupling_candidate.md",
        ROOT / "theory" / "berger_anisotropy_variation_candidate.md",
        ROOT / "theory" / "Arep_true_boundary_connection_candidate.md",
        ROOT / "theory" / "down_projector_action_coupling_note.md",
        ROOT / "audits" / "berger_base_action_coupling_normalization_audit.md",
        ROOT / "audits" / "berger_base_action_coupling_normalization_audit.json",
    ]
    for path in report_paths:
        assert path.exists()

    parsed = json.loads((ROOT / "audits" / "berger_base_action_coupling_normalization_audit.json").read_text())
    assert parsed["official_outputs_modified"] is False
    assert parsed["frozen_predictions_modified"] is False
    assert parsed["does_this_close_boundary_connection"] is False


def test_reports_do_not_contain_forbidden_overclaims() -> None:
    export_berger_base_action_coupling_outputs(ROOT)
    forbidden = [
        "bhsm is proven",
        "bhsm is confirmed",
        "replaces the standard model",
        "ordinary faster-than-light neutrino",
        "ordinary environmental mass-drift",
        "ordinary environmental mass drift",
        "full standard model derivation",
        "lepton 8/9 is derived",
    ]
    paths = [
        ROOT / "theory" / "berger_base_action_coupling_normalization.md",
        ROOT / "audits" / "berger_base_action_coupling_normalization_audit.md",
        ROOT / "theory" / "boundary_minimal_coupling_candidate.md",
    ]
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in paths)
    for phrase in forbidden:
        assert phrase not in text
