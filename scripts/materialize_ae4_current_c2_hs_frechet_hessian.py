"""Materialize the current-C2 AE4 HS Fréchet Hessian."""

from __future__ import annotations

import hashlib
import json
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
from scipy.linalg import eigh


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae3_c2_action_puzzle import (
    assemble_tridiagonal,
    reduced_product_dirac_hs_source_jet,
)
from bhsm.interface.ae4_current_c2_hs_frechet_hessian import (
    ACTION_VERSION,
    CLASSIFICATION,
    claim_boundary,
    generalized_e1_coordinate_jet,
)


A = ROOT / "artifacts/action_extension"
DESCRIPTOR_JSON = ROOT / "artifacts/flagship_integration/BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.json"
DESCRIPTOR_NPZ = ROOT / "artifacts/flagship_integration/BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.npz"
TARGET = A / "BHSM_AE4_CURRENT_C2_HS_FRECHET_HESSIAN.json"
GALERKIN_DIMENSION = 128
INPUTS = (
    A / "BHSM_AE4_STRATIFIED_DIRAC_ZETA_INDUCED_OWNER.json",
    A / "BHSM_AE4_C2_STRATIFIED_EVENT_FLUX_ASSEMBLY.json",
    A / "BHSM_AE3_C2_FULL_FIELD_PUZZLE_ASSEMBLY.json",
    A / "BHSM_AE3_C2_HS_FERMION_MIXED_VARIATION.json",
    DESCRIPTOR_JSON,
    DESCRIPTOR_NPZ,
    ROOT / "src/bhsm/interface/ae4_current_c2_hs_frechet_hessian.py",
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _channel(
    data: Any, *, suffix: str, durations: np.ndarray
) -> dict[str, Any]:
    n = GALERKIN_DIMENSION
    stiffness = assemble_tridiagonal(
        data[f"{suffix}__K_diagonal"][:n],
        data[f"{suffix}__K_off_diagonal"][: n - 1],
    )
    mass = assemble_tridiagonal(
        data[f"{suffix}__M_diagonal"][:n],
        data[f"{suffix}__M_off_diagonal"][: n - 1],
    )
    W = np.asarray(data[f"{suffix}__element_coefficient"][:n], dtype=float)
    source_jet = reduced_product_dirac_hs_source_jet(
        proper_durations=durations[:n],
        base_W=W,
        source_profile=np.ones_like(W),
    )
    vertex = assemble_tridiagonal(
        source_jet["vertex_diagonal"], source_jet["vertex_off_diagonal"]
    )
    contact = assemble_tridiagonal(
        source_jet["contact_diagonal"], source_jet["contact_off_diagonal"]
    )
    minimum = float(eigh(stiffness, mass, eigvals_only=True, subset_by_index=[0, 0])[0])
    witness_length = 1.0 / np.sqrt(minimum)
    result = generalized_e1_coordinate_jet(
        stiffness=stiffness,
        mass=mass,
        vertex=vertex,
        contact=contact,
        spectral_length=witness_length,
        supertrace_weight=-1.0,
    )
    return {
        **result,
        "witness_spectral_length_rule": "ell_witness=lambda_min_birth_prefix^(-1/2)",
        "witness_spectral_length_is_physical_ell_star": False,
    }


def _full_core_conditioning(
    data: Any, *, suffix: str, analytic_gap_lower: float
) -> dict[str, Any]:
    mass_diagonal = np.asarray(data[f"{suffix}__M_diagonal"], dtype=float)
    stiffness_diagonal = np.asarray(data[f"{suffix}__K_diagonal"], dtype=float)
    scaled_diagonal = stiffness_diagonal / mass_diagonal
    largest = float(np.max(scaled_diagonal))
    smallest = float(np.min(scaled_diagonal))
    gap = float(analytic_gap_lower)
    resolvable_ratio = gap / largest
    return {
        "dimension": int(mass_diagonal.size),
        "mass_diagonal_equilibrated_stiffness_minimum": smallest,
        "mass_diagonal_equilibrated_stiffness_maximum": largest,
        "equilibrated_diagonal_dynamic_range": largest / smallest,
        "analytic_generalized_gap_lower": gap,
        "analytic_gap_to_largest_diagonal_ratio": resolvable_ratio,
        "ratio_below_float64_machine_epsilon": bool(
            resolvable_ratio < np.finfo(float).eps
        ),
        "dense_full_generalized_eigensolve_authorized": False,
        "required_route": (
            "FIRST_ORDER_PRODUCT_DIRAC_FACTORIZATION_OR_INVERSE_FREE_"
            "STURM_TRANSFER_RESOLVENT_WITH_ANALYTIC_GAP_CONTROL"
        ),
    }


@lru_cache(maxsize=1)
def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    source_artifacts = [_load(path) for path in INPUTS[:5]]
    descriptor = source_artifacts[-1]
    channels: dict[str, Any] = {}
    conditioning: dict[str, Any] = {}
    with np.load(DESCRIPTOR_NPZ) as data:
        durations = np.asarray(data["segment_proper_duration_proof_center"], dtype=float)
        for chirality, suffix in (
            (1, "product_Dirac_lambda1_5_chirality_plus"),
            (-1, "product_Dirac_lambda1_5_chirality_minus"),
        ):
            channels[suffix] = {
                "chirality": chirality,
                **_channel(data, suffix=suffix, durations=durations),
            }
            conditioning[suffix] = _full_core_conditioning(
                data,
                suffix=suffix,
                analytic_gap_lower=descriptor["descriptor_pencils"][suffix][
                    "generalized_gap_lower"
                ],
            )
    boundary = claim_boundary()
    validation = {
        "all_JSON_inputs_validated": all(row["validation_passed"] for row in source_artifacts),
        "both_current_C2_chiralities_evaluated": len(channels) == 2,
        "birth_local_128_segment_Galerkin_prefix_used": all(
            row["dimension"] == GALERKIN_DIMENSION for row in channels.values()
        ),
        "positive_generalized_operators": all(
            row["minimum_generalized_eigenvalue"] > 0.0 for row in channels.values()
        ),
        "real_sources_and_curvatures": all(
            row["imaginary_source_residual"] < 1.0e-10
            and row["imaginary_curvature_residual"] < 1.0e-10
            for row in channels.values()
        ),
        "same_operator_used_for_each_jet": all(
            row["same_operator_supplies_source_and_curvature"] for row in channels.values()
        ),
        "conditioned_HS_curvatures_positive": all(
            row["HS_curvature"] > 0.0 for row in channels.values()
        ),
        "chiral_HS_jets_equal": (
            abs(
                channels["product_Dirac_lambda1_5_chirality_plus"]["HS_source"]
                - channels["product_Dirac_lambda1_5_chirality_minus"]["HS_source"]
            )
            < 1.0e-40
            and abs(
                channels["product_Dirac_lambda1_5_chirality_plus"]["HS_curvature"]
                - channels["product_Dirac_lambda1_5_chirality_minus"]["HS_curvature"]
            )
            < 1.0e-72
        ),
        "no_explicit_inverse": all(
            not row["explicit_matrix_inverse_formed"] for row in channels.values()
        ),
        "proof_center_not_promoted_to_physical_history": not descriptor[
            "coefficient_path"
        ]["proof_centers_are_exact_physical_states"],
        "far_core_edge_not_promoted_to_physical_endpoint": not descriptor[
            "endpoint_event_child_partition"
        ]["far_core_edge_is_physical_endpoint"],
        "physical_scale_not_overclaimed": not boundary[
            "AE4_PHYSICAL_ELL_STAR_NUMERICALLY_EVALUATED"
        ],
        "physical_HS_kernel_not_overclaimed": not boundary[
            "AE4_MAXIMAL_HISTORY_HS_CALDERON_BLOCK_EVALUATED"
        ],
        "full_core_dense_spectral_route_rejected": all(
            row["ratio_below_float64_machine_epsilon"]
            and not row["dense_full_generalized_eigensolve_authorized"]
            for row in conditioning.values()
        ),
    }
    return {
        "artifact": "BHSM_AE4_CURRENT_C2_HS_FRECHET_HESSIAN",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "operator_domain": {
            "background": "RESET_GENERATED_CURRENT_C2_PROOF_CENTER_FAMILY",
            "retained_boundary": "C2_BIRTH_TRACE_NODE_0",
            "far_boundary": "BIRTH_LOCAL_GALERKIN_PREFIX_DIRICHLET_TRUNCATION_ONLY",
            "parent_descriptor_dimension": 1222,
            "evaluated_birth_local_Galerkin_dimension": GALERKIN_DIMENSION,
            "spectral_length": "lambda_min_birth_prefix^(-1/2)",
            "spectral_length_role": "CONDITIONED_OWNER_WITNESS_NOT_PHYSICAL_ELL_STAR",
            "supertrace_weight": -1.0,
            "supertrace_weight_role": "ONE_WEYL_BLOCK_BEFORE_PHYSICAL_CHANNEL_MULTIPLICITY",
        },
        "channels": channels,
        "full_core_conditioning_gate": conditioning,
        "claim_boundary": boundary,
        "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("current-C2 AE4 HS Hessian failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
