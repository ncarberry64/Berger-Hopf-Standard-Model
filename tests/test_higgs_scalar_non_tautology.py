import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_higgs_scalar as hs  # noqa: E402


def test_higgs_scalar_non_tautology_rows():
    hs.export_outputs(ROOT)
    text = (ROOT / "theory" / "higgs_scalar_non_tautology_audit.md").read_text()
    for row in [
        "cyclic neutrality C=0",
        "active-orientation fundamental",
        "neutral-vacuum requirement",
        "Y=+1 selection up to conjugation",
        "scalar charge table",
        "conjugate doublet",
        "unbroken Q",
        "scalar covariant derivative",
        "gauge-boson mass skeleton",
        "scalar potential skeleton",
        "comparison to known Higgs representation",
    ]:
        assert row in text
    assert "does not use the known SM Higgs representation as input" in text


def test_known_higgs_representation_not_used_as_premise():
    hs.export_outputs(ROOT)
    text = "\n".join(
        (ROOT / "theory" / name).read_text()
        for name in [
            "theorem_discharge_higgs_scalar_boundary_mechanism.md",
            "derived_active_scalar_orientation_doublet.md",
            "derived_scalar_charge_table.md",
            "derived_scalar_conjugate_doublet.md",
            "derived_electroweak_breaking_generator.md",
            "derived_scalar_covariant_derivative.md",
            "derived_scalar_potential_skeleton.md",
            "higgs_scalar_non_tautology_audit.md",
        ]
    )
    for phrase in [
        "because the SM Higgs is a doublet with Y=1",
        "known Standard Model Higgs doublet as input",
        "Higgs mass is predicted",
        "VEV is predicted",
        "quartic coupling is predicted",
        "Yukawa sector is derived",
    ]:
        assert phrase not in text
