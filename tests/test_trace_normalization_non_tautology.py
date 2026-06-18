import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_trace_normalization as trace  # noqa: E402


def test_non_tautology_audit_contains_required_rows():
    trace.export_outputs(ROOT)
    text = (ROOT / "theory" / "trace_normalization_non_tautology_audit.md").read_text(
        encoding="utf-8"
    )
    required = [
        "boundary Y table from prior theorem",
        "active sector trace contribution",
        "conjugate inactive sector trace contribution",
        "channel multiplicity",
        "orientation trace index",
        "cyclic trace index",
        "Abelian K1=10/3",
        "non-Abelian K2=K3=2",
        "eta_Y=3/5",
        "comparison to conventional hypercharge normalization",
    ]
    for row in required:
        assert row in text
    assert "does not use known Standard Model/GUT normalization as input" in text


def test_known_normalization_is_not_used_as_premise():
    trace.export_outputs(ROOT)
    derivation_text = "\n".join(
        (ROOT / "theory" / name).read_text(encoding="utf-8")
        for name in [
            "theorem_discharge_boundary_trace_normalization.md",
            "derived_boundary_trace_weights.md",
            "derived_hypercharge_normalization_factor.md",
            "derived_normalized_gauge_action_skeleton.md",
            "trace_normalization_non_tautology_audit.md",
        ]
    )
    forbidden_premises = [
        "because the SM uses 5/3 normalization",
        "because SU(5) uses 5/3",
        "imported from GUT normalization",
        "measured coupling values are predicted",
        "RG running is derived",
    ]
    for phrase in forbidden_premises:
        assert phrase not in derivation_text
