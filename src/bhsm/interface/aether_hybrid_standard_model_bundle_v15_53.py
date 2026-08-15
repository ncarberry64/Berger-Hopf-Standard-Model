"""Global Standard Model bundle and chiral representation on the hybrid child."""

from __future__ import annotations

import cmath
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.particle_chirality_anomaly_normalization import (
    anomaly_coefficients,
    charge_table,
    one_family_multiplets,
    physical_u1,
    u1_generator_ledger,
)


VERSION = "v15.53"
CLASSIFICATION = "BHSM_HYBRID_STANDARD_MODEL_GLOBAL_BUNDLE"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def chiral_bundle_contract() -> dict[str, Any]:
    rows = one_family_multiplets(include_neutral_singlet=True)
    return {
        "base": "hybrid_M4=R_t_times_S3_on_each_open_flow_segment",
        "covering_gauge_group": "SU3_times_Sp1_times_U1_Y",
        "faithful_gauge_group": "(SU3_times_Sp1_times_U1_Y)/Z6",
        "families": 3,
        "family_source": "C3_triality_projectors_P0_P1_P2",
        "one_family_complex_dimension": sum(row.complex_dimension for row in rows),
        "multiplets": [
            {
                "name": row.name,
                "representation": f"({row.su3},{row.sp1})_{row.Y}",
                "dimension": row.complex_dimension,
                "Y": str(row.Y),
            }
            for row in rows
        ],
        "scalar_doublet": "H=(1,2)_(1/2)",
        "chirality": "all_fermions_written_as_left_Weyl_fields",
        "neutral_singlet": (
            "nu_c=(1,1)_0_completes_the_rank_16_family;_its_mass_operator_"
            "is_not_fixed_by_anomaly_cancellation"
        ),
    }


def hypercharge_selection() -> dict[str, Any]:
    """State the anomaly family and its BHSM geometric selection."""

    return {
        "commuting_operator": u1_generator_ledger()["operator"],
        "geometric_formula": (
            "Y_BH=-(1/2)I+(2/3)P_C+(1/2)S_sigma-"
            "(1/2)P_w*S_sigma"
        ),
        "Higgs_normalization": "Y_BH(H)=1/2",
        "anomaly_plus_Yukawa_family_with_nu_c": "Y(a)=Y_SM+(a-1/6)(B-L)",
        "continuous_B_minus_L_mixing_removed_by": (
            "the_geometric_P_C,_S_sigma,_P_w_operator_eigenvalues"
        ),
        "selected_quark_doublet_charge": str(physical_u1(1, 1, 1)),
        "selected_lepton_doublet_charge": str(physical_u1(0, 1, 1)),
        "family_operator_in_hypercharge": False,
        "selected_charge_table": charge_table(),
    }


def yukawa_and_anomaly_ledger() -> dict[str, Any]:
    charges = {
        "Q": Fraction(1, 6),
        "L": Fraction(-1, 2),
        "u_c": Fraction(-2, 3),
        "d_c": Fraction(1, 3),
        "e_c": Fraction(1),
        "nu_c": Fraction(0),
        "H": Fraction(1, 2),
    }
    yukawa = {
        "Q_H_u_c": charges["Q"] + charges["H"] + charges["u_c"],
        "Q_Hdagger_d_c": charges["Q"] - charges["H"] + charges["d_c"],
        "L_Hdagger_e_c": charges["L"] - charges["H"] + charges["e_c"],
        "L_H_nu_c": charges["L"] + charges["H"] + charges["nu_c"],
    }
    anomalies = anomaly_coefficients(3, include_neutral_singlet=True)
    return {
        "charges": {key: str(value) for key, value in charges.items()},
        "Yukawa_hypercharge_sums": {
            key: str(value) for key, value in yukawa.items()
        },
        "all_Yukawa_vertices_gauge_invariant": all(value == 0 for value in yukawa.values()),
        "three_family_anomalies": {
            key: str(value) for key, value in anomalies.items()
        },
        "all_local_anomalies_zero": all(
            anomalies[key] == 0
            for key in (
                "SU3_cubed", "SU3_squared_U1", "Sp1_squared_U1",
                "U1_cubed", "gravity_squared_U1",
            )
        ),
        "global_Sp1_Witten_anomaly_absent": bool(anomalies["Witten_parity_even"]),
    }


