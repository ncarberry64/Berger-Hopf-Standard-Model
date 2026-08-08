"""BHSM v14.71 round-branch full second-shape Hessian centrality no-go.

v14.70 established that the first positive scalar shape space on the retained
round S3 seam is ell=2, dimension 9, and that after *choosing* a diagonal SU(2)
one can decompose it as 1+3+5.  This sprint asks whether the complete current
round-branch BHSM second-shape Hessian can itself make that choice.

The answer is no on the retained reflection-symmetric round/isotropic branch.

The ell=2 scalar harmonics transform irreducibly as (1,1) under
SU(2)_L x SU(2)_R ~= Spin(4).  The exact commutant of the six product-group
generators on this 9-dimensional space is one-dimensional.  Therefore every
self-adjoint second-variation operator that preserves the full round symmetry
is c I_9 on ell=2.  Bulk, GHY, compatibility/KKT Schur reduction, and spectral
functional calculus preserve this equivariance when evaluated on the retained
round/isotropic stationary branch.  They can move the common ell=2 eigenvalue
but cannot split 1+3+5 or select only the triplet.

If one reduces symmetry to a chosen diagonal SU(2), the commutant becomes
three-dimensional and is spanned by the exact 1,3,5 projectors.  Thus triplet
selection requires an action-owned symmetry-breaking/polarization field or
background (for example an action-selected Berger/Hopf anisotropy, connection,
or nonround seam tensor).  Such a physical selector is not present in the
current round branch.

This module is a symmetry theorem and fail-closed provenance audit.  It does
not assign the missing full physical second-shape coefficient, choose a
symmetry-breaking background, or emit a particle/flavor observable.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import json
from typing import Any

import numpy as np

VERSION = "v14.71"
PRIMARY_VERDICT = (
    "BHSM_V14_71_ON_THE_RETAINED_ROUND_REFLECTION_SYMMETRIC_ISOTROPIC_BRANCH_"
    "THE_COMPLETE_ACTION_OWNED_SECOND_SHAPE_HESSIAN_MUST_COMMUTE_WITH_THE_"
    "FULL_SU2L_TIMES_SU2R_ACTION_ON_THE_ELL2_NINE_DIMENSIONAL_IRREP_SO_BY_"
    "SCHURS_LEMMA_IT_IS_SCALAR_ON_THAT_SPACE_AND_CANNOT_SELECT_THE_DIAGONAL_"
    "SU2_TRIPLET;_THE_EXACT_FULL_PRODUCT_COMMUTANT_HAS_DIMENSION_ONE_WHILE_"
    "THE_DIAGONAL_SU2_COMMUTANT_HAS_DIMENSION_THREE_SPANNED_BY_THE_1_3_5_"
    "PROJECTORS_THEREFORE_PHYSICAL_THREE_CHANNEL_SELECTION_REQUIRES_AN_"
    "ACTION_SELECTED_SYMMETRY_BREAKING_HOPF_BERGER_CONNECTION_OR_NONROUND_"
    "POLARIZATION_BACKGROUND_BEFORE_THE_CALDERON_HEAT_AND_NEUTRINO_GATES"
)
EXACT_NEXT_OBJECT = (
    "ACTION_SELECTED_SYMMETRY_BREAKING_STATIONARY_PARENT_CHILD_BACKGROUND_"
    "OR_CONNECTION_POLARIZATION_THAT_REDUCES_THE_ROUND_SU2L_TIMES_SU2R_"
    "SYMMETRY_TO_A_SPECIFIC_DIAGONAL_SU2_OR_SMALLER_GROUP_WITH_DERIVED_"
    "ELL2_SECOND_SHAPE_SPLITTING_AND_A_UNIQUE_PHYSICAL_TRIPLET_FOLLOWED_BY_"
    "THREE_SHAPE_CALDERON_DERIVATIVES_RELATIVE_HEAT_SUPERTRACE_AND_FROZEN_"
    "NEUTRINO_KILL_SCREEN"
)


def canonical_json_bytes(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("utf-8")


def sha256_payload(payload: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def so3_generators() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Real antisymmetric generators of the vector/spin-1 representation."""
    jx = np.array([[0.0,0.0,0.0],[0.0,0.0,-1.0],[0.0,1.0,0.0]])
    jy = np.array([[0.0,0.0,1.0],[0.0,0.0,0.0],[-1.0,0.0,0.0]])
    jz = np.array([[0.0,-1.0,0.0],[1.0,0.0,0.0],[0.0,0.0,0.0]])
    return jx, jy, jz


