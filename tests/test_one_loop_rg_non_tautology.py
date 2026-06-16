import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_one_loop_rg as rg  # noqa: E402


def test_non_tautology_audit_contains_required_rows():
    rg.export_outputs(ROOT)
    text = (ROOT / "theory" / "one_loop_rg_non_tautology_audit.md").read_text(
        encoding="utf-8"
    )
    required = [
        "one-loop QFT formula",
        "boundary fermion trace sums",
        "three-generation multiplicity",
        "gauge self-interaction terms",
        "scalar active-orientation doublet",
        "beta coefficient totals",
        "comparison to known low-energy SM one-loop coefficients",
    ]
    for row in required:
        assert row in text
    assert "does not use known SM beta coefficients as input" in text


def test_known_beta_table_is_not_used_as_premise():
    rg.export_outputs(ROOT)
    text = "\n".join(
        (ROOT / "theory" / name).read_text(encoding="utf-8")
        for name in [
            "theorem_discharge_one_loop_rg_boundary_content.md",
            "derived_one_loop_rg_formula_boundary.md",
            "derived_boundary_fermion_trace_sums.md",
            "derived_boundary_scalar_trace_sums.md",
            "derived_boundary_beta_coefficients.md",
            "one_loop_rg_non_tautology_audit.md",
        ]
    )
    forbidden = [
        "because the SM beta coefficients are known",
        "known Standard Model beta table as input",
        "using a Standard Model beta-coefficient table as input",
        "measured coupling values are predicted",
        "two-loop RG is derived",
    ]
    for phrase in forbidden:
        assert phrase not in text
