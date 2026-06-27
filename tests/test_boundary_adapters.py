from pathlib import Path

from bhsm.interface.boundary_adapters import load_boundary_constants_artifact, load_charged_bridge_constants_artifact, load_neutral_operator_artifact

ROOT = Path(__file__).resolve().parents[1]


def test_boundary_adapters_load_no_fit_package_without_theorem_promotion():
    constants = load_boundary_constants_artifact(ROOT)
    charged = load_charged_bridge_constants_artifact(ROOT)
    neutral = load_neutral_operator_artifact(ROOT)
    assert constants.value["Z_H"] == 1
    assert "sigma" in constants.value and "tau" in constants.value
    assert charged.value
    assert neutral.value["H_nu"] == [[1, 1], [1, 2]]
    assert "PHYSICAL_BASIS_SCALE_OPEN" in neutral.provenance.claim_status
    assert all(item.provenance.empirical_derivation_input is False for item in (constants, charged, neutral))


def test_missing_boundary_package_is_not_inferred(tmp_path):
    assert load_boundary_constants_artifact(tmp_path).source_status == "ARTIFACT_NOT_FOUND"
