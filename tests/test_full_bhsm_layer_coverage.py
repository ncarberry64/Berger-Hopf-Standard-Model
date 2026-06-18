from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_full_bhsm_completion import layer_registry  # noqa: E402


def test_all_required_layers_are_registered() -> None:
    names = {row["name"] for row in layer_registry()}
    assert "local SM gauge representation layer" in names
    assert "Berger-Hopf boundary channel layer" in names
    assert "topographic fourth-order stability layer" in names
    assert "response-selector layer" in names
    assert "collective curvature threshold layer" in names


def test_completion_document_contains_required_pipeline_and_ledgers() -> None:
    text = (ROOT / "theory" / "full_bhsm_completion_v1_candidate.md").read_text(
        encoding="utf-8"
    )
    assert "Full BHSM v1.0 Candidate is a repo-audited candidate architecture" in text
    assert "S_BHSM,candidate" in text
    assert "(B,L,T3)" in text
    assert "O_q = 3B - L" in text
    assert "O_j = -4T3 + 2(3B)(1/2 - T3)" in text
    assert "Omega_f_star = 3 * 2^(3B + (3B)(1/2 - T3))" in text
    assert "| charged lepton | (0,0) | (5,2) | (9,3) |" in text
    assert "| neutrino | (0,0) | (3,0) | (3,1) |" in text
    assert "| up | (0,0) | (6,0) | (10,1) |" in text
    assert "| down | (0,0) | (6,3) | (8,2) |" in text


def test_master_equation_map_classifies_required_equations() -> None:
    text = (ROOT / "theory" / "full_bhsm_master_equation_map.md").read_text(
        encoding="utf-8"
    )
    for equation in [
        "Omega_f = O_q q + O_j j",
        "H_f = C[Z_|Omega|]",
        "L_T = nabla^2 - B*nabla^4",
        "m_i = M_f [K_eff - K_crit]_+^p Z_i",
        "K_obs = K_visible + K_collective",
        "alpha_G = C_G/(6*pi^2)",
        "I_ff' mixing kernel",
    ]:
        assert equation in text
    for status in [
        "operational_tested",
        "structural_candidate",
        "partial_derivation",
        "failed_or_limited_candidate",
        "open_proof_obligation",
    ]:
        assert status in text
