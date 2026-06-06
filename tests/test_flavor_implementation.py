from math import isclose, sqrt

from bhsm_model import build_bhsm_model, compute_ckm_from_internal_rules, compute_pmns_from_internal_rules, compute_yukawa_ratios
from claims import ClaimStatus, build_claims_ledger
from constants import ALPHA_INV_LOW_ENERGY
from ckm import ckm_angles_from_bhsm_ratios
from pmns import pmns_effective_angles
from prediction_ledger import CKM_REFERENCES, build_prediction_ledger
from residual_audit import build_residual_audit


def test_ckm_predictions_are_nonzero_and_finite():
    ckm = compute_ckm_from_internal_rules(build_bhsm_model())

    for value in ckm["angles"].values():
        assert value > 0
        assert value < 1


def test_ckm_angles_are_generated_from_bhsm_ratios_not_empirical_values():
    model = build_bhsm_model()
    ratios = compute_yukawa_ratios(model)
    angles = ckm_angles_from_bhsm_ratios(ratios)

    assert isclose(angles["sin_theta_12"], sqrt(ratios["down_quarks"]["light"] / ratios["down_quarks"]["middle"]))
    assert isclose(angles["sin_theta_23"], 2.0 * ratios["down_quarks"]["middle"])
    assert isclose(angles["sin_theta_13"], sqrt(ratios["up_quarks"]["light"]))
    assert not isclose(angles["sin_theta_12"], CKM_REFERENCES["sin_theta_12"])


def test_pmns_effective_rows_use_alpha_not_empirical_fit_values():
    alpha = 1.0 / ALPHA_INV_LOW_ENERGY
    angles = pmns_effective_angles(alpha)
    pmns = compute_pmns_from_internal_rules(build_bhsm_model())

    assert pmns["status"] == "EFFECTIVE_EXTENSION_SCREEN"
    assert pmns["angles"] == angles
    assert isclose(angles["sin2_theta_13"], 3.0 * alpha)
    assert isclose(angles["sin2_theta_12"], (1.0 / 3.0) - 3.0 * alpha)
    assert isclose(angles["sin2_theta_23"], 0.5 + 6.0 * alpha)
    assert isclose(angles["delta_m2_21_over_delta_m2_31"], 4.0 * alpha)


def test_quark_prediction_rows_are_marked_scheme_sensitive():
    ledger = build_prediction_ledger(build_bhsm_model())
    quark_rows = [
        row for row in ledger
        if row.sector == "fermion_mass_ratios"
        and ("up_quarks" in row.id or "down_quarks" in row.id)
        and not row.id.endswith(".heavy")
    ]

    assert quark_rows
    assert all(row.metadata["scheme_sensitive"] is True for row in quark_rows)
    assert all(row.metadata["scheme_consistent"] is False for row in quark_rows)
    assert all("mixed" in row.metadata["mass_scheme"].lower() for row in quark_rows)


def test_prediction_and_residual_ledgers_rebuild_with_flavor_screens():
    ledger = build_prediction_ledger(build_bhsm_model())
    audit = build_residual_audit(ledger)

    assert any(row.id == "ckm.sin_theta_12" and row.predicted > 0 for row in ledger)
    assert any(row.id == "ckm.delta_cp" and row.predicted > 0 for row in ledger)
    assert not any(row.id == "ckm.delta_cp" and row.status == "PLACEHOLDER" for row in ledger)
    assert any(row.id == "pmns_effective.sin2_theta_13" and row.predicted > 0 for row in ledger)
    assert len(audit) == len(ledger)


def test_no_tuning_parameters_changed_by_flavor_screens():
    ratios_before = compute_yukawa_ratios(build_bhsm_model())

    compute_ckm_from_internal_rules(build_bhsm_model())
    compute_pmns_from_internal_rules(build_bhsm_model())

    ratios_after = compute_yukawa_ratios(build_bhsm_model())
    assert ratios_after == ratios_before


def test_no_claim_is_upgraded_to_final_prediction_or_proof():
    claims = {claim.id: claim for claim in build_claims_ledger()}

    assert claims["ht_proxy_spectral_gap"].status == ClaimStatus.PROXY_AUDIT
    assert claims["yukawa_overlap_structure"].status == ClaimStatus.STRONG_SCREEN
    assert claims["forbidden_numerical_predictions"].status == ClaimStatus.FORBIDDEN
