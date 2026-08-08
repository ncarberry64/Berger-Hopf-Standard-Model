"""Fail-closed recovery audit for the manual BHSM v14.31--v14.83 campaign.

The downloaded packages contain useful exact calculations, conditional
operator constructions, and no-go results.  This module records their
provenance and independently checks the most consequential scalar identities.
It deliberately does not promote provisional bridges to action-derived
physics or declare BHSM complete.
"""

from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json
from math import atanh, sqrt, tanh
from pathlib import Path
from typing import Any


PRIMARY_VERDICT = (
    "BHSM_V14_31_TO_V14_83_MANUAL_CAMPAIGN_INTEGRATED_WITH_EXACT_RESULTS_"
    "CONDITIONAL_THEOREMS_AND_NO_GOS_PRESERVED_BUT_FULL_PHYSICAL_CLOSURE_"
    "REMAINS_BLOCKED_BY_THE_MISSING_ACTION_SELECTED_GLOBAL_DEGREE_ONE_"
    "FULL_PREIMAGE_BACKGROUND_AND_COMPLETE_STRATIFIED_OPERATOR_DOMAIN"
)

EXACT_NEXT_OBJECT = (
    "ACTION_OWNED_FULL_PREIMAGE_TWO_STRATUM_KINETIC_REDUCTION_WITH_DERIVED_"
    "LAYER_INERTIAS_SHEAR_COVARIANCE_AND_DEGREE_ONE_SELF_ADJOINT_BACKGROUND"
)

CHARGED_CURRENT_PROVENANCE_GATE = (
    "PARENT_ACTION_DERIVATION_OR_UNIQUENESS_SELECTION_OF_THE_SPECTRAL_"
    "CHARGED_CURRENT_KERNEL"
)

NONCENTRAL_CURRENT_GATE = "ACTION_OWNED_FAMILY_NONCENTRAL_LEFT_HANDED_CURRENT_SOURCE"

CANONICAL_BUNDLE_COUNT = 49
CANONICAL_BUNDLE_AGGREGATE_SHA256 = (
    "6d9b56b6efdc54c67ee3f5adc0bcd42d5f41d201ec34049990aa2785f6adca2e"
)

