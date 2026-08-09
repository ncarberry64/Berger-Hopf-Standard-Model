from pathlib import Path
import json
import numpy as np

from bhsm.interface.completion.round_hessian_centrality_no_go_v14_71 import (
    VERSION, PRIMARY_VERDICT, EXACT_NEXT_OBJECT,
    so3_generators, product_generators, diagonal_generators, commutator,
    commutant_constraint_matrix, nullity, product_commutant_dimension,
    diagonal_commutant_dimension, l2_projectors, projector_quality,
    full_symmetry_central_operator, diagonal_only_operator, max_commutator_norm,
    equivariant_schur_witness, spectral_function_centrality_witness,
    full_product_commutant_payload, diagonal_commutant_payload,
    sector_ledger_payload, triplet_selection_no_go_payload,
    symmetry_breaking_requirements_payload, neutrino_kill_screen_payload,
    status_payload, completion_gate_payload, artifact_payloads, materialize,
)

def test_version_and_verdict():
    assert VERSION=="v14.71"
    assert "SU2L" in PRIMARY_VERDICT
    assert "SYMMETRY_BREAKING" in EXACT_NEXT_OBJECT

def test_so3_generators_are_antisymmetric():
    for j in so3_generators():
        assert np.linalg.norm(j+j.T)<1e-14

def test_product_generator_counts():
    left,right=product_generators()
    assert len(left)==3 and len(right)==3
    assert all(g.shape==(9,9) for g in left+right)

def test_left_right_generators_commute():
    left,right=product_generators()
    assert max(np.linalg.norm(commutator(l,r)) for l in left for r in right)<1e-14

def test_product_commutant_dimension_one():
    assert product_commutant_dimension()==1

def test_diagonal_commutant_dimension_three():
    assert diagonal_commutant_dimension()==3

def test_constraint_matrix_nullities():
    left,right=product_generators()
    assert nullity(commutant_constraint_matrix(left+right))==1
    assert nullity(commutant_constraint_matrix(diagonal_generators()))==3

def test_projector_ranks():
    p1,p3,p5=l2_projectors()
    assert [np.linalg.matrix_rank(p,tol=1e-11) for p in (p1,p3,p5)]==[1,3,5]

def test_projector_quality():
    q=projector_quality()
    assert q["sum_identity_residual"]<1e-12
    assert q["pairwise_orthogonality_residual"]<1e-12
    assert q["idempotence_residual"]<1e-12
    assert q["self_adjoint_residual"]<1e-12

def test_full_central_operator_commutes_with_product():
    left,right=product_generators()
    assert max_commutator_norm(full_symmetry_central_operator(),left+right)<1e-14

def test_diagonal_split_operator_commutes_with_diagonal_only():
    op=diagonal_only_operator()
    assert max_commutator_norm(op,diagonal_generators())<1e-12

def test_diagonal_split_operator_breaks_product_symmetry():
    left,right=product_generators()
    assert max_commutator_norm(diagonal_only_operator(),left+right)>1e-3

def test_schur_witness_preserves_centrality():
    p=equivariant_schur_witness()
    assert p["centrality_residual"]<1e-12
    assert p["full_product_commutator_residual"]<1e-12

def test_spectral_functional_calculus_centrality():
    p=spectral_function_centrality_witness()
    assert p["heat_commutator_residual"]<1e-12
    assert p["resolvent_commutator_residual"]<1e-12
    assert p["log_commutator_residual"]<1e-12

def test_full_commutant_payload():
    p=full_product_commutant_payload()
    assert p["commutant_dimension"]==1
    assert p["constraint_rank"]==80
    assert p["triplet_selection_possible_without_symmetry_breaking"] is False

def test_diagonal_payload():
    p=diagonal_commutant_payload()
    assert p["commutant_dimension"]==3
    assert p["triplet_projector_rank"]==3
    assert p["diagonal_SU2_selected_by_current_round_BHSM_action"] is False

def test_sector_ledger_fail_closed():
    p=sector_ledger_payload()
    assert p["all_current_round_equivariant_sectors_fail_to_select_triplet"] is True
    assert p["complete_numeric_full_BHSM_second_shape_Hessian_evaluated"] is False
    assert p["nonround_or_anisotropic_stationary_branch_excluded"] is False

def test_triplet_no_go():
    p=triplet_selection_no_go_payload()
    assert p["full_round_commutant_dimension"]==1
    assert p["diagonal_SU2_commutant_dimension"]==3
    assert p["round_action_can_split_1_3_5"] is False
    assert p["round_action_can_uniquely_select_rank3_triplet"] is False

def test_symmetry_breaking_requirements():
    p=symmetry_breaking_requirements_payload()
    assert p["current_round_branch_meets_requirements"] is False
    assert len(p["minimum_theorem_requirements"])>=7

def test_neutrino_kill_screen():
    p=neutrino_kill_screen_payload()
    assert p["current_result"]=="PHYSICAL_EXECUTION_BLOCKED"
    assert p["physical_execution_allowed"] is False

def test_status():
    p=status_payload()
    assert len(p["validated"])>=10
    assert p["FULL_BHSM_COMPLETE"] is False
    assert p["MARK_III"]=="NOT_REACHED"
    assert p["USB_touched"] is False

def test_completion_gate():
    p=completion_gate_payload()
    assert p["validation_passed"] is True
    assert p["full_BHSM_complete"] is False
    assert p["physical_execution_allowed"] is False

def test_artifact_count():
    p=artifact_payloads()
    assert len(p)==10
    assert "BHSM_completion_gate_v14_71.json" in p
    assert "BHSM_triplet_selection_no_go_v14_71.json" in p

def test_materialization_deterministic(tmp_path:Path):
    a=tmp_path/"a"; b=tmp_path/"b"
    pa=materialize(a); pb=materialize(b)
    assert [x.name for x in pa]==[x.name for x in pb]
    for x,y in zip(pa,pb):
        assert x.read_bytes()==y.read_bytes()
        json.loads(x.read_text())
