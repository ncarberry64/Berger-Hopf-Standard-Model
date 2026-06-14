from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm_hopf_berger_oneforms import (  # noqa: E402
    A_J_EXPLICIT_BERGER_BASE_COMPONENT_SUPPORTED,
    A_Q_EXPLICIT_HOPF_FIBER_ONEFORM_SUPPORTED,
    EXPLICIT_HOPF_BERGER_ONEFORMS_PARTIAL,
    HOPF_NORMALIZATION_RESOLVED,
    O_j,
    O_q,
    audit_payload,
    base_curvature_flux,
    export_explicit_hopf_berger_oneform_outputs,
    hopf_connection_symbolic,
    hopf_curvature_symbolic,
    hopf_fiber_holonomy,
    normalized_hopf_connection,
    omega_from_explicit_connection,
    q_from_kj,
    sector_connection_eigenvalues,
    sigma_1_symbolic,
    sigma_2_symbolic,
    sigma_3_symbolic,
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_symbolic_hopf_berger_oneforms_exist() -> None:
    assert "sigma_1" in sigma_1_symbolic()
    assert "sigma_2" in sigma_2_symbolic()
    assert sigma_3_symbolic() == "sigma_3 = dpsi + cos(theta) dphi"
    assert hopf_connection_symbolic() == "A_Hopf = sigma_3"
    assert normalized_hopf_connection() == "A_Hopf_norm = sigma_3/(2*pi)"
    assert "dA_Hopf" in hopf_curvature_symbolic()


def test_normalization_values_are_explicit() -> None:
    assert hopf_fiber_holonomy("unit_fiber_holonomy") == Fraction(1)
    assert hopf_fiber_holonomy("integer_phase") == Fraction(2)
    assert base_curvature_flux("chern_unit") == Fraction(1)
    assert base_curvature_flux("raw_sphere") == Fraction(2)

    payload = audit_payload()
    assert payload["hopf_normalization_status"] == HOPF_NORMALIZATION_RESOLVED
    assert payload["berger_base_normalization_status"] == "BERGER_BASE_NORMALIZATION_CONVENTION_DEPENDENT"
    assert payload["normalization_ambiguities"]


def test_q_and_representation_operator_values_are_exact() -> None:
    assert q_from_kj(5, 2) == 1
    assert q_from_kj(9, 3) == 3
    assert q_from_kj(6, 0) == 6
    assert q_from_kj(10, 1) == 8
    assert q_from_kj(6, 3) == 0
    assert q_from_kj(8, 2) == 4

    assert O_q(Fraction(0), Fraction(1)) == -1
    assert O_q(Fraction(1, 3), Fraction(0)) == 1
    assert O_j(Fraction(0), Fraction(-1, 2)) == 2
    assert O_j(Fraction(1, 3), Fraction(1, 2)) == -2
    assert O_j(Fraction(1, 3), Fraction(-1, 2)) == 4


def test_sector_eigenvalues_and_omega_pairs() -> None:
    lepton = sector_connection_eigenvalues("charged_lepton")
    up = sector_connection_eigenvalues("up")
    down = sector_connection_eigenvalues("down")
    neutrino = sector_connection_eigenvalues("neutrino")

    assert (lepton.O_q, lepton.O_j) == (Fraction(-1), Fraction(2))
    assert (up.O_q, up.O_j) == (Fraction(1), Fraction(-2))
    assert (down.O_q, down.O_j) == (Fraction(1), Fraction(4))
    assert (neutrino.O_q, neutrino.O_j) == (Fraction(-1), Fraction(-2))
    assert neutrino.candidate_only is True

    assert omega_from_explicit_connection(q_from_kj(5, 2), 2, 0, 1, Fraction(-1, 2)) == 3
    assert omega_from_explicit_connection(q_from_kj(9, 3), 3, 0, 1, Fraction(-1, 2)) == 3
    assert omega_from_explicit_connection(q_from_kj(6, 0), 0, Fraction(1, 3), 0, Fraction(1, 2)) == 6
    assert omega_from_explicit_connection(q_from_kj(10, 1), 1, Fraction(1, 3), 0, Fraction(1, 2)) == 6
    assert omega_from_explicit_connection(q_from_kj(6, 3), 3, Fraction(1, 3), 0, Fraction(-1, 2)) == 12
    assert omega_from_explicit_connection(q_from_kj(8, 2), 2, Fraction(1, 3), 0, Fraction(-1, 2)) == 12


def test_payload_statuses_are_conservative() -> None:
    payload = audit_payload()

    assert payload["explicit_hopf_berger_oneform_status"] == EXPLICIT_HOPF_BERGER_ONEFORMS_PARTIAL
    assert payload["A_q_status"] == A_Q_EXPLICIT_HOPF_FIBER_ONEFORM_SUPPORTED
    assert payload["A_j_status"] == A_J_EXPLICIT_BERGER_BASE_COMPONENT_SUPPORTED
    assert payload["does_A_q_have_explicit_oneform"] is True
    assert payload["does_A_j_have_explicit_oneform_or_curvature"] is True
    assert payload["does_q_couple_to_hopf_fiber"] is True
    assert payload["does_j_couple_to_berger_base"] is True
    assert payload["does_explicit_connection_reproduce_omega_l_u_d"] is True
    assert payload["does_this_close_boundary_connection"] is False
    assert payload["does_this_promote_lepton_8_9"] is False
    assert payload["forbidden_claims_absent"] is True
    assert payload["safe_to_merge_as_candidate_only"] is True
    assert payload["blockers_remaining"]


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

    export_explicit_hopf_berger_oneform_outputs(ROOT)

    after = {path: _sha(path) for path in frozen_paths}
    assert before == after

    report_paths = [
        ROOT / "theory" / "explicit_hopf_berger_boundary_oneforms.md",
        ROOT / "theory" / "hopf_fiber_connection_Aq.md",
        ROOT / "theory" / "berger_base_connection_Aj.md",
        ROOT / "theory" / "normalization_conventions_hopf_berger.md",
        ROOT / "theory" / "base_curvature_vs_oneform_Aj.md",
        ROOT / "theory" / "q_equals_k_minus_2j_representation_note.md",
        ROOT / "theory" / "Arep_with_explicit_hopf_berger_components.md",
        ROOT / "audits" / "explicit_hopf_berger_boundary_oneforms_audit.md",
        ROOT / "audits" / "explicit_hopf_berger_boundary_oneforms_audit.json",
    ]
    for path in report_paths:
        assert path.exists()

    parsed = json.loads((ROOT / "audits" / "explicit_hopf_berger_boundary_oneforms_audit.json").read_text())
    assert parsed["official_outputs_modified"] is False
    assert parsed["frozen_predictions_modified"] is False
    assert parsed["does_this_close_boundary_connection"] is False


def test_reports_do_not_contain_forbidden_overclaims() -> None:
    export_explicit_hopf_berger_oneform_outputs(ROOT)
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
        ROOT / "theory" / "explicit_hopf_berger_boundary_oneforms.md",
        ROOT / "audits" / "explicit_hopf_berger_boundary_oneforms_audit.md",
        ROOT / "theory" / "hopf_fiber_connection_Aq.md",
        ROOT / "theory" / "berger_base_connection_Aj.md",
    ]
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in paths)
    for phrase in forbidden:
        assert phrase not in text