BUNDLE_SHA256 = {
    "BHSM_v14_31_to_v14_33_cumulative_patch_bundle.zip": "5291b8c5b21fe7504f875219abfbf93320f64059074a91eedaa8baa44759fc41",
    "BHSM_v14_34_Hopf_phase_flavor_patch_bundle.zip": "a7eb9a21cfc3eb7b28d8e151f02fbb459b5d2f013059a2231e73cffcecbf7ad0",
    "BHSM_v14_35_Hopf_phase_bifurcation_patch_bundle.zip": "8e52bacb5ea42834ca6bc4f2fe37ee95b3da9f922d7fafe9a9d02781057a9b2b",
    "BHSM_v14_36_degree_one_phase_hessian_patch_bundle.zip": "52e951147c1ddde568c755fb75e2474f0c0b7b85e071cb4550c7bb4e1818e070",
    "BHSM_v14_37_relative_holonomy_full_shape_hessian_patch_bundle.zip": "cfeae62f321195a1ec9399a4f1c9c3ea8ed4a741a5bf2d2281146f1b6418914b",
    "BHSM_v14_38_Lambda85_eta_mixed_hessian_patch_bundle.zip": "56637006293918de01e16e6992b44b694a45f09d0bfaed3b5816c15714592920",
    "BHSM_v14_39_static_eta_metric_spin4_source_patch_bundle.zip": "ebd06b89a42b049ded39905d9d61a55a6301d7a38310b4483cecd665ee55213d",
    "BHSM_v14_40_matter_sourced_spin4_multipole_patch_bundle.zip": "b7dd0735f0d9b0ad01a56ae020aba843b8b64ccbb41fd44869af0b0793096218",
    "BHSM_v14_41_source_free_relative_frame_patch_bundle.zip": "5ba2efc3b01d0ec6bd3e4592fa7e50ae9891073a0e559232af6f2045d7e7a25c",
    "BHSM_v14_42_collective_dirac_vacuum_polarization_patch_bundle.zip": "68171a06eba2e8c3ba9e5896a1b3667e09f73a99261c39036fa1e73b4e590077",
    "BHSM_v14_43_moduli_clifford_matcher_zeta_patch_bundle.zip": "d215870428c25d06d61c9622a59b6e59b2538ddc540af382b5290460a081e3a0",
    "BHSM_v14_44_worldline_clifford_spin_lift_patch_bundle.zip": "cb1b69788a37c684aa13e7eef04e821cc5fb72b153d85fb21ea1e1115379c72b",
    "BHSM_v14_45_foundational_dirac_spin_glue_patch_bundle.zip": "52bd7d9b22af3111a02c091cb7b2c9f92e70d270d56e1fbfcf629505ac205d2a",
    "BHSM_v14_46_cap_regularization_fiber_automorphism_patch_bundle.zip": "9e6439f7549b2e2c580ac3056ddaf3704354f48d9d18502f50a3f44088e8f845",
    "BHSM_v14_47_covariant_cap_projection_patch_bundle.zip": "77f17eeeb99687cb4a75cacbdb1e7136b668d2a46fb56467ae3974ab7f2572a9",
    "BHSM_v14_48_completion_minimum_input_patch_bundle.zip": "054d7de7128e1f170d49500977b9cfd097f03e2f4377c50c035f1681a7922985",
    "BHSM_v14_49_zeta_spectral_ray_patch_bundle.zip": "5150c69b7fe371141ed259753aa33c8b210704e333b2573156ec3bd7cda22790",
    "BHSM_v14_50_full_dirac_a4_trace_patch_bundle.zip": "a51fff82a91d5275e46dc40163deb9193eba2f07cb213f2e6f6cd8d516eea9db",
    "BHSM_v14_51_geometry_first_nonlocal_patch_bundle.zip": "d6db49c98edcbef9d714b3d2783186898a88358bf195f491acebf7892f0fa9c8",
    "BHSM_v14_52_stratified_scale_flavor_convergence_patch_bundle.zip": "41b7c1522bbc19be7b971419a0e616609d9093e72d2f099b9cb3feb81b946358",
    "BHSM_v14_53_relative_anomaly_tensor_current_patch_bundle.zip": "81b499857cfd61796a0c5fa06a346045aa6f32092345f7afaabf8991574f15d0",
    "BHSM_v14_54_cosmological_parent_dynamic_envelopment_patch_bundle.zip": "412a720ed5fb797f1af85f6c4e0d2a0547a7f32bca713140f32a51e03842dac7",
    "BHSM_v14_55_pair_wake_neutrino_bvp_patch_bundle.zip": "1564156ad96569a114d5ab0b99859ee5f4b721974076bfff9a44a9f8647bc0a2",
    "BHSM_v14_56_pair_wake_hybrid_action_patch_bundle.zip": "b44c8b26d80022fa69ea5b098611629d5c998734741e8ab6f921436bcbb78313",
    "BHSM_v14_57_dtn_heat_kernel_neutrino_kill_screen_patch_bundle.zip": "8e8afe0c2c49e656004c5cabe2c1e7b525ca732c6fb98ead458fcd56d7765f22",
    "BHSM_v14_58_round_collar_spectral_baseline_patch_bundle.zip": "c27faf6c502971844c8a2f4c40d6e5ea51130b9be96654f4e416f51d536f3fa0",
    "BHSM_v14_59_exact_berger_dirac_cap_obstruction_patch_bundle.zip": "0ed571a0f1604507d7c8767c9cc16576d6716d2b8f1f2f59c45a07331dff724f",
    "BHSM_v14_60_global_envelopment_cap_selection_patch_bundle.zip": "e5aecbecd8a4c57e349497283f3a800c132d79ee47034345f2393c576f051ef8",
    "BHSM_v14_61_full_global_envelopment_hessian_gate_patch_bundle.zip": "f7144e858ce22e7f0f4fe348a102a47772737fc950f512266f50a3369570ba7b",
    "BHSM_v14_62_coefficient_provenance_quotient_patch_bundle.zip": "03f63431bcbba8299e24c3d7aa27c20899acd11c3a470ec044638ec83312b0b6",
    "BHSM_v14_63_stratified_dirac_zeta_micro_source_exhaustion_patch_bundle.zip": "f3fb4956d44d57eb3f65964c7d3d95638e1fcde0105c734f6ed250c246f0f456",
    "BHSM_v14_64_envelopment_spectral_correspondence_patch_bundle.zip": "ec4e79a638fc87863d04cdf69a70f97d991ab8afbeb34edaee826bc8132b8c44",
    "BHSM_v14_65_boundary_triple_heat_semigroup_patch_bundle.zip": "fa633d9fa1dd37dd3cc2b42801e6a51b01123c46ad653e16d5de04fa83051d73",
    "BHSM_v14_66_operator_valued_calderon_wentzell_patch_bundle.zip": "dcafbb35ee19a61173db5c2fbbc8c2449e67b92c3f575468d03852ef16fd9231",
    "BHSM_v14_67_action_attachment_wentzell_patch_bundle.zip": "b92ff9098bcb7262688a3abd1193bce6c17c9fd08e7d556d69f14bca271be1f1",
    "BHSM_v14_68_global_attachment_incidence_curvature_patch_bundle.zip": "020f191fffa64fd1c6f707789f9164f6ee848a9777c0e52b09b6b93b8ac7e742",
    "BHSM_v14_69_tensor_differential_incidence_patch_bundle.zip": "874075ffbe1c7c52b40312eeeb460e31736cf5b4a91a51ef5d90720a7b3721ad",
    "BHSM_v14_70_second_shape_jacobi_triplet_patch_bundle.zip": "0e052e7b8b7771644c01412e0dbed51347c9c9b4019d91259c9043127e7de9cf",
    "BHSM_v14_71_round_hessian_centrality_no_go_patch_bundle.zip": "0c7d8513eecfa06ac6299d47d3436d8c8cfe7aff3f35f1a9ae1b92de4f3bd3c9",
    "BHSM_v14_72_berger_rank3_polarization_gate_patch_bundle.zip": "067e866c8b815da1c1932c20163616a732ac4ac1a363549c2f54e42830fdb7a3",
    "BHSM_v14_73_hopf_u1_obstruction_diagonal_locking_patch_bundle.zip": "ed2642d243a3436bd6cdf18262cbdf15bf4850de7846f4feee4a6f451925443d",
    "BHSM_v14_74_l2_landau_goldstone_triplet_patch_bundle.zip": "5a0c0d65ccfdfb10effa21d40ed5989041423f77a01bf3ffc2c5ccd4dcb53f4b",
    "BHSM_v14_75_landau_coefficient_provenance_patch_bundle.zip": "b5ced1e65cd2b9a90554c1df54c105dcddc6f8eedb3b30de65379b451405f637",
    "BHSM_v14_76_landau_source_exhaustion_response_sign_patch_bundle.zip": "caa1c6e20e6b06c8ca1761b7b2a1b859da7aeb27f16566934c87153254429cea",
    "BHSM_v14_77_bulk_cancellation_dtn_shape_d4_patch_bundle.zip": "388da38ed2dd3f1cdc9314a7748718207afb925f3a23575b44a7bd23e6f8323e",
    "BHSM_v14_79_alpha_dynamic_band_p8_bridge_patch_bundle.zip": "125fdb152a5c280dd76fe065c91c4fb0898c3c69af763205d9b78ba1851cfa04",
    "BHSM_v14_81_driven_hypersphere_black_hole_flux_gate_patch_bundle.zip": "4d519241d6d02c1f3e70632898832354679b3175f8a0167ecd8b1b44e254d564",
    "BHSM_v14_82_master_action_bh_susceptibility_patch_bundle.zip": "83e0a2ff1a74459a1196da7f258a9255c39807755b82276f2dafc1ac9f9daf2b",
    "BHSM_v14_83_volume_work_core_softening_gate_patch_bundle.zip": "0aed3073bf5be3b3220b6158a95d00b1413deb85a2219ad99d37483f7b805e2b",
}


