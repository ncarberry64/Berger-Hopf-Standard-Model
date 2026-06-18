import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_qj_eigenfunction_map as qj  # noqa: E402


def test_internal_local_feature_vector_has_value_gradient_and_hessian_entries():
    qj.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_internal_local_feature_vectors.md").read_text()
    mode = qj.generation_modes()["cyclic_upper"][1]
    vector = qj.local_feature_vector(mode)

    assert len(vector) == 10
    assert vector[0] == "psi_q6_j0(y)|_y0"
    assert vector[1:4] == ("d1 psi_q6_j0(y)|_y0", "d2 psi_q6_j0(y)|_y0", "d3 psi_q6_j0(y)|_y0")
    assert vector[4:] == (
        "d11 psi_q6_j0(y)|_y0",
        "d12 psi_q6_j0(y)|_y0",
        "d13 psi_q6_j0(y)|_y0",
        "d22 psi_q6_j0(y)|_y0",
        "d23 psi_q6_j0(y)|_y0",
        "d33 psi_q6_j0(y)|_y0",
    )
    assert "\n".join(vector) in text
    assert "one value, three gradient components, and six Hessian components" in text
