"""Assemble the AE4 current-C2 event operator and its flux balance.

This module closes the algebraic assembly step between the already-selected
future-child relative boundary domain and a physical sector evaluation.  It
does not fabricate the still-unevaluated nonzero Calderon blocks.  Given those
action-derived blocks, it forms their graded direct sum, eliminates the future
child with the same retarded prescription, includes explicit source and
response-multiplier rows, and proves the event traction balance.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np

from bhsm.interface.ae4_stratified_dirac_zeta_induced_owner import ACTION_VERSION


CLASSIFICATION = "AE4_C2_STRATIFIED_EVENT_FLUX_ASSEMBLY"
SECTOR_ORDER = (
    "geometry_eta_sigma",
    "gauge_transverse",
    "gauge_constraint",
    "BRST_ghost",
    "fermion_family",
    "HS_scalar",
)


def _matrix(value: object, name: str) -> np.ndarray:
    result = np.asarray(value, dtype=complex)
    if result.ndim != 2 or not np.all(np.isfinite(result)):
        raise ValueError(f"{name} must be a finite matrix")
    return result


def _square(value: object, name: str) -> np.ndarray:
    result = _matrix(value, name)
    if result.shape[0] != result.shape[1]:
        raise ValueError(f"{name} must be square")
    return result


def _block_diagonal(blocks: list[np.ndarray]) -> np.ndarray:
    rows = sum(block.shape[0] for block in blocks)
    cols = sum(block.shape[1] for block in blocks)
    result = np.zeros((rows, cols), dtype=complex)
    row = 0
    col = 0
    for block in blocks:
        height, width = block.shape
        result[row : row + height, col : col + width] = block
        row += height
        col += width
    return result


def assemble_stratified_direct_sum(
    sector_blocks: Mapping[str, tuple[object, object, object]],
) -> dict[str, Any]:
    """Assemble parent, parent-child and retarded-child sector blocks.

    Each row is ``(H_pp, H_pc, H_cc^R)``.  The ghost/fermion statistics sign
    must already be the sign inherited from the AE4 supertrace; it is not an
    independently adjustable normalization in this function.
    """

    if tuple(sector_blocks) != SECTOR_ORDER:
        raise ValueError(f"sector order must be exactly {SECTOR_ORDER!r}")
    parents: list[np.ndarray] = []
    couplings: list[np.ndarray] = []
    children: list[np.ndarray] = []
    parent_slices: dict[str, tuple[int, int]] = {}
    child_slices: dict[str, tuple[int, int]] = {}
    parent_offset = 0
    child_offset = 0
    for sector in SECTOR_ORDER:
        parent = _square(sector_blocks[sector][0], f"{sector}.parent")
        coupling = _matrix(sector_blocks[sector][1], f"{sector}.coupling")
        child = _square(sector_blocks[sector][2], f"{sector}.child")
        if coupling.shape != (parent.shape[0], child.shape[0]):
            raise ValueError(f"{sector}.coupling has incompatible shape")
        if not np.allclose(parent, parent.conj().T, rtol=0.0, atol=1.0e-11):
            raise ValueError(f"{sector}.parent must be Hermitian")
        parent_slices[sector] = (parent_offset, parent_offset + parent.shape[0])
        child_slices[sector] = (child_offset, child_offset + child.shape[0])
        parent_offset += parent.shape[0]
        child_offset += child.shape[0]
        parents.append(parent)
        couplings.append(coupling)
        children.append(child)
    return {
        "parent_block": _block_diagonal(parents),
        "parent_child_coupling": _block_diagonal(couplings),
        "child_retarded_block": _block_diagonal(children),
        "parent_sector_slices": parent_slices,
        "child_sector_slices": child_slices,
        "sector_order": SECTOR_ORDER,
        "all_required_sectors_explicit": True,
        "independent_sector_normalization_inserted": False,
    }


def solve_retarded_event_kkt(
    *,
    parent_block: object,
    parent_child_coupling: object,
    child_retarded_block: object,
    response_operator: object,
    source: object,
    response_target: object,
) -> dict[str, Any]:
    """Solve the full and child-eliminated event stationarity equations.

    With parent trace ``q``, child coordinate ``c`` and multiplier ``lambda``,
    the equations are

    ``H_pp q + H_pc c + C^dagger lambda + J = 0``,
    ``H_cp q + H_cc^R c = 0`` and ``C q = d``.

    Child elimination returns the AE4 retarded Schur block.  The four event
    tractions (parent, returned child, explicit source, response multiplier)
    then sum to zero.  This is the nonzero-source extension of the historical
    homogeneous event-child flux match.
    """

    parent = _square(parent_block, "parent_block")
    child = _square(child_retarded_block, "child_retarded_block")
    coupling = _matrix(parent_child_coupling, "parent_child_coupling")
    response = _matrix(response_operator, "response_operator")
    current = np.asarray(source, dtype=complex)
    target = np.asarray(response_target, dtype=complex)
    n = parent.shape[0]
    m = child.shape[0]
    r = response.shape[0]
    if coupling.shape != (n, m):
        raise ValueError("parent_child_coupling has incompatible shape")
    if response.shape[1] != n or current.shape != (n,) or target.shape != (r,):
        raise ValueError("response/source data have incompatible shape")
    if not all(np.all(np.isfinite(value)) for value in (current, target)):
        raise ValueError("response/source data must be finite")
    if not np.allclose(parent, parent.conj().T, rtol=0.0, atol=1.0e-11):
        raise ValueError("parent_block must be Hermitian")

    inverse = np.linalg.inv(child)
    returned_child = -coupling @ inverse @ coupling.conj().T
    effective = parent + returned_child
    if r:
        kkt = np.block(
            [[effective, response.conj().T], [response, np.zeros((r, r))]]
        )
        rhs = np.concatenate((-current, target))
    else:
        kkt = effective
        rhs = -current
    solution = np.linalg.solve(kkt, rhs)
    trace = solution[:n]
    multiplier = solution[n:]
    child_state = -inverse @ coupling.conj().T @ trace

    parent_traction = parent @ trace
    child_traction = coupling @ child_state
    source_traction = current
    response_traction = response.conj().T @ multiplier
    balance = parent_traction + child_traction + source_traction + response_traction
    child_equation = coupling.conj().T @ trace + child @ child_state
    constraint = response @ trace - target

    child_imaginary = (child - child.conj().T) / (2.0j)
    effective_imaginary = (effective - effective.conj().T) / (2.0j)
    expected_imaginary = (
        coupling @ inverse.conj().T @ child_imaginary @ inverse @ coupling.conj().T
    )
    return {
        "parent_trace": trace,
        "future_child_state": child_state,
        "response_multiplier": multiplier,
        "effective_retarded_parent_block": effective,
        "event_tractions": {
            "parent_bulk": parent_traction,
            "returned_future_child": child_traction,
            "explicit_source": source_traction,
            "response_multiplier": response_traction,
        },
        "event_canonical_flux_balance": balance,
        "event_canonical_flux_balance_norm": float(np.linalg.norm(balance)),
        "future_child_equation_residual_norm": float(np.linalg.norm(child_equation)),
        "response_constraint_residual_norm": float(np.linalg.norm(constraint)),
        "retarded_passivity_identity_residual": float(
            np.linalg.norm(effective_imaginary - expected_imaginary)
        ),
        "child_imaginary_part_positive_semidefinite": bool(
            np.min(np.linalg.eigvalsh(child_imaginary)) >= -1.0e-11
        ),
        "effective_imaginary_part_positive_semidefinite": bool(
            np.min(np.linalg.eigvalsh(effective_imaginary)) >= -1.0e-11
        ),
        "nonzero_source_present": bool(np.linalg.norm(current) > 0.0),
        "nonzero_response_target_present": bool(np.linalg.norm(target) > 0.0),
        "explicit_inverse_formed_for_finite_theorem_witness": True,
        "continuum_implementation_requires_retarded_resolvent": True,
    }


def canonical_noether_flux_balance(
    *, trace: object, event_tractions: Mapping[str, object], generator: object
) -> dict[str, Any]:
    """Contract the canonical event balance with an infinitesimal symmetry.

    Sector statistics and BRST signs are inherited through the tractions from
    the common AE4 supertrace.  For an anti-Hermitian generator ``T``, the
    returned terms are ``2 Re <Tq,Pi_i>`` and their sum is the event Noether
    flux residual.
    """

    q = np.asarray(trace, dtype=complex)
    transform = _square(generator, "generator")
    if transform.shape != (q.size, q.size):
        raise ValueError("generator has incompatible shape")
    if not np.allclose(transform.conj().T, -transform, rtol=0.0, atol=1.0e-11):
        raise ValueError("generator must be anti-Hermitian")
    tangent = transform @ q
    parts: dict[str, float] = {}
    total_traction = np.zeros_like(q)
    for name, value in event_tractions.items():
        traction = np.asarray(value, dtype=complex)
        if traction.shape != q.shape or not np.all(np.isfinite(traction)):
            raise ValueError(f"{name} traction has incompatible shape")
        total_traction += traction
        parts[name] = float(2.0 * np.real(np.vdot(tangent, traction)))
    return {
        "generator_anti_Hermitian": True,
        "canonical_noether_flux_terms": parts,
        "canonical_noether_flux_residual": float(sum(parts.values())),
        "traction_contraction_residual": float(
            2.0 * np.real(np.vdot(tangent, total_traction))
        ),
        "Ward_or_global_charge_normalization_inferred": False,
    }


def assembly_contract() -> dict[str, Any]:
    return {
        "action_version": ACTION_VERSION,
        "sector_order": SECTOR_ORDER,
        "graded_direct_sum": (
            "geometry_eta_sigma_DIRECT_SUM_gauge_transverse_DIRECT_SUM_"
            "gauge_constraint_DIRECT_SUM_BRST_ghost_DIRECT_SUM_fermion_family_"
            "DIRECT_SUM_HS_scalar"
        ),
        "source_rows": "J_gauge,J_fermion,J_HS_AND_EXISTING_CURRENT_C2_JY,J3",
        "response_rows": "AE3_eta_sigma_response_AND_ACTION_OWNED_HS_constraints",
        "child_rule": "ONE_FUTURE_RETARDED_RESOLVENT_FOR_ALL_SECTORS",
        "event_balance": "Pi_parent+Pi_child_return+J+C_dagger*lambda=0",
        "physical_blocks_may_be_supplied_by_independent_fits": False,
        "zero_background_homogeneous_match_recovered_at_J=d=0": True,
        "particle_identity_and_family_projectors_rebuilt": False,
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "AE4_STRATIFIED_FULL_FIELD_DIRECT_SUM_ASSEMBLY_DERIVED": True,
        "AE4_NONZERO_SOURCE_RESPONSE_KKT_REDUCTION_DERIVED": True,
        "AE4_EVENT_CANONICAL_FLUX_BALANCE_IDENTITY_DERIVED": True,
        "AE4_EVENT_NOETHER_FLUX_CONTRACTION_IDENTITY_DERIVED": True,
        "AE4_N12_CONTINUUM_CHILD_REUSED_WITHOUT_RECONSTRUCTION": True,
        "AE4_CURRENT_C2_CANONICAL_STOP_GAUGE_BRST_CENTER_BLOCK_EVALUATED": True,
        "AE4_CURRENT_C2_AFFINE72_GAUGE_BRST_FIRST_JET_CANDIDATE_EVALUATED": True,
        "AE4_CURRENT_C2_AFFINE72_PARTICLE_FIBER_CALDERON_CANDIDATE_EVALUATED": True,
        "AE4_ALL_NINE_EXISTING_CHARGED_PARTICLE_FIBERS_ATTACHED": True,
        "AE4_G7_SINGLE_RADIUS_74D_CONTRACTION_OBSTRUCTION_ADJUDICATED": True,
        "AE4_G7_ACTION_BLOCK_RADII_POLYNOMIAL_OPEN": True,
        "AE4_CURRENT_C2_NONZERO_SECTOR_CALDERON_BLOCKS_EVALUATED": False,
        "AE4_CURRENT_C2_PHYSICAL_EVENT_FLUX_NUMERICALLY_EVALUATED": False,
        "AE4_CURRENT_C2_NOETHER_HAMILTONIAN_BALANCE_PHYSICALLY_CLOSED": False,
        "CURRENT_C2_LORENTZIAN_MAXWELL_RESIDUE_DERIVED": False,
        "CURRENT_C2_ACTION_SELECTED_HADAMARD_STATE_DERIVED": False,
        "PHYSICAL_ENCAPSULATION_IDENTIFIED": False,
        "FULL_BHSM_COMPLETE": False,
        "exact_next_calculation": (
            "CERTIFY_THE_SAME_FROZEN_CENTER_WITH_AN_ACTION_BLOCK_OR_"
            "COMPONENTWISE_RADII_POLYNOMIAL_USING_EXISTING_OUTWARD_OPERANDS,_"
            "THEN_PROMOTE_THE_EVALUATED_GAUGE_BRST_AND_PRODUCT_DIRAC_JETS_AND_"
            "COMPOSE_THE_HS_"
            "FERMION_MIXED_BLOCK,_THEN_INSERT_ALL_PHYSICAL_SECTORS_WITHOUT_"
            "FITTED_NORMALIZATION"
        ),
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "SECTOR_ORDER",
    "assemble_stratified_direct_sum",
    "assembly_contract",
    "canonical_noether_flux_balance",
    "claim_boundary",
    "solve_retarded_event_kkt",
]