def bundle_aggregate_sha256() -> str:
    ledger = "\n".join(f"{name}:{digest}" for name, digest in BUNDLE_SHA256.items())
    return sha256(ledger.encode("utf-8")).hexdigest()


def area_landau_coefficients() -> dict[str, Fraction]:
    """Recompute the exact v14.75 round-area Landau coefficients."""

    i2_sq = Fraction(7, 8) * Fraction(2, 5) - Fraction(1, 4) * Fraction(16, 15) - Fraction(1, 8) * Fraction(176, 15)
    i4 = -Fraction(7, 8) * Fraction(1, 5) + Fraction(1, 4) * Fraction(8, 15) + Fraction(1, 8) * Fraction(16, 5)
    return {
        "r": Fraction(5, 3),
        "u": 4 * i2_sq,
        "v": 4 * i4,
        "three_u_plus_v": 12 * i2_sq + 4 * i4,
    }


def dtn_shape_quartic(q: float, length: float) -> dict[str, float | str]:
    """Return the exact uniform two-sided DtN fourth-order coefficient."""

    if q <= 0 or length <= 0:
        raise ValueError("q and length must be positive")
    x = q * length
    t = tanh(x)
    a4 = (2.0 / 3.0) * q**5 * t * (1.0 - t * t) * (2.0 - 3.0 * t * t)
    threshold = atanh(sqrt(2.0 / 3.0))
    sign = "POSITIVE" if a4 > 0 else "NEGATIVE" if a4 < 0 else "ZERO"
    return {"qL": x, "a4": a4, "threshold_qL": threshold, "sign": sign}


