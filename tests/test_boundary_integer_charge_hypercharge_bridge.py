from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_boundary_integer_primitives import (  # noqa: E402
    CLAIM_LABELS,
    build_results_payload,
    electric_charge_closed_form,
    electric_charge_from_integer_primitives,
    export_outputs,
    hypercharge_from_integer_primitives,
    sm_charge_table,
    t3_from_integer_primitives,
    validate_w,
)


EXPECTED = {
    "nu_L": (0, 1, +1, 1, Fraction(1, 2), Fraction(-1, 1), Fraction(0, 1)),
    "e_L": (0, 1, -1, 1, Fraction(-1, 2), Fraction(-1, 1), Fraction(-1, 1)),
    "u_L": (1, 0, +1, 1, Fraction(1, 2), Fraction(1, 3), Fraction(2, 3)),
    "d_L": (1, 0, -1, 1, Fraction(-1, 2), Fraction(1, 3), Fraction(-1, 3)),
    "nu_R optional": (0, 1, +1, 0, Fraction(0, 1), Fraction(0, 1), Fraction(0, 1)),
    "e_R": (0, 1, -1, 0, Fraction(0, 1), Fraction(-2, 1), Fraction(-1, 1)),
    "u_R": (1, 0, +1, 0, Fraction(0, 1), Fraction(4, 3), Fraction(2, 3)),
    "d_R": (1, 0, -1, 0, Fraction(0, 1), Fraction(-2, 3), Fraction(-1, 3)),
}

FROZEN_HASHES = {
    "docs/frozen_predictions.md": "A413C72F731A15B5AF0ED4DDDC3A58D428A60BA3367676FFCDA03FF546593439",
    "docs/frozen_predictions.json": "A9735A4A17934B524C4DE317254AE40838078FBA99274C95C0DBAE11A43C6C17",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def test_validate_w_accepts_only_weak_interface_activity_indicator() -> None:
    validate_w(0)
    validate_w(1)
    with pytest.raises(ValueError, match="w must be 0 or 1"):
        validate_w(2)


@pytest.mark.parametrize("field,values", EXPECTED.items())
def test_sm_charge_table_reproduced_exactly(field: str, values: tuple) -> None:
    C, ell, sigma, w, T3, Y, Q = values
    assert t3_from_integer_primitives(sigma, w) == T3
    assert hypercharge_from_integer_primitives(C, ell, sigma, w) == Y
    assert electric_charge_from_integer_primitives(C, ell, sigma, w) == Q


def test_electric_charge_is_independent_of_w_for_fixed_C_ell_sigma() -> None:
    for C in (0, 1):
        for ell in (0, 1):
            for sigma in (-1, 1):
                q_inactive = electric_charge_from_integer_primitives(C, ell, sigma, 0)
                q_active = electric_charge_from_integer_primitives(C, ell, sigma, 1)
                assert q_inactive == q_active
                assert q_active == electric_charge_closed_form(C, ell, sigma)


def test_table_uses_nu_R_for_neutrino_and_u_R_for_up_quark() -> None:
    fields = {row["field"] for row in sm_charge_table()}
    assert "nu_R optional" in fields
    assert "u_R" in fields
    assert "u_R optional" not in fields


def test_bridge_markdown_and_json_schema() -> None:
    payload = export_outputs(ROOT)
    parsed = json.loads(
        (ROOT / "theory" / "boundary_integer_primitives_results.json").read_text(
            encoding="utf-8"
        )
    )
    assert parsed == payload
    bridge = parsed["charge_hypercharge_bridge"]
    assert bridge == {
        "status": "candidate_diagnostic",
        "T3": "w*sigma/2",
        "Y": "C/3 - ell + (1-w)*sigma",
        "Q": "sigma/2 + C/6 - ell/2",
        "sm_charge_table_reproduced": True,
        "primitive_derivation_complete": False,
        "full_sm_derivation_claimed": False,
    }
    assert set(CLAIM_LABELS) <= set(parsed["claim_labels"])
    assert parsed["official_predictions_changed"] is False
    assert parsed["frozen_predictions_changed"] is False


def test_bridge_doc_has_required_guardrail_language_and_equations() -> None:
    text = (
        ROOT / "theory" / "boundary_integer_charge_hypercharge_bridge.md"
    ).read_text(encoding="utf-8")
    assert "This bridge reproduces the Standard Model electric charge and hypercharge table" in text
    assert "does not yet derive those primitives from Berger-Hopf boundary geometry" in text
    assert "does not constitute a full Standard Model derivation" in text
    assert "T3 = w*sigma/2" in text
    assert "Y = C/3 - ell + (1-w)*sigma" in text
    assert "Q = sigma/2 + C/6 - ell/2" in text
    assert "WEAK_INTERFACE_ACTIVITY_DERIVATION_REMAINS_OPEN" in text
    assert "CHIRAL_STRUCTURE_DERIVATION_REMAINS_OPEN" in text


def test_new_open_proof_obligations_are_present() -> None:
    payload = build_results_payload()
    obligations = payload["open_proof_obligations"]
    assert "Derive C as a color-active boundary sector from Berger-Hopf channel geometry." in obligations
    assert "Derive ell as a lepton-sector boundary indicator from boundary closure." in obligations
    assert "Derive sigma as upper/lower weak-interface orientation." in obligations
    assert "Derive w as weak-interface activity and explain why it corresponds to SM chiral doublet/singlet structure." in obligations
    assert "Derive anomaly cancellation from global boundary closure using the integer primitive charge table." in obligations


def test_frozen_prediction_files_are_unchanged() -> None:
    for relative, expected in FROZEN_HASHES.items():
        assert _sha256(ROOT / relative) == expected
