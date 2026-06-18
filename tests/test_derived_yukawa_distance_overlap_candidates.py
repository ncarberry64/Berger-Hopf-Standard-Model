import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_yukawa_distance_overlap as d  # noqa: E402


def test_candidate_overlap_laws_have_expected_statuses():
    laws = {law.name: law for law in d.candidate_overlap_laws()}
    assert set(laws) == {
        "exponential_L1",
        "gaussian_D2",
        "power_dressing",
        "boundary_action_hessian",
        "selection_only",
    }
    assert laws["selection_only"].status == d.LawStatus.DERIVED_CONDITIONAL.value
    assert laws["exponential_L1"].status == d.LawStatus.STRUCTURALLY_MOTIVATED_NOT_DERIVED.value
    assert laws["gaussian_D2"].status == d.LawStatus.STRUCTURALLY_MOTIVATED_NOT_DERIVED.value
    assert laws["power_dressing"].status == d.LawStatus.STRUCTURALLY_MOTIVATED_NOT_DERIVED.value
    assert laws["boundary_action_hessian"].status == d.LawStatus.REMAINS_OPEN.value
    assert "exp[-eta_f D_f(i,j)]" in laws["exponential_L1"].formula


def test_candidate_laws_document_contains_all_rows():
    d.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_yukawa_distance_overlap_candidates.md").read_text()
    for name in ["exponential_L1", "gaussian_D2", "power_dressing", "boundary_action_hessian", "selection_only"]:
        assert name in text
    assert "STRUCTURALLY_MOTIVATED_NOT_DERIVED" in text
    assert "REMAINS_OPEN" in text