def radial_core_softening_identity(zeta: float, b0_prime: float, radius: float, inertia: float) -> dict[str, float | bool]:
    """Evaluate the v14.83 fixed-parameter radial susceptibility identity."""

    if not 0 <= zeta <= 1:
        raise ValueError("zeta must be a kinetic fraction in [0,1]")
    if radius <= 0 or inertia <= 0:
        raise ValueError("radius and inertia must be positive")
    chi_h = 2.0 * (3.0 * zeta - 1.0) * b0_prime / (radius * inertia)
    return {
        "zeta": zeta,
        "chi_h": chi_h,
        "softens": chi_h > 0,
        "threshold": 1.0 / 3.0,
    }


def completion_payload() -> dict[str, Any]:
    area = area_landau_coefficients()
    validation = {
        "canonical_bundle_count": len(BUNDLE_SHA256) == CANONICAL_BUNDLE_COUNT,
        "canonical_bundle_aggregate": bundle_aggregate_sha256() == CANONICAL_BUNDLE_AGGREGATE_SHA256,
        "area_landau_exact": area == {
            "r": Fraction(5, 3),
            "u": Fraction(-83, 15),
            "v": Fraction(43, 30),
            "three_u_plus_v": Fraction(-91, 6),
        },
        "dtn_sign_change": dtn_shape_quartic(1.0, 0.5)["sign"] == "POSITIVE" and dtn_shape_quartic(1.0, 2.0)["sign"] == "NEGATIVE",
        "core_softening_threshold": not radial_core_softening_identity(0.2, 1.0, 2.0, 3.0)["softens"] and radial_core_softening_identity(0.5, 1.0, 2.0, 3.0)["softens"],
    }
    return {
        "artifact": "BHSM_manual_campaign_recovery_v14_83",
        "version": "v14.83-recovery",
        "primary_verdict": PRIMARY_VERDICT,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "bundle_provenance": {
            "canonical_bundle_count": CANONICAL_BUNDLE_COUNT,
            "aggregate_sha256": CANONICAL_BUNDLE_AGGREGATE_SHA256,
            "bundle_sha256": BUNDLE_SHA256,
            "steering_only_version_jumps": ["v14.78", "v14.80"],
            "duplicate_v14_48": "BYTE_IDENTICAL_EXCLUDED",
            "standalone_v14_31": "SUPERSEDED_BY_HASH_VALID_CUMULATIVE_V14_31_TO_V14_33",
            "final_shear_handoff_sha256": "aa8b8cfc3c07b8538c72b759485e1da91f0599ffbfc233b18c050cb4b7815c9f",
        },
        "validated": [
            "Path B and the eta-bound Dirac layer are explicit foundational effective postulates, not derivations from the pre-v14.31 action",
            "the physical M4 S6 field alone has no degree-one or FR sector because pi3(S6)=pi4(S6)=0",
            "round full-symmetry Hessians cannot select a physical ell=2 triplet",
            "the c2=1 quaternionic Hopf bundle has no global U1 reduction",
            "the reflection-even ell=2 Landau phase has exactly three Goldstone directions when r<0, v>0, and 3u+v>0",
            "the round-area coefficients are r=5/3, u=-83/15, v=43/30 and fail the locking cone",
            "the uniform two-sided DtN shape quartic changes sign at atanh(sqrt(2/3))",
            "the radial core softens under outward work if and only if zeta>1/3",
            "differential shear gives a negative-semidefinite reduced stiffness contribution and positive isotropic ell=2 susceptibility",
        ],
        "conditional_or_provisional": [
            "full-preimage Hopf-smash current transgression",
            "operator-valued Calderon/Wentzell realization before physical tangential operators and projectors",
            "constant-modulus p8 bridge",
            "dynamic band and family-count architecture",
            "black-hole/environment origin and magnitude of the layer shear",
            "seven-volume work source B0(R)=R^7",
        ],
        "not_promoted": [
            "nontrivial CKM or PMNS",
            "physical family count",
            "physical Landau r,u,v",
            "physical black-hole drive D_BH or susceptibility",
            "neutrino mass or oscillation output",
            "zero-input coefficient unification",
            "BHSM full completion or Mark III",
        ],
        "open_gates": {
            "global_background_and_domain": EXACT_NEXT_OBJECT,
            "charged_current_kernel": CHARGED_CURRENT_PROVENANCE_GATE,
            "noncentral_left_handed_current": NONCENTRAL_CURRENT_GATE,
            "coefficient_provenance": "FINITE_INPUT_STRATIFIED_EFT_FREEZE_OR_ACTION_DERIVED_MICROSCOPIC_RELATION",
            "landau_response": "FULL_D2_D3_D4_EFFECTIVE_ACTION_ON_ONE_GLOBAL_STATIONARY_BACKGROUND",
            "differential_shear": EXACT_NEXT_OBJECT,
            "black_hole_driver": "ACTION_DERIVATION_OF_THE_PHYSICAL_LAYER_VELOCITIES_AND_SHEAR_COVARIANCE",
        },
        "completion_status": {
            "Mark_I": "REACHED",
            "Mark_II": "REACHED_CONDITIONALLY_WITH_DECLARED_FOUNDATIONAL_EFFECTIVE_DATA",
            "Mark_III": "NOT_REACHED",
            "Mark_IV": "NOT_REACHED",
            "BHSM_complete": False,
            "physical_execution_blocked": True,
            "USB_synchronization_eligible": False,
        },
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def status_text() -> str:
    payload = completion_payload()
    status = payload["completion_status"]
    return (
        "# BHSM v14.83 manual campaign recovery\n\n"
        f"Verdict: `{payload['primary_verdict']}`\n\n"
        f"BHSM complete: `{str(status['BHSM_complete']).lower()}`\n\n"
        f"Physical execution blocked: `{str(status['physical_execution_blocked']).lower()}`\n\n"
        "## Exact next object\n\n"
        f"`{payload['exact_next_object']}`\n"
    )


def materialize(repository: Path | None = None) -> Path:
    root = Path(__file__).resolve().parents[4] if repository is None else Path(repository)
    output = root / "artifacts" / "BHSM_manual_campaign_recovery_v14_83.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(deterministic_json(completion_payload()), encoding="utf-8", newline="\n")
    return output
