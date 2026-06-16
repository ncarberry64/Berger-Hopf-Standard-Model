import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_finite_algebra_charge as discharge  # noqa: E402


def test_non_tautology_audit_contains_required_rows():
    discharge.export_outputs(ROOT)
    text = (ROOT / "theory" / "finite_algebra_charge_non_tautology_audit.md").read_text(encoding="utf-8")
    required_steps = [
        "finite algebra from closure dimensions",
        "C from central cyclic-channel projector",
        "sigma from orientation grading",
        "w from active orientation projection",
        "Q from orientation lowering plus cyclic shift",
        "T3 from active orientation generator",
        "Y as residual 2(Q-T3)",
        "comparison to SM charges",
    ]
    for step in required_steps:
        assert step in text
    assert "does not use SM particle names or known SM hypercharges" in text


def test_derivation_sections_do_not_import_specific_particle_labels():
    discharge.export_outputs(ROOT)
    derivation_files = [
        ROOT / "theory" / "derived_finite_algebra_uniqueness.md",
        ROOT / "theory" / "derived_boundary_charge_operator.md",
        ROOT / "theory" / "derived_boundary_hypercharge_operator.md",
    ]
    forbidden = re.compile(r"\b(quark|lepton|electron|neutrino|up|down)\b", re.IGNORECASE)
    for path in derivation_files:
        assert forbidden.search(path.read_text(encoding="utf-8")) is None
