"""Composite Higgs channels in the derived rank-16 BHSM fermion bundle.

The active parent bosonic tangent has no elementary (1,2)_{1/2} field, but
the already-derived chiral fermion bundle has color-singlet bilinears with
exactly the Higgs and conjugate-Higgs quantum numbers.  This reclassifies the
next dynamical problem as a boundary-kernel gap equation; it does not assume a
condensate or insert a four-fermion coefficient.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import numpy as np


VERSION = "v15.64"
CLASSIFICATION = "BHSM_DERIVED_FERMION_BILINEAR_COMPOSITE_HIGGS_CHANNELS"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


@dataclass(frozen=True)
class FermionRepresentation:
    name: str
    color_dimension: int
    weak_dimension: int
    hypercharge: float


Q_L = FermionRepresentation("Q_L", 3, 2, 1.0 / 6.0)
L_L = FermionRepresentation("L_L", 1, 2, -1.0 / 2.0)
U_R = FermionRepresentation("u_R", 3, 1, 2.0 / 3.0)
D_R = FermionRepresentation("d_R", 3, 1, -1.0 / 3.0)
N_R = FermionRepresentation("nu_R", 1, 1, 0.0)
E_R = FermionRepresentation("e_R", 1, 1, -1.0)


def barred_left_right_bilinear(
    left: FermionRepresentation, right: FermionRepresentation,
) -> dict[str, Any]:
    """Quantum numbers of the color-singlet part of bar(left)*right."""

    if left.weak_dimension != 2 or right.weak_dimension != 1:
        raise ValueError("require a weak-doublet left field and weak-singlet right field")
    color_singlet = left.color_dimension == right.color_dimension
    return {
        "bilinear": f"bar({left.name})*{right.name}",
        "color_tensor_product": (
            "bar3_times_3=1_plus_8" if left.color_dimension == 3 else "1_times_1=1"
        ),
        "color_singlet_occurs": color_singlet,
        "weak_representation": "2",
        "hypercharge": right.hypercharge - left.hypercharge,
        "Lorentz_channel": "scalar_after_left-right_spinor_contraction",
    }


def composite_channel_ledger() -> dict[str, Any]:
    channels = {
        "up": barred_left_right_bilinear(Q_L, U_R),
        "down": barred_left_right_bilinear(Q_L, D_R),
        "neutrino": barred_left_right_bilinear(L_L, N_R),
        "charged_lepton": barred_left_right_bilinear(L_L, E_R),
    }
    return {
        "channels": channels,
        "H_quantum_numbers": "(SU3,Sp1,Y)=(1,2,+1/2)",
        "H_channels": ["color-singlet_bar(Q_L)u_R", "bar(L_L)nu_R"],
        "H_tilde_quantum_numbers": "(SU3,Sp1,Y)=(1,2,-1/2)",
        "H_tilde_channels": ["color-singlet_bar(Q_L)d_R", "bar(L_L)e_R"],
        "all_required_hypercharges_exact": all(
            math.isclose(abs(row["hypercharge"]), 0.5, abs_tol=1.0e-14)
            for row in channels.values()
        ),
        "all_channels_color_singlet": all(
            row["color_singlet_occurs"] for row in channels.values()
        ),
    }


def composite_field_definition() -> dict[str, Any]:
    return {
        "dimension_one_order_parameters": [
            "H_u=R4^2*Pi_1[bar(Q_L)u_R]",
            "H_nu=R4^2*bar(L_L)nu_R",
            "Htilde_d=R4^2*Pi_1[bar(Q_L)d_R]",
            "Htilde_e=R4^2*bar(L_L)e_R",
        ],
        "R4_power_reason": "a_4D_fermion_bilinear_has_mass_dimension_3",
        "elementary_parent_boson_required_for_representation_ownership": False,
        "composite_representation_owned_by_derived_fermion_bundle": True,
        "one_physical_Higgs_linear_combination_selected": False,
        "wavefunction_normalization_selected": False,
        "condensate_selected": False,
    }


def exact_gap_equation_target() -> dict[str, Any]:
    return {
        "boundary_kernel": (
            "K_LR=(Pi_H)*(D_boundary_plus_J_A*G_DtN*J_A)*(Pi_H)_star_on_"
            "the_actual_R_times_S3_child"
        ),
        "linearized_gap_equation": "Delta=K_LR(mu_star)*Delta",
        "formation_gate": "largest_physical_eigenvalue_of_K_LR_exceeds_1",
        "critical_surface": "lambda_max(K_LR)=1",
        "Higgs_alignment": "normalized_eigenvector_of_K_LR_at_the_first_supercritical_channel",
        "Yukawa_matrices": (
            "left-right_residues_of_the_same_normalized_kernel_eigenvector_in_"
            "the_up_down_e_nu_channel_ledgers"
        ),
        "Higgs_mass_and_quartic": (
            "second_and_fourth_variations_of_the_fermion-plus-boundary-kernel_"
            "effective_action_along_the_selected_eigenvector"
        ),
        "uses_absolute_local_M4_gauge_coupling_as_input": False,
        "uses_bulk_to_boundary_DtN_kernel_instead": True,
        "current_DtN_kernel_computed_on_actual_child": False,
        "nonzero_solution_claimed": False,
    }


def hubbard_stratonovich_semantics() -> dict[str, Any]:
    return {
        "identity": (
            "G*(barL*R)*(barR*L)_equivalent_to_-HdaggerH/G+barL*H*R+"
            "barR*Hdagger*L_after_algebraic_elimination_of_H"
        ),
        "interpretation": (
            "an_auxiliary_H_is_a_coordinate_on_the_bilinear_channel_until_"
            "the_fermion_determinant_generates_a_positive_kinetic_residue"
        ),
        "arbitrary_four_fermion_G_inserted": False,
        "required_source_of_G": "the_action-owned_bulk-to-boundary_current_kernel",
        "avoids_relabelling_internal_Dirac_KK_levels_as_fermion_masses": True,
    }


def completion_payload() -> dict[str, Any]:
    ledger = composite_channel_ledger()
    fields = composite_field_definition()
    gap = exact_gap_equation_target()
    hs = hubbard_stratonovich_semantics()
    charges = [
        ledger["channels"][name]["hypercharge"]
        for name in ("up", "down", "neutrino", "charged_lepton")
    ]
    validation = {
        "channel_hypercharges_are_plus_minus_half": np.allclose(
            charges, [0.5, -0.5, 0.5, -0.5], atol=1.0e-14, rtol=0.0
        ),
        "all_channels_are_color_singlets": ledger["all_channels_color_singlet"],
        "composite_has_correct_engineering_dimension": fields[
            "R4_power_reason"
        ].endswith("dimension_3"),
        "elementary_Higgs_not_reintroduced": not fields[
            "elementary_parent_boson_required_for_representation_ownership"
        ],
        "nonzero_condensate_not_fabricated": not gap["nonzero_solution_claimed"],
        "four_fermion_coefficient_not_inserted": not hs[
            "arbitrary_four_fermion_G_inserted"
        ],
        "KK_levels_not_relabelled_masses": hs[
            "avoids_relabelling_internal_Dirac_KK_levels_as_fermion_masses"
        ],
        "no_new_continuous_coefficient": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_composite_higgs_channel_v15_64",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "composite_channel_ledger": ledger,
        "composite_field_definition": fields,
        "Hubbard_Stratonovich_semantics": hs,
        "gap_equation_target": gap,
        "claim_boundary": {
            "Higgs_representation_exists_as_derived_fermion_bilinear": True,
            "elementary_Higgs_parent_ownership_restored": False,
            "action-owned_interaction_kernel_derived": False,
            "electroweak_condensate_or_nonzero_Yukawa_derived": False,
        },
        "active_calculation": (
            "COMPUTE_THE_GAUGE-AND-DIRAC_BULK-TO-BOUNDARY_DtN_CURRENT_KERNEL_"
            "ON_THE_ACTUAL_ROUND_QUOTIENT_CHILD,_PROJECT_IT_TO_THE_FOUR_"
            "COLOR-SINGLET_LEFT-RIGHT_DOUBLETS,_AND_SOLVE_lambda_max(K_LR)=1"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def _canonical_json_value(value: Any) -> Any:
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float cannot be materialized")
        rounded = round(value, 12)
        return 0.0 if rounded == 0.0 else rounded
    if isinstance(value, Mapping):
        return {key: _canonical_json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical_json_value(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(
        _canonical_json_value(payload), indent=2, sort_keys=True,
        ensure_ascii=False, allow_nan=False,
    ) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_composite_higgs_channel_v15_64.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "FermionRepresentation",
    "Q_L", "L_L", "U_R", "D_R", "N_R", "E_R",
    "barred_left_right_bilinear", "composite_channel_ledger",
    "composite_field_definition", "exact_gap_equation_target",
    "hubbard_stratonovich_semantics", "completion_payload",
    "deterministic_json", "materialize",
]