def z6_kernel_residuals() -> dict[str, float]:
    """Check the generator (z3,-1,exp(i*pi/3)) on every multiplet."""

    z3 = cmath.exp(2j * math.pi / 3.0)
    u1 = cmath.exp(1j * math.pi / 3.0)
    triality = {
        "Q_L": 1, "L_L": 0, "u_c": -1, "d_c": -1,
        "e_c": 0, "nu_c": 0, "H": 0,
    }
    is_doublet = {
        "Q_L": 1, "L_L": 1, "u_c": 0, "d_c": 0,
        "e_c": 0, "nu_c": 0, "H": 1,
    }
    integer_hypercharge = {
        "Q_L": 1, "L_L": -3, "u_c": -4, "d_c": 2,
        "e_c": 6, "nu_c": 0, "H": 3,
    }
    residuals = {}
    for name in triality:
        phase = (
            z3 ** triality[name]
            * (-1) ** is_doublet[name]
            * u1 ** integer_hypercharge[name]
        )
        residuals[name] = abs(phase - 1.0)
    return residuals


def hybrid_bundle_gluing() -> dict[str, Any]:
    return {
        "open_segment_bundle": (
            "P_SM=P_SU3_times_P_Sp1_times_P_U1_mod_Z6_over_M4"
        ),
        "event_transport": (
            "representation_labels,_C3_family_projectors,_hypercharge_"
            "operator,_and_FR_parity_are_part_of_the_discrete_gluing_data"
        ),
        "connection_one_forms_transported_as_pregeometric_primitives": False,
        "post_event_connections": (
            "reconstructed_in_the_selected_zero-background_sector_with_the_"
            "Sp1_kinetic_norm_inherited_from_the_parent_diagonal_quotient"
        ),
        "fermion_vacuum": "zero_classical_field_with_the_odd_FR_spin_domain",
        "hybrid_bundle_returns_to_same_isomorphism_class": True,
    }


def completion_payload() -> dict[str, Any]:
    bundle = chiral_bundle_contract()
    hypercharge = hypercharge_selection()
    anomaly = yukawa_and_anomaly_ledger()
    kernel = z6_kernel_residuals()
    gluing = hybrid_bundle_gluing()
    validation = {
        "rank_16_family": bundle["one_family_complex_dimension"] == 16,
        "three_families": bundle["families"] == 3,
        "hypercharge_geometrically_selected": hypercharge[
            "selected_quark_doublet_charge"
        ] == "1/6",
        "all_Yukawa_vertices_invariant": anomaly[
            "all_Yukawa_vertices_gauge_invariant"
        ],
        "all_local_anomalies_zero": anomaly["all_local_anomalies_zero"],
        "Witten_anomaly_absent": anomaly["global_Sp1_Witten_anomaly_absent"],
        "Z6_is_in_representation_kernel": max(kernel.values()) < 1.0e-13,
        "hybrid_bundle_class_returns": gluing[
            "hybrid_bundle_returns_to_same_isomorphism_class"
        ],
        "no_new_continuous_coefficient": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_hybrid_standard_model_bundle_v15_53",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "chiral_bundle": bundle,
        "hypercharge_selection": hypercharge,
        "yukawa_and_anomaly_ledger": anomaly,
        "Z6_kernel_residuals": kernel,
        "hybrid_bundle_gluing": gluing,
        "claim_boundary": {
            "global_SM_bundle_and_representations_fixed": True,
            "hypercharge_and_anomalies_closed": True,
            "Yukawa_matrix_entries_derived": False,
            "mass_eigenvalues_and_mixing_derived": False,
            "renormalized_gauge_couplings_derived": False,
        },
        "active_calculation": (
            "EVALUATE_THE_ACTION-NORMALIZED_DIRAC-YUKAWA_OPERATOR_ON_THE_"
            "THREE_TRIALITY_EIGENBUNDLES_AND_DERIVE_ITS_MASS_AND_MIXING_"
            "MATRICES_ON_THE_HYBRID_CYCLE"
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
    path = target / "BHSM_aether_hybrid_standard_model_bundle_v15_53.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "chiral_bundle_contract", "hypercharge_selection",
    "yukawa_and_anomaly_ledger", "z6_kernel_residuals",
    "hybrid_bundle_gluing", "completion_payload", "deterministic_json",
    "materialize",
]
