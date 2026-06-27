from pathlib import Path

from bhsm.interface.matrix_adapters import load_ckm_matrix_artifact, load_cp_phase_artifact, load_pmns_matrix_artifact

ROOT = Path(__file__).resolve().parents[1]


def test_matrix_and_phase_adapters_use_local_artifacts():
    ckm = load_ckm_matrix_artifact(ROOT)
    pmns = load_pmns_matrix_artifact(ROOT)
    cp = load_cp_phase_artifact(ROOT)
    assert len(ckm.value) == len(pmns.value) == 3
    assert ckm.source_status == pmns.source_status == cp.source_status == "DISCOVERED"
    assert cp.value["delta_BH_formula"] == "pi/3"
    for value in (ckm, pmns, cp):
        assert value.provenance.empirical_derivation_input is False
        assert value.provenance.reference_comparison_input is False


def test_missing_matrix_artifact_returns_structured_status(tmp_path):
    result = load_ckm_matrix_artifact(tmp_path)
    assert result.value is None
    assert result.source_status == "ARTIFACT_NOT_FOUND"