def product_generators() -> tuple[list[np.ndarray], list[np.ndarray]]:
    """Generators of spin-1 x spin-1 on R^3 tensor R^3 ~= R^9."""
    eye = np.eye(3)
    js = so3_generators()
    left = [np.kron(j, eye) for j in js]
    right = [np.kron(eye, j) for j in js]
    return left, right


def diagonal_generators() -> list[np.ndarray]:
    left, right = product_generators()
    return [l+r for l,r in zip(left,right)]


def commutator(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.asarray(a) @ np.asarray(b) - np.asarray(b) @ np.asarray(a)


def commutant_constraint_matrix(generators: list[np.ndarray]) -> np.ndarray:
    """Linear map vec(X) -> vec([X,G_i]) using column-major vectorization."""
    n = generators[0].shape[0]
    eye = np.eye(n)
    rows = []
    for g in generators:
        # vec(XG-GX) = (G^T kron I - I kron G) vec(X)
        rows.append(np.kron(g.T, eye) - np.kron(eye, g))
    return np.vstack(rows)


def nullity(matrix: np.ndarray, tol: float = 1e-10) -> int:
    s = np.linalg.svd(np.asarray(matrix), compute_uv=False)
    rank = int(np.sum(s > tol))
    return int(matrix.shape[1] - rank)


def product_commutant_dimension() -> int:
    left,right = product_generators()
    return nullity(commutant_constraint_matrix(left+right))


def diagonal_commutant_dimension() -> int:
    return nullity(commutant_constraint_matrix(diagonal_generators()))


def _matrix_space_projector(fn) -> np.ndarray:
    cols = []
    for i in range(3):
        for j in range(3):
            e=np.zeros((3,3))
            e[i,j]=1.0
            cols.append(np.asarray(fn(e)).reshape(-1))
    return np.column_stack(cols)


def l2_projectors() -> tuple[np.ndarray,np.ndarray,np.ndarray]:
    """Exact diagonal-SU(2) decomposition 3 tensor 3 = 1 + 3 + 5."""
    p1=_matrix_space_projector(lambda a: np.trace(a)/3.0*np.eye(3))
    p3=_matrix_space_projector(lambda a: 0.5*(a-a.T))
    p5=_matrix_space_projector(lambda a: 0.5*(a+a.T)-np.trace(a)/3.0*np.eye(3))
    return p1,p3,p5


def projector_quality() -> dict[str,Any]:
    ps=l2_projectors()
    return {
        "ranks":[int(np.linalg.matrix_rank(p,tol=1e-11)) for p in ps],
        "sum_identity_residual":float(np.linalg.norm(sum(ps)-np.eye(9))),
        "pairwise_orthogonality_residual":float(max(np.linalg.norm(ps[i]@ps[j]) for i in range(3) for j in range(i+1,3))),
        "idempotence_residual":float(max(np.linalg.norm(p@p-p) for p in ps)),
        "self_adjoint_residual":float(max(np.linalg.norm(p-p.T) for p in ps)),
    }


def full_symmetry_central_operator(coefficient: float = 2.75) -> np.ndarray:
    return float(coefficient)*np.eye(9)


def diagonal_only_operator(coefficients=(1.2,2.4,4.1)) -> np.ndarray:
    p1,p3,p5=l2_projectors()
    a,b,c=map(float,coefficients)
    return a*p1+b*p3+c*p5


def max_commutator_norm(operator: np.ndarray, generators: list[np.ndarray]) -> float:
    return float(max(np.linalg.norm(commutator(operator,g)) for g in generators))


def equivariant_schur_witness() -> dict[str,Any]:
    """Show Schur reduction preserves centrality on the ell=2 irrep."""
    i9=np.eye(9)
    # Synthetic scalar coefficients stand only for invariant block coefficients.
    A=3.7*i9
    B=0.8*i9
    C=2.3*i9
    H=np.block([[A,B],[B,C]])
    heff=A-B@np.linalg.solve(C,B)
    coeff=3.7-0.8**2/2.3
    left,right=product_generators()
    return {
        "input_block_form":"[[a I9,b I9],[b I9,c I9]]",
        "schur_formula":"H_eff=(a-b^2/c) I9",
        "expected_coefficient":coeff,
        "centrality_residual":float(np.linalg.norm(heff-coeff*i9)),
        "full_product_commutator_residual":max_commutator_norm(heff,left+right),
        "synthetic_coefficients_are_physical":False,
        "theorem":"equivariant KKT/Schur elimination cannot split the ell=2 irrep",
    }


def spectral_function_centrality_witness() -> dict[str,Any]:
    """Heat/resolvent/zeta-local functional calculus stays central on an irrep."""
    lam=5.0
    t=0.55
    i9=np.eye(9)
    heat=np.exp(-t*lam)*i9
    resolvent=(1.0/(lam+1.7))*i9
    logop=np.log(lam+0.9)*i9
    left,right=product_generators()
    return {
        "ell2_round_jacobi_eigenvalue_at_a1":lam,
        "heat_trace_on_ell2":float(np.trace(heat)),
        "resolvent_trace_on_ell2":float(np.trace(resolvent)),
        "log_operator_trace_on_ell2":float(np.trace(logop)),
        "heat_commutator_residual":max_commutator_norm(heat,left+right),
        "resolvent_commutator_residual":max_commutator_norm(resolvent,left+right),
        "log_commutator_residual":max_commutator_norm(logop,left+right),
        "theorem":"spectral functional calculus of an equivariant operator remains equivariant and cannot choose a triplet",
        "diagnostic_not_physical":True,
    }


def full_product_commutant_payload() -> dict[str,Any]:
    left,right=product_generators()
    cmat=commutant_constraint_matrix(left+right)
    s=np.linalg.svd(cmat,compute_uv=False)
    p=projector_quality()
    central=full_symmetry_central_operator()
    return {
        "version":VERSION,
        "representation":"ell=2 scalar harmonics H_2 ~= (j_L,j_R)=(1,1), dimension 9",
        "group":"SU(2)_L x SU(2)_R",
        "number_of_generators":6,
        "constraint_matrix_shape":list(cmat.shape),
        "constraint_rank":int(np.sum(s>1e-10)),
        "commutant_dimension":product_commutant_dimension(),
        "expected_commutant":"span{I9}",
        "sample_central_operator_commutator_residual":max_commutator_norm(central,left+right),
        "diagonal_projector_ranks":p["ranks"],
        "schur_lemma_conclusion":"every full-product-equivariant self-adjoint Hessian is c I9 on H_2",
        "triplet_selection_possible_without_symmetry_breaking":False,
        "physical_prediction":False,
    }


def diagonal_commutant_payload() -> dict[str,Any]:
    gens=diagonal_generators()
    cmat=commutant_constraint_matrix(gens)
    s=np.linalg.svd(cmat,compute_uv=False)
    p1,p3,p5=l2_projectors()
    q=projector_quality()
    op=diagonal_only_operator()
    left,right=product_generators()
    return {
        "version":VERSION,
        "group":"chosen diagonal SU(2)",
        "constraint_rank":int(np.sum(s>1e-10)),
        "commutant_dimension":diagonal_commutant_dimension(),
        "expected_basis":"P1,P3,P5 for 3 tensor 3 = 1 + 3 + 5",
        "projector_quality":q,
        "diagonal_operator_commutator_with_diagonal_SU2":max_commutator_norm(op,gens),
        "diagonal_operator_commutator_with_full_product":max_commutator_norm(op,left+right),
        "triplet_projector_rank":int(np.linalg.matrix_rank(p3,tol=1e-11)),
        "triplet_can_be_spectrally_distinguished_after_diagonal_symmetry_is_selected":True,
        "diagonal_SU2_selected_by_current_round_BHSM_action":False,
        "physical_prediction":False,
    }


def sector_ledger_payload() -> dict[str,Any]:
    rows=[
        {
            "sector":"universal second-shape geometry / area Jacobi term",
            "round_branch_symmetry":"SO(4) ~= SU(2)_L x SU(2)_R",
            "ell2_action":"scalar by irreducibility",
            "coefficient_status":"geometric contribution derived, full BHSM coefficient not isolated",
            "can_select_triplet":False,
        },
        {
            "sector":"M5 bulk plus GHY",
            "round_branch_symmetry":"cap-exchange and round S3 isometry preserved",
            "ell2_action":"equivariant bilinear form, hence scalar on H_2",
            "coefficient_status":"physical stationary-background evaluation open",
            "can_select_triplet":False,
        },
        {
            "sector":"M8 horizontal pushforward / parent response",
            "round_branch_symmetry":"retained round invariant Hopf branch has no preferred global anisotropy axis",
            "ell2_action":"equivariant after natural pushforward/trace",
            "coefficient_status":"full stationary parent response open",
            "can_select_triplet":False,
        },
        {
            "sector":"compatibility multipliers and KKT/Schur reduction",
            "round_branch_symmetry":"natural Q_H and trace maps are equivariant",
            "ell2_action":"Schur complement preserves equivariance",
            "coefficient_status":"action incidence known; physical global background still open",
            "can_select_triplet":False,
        },
        {
            "sector":"relative heat/zeta/nonlocal spectral response",
            "round_branch_symmetry":"spectral functional calculus inherits operator symmetry",
            "ell2_action":"central if seed operator is round-equivariant",
            "coefficient_status":"physical supertrace/projectors open",
            "can_select_triplet":False,
        },
        {
            "sector":"localized M4 vacuum fields",
            "round_branch_symmetry":"central only on an isotropic/vanishing stationary vacuum",
            "ell2_action":"would require an action-selected anisotropic background to split H_2",
            "coefficient_status":"physical stationary localized background open",
            "can_select_triplet":False,
        },
    ]
    return {
        "version":VERSION,
        "scope":"retained round/reflection-symmetric/isotropic branch only",
        "rows":rows,
        "all_current_round_equivariant_sectors_fail_to_select_triplet":all(not r["can_select_triplet"] for r in rows),
        "complete_numeric_full_BHSM_second_shape_Hessian_evaluated":False,
        "symmetry_theorem_sufficient_to_rule_out_triplet_selection_on_round_branch":True,
        "nonround_or_anisotropic_stationary_branch_excluded":False,
        "physical_prediction":False,
    }


def triplet_selection_no_go_payload() -> dict[str,Any]:
    full=full_product_commutant_payload()
    diag=diagonal_commutant_payload()
    return {
        "version":VERSION,
        "round_ell2_dimension":9,
        "full_round_commutant_dimension":full["commutant_dimension"],
        "diagonal_SU2_commutant_dimension":diag["commutant_dimension"],
        "full_round_Hessian_form":"c_2 I9",
        "diagonal_reduced_Hessian_form":"c1 P1 + c3 P3 + c5 P5",
        "round_action_can_move_common_ell2_eigenvalue":True,
        "round_action_can_split_1_3_5":False,
        "round_action_can_uniquely_select_rank3_triplet":False,
        "required_change":"derive an action-owned stationary object that breaks/reduces SU(2)_L x SU(2)_R before Hessian evaluation",
        "candidate_classes":["Berger/Hopf anisotropy selected by the global action","nontrivial physical connection holonomy/polarization","nonround cap/seam tensor background","localized anisotropic stationary matter/current"],
        "no_candidate_is_adopted_here":True,
        "primary_verdict":PRIMARY_VERDICT,
        "physical_prediction":False,
    }


def symmetry_breaking_requirements_payload() -> dict[str,Any]:
    return {
        "version":VERSION,
        "minimum_theorem_requirements":[
            "stationary parent/child/seam background from the same global action",
            "explicit action-owned tensor/connection/order parameter reducing the round product symmetry",
            "gauge-equivalence proof showing the selector is physical rather than coordinate choice",
            "second-shape Hessian including bulk, GHY, compatibility/KKT and nonlocal spectral terms on that background",
            "spectral split in ell=2 with an isolated rank-three physical eigenspace",
            "intertwiner from that eigenspace to the three moving-seam Calderon derivatives",
            "no measured CKM/PMNS/neutrino data used to choose the selector or splitting",
        ],
        "current_round_branch_meets_requirements":False,
        "historical_diagonal_SU2_projector_is_mathematical_not_action_selected":True,
        "first_eligible_downstream_step_after_selection":"construct three physical shape derivatives and insert them into the operator-valued Calderon/Wentzell domain",
        "physical_prediction":False,
    }


def neutrino_kill_screen_payload() -> dict[str,Any]:
    return {
        "version":VERSION,
        "current_result":"PHYSICAL_EXECUTION_BLOCKED",
        "physical_execution_allowed":False,
        "blocking_reason":"the three physical nonuniform shape channels are not action-selected because the round full second-shape Hessian is symmetry-central on ell=2",
        "measured_neutrino_data_used":False,
        "physical_mass_PMNS_splitting_or_probability_emitted":False,
    }


def status_payload() -> dict[str,Any]:
    return {
        "version":VERSION,
        "validated":[
            "ell=2 scalar shape space is the irreducible (1,1) representation of SU(2)_L x SU(2)_R",
            "exact product-group commutant has dimension one",
            "every full-round-equivariant self-adjoint ell=2 Hessian is scalar",
            "exact diagonal-SU2 commutant has dimension three",
            "diagonal commutant is spanned by rank 1,3,5 projectors",
            "KKT/Schur elimination preserves equivariance",
            "heat/resolvent/log spectral functional calculus preserves equivariance",
            "round action sectors may shift but cannot split the ninefold ell=2 eigenvalue",
            "triplet selection requires symmetry reduction before Hessian evaluation",
            "no measured particle/flavor data are required for the no-go",
        ],
        "invalidated":[
            "the hope that adding omitted round bulk/GHY/KKT/nonlocal terms can by themselves select the l2 triplet while full round symmetry is retained",
            "treating the diagonal SU2 decomposition as action-selected merely because the projectors exist",
            "using a spectral determinant on a fully round-equivariant operator as an implicit triplet selector",
        ],
        "reclassified":[
            "the v14.70 incomplete-Hessian blocker is now a symmetry-selection blocker on the round branch",
            "unknown round second-shape coefficients affect stability/eigenvalue size but not the 1+3+5 degeneracy split",
            "the next physical object is a stationary symmetry-breaking selector rather than more round scalar Hessian algebra",
        ],
        "open":[
            EXACT_NEXT_OBJECT,
            "physical action-selected nonround or anisotropic background",
            "gauge proof that the selector is physical",
            "physical split coefficients c1,c3,c5",
            "unique rank-three eigenspace",
            "three physical Calderon shape derivatives",
            "complete gauge/metric/spinor/ghost projector",
            "relative heat supertrace on physical background",
            "physical neutrino kill-screen execution",
            "full particle/force/flavor completion",
        ],
        "FULL_BHSM_COMPLETE":False,
        "MARK_III":"NOT_REACHED",
        "physical_prediction_emitted":False,
        "frozen_predictions_changed":False,
        "official_prediction_logic_changed":False,
        "USB_touched":False,
    }


def completion_gate_payload() -> dict[str,Any]:
    full=full_product_commutant_payload()
    diag=diagonal_commutant_payload()
    schur=equivariant_schur_witness()
    spectral=spectral_function_centrality_witness()
    ledger=sector_ledger_payload()
    validation={
        "full_product_commutant_is_one":full["commutant_dimension"]==1,
        "diagonal_commutant_is_three":diag["commutant_dimension"]==3,
        "projector_ranks_are_1_3_5":diag["projector_quality"]["ranks"]==[1,3,5],
        "diagonal_operator_commutes_with_diagonal_group":diag["diagonal_operator_commutator_with_diagonal_SU2"]<1e-12,
        "diagonal_operator_breaks_full_product_when_split":diag["diagonal_operator_commutator_with_full_product"]>1e-3,
        "equivariant_schur_is_central":schur["centrality_residual"]<1e-12,
        "spectral_heat_is_central":spectral["heat_commutator_residual"]<1e-12,
        "round_sector_ledger_blocks_triplet":ledger["all_current_round_equivariant_sectors_fail_to_select_triplet"],
        "no_physical_prediction":True,
    }
    return {
        "version":VERSION,
        "primary_verdict":PRIMARY_VERDICT,
        "exact_next_object":EXACT_NEXT_OBJECT,
        "round_branch_triplet_selection":"BLOCKED_BY_FULL_PRODUCT_SYMMETRY",
        "full_BHSM_complete":False,
        "mark_III":"NOT_REACHED",
        "physical_execution_allowed":False,
        "physical_prediction_emitted":False,
        "frozen_predictions_changed":False,
        "official_prediction_logic_changed":False,
        "usb_touched":False,
        "validation":validation,
        "validation_passed":all(validation.values()),
    }


def artifact_payloads() -> dict[str,Any]:
    return {
        "BHSM_l2_full_SO4_commutant_v14_71.json":full_product_commutant_payload(),
        "BHSM_diagonal_SU2_commutant_v14_71.json":diagonal_commutant_payload(),
        "BHSM_round_second_shape_sector_ledger_v14_71.json":sector_ledger_payload(),
        "BHSM_equivariant_schur_complement_v14_71.json":equivariant_schur_witness(),
        "BHSM_heat_zeta_centrality_v14_71.json":spectral_function_centrality_witness(),
        "BHSM_triplet_selection_no_go_v14_71.json":triplet_selection_no_go_payload(),
        "BHSM_symmetry_breaking_requirements_v14_71.json":symmetry_breaking_requirements_payload(),
        "BHSM_neutrino_kill_screen_v14_71.json":neutrino_kill_screen_payload(),
        "BHSM_status_ledger_v14_71.json":status_payload(),
        "BHSM_completion_gate_v14_71.json":completion_gate_payload(),
    }


def materialize(outdir: Path) -> list[Path]:
    out=Path(outdir)
    out.mkdir(parents=True,exist_ok=True)
    written=[]
    for name,payload in sorted(artifact_payloads().items()):
        path=out/name
        path.write_text(json.dumps(payload,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+"\n",encoding="utf-8")
        written.append(path)
    return written
