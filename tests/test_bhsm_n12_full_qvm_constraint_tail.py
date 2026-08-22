import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT / "artifacts" / "n12_direct_checkpoint"
    / "BHSM_N12_FULL_QVM_CONSTRAINT_TAIL_DIAGNOSTIC.json"
)


def _payload():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_full_qvm_tail_audit_preserves_claim_boundary():
    payload = _payload()
    assert payload["validation_passed"] is True
    assert payload["CONTINUUM_EVENT_CHILD_CERTIFIED"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert payload["validation"][
        "zero_padded_probes_not_promoted_as_complete_children"
    ] is True
    assert payload["validation"][
        "physical_equations_and_gates_unchanged"
    ] is True


def test_exact_source_is_cauchy_and_s2_bounded_on_sampled_cuts():
    payload = _payload()
    for name in ("event", "child"):
        rows = payload["exact_source_correction_cauchy_diagnostic"][name]
        assert [row["target_N"] for row in rows] == [20, 24, 32, 40, 48]
        assert max(row["source_N_squared_distance"] for row in rows) < 1.5
        assert max(row["target_correction_S2_norm"] for row in rows) < 0.65
        assert payload["exact_source_summary"][name][
            "N48_exact_source_soft_required_correction_amplitude"
        ] < 1.1e-3


def test_naive_worst_inverse_summability_is_not_promoted():
    payload = _payload()
    for name in ("event", "child"):
        fit = payload["finite_power_fits"][name][
            "full_qvm_all_mode_normal_map"
        ]
        assert fit["measured_inverse_growth_exponent"] > 1.0
        assert fit[
            "summable_with_n_minus_2_tail_if_exponent_below_one"
        ] is False
        assert fit["finite_probe_fit_is_not_an_asymptotic_proof"] is True
