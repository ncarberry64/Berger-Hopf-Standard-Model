import hashlib
from collections import OrderedDict

import numpy as np
import pytest

from bhsm.interface.ae4_c2_stratified_event_flux_assembly import (
    SECTOR_ORDER,
    assemble_stratified_direct_sum,
    canonical_noether_flux_balance,
    claim_boundary,
    solve_retarded_event_kkt,
)
from scripts.materialize_ae4_c2_stratified_event_flux_assembly import (
    TARGET,
    build_payload,
    main,
    theorem_witness,
)


def test_direct_sum_requires_the_full_sector_order():
    blocks = OrderedDict(
        (sector, (np.eye(1), np.eye(1), np.eye(1) * (1.0 + 0.1j)))
        for sector in SECTOR_ORDER
    )
    result = assemble_stratified_direct_sum(blocks)
    assert result["parent_block"].shape == (6, 6)
    assert result["all_required_sectors_explicit"]
    blocks.move_to_end("geometry_eta_sigma")
    with pytest.raises(ValueError):
        assemble_stratified_direct_sum(blocks)


def test_nonzero_retarded_event_kkt_closes_flux_and_constraints():
    witness = theorem_witness()
    solution = witness["solution"]
    assert solution["nonzero_source_present"]
    assert solution["nonzero_response_target_present"]
    assert solution["event_canonical_flux_balance_norm"] < 2e-14
    assert solution["future_child_equation_residual_norm"] < 2e-14
    assert solution["response_constraint_residual_norm"] < 2e-14
    assert solution["retarded_passivity_identity_residual"] < 2e-14
    assert solution["child_imaginary_part_positive_semidefinite"]
    assert solution["effective_imaginary_part_positive_semidefinite"]


def test_reduced_solution_matches_full_parent_child_equations():
    solution = theorem_witness()["solution"]
    total = sum(solution["event_tractions"].values())
    assert np.linalg.norm(total) < 2e-14


def test_noether_balance_is_the_generator_contraction_of_event_balance():
    noether = theorem_witness()["noether"]
    assert noether["generator_anti_Hermitian"]
    assert abs(noether["canonical_noether_flux_residual"]) < 2e-14
    assert abs(noether["traction_contraction_residual"]) < 2e-14
    with pytest.raises(ValueError):
        canonical_noether_flux_balance(
            trace=np.ones(2),
            event_tractions={"one": np.ones(2)},
            generator=np.eye(2),
        )


def test_incompatible_event_data_fail_closed():
    with pytest.raises(ValueError):
        solve_retarded_event_kkt(
            parent_block=np.eye(2),
            parent_child_coupling=np.ones((3, 2)),
            child_retarded_block=np.eye(2),
            response_operator=np.ones((1, 2)),
            source=np.ones(2),
            response_target=np.ones(1),
        )


def test_claim_boundary_advances_assembly_not_physical_evaluation():
    boundary = claim_boundary()
    assert boundary["AE4_STRATIFIED_FULL_FIELD_DIRECT_SUM_ASSEMBLY_DERIVED"]
    assert boundary["AE4_EVENT_CANONICAL_FLUX_BALANCE_IDENTITY_DERIVED"]
    assert boundary["AE4_EVENT_NOETHER_FLUX_CONTRACTION_IDENTITY_DERIVED"]
    assert not boundary["AE4_CURRENT_C2_NONZERO_SECTOR_CALDERON_BLOCKS_EVALUATED"]
    assert not boundary["PHYSICAL_ENCAPSULATION_IDENTIFIED"]


def test_materialized_event_flux_assembly_is_valid_and_deterministic():
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
