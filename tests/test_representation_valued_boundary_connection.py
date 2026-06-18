from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm_representation_boundary_connection import (  # noqa: E402
    NEUTRINO_PROJECTOR_CONSEQUENCE_CANDIDATE,
    O_j,
    O_q,
    audit_payload,
    color_coframe_operator,
    colored_lower_projector,
    export_representation_boundary_connection_outputs,
    lower_weak_projector,
    omega_charged_lepton,
    omega_down,
    omega_neutrino_candidate,
    omega_up,
    q_from_kj,
    sector_connection_eigenvalues,
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_representation_projectors_have_expected_values() -> None:
    assert color_coframe_operator(Fraction(0)) == 0
    assert color_coframe_operator(Fraction(1, 3)) == 1

    assert lower_weak_projector(Fraction(1, 2)) == 0
    assert lower_weak_projector(Fraction(-1, 2)) == 1

    assert colored_lower_projector(Fraction(0), Fraction(-1, 2)) == 0
    assert colored_lower_projector(Fraction(1, 3), Fraction(1, 2)) == 0
    assert colored_lower_projector(Fraction(1, 3), Fraction(-1, 2)) == 1

    assert O_q(Fraction(0), Fraction(1)) == -1
    assert O_q(Fraction(1, 3), Fraction(0)) == 1
    assert O_j(Fraction(0), Fraction(-1, 2)) == 2
    assert O_j(Fraction(1, 3), Fraction(1, 2)) == -2
    assert O_j(Fraction(1, 3), Fraction(-1, 2)) == 4


def test_sector_eigenvalues_reproduce_operational_omega_coefficients() -> None:
    lepton = sector_connection_eigenvalues("charged_lepton")
    up = sector_connection_eigenvalues("up")
    down = sector_connection_eigenvalues("down")
    neutrino = sector_connection_eigenvalues("neutrino")

    assert (lepton.O_q, lepton.O_j) == (Fraction(-1), Fraction(2))
    assert (up.O_q, up.O_j) == (Fraction(1), Fraction(-2))
    assert (down.O_q, down.O_j) == (Fraction(1), Fraction(4))
    assert (neutrino.O_q, neutrino.O_j) == (Fraction(-1), Fraction(-2))
    assert neutrino.status == NEUTRINO_PROJECTOR_CONSEQUENCE_CANDIDATE


def test_connection_reproduces_charged_mode_ledger_constants() -> None:
    for k, j in ((5, 2), (9, 3)):
        assert omega_charged_lepton(q_from_kj(k, j), j) == 3

    for k, j in ((6, 0), (10, 1)):
        assert omega_up(q_from_kj(k, j), j) == 6

    for k, j in ((6, 3), (8, 2)):
        assert omega_down(q_from_kj(k, j), j) == 12

    assert omega_neutrino_candidate(q=1, j=2) == -5


def test_audit_payload_is_candidate_only_and_keeps_blockers_explicit() -> None:
    payload = audit_payload()

    assert payload["does_universal_connection_reproduce_omega_l_u_d"] is True
    assert payload["does_connection_act_before_sector_evaluation"] is True
    assert payload["does_this_close_boundary_connection"] is False
    assert payload["does_this_promote_lepton_8_9"] is False
    assert payload["safe_to_merge_as_candidate_only"] is True
    assert payload["theorem_complete"] is False
    assert "representation_operator_embedding_of_sector_projector" in payload["blockers_closed"]
    assert "universal_tensor_product_connection_form" in payload["blockers_closed"]
    assert payload["blockers_remaining"]
    assert payload["missing_assumptions"] == payload["blockers_remaining"]
    assert payload["neutrino_candidate"]["ordinary_FTL_claim"] is False
    assert payload["neutrino_candidate"]["candidate_only"] is True
    assert payload["neutrino_candidate"]["no_numerical_PMNS_claims"] is True


def test_frozen_sanity_remains_unchanged() -> None:
    sanity = audit_payload()["frozen_sanity"]

    assert sanity["BHSM_BARE_V1_unchanged"] is True
    assert sanity["BHSM_DRESSED_V1_CANDIDATE_unchanged"] is True
    assert sanity["a_unchanged"] is True
    assert sanity["S_unchanged"] is True
    assert sanity["dressed_branch_changes_only_c_over_t"] is True
    assert sanity["u_over_t_unchanged"] is True
    assert sanity["ckm_sin_theta_13_unchanged"] is True


def test_export_writes_valid_reports_without_touching_frozen_predictions() -> None:
    frozen_paths = [
        ROOT / "docs" / "frozen_predictions.md",
        ROOT / "docs" / "frozen_predictions.json",
    ]
    before = {path: _sha(path) for path in frozen_paths}

    payload = export_representation_boundary_connection_outputs(ROOT)

    after = {path: _sha(path) for path in frozen_paths}
    assert before == after
    assert payload["official_outputs_modified"] is False
    assert payload["frozen_predictions_modified"] is False

    report_paths = [
        ROOT / "theory" / "representation_valued_boundary_connection.md",
        ROOT / "theory" / "tensor_product_boundary_connection_candidate.md",
        ROOT / "theory" / "hopf_berger_two_component_connection.md",
        ROOT / "theory" / "gauge_safe_boundary_projectors.md",
        ROOT / "theory" / "neutrino_representation_connection_consequence.md",
        ROOT / "audits" / "representation_valued_boundary_connection_audit.md",
        ROOT / "audits" / "representation_valued_boundary_connection_audit.json",
    ]
    for path in report_paths:
        assert path.exists()

    parsed = json.loads((ROOT / "audits" / "representation_valued_boundary_connection_audit.json").read_text())
    assert parsed["does_universal_connection_reproduce_omega_l_u_d"] is True
    assert parsed["does_this_close_boundary_connection"] is False


def test_reports_do_not_contain_forbidden_overclaims() -> None:
    export_representation_boundary_connection_outputs(ROOT)
    forbidden = [
        "standard model replacement",
        "bhsm is proven",
        "bhsm is confirmed",
        "ordinary faster-than-light neutrino claim is made",
        "ordinary environmental mass-drift claim",
        "full standard model derivation claim is made",
    ]
    paths = [
        ROOT / "theory" / "representation_valued_boundary_connection.md",
        ROOT / "audits" / "representation_valued_boundary_connection_audit.md",
        ROOT / "theory" / "tensor_product_boundary_connection_candidate.md",
    ]
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in paths)
    for phrase in forbidden:
        assert phrase not in text
