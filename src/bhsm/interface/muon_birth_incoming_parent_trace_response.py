"""Normalized incoming carrier trace entries with physical P_F left unbound.

The complete signed round-S3 shells of the stored channel rows are represented
in inherited eigenfunction coordinates.  Their diagonal carrier pairings are
enclosed over one shared amplitude family.  This is neither a physical angular
cutoff nor an invariant truncation of the full lower-order fermion operator.
"""

from __future__ import annotations

import ast
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
from typing import Any

import sympy as sp

from bhsm.interface.muon_birth_parametric_carrier_bounds import (
    retained_carrier_bound_inputs, uniform_carrier_majorants,
)
from bhsm.interface.muon_birth_parametric_fermion_seam import fraction_record


RETAINED_SPATIAL_LEVELS = (0, 1, 2, 3)


def _level(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("spatial level must be an exact integer")
    if value < 0:
        raise ValueError("spatial level must be nonnegative")
    return value


def particle_trace_shell_basis(spatial_level: int) -> list[dict[str, Any]]:
    """Label a COMPLETE signed shell, without selecting physical support.

    A four-component field has two Weyl copies of the intrinsic rank-two S3
    spinor bundle. Each copy contains both intrinsic spatial Dirac signs,
    each of multiplicity d_n=(n+1)(n+2).  No further C4 or transfer (u,v)
    multiplicity is applied.  v is a conormal, not another free trace.
    """
    n = _level(spatial_level)
    degeneracy = (n+1)*(n+2)
    rows = []
    for weyl, epsilon in (("L", -1), ("R", 1)):
        for spatial_sign in (1, -1):
            for angular_index in range(degeneracy):
                index = len(rows)
                rows.append(dict(
                    index=index, n=n, weyl=weyl, weyl_hamiltonian_sign=epsilon,
                    spatial_dirac_sign=spatial_sign,
                    angular_degeneracy_index=angular_index,
                    per_spatial_sign_multiplicity=degeneracy,
                    squared_factor_sign=epsilon*spatial_sign,
                    unit_radius_absolute_dirac_eigenvalue=str(Fraction(2*n+3, 2)),
                    internal_sector="charged_lepton", internal_slot=1,
                    internal_Berger_label=[5, 2],
                    internal_family_basis_vector=[0, 1, 0],
                    coordinate_basis_vector={"unit_index": index, "dimension": 4*degeneracy},
                    physical_field_amplitude=None,
                ))
    return rows


def exact_chiral_frame_identity() -> dict[str, Any]:
    """Derive the Weyl/sign bookkeeping from the owned Dirac gamma basis."""
    eye, zero = sp.eye(2), sp.zeros(2)
    pauli = (sp.Matrix([[0, 1], [1, 0]]),
             sp.Matrix([[0, -sp.I], [sp.I, 0]]), sp.diag(1, -1))
    change = sp.BlockMatrix([[eye, eye], [-eye, eye]]).as_explicit()/sp.sqrt(2)
    beta = sp.diag(eye, -eye)
    gamma5 = sp.BlockMatrix([[zero, eye], [eye, zero]]).as_explicit()
    alpha = [sp.BlockMatrix([[zero, s], [s, zero]]).as_explicit() for s in pauli]
    targets = [sp.diag(-s, s) for s in pauli]
    zero4 = sp.zeros(4)
    residuals = dict(
        unitary=sp.simplify(change.H*change-sp.eye(4)) == zero4,
        chiral_grading=sp.simplify(change.H*gamma5*change-sp.diag(-eye, eye)) == zero4,
        beta=sp.simplify(change.H*beta*change-sp.BlockMatrix([[zero, eye], [eye, zero]]).as_explicit()) == zero4,
        spatial_alpha=[sp.simplify(change.H*a*change-target) == zero4
                       for a, target in zip(alpha, targets)],
    )
    return dict(
        classification="EXACT_RETAINED_GAMMA_FRAME_IDENTITY",
        change_of_basis=str(change), residuals=residuals,
        validation_passed=all(all(v) if isinstance(v, list) else v for v in residuals.values()),
        massless_spatial_Hamiltonian="H_car=diag(-D_S3,+D_S3)/R4",
        squared_factor="A_(b,sigma,n)=partial_tau+epsilon_b*sigma*(n+3/2)*exp(-x)",
        spin_frame_is_not_a_covariance_or_field_state=True,
    )


def normalized_trace_representation_contract() -> dict[str, Any]:
    """State the all-level Hilbert/charge representation, without a cutoff."""
    return dict(
        classification="INHERITED_NORMALIZED_CARRIER_TRACE_REPRESENTATION",
        carrier_space="direct_sum_(n>=0,b=L/R,sigma=+/-,a=1..d_n) C phi_(n,sigma,a) tensor e_b tensor e_mu",
        spatial_eigenvalue="sigma*(n+3/2)/R4; d_n=(n+1)(n+2) PER spatial sign",
        shell_particle_dimension="4*d_n=4*(n+1)*(n+2)",
        shell_self_dual_dimension="8*d_n",
        angular_eigenspinors_already_include_two_spin_components=True,
        pointwise_charged_Dirac_fiber_dimension=4,
        pointwise_muon_family_rank=1,
        pointwise_dimension_is_full_angular_trace_dimension=False,
        normal_pullback="u_eta=N J^(-1/2) sin(f_eta); integral ds J|u_eta|^2=1; two-sheet Yukawa overlap=1",
        normalized_angular_pairing="<phi_(n,sigma,a),phi_(m,tau,c)>_unit_S3=delta_nm delta_sigma,tau delta_ac",
        physical_round_slice_isometry="psi_physical=R4^(-3/2)*psi_unit; dmu_slice=R4^3 dOmega; no new residue",
        Gram="identity in inherited orthonormal coefficient coordinates; positive Hilbert pairing",
        scalar_identity_scope="One M_(chi,n) multiplies each normalized degenerate carrier channel copy; all copies share the same incoming amplitude lambda",
        operator_action_all_levels="(M_car q)_(n,b,sigma,a)=M_(epsilon_b*sigma,n)(lambda,z)*q_(n,b,sigma,a)",
        all_levels_coercivity_bound_evaluated=False,
        arbitrary_level_bound_rule="Use the retained |W_n|<=S_n=(n+3/2)*sup(exp(-x_C1)); rational companion needs 4*S_n*a_upper*lambda_star^2<1. No finite common S over all n is asserted.",
        internal_Berger_label_is_spatial_level=False,
        physical_angular_support_or_cutoff=None,
        four_retained_rows_are_a_physical_truncation=False,
        canonical_one_seam_reference="External E0 birth trace zero after differentiation; internal terminal M_f=M11 remains nonzero",
        old_closed_E0_birth_graph_reintroduced=False,
        positive_carrier_equals_complete_graded_parent_slot=False,
        statistics="AE4 supertrace fermion sign is inherited separately; it is not a negative Hilbert Gram or an adjustable coefficient",
    )


def _self_dual_representation(particle_dimension: int) -> dict[str, Any]:
    """Coordinate maps only: no covariance or parent statistics lift."""
    return dict(
        particle_dimension=particle_dimension, doubled_dimension=2*particle_dimension,
        basis_order="particle inherited shell basis, then its compatible charge-conjugate basis",
        Gram={"dimension": 2*particle_dimension, "diagonal": "1", "off_diagonal": "0"},
        conjugation="Gamma=(0 I;I 0) K in the compatible particle/conjugate coefficient bases",
        Gamma_matrix_blocks=[["0", "I"], ["I", "0"]],
        charge_grading="diag(I,-I)", physical_EM_charge="diag(-I,+I)",
        doubled_family_projector="I on this inherited muon family-restricted coefficient space",
        full_parent_conjugate_statistics_lift=None,
        covariance=None, representation_selects_covariance=False,
    )


def retained_carrier_shell_enclosure(root: str | Path, spatial_level: int) -> dict[str, Any]:
    """Enclose all pairings of one stored shell over the shared family.

    Only the four already stored |mu| rows may be numerically extracted.
    Diagonal records denote repeated TWO channel functions, not independent
    choices in a box.  Off-diagonal zeros apply to the separated carrier only.
    """
    n = _level(spatial_level)
    if n not in RETAINED_SPATIAL_LEVELS:
        raise ValueError("No stored numerical carrier bound for this spatial level")
    inputs = retained_carrier_bound_inputs(
        root, absolute_unit_radius_eigenvalue=Fraction(2*n+3, 2), kappa_squared=Fraction(1))
    majorants = uniform_carrier_majorants(**{
        name: Fraction(value) for name, value in inputs["parameters"].items()
    })
    rows = particle_trace_shell_basis(n)
    dimension = len(rows)
    lower, upper = majorants["scaled_Mf_lower"], majorants["scaled_Mf_upper"]
    diagonal = [dict(
        row_index=row["index"], column_index=row["index"],
        shared_channel_function=f"lambda^2*M_(chi={row['squared_factor_sign']},n={n})(lambda,z=-1)",
        lower=str(lower), upper=str(upper),
        classification="UNIFORM_SCALED_INCOMING_CARRIER_PAIRING_ENCLOSURE",
    ) for row in rows]
    result = dict(
        n=n, absolute_unit_radius_eigenvalue=str(Fraction(2*n+3, 2)),
        particle_dimension=dimension, self_dual_dimension=2*dimension,
        per_spatial_sign_multiplicity=(n+1)*(n+2),
        each_squared_factor_sign_multiplicity=dimension//2,
        particle_basis=rows,
        particle_Gram={"dimension": dimension, "diagonal": "1", "off_diagonal": "0"},
        self_dual_representation=_self_dual_representation(dimension),
        diagonal_pairings=diagonal, diagonal_pairing_count=dimension,
        ordered_offdiagonal_pairing_count=dimension*(dimension-1),
        exact_offdiagonal_rule="<e_i,lambda^2*M_car e_j>=0 for i!=j in the inherited separated round-carrier eigenbasis",
        exact_offdiagonal_zero="0",
        zero_provenance="tau-independent orthonormal spatial eigenbasis; W_(b,sigma,n)(tau) is scalar on every degeneracy/family copy; channel transfer and E0 Dirichlet restriction preserve each copy",
        offdiagonal_zeros_are_full_LR_or_PF_zeros=False,
        scaled_diagonal_enclosure={"lower": fraction_record(lower), "upper": fraction_record(upper)},
        operator_Loewner_enclosure="lower*I <= lambda^2*M_car <= upper*I on this complete carrier shell",
        unscaled_uniform_upper_bound=None,
        same_shared_lambda_for_all_diagonal_entries=True,
        physical_lambda_or_duration_selected=False,
        spectral_scope={"z": "-1", "kappa_squared": "1", "probe_is_physical_momentum": False},
        retained_inputs=inputs,
        physical_full_PF_order0=None,
        full_LR_shell_invariance_established=False,
    )
    if n == 0:
        result["explicit_scaled_8_by_8_entry_enclosures"] = [
            [{"lower": str(lower), "upper": str(upper)} if i == j
             else {"exact": "0", "classification": "EXACT_CARRIER_ZERO"}
             for j in range(dimension)] for i in range(dimension)
        ]
        doubled = result["self_dual_representation"]
        doubled["explicit_basis_rows"] = [
            {"index": i, "copy": "particle" if i < dimension else "conjugate",
             "particle_basis_index": i % dimension, "physical_field_amplitude": None}
            for i in range(2*dimension)
        ]
        doubled["explicit_Gram"] = [
            [int(i == j) for j in range(2*dimension)] for i in range(2*dimension)
        ]
        doubled["explicit_Gamma_linear_matrix"] = [
            [int(j == (i+dimension) % (2*dimension)) for j in range(2*dimension)]
            for i in range(2*dimension)
        ]
        doubled["explicit_charge_grading"] = [
            [int(i == j)*(1 if i < dimension else -1) for j in range(2*dimension)]
            for i in range(2*dimension)
        ]
        doubled["explicit_EM_charge"] = [
            [-entry for entry in row] for row in doubled["explicit_charge_grading"]
        ]
    return result


def parent_consumer_sufficiency_contract() -> dict[str, Any]:
    """Describe the existing full-matrix consumer and legitimate reductions."""
    return dict(
        callback="ae4_event_response_jet_integration.solve_retarded_event_kkt_jet",
        required_value="parent_jet[0]=P_F=H_pp,F, Hermitian n by n in inherited normalized common-domain coordinates",
        dimension_is_inferred_from_supplied_physical_PF=True,
        fixed_physical_finite_angular_trace_dimension=None,
        coupling_shape="n by m", retarded_child_shape="m by m", response_shape="r by n",
        source_shape="n", target_shape="r",
        effective_parent="H_eff=P_F-B_F (L_F^R)^(-1) B_F^dagger",
        consumed_parent_traction="Pi_parent=P_F q_F",
        one_scalar_p_dagger_R_r_supplies_full_parent_matrix=False,
        scalar_contraction_scope="A source/readout contraction can close its own adjoint observable; it does not provide the full KKT operator action or all parent tractions",
        exact_reduction_conditions=[
            "Q preserves the full action/domain and reduces P_F: [P_F,Q]=0",
            "Q_child reduces L_F^R and Q B_F=B_F Q_child",
            "C_F Q=Q_response C_F and J_F=Q J_F; d_F=Q_response d_F",
            "All relevant explicit-source/readout/domain contacts respect the same subspace",
        ],
        reducing_subspace_consequence="The full KKT system splits and the Q block returns the full solution/tractions on Ran(Q)",
        nonreducing_subspace_elimination={
            "first_eliminate_child": "H=P_F-B_F(L_F^R)^(-1)B_F^dagger; H need not be Hermitian",
            "kept_KKT": "K0=[[H_KK,C_K^dagger],[C_K,0]]",
            "complement_couplings": "X=[H_KQ;C_Q], Y=[H_QK,C_Q^dagger]; Y=X^dagger only if H is Hermitian",
            "exact_complement_Schur": "K_red=K0-X H_QQ^(-1) Y",
            "exact_reduced_source": "rhs_red=[-J_K;d]+X H_QQ^(-1) J_Q",
            "induced_multiplier_block": "-C_Q H_QQ^(-1) C_Q^dagger",
            "zero_multiplier_block_callback_accepts_general_reduction": False,
            "callback_reuse_condition": "Prove the induced multiplier block and all relevant reactions vanish or provide an equivalent retained system; compression alone does not meet the existing callback",
        },
        already_owned_reductions={
            "carrier_spatial_eigenspaces": "exact for the separated round carrier",
            "muon_internal_family": "fixed family-compatible transport/reset and diagonal Y_l preserve Pi_mu; fixed family-central HS/gauge vertices do likewise",
            "full_lower_order_spatial_shell": None,
            "full_sourced_KKT_reducing_subspace": None,
        },
        no_basis_choice_selects_C_or_lambda=True,
        statistical_lift_of_positive_carrier_to_full_parent_slot=None,
        positive_carrier_is_complete_graded_PF=False,
        consumed_parent_status={"argument": "parent_jet", "operand": "P_F", "order": 0,
                                "value": None, "classification": "UNEVALUATED_FULL_ACTION_PARENT_SLOT"},
        current_unresolved_full_minus_carrier={
            "order0": "Actual incoming LR/gauge/HS/internal coefficients and their same-domain stationary boundary response; all required response contacts are retained",
            "incoming_LR_Euler_coefficient": "M_mu,C1=y_mu h_C1, with full chiral/gauge tensor structure; not the current-C2 vacuum mass",
            "primal_scalar_source": "F_H(H_C1,Psi_C1,A_C1,g_C1)=0 with the existing intrinsic action, retained fermion source and causal/constraint/trace data; that source is not defaulted to zero",
            "same_domain_response_pairings": "R_ij=<E_0,L e_i,(L_full-L_car)E_full,R e_j> when the inherited common-domain realization is verified",
            "unknown_pairing_values": None,
            "actual_squared_carrier_embedding": None,
            "lower_order_offdiagonal_entries": None,
            "missing_values_replaced_with_zero": False,
        },
    )


def _source_record(root: Path, path: str, symbols: tuple[str, ...] = ()) -> dict[str, Any]:
    raw = (root/path).read_bytes()
    record = dict(path=path, raw_sha256=sha256(raw).hexdigest(), bytes=len(raw))
    if symbols:
        nodes = {node.name: node for node in ast.parse(raw.decode("utf-8-sig")).body
                 if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
        record["symbols"] = [dict(symbol=name, start_line=nodes[name].lineno,
                                  end_line=nodes[name].end_lineno) for name in symbols]
    return record


def incoming_parent_trace_packet(root: str | Path) -> dict[str, Any]:
    """Materialize all complete shells of the four retained channel rows."""
    base = Path(root)
    shells = [retained_carrier_shell_enclosure(base, n) for n in RETAINED_SPATIAL_LEVELS]
    dimension = sum(shell["particle_dimension"] for shell in shells)
    domains = {shell["retained_inputs"]["parameter_domain"] for shell in shells}
    duration_parameters = [tuple(shell["retained_inputs"]["parameters"][key]
                                 for key in ("a_lower", "a_upper", "lambda_upper"))
                           for shell in shells]
    if len(domains) != 1 or len(set(duration_parameters)) != 1:
        raise ValueError("Carrier shells must share one retained amplitude/duration family")
    source_specs = [
        ("src/bhsm/interface/completion/foundational_dirac_spin_glue_v14_45.py",
         ("dirac_gamma_matrices", "zero_mode_pullback_payload")),
        ("src/bhsm/interface/completion/collective_dirac_vacuum_polarization_v14_42.py",
         ("round_s3_dirac_multiplicity",)),
        ("src/bhsm/interface/ae31_c2_calderon_principal_symbol.py", ("family_dirac_projectors",)),
        ("src/bhsm/interface/aether_forward_channel_transfer.py",
         ("product_dirac_channel_transfer_generator", "restrict_two_boundary_weyl_to_dirichlet_birth_jets")),
        ("src/bhsm/interface/ae4_event_response_jet_integration.py", ("solve_retarded_event_kkt_jet",)),
        ("src/bhsm/interface/ae4_c2_stratified_event_flux_assembly.py", ("assemble_stratified_direct_sum",)),
        ("src/bhsm/interface/ae3_reciprocal_join_localization.py", ("family_fiber_transport_certificate",)),
        ("src/bhsm/interface/muon_birth_parametric_carrier_bounds.py",
         ("retained_carrier_bound_inputs", "uniform_carrier_majorants")),
        ("artifacts/flagship_integration/BHSM_N12_FORWARD_FIXED_CHANNEL_TRANSFER.json", ()),
        ("theory/n12_gate7_external_birth_source_role_supersession.md", ()),
    ]
    records = [_source_record(base, path, symbols) for path, symbols in source_specs]
    for record in shells[0]["retained_inputs"]["source_records"]:
        records.append(record)
    consumer = parent_consumer_sufficiency_contract()
    return dict(
        classification="INCOMING_C1_COMPLETE_RETAINED_CARRIER_SHELL_PAIRINGS_ENCLOSED_FULL_PF_UNEVALUATED",
        scope="C1/branch23/E1-minus; retained round separated incoming carrier at z=-1",
        normalized_basis_contract=normalized_trace_representation_contract(),
        exact_chiral_frame=exact_chiral_frame_identity(),
        shell_counts={"retained_spatial_levels": list(RETAINED_SPATIAL_LEVELS),
                      "particle_dimensions": [s["particle_dimension"] for s in shells],
                      "particle_dimension_total": dimension, "self_dual_dimension_total": 2*dimension,
                      "diagonal_pairings_enclosed": dimension,
                      "exact_ordered_offdiagonal_pairings": dimension*(dimension-1),
                      "exact_cross_shell_pairings": dimension*dimension-sum(s["particle_dimension"]**2 for s in shells)},
        shells=shells,
        whole_retained_sum_Gram={"dimension": dimension, "diagonal": "1", "off_diagonal": "0"},
        cross_shell_offdiagonal_rule="All separated-carrier pairings between distinct shells are exactly zero by the inherited orthogonal spatial eigenspace decomposition",
        one_shared_amplitude_domain=next(iter(domains)),
        physical_amplitude_selected=False, physical_angular_cutoff_selected=False,
        covariance_selected=False, full_LR_offdiagonal_zeros_asserted=False,
        point_KKT_solver_called=False, old_producers_recomputed=False,
        source_records=records,
        consumer_sufficiency=consumer,
        consumed_parent_status=consumer["consumed_parent_status"],
        complete_physical_PF_order0=None,
        a_mu=None, g_mu=None,
    )


__all__ = ["incoming_parent_trace_packet", "particle_trace_shell_basis",
           "retained_carrier_shell_enclosure", "normalized_trace_representation_contract",
           "exact_chiral_frame_identity", "parent_consumer_sufficiency_contract"]
