"""Canonical AE2/Gate-7 semantic registries and regression guardrails."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Iterable, Mapping


ACTION_VERSION = "BHSM-AE-2.0.0"
ONTOLOGY_VERSION = "BHSM-AE2-ONTOLOGY-1.3.0"
REQUIRED_RECORD_FIELDS = (
    "canonical_id",
    "formula",
    "mathematical_class",
    "semantic_layer",
    "physical_meaning",
    "action_version",
    "ontology_version",
    "domain",
    "provenance",
    "equivalent_forms",
    "dimensions",
    "current_status",
    "source_weighting_required",
    "observable_status",
    "frozen_output_status",
    "superseded_meanings",
    "forbidden_interpretations",
    "downstream_consumers",
    "artifact_hashes",
    "tests",
)


def record(
    canonical_id: str,
    formula: str,
    mathematical_class: str,
    semantic_layer: str,
    physical_meaning: str,
    domain: str,
    provenance: Iterable[str],
    *,
    equivalent_forms: Iterable[str] = (),
    dimensions: str = "DIMENSIONLESS_OR_OPERATOR_TYPED",
    current_status: str = "CURRENT",
    source_weighting_required: bool = False,
    observable_status: str = "NOT_AN_OBSERVABLE",
    frozen_output_status: str = "NOT_FROZEN_OUTPUT",
    superseded_meanings: Iterable[str] = (),
    forbidden_interpretations: Iterable[str] = (),
    downstream_consumers: Iterable[str] = (),
    artifact_hashes: Mapping[str, str] | None = None,
    tests: Iterable[str] = ("test_required_fields",),
) -> dict[str, Any]:
    """Return a complete normalized formula/object record."""

    return {
        "canonical_id": canonical_id,
        "formula": formula,
        "mathematical_class": mathematical_class,
        "semantic_layer": semantic_layer,
        "physical_meaning": physical_meaning,
        "action_version": ACTION_VERSION,
        "ontology_version": ONTOLOGY_VERSION,
        "domain": domain,
        "provenance": list(provenance),
        "equivalent_forms": list(equivalent_forms),
        "dimensions": dimensions,
        "current_status": current_status,
        "source_weighting_required": source_weighting_required,
        "observable_status": observable_status,
        "frozen_output_status": frozen_output_status,
        "superseded_meanings": list(superseded_meanings),
        "forbidden_interpretations": list(forbidden_interpretations),
        "downstream_consumers": list(downstream_consumers),
        "artifact_hashes": dict(artifact_hashes or {}),
        "tests": list(tests),
    }


def _with_hashes(rows: Iterable[dict[str, Any]], hashes: Mapping[str, str]) -> list[dict[str, Any]]:
    output = []
    for row in rows:
        copy = deepcopy(row)
        copy["artifact_hashes"] = {
            source: hashes[source] for source in copy["provenance"] if source in hashes
        }
        output.append(copy)
    return output


def _basis() -> list[dict[str, Any]]:
    p_ae2 = "artifacts/action_extension/BHSM_ACTION_AE2_GLOBAL_SPIN_RESET_ACTION.json"
    p_proper = "artifacts/flagship_integration/BHSM_N12_FORWARD_PROPER_TIME_FORM_OWNERSHIP.json"
    p_fixed = "artifacts/flagship_integration/BHSM_N12_FORWARD_FIXED_CHANNEL_TRANSFER.json"
    p_weyl = "artifacts/flagship_integration/BHSM_N12_FORWARD_GAUGE_WEYL_READOUT_FAMILY.json"
    p_seam = "artifacts/flagship_integration/BHSM_N12_EVENT_NORMAL_TWO_SIDED_SEAM_CORRECTION.json"
    p_seam_enclosure = "artifacts/flagship_integration/BHSM_N12_AE2_COVARIANT_SEAM_ENCLOSURE_Z_MINUS_1.json"
    p_seam_family = "artifacts/flagship_integration/BHSM_N12_AE2_NEGATIVE_AXIS_SEAM_FAMILY.json"
    p_projected_saddle = "artifacts/flagship_integration/BHSM_N12_CONSTRAINT_PROJECTED_REPLACEMENT_SADDLE.json"
    p_parametric_oracle = "artifacts/flagship_integration/BHSM_N12_PARAMETRIC_RESET_FIBER_EXTERIOR_ORACLE_THEOREM.json"
    p_radius_jet = "artifacts/flagship_integration/BHSM_N12_RESET_FIBER_RADIUS_JET_AND_SCALE_CENTER_AUDIT.json"
    p_executable_oracle = "artifacts/flagship_integration/BHSM_N12_PARAMETRIC_EXTERIOR_ORACLE_EXECUTABLE_INTERFACE.json"
    p_w7_descriptor = "artifacts/flagship_integration/BHSM_N12_WEIGHT_SEVEN_TRANSVERSE_DESCRIPTOR.json"
    p_w5_modulation = "artifacts/flagship_integration/BHSM_N12_WEIGHT_FIVE_CENTER_MODULATION.json"
    p_w5_mp_audit = "artifacts/flagship_integration/BHSM_N12_WEIGHT_FIVE_MULTIPRECISION_NONPROMOTION.json"
    p_w5_analytic = "artifacts/flagship_integration/BHSM_N12_ANALYTIC_LOCAL_BLOCK_CENTER_LIFT.json"
    p_w5_interval = "artifacts/flagship_integration/BHSM_N12_INTERVAL_WEIGHT_FIVE_CENTER_LIFT.json"
    p_full_asymptotic = "artifacts/flagship_integration/BHSM_N12_FULL_RETAINED_ASYMPTOTIC_BRANCH.json"
    p_exact_field = "artifacts/flagship_integration/BHSM_N12_C2_EXACT_FIXED_S_FIELD_ORACLE.json"
    p_launch_chart = "artifacts/flagship_integration/BHSM_N12_C2_RESET_GENERATED_LAUNCH_CHART.json"
    p_launch_adjoint = "artifacts/flagship_integration/BHSM_N12_C2_RESET_LAUNCH_ADJOINT_INTERFACE.json"
    p_fixed_seed_owner = "artifacts/flagship_integration/BHSM_N12_C2_FIXED_SEED_UPSTREAM_FORCE_OWNER.json"
    p_tail_support = "artifacts/flagship_integration/BHSM_N12_GATE7_MAXIMAL_TAIL_SUPPORT_REDUCTION.json"
    p_flow_tail = "artifacts/flagship_integration/BHSM_N12_GATE7_OUTGOING_FLOW_TAIL_CLOSURE.json"
    p_seed_ward_gauge = "artifacts/flagship_integration/BHSM_N12_GATE7_SEED_IMAGE_WARD_GAUGE_AUDIT.json"
    p_rank72_relative_form = "artifacts/flagship_integration/BHSM_N12_GATE7_RANK72_RELATIVE_FORM_TAIL.json"
    p_rank72_route_adjudication = "artifacts/flagship_integration/BHSM_N12_GATE7_RANK72_MAXIMAL_TAIL_ROUTE_ADJUDICATION.json"
    p_ae2_boundary_hamiltonian = "artifacts/flagship_integration/BHSM_N12_AE2_CHILD_BOUNDARY_HAMILTONIAN_NON_SUPERSESSION.json"
    p_nhim_rank72_relative_tail = "artifacts/flagship_integration/BHSM_N12_GATE7_NHIM_RANK72_RELATIVE_TAIL_THEOREM.json"
    p_parametric_base = "artifacts/flagship_integration/BHSM_N12_C2_1222_PARAMETRIC_BASE_FAMILY.json"
    p_signed_adjoint = "artifacts/flagship_integration/BHSM_N12_C2_1222_SIGNED_ADJOINT_ASSEMBLY.json"
    p_duration_incidence = "artifacts/flagship_integration/BHSM_N12_C2_SIGNED_DURATION_INCIDENCE_OWNER.json"
    p_ddelta_transport = "artifacts/flagship_integration/BHSM_N12_C2_SIGNED_DDELTA_SEED_TRANSPORT_AUDIT.json"
    p_ddelta_row = "artifacts/flagship_integration/BHSM_N12_C2_DIRECT_DDELTA_ROW_RECONNAISSANCE.json"
    p_reduced_row = "artifacts/flagship_integration/BHSM_N12_C2_FULLY_REDUCED_SIGNED_ROW_CERTIFICATE.json"
    p_suppressed_row = "artifacts/flagship_integration/BHSM_N12_C2_SUPPRESSED_HARD_RESPONSE_ROW_CERTIFICATE.json"
    p_core_audit = "artifacts/flagship_integration/BHSM_N12_CORE_TRANSMITTED_PHYSICAL_MANIFOLD_AUDIT.json"
    p_e1 = "artifacts/flagship_integration/BHSM_N12_FORWARD_E1_SOURCE_MEASURE_CRITERION.json"
    p_nf = "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_NONFERMION_THRESHOLD_MARGIN.json"
    p_fac = "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_COMPACT_SOURCE_DINI_CLOSURE.json"
    return [
        record(
            "ACTION_VERSION_TUPLE",
            "A_v=(C_v,S_v,D_v,B_v,O_v)",
            "VERSIONED_PHYSICAL_THEORY_TUPLE",
            "BHSM_ONTOLOGY",
            "A physical action version includes ontology, action, domains, boundary graphs, and observable maps.",
            "BHSM action-version space",
            [p_ae2],
            downstream_consumers=["AE2_GLOBAL_DOMAIN", "CURRENT_GATE7_DAG"],
            forbidden_interpretations=["Same bulk integrand implies same physical theory."],
        ),
        record(
            "QUOTIENT_RADIUS",
            "R4=A*B/sqrt(A^2+B^2)",
            "GEOMETRIC_QUOTIENT",
            "MATHEMATICAL_OBJECT",
            "Retained Berger-Hopf quotient radius.",
            "A>0, B>0",
            [p_proper],
            dimensions="LENGTH",
            downstream_consumers=["LOG_RADIUS"],
        ),
        record(
            "LOG_RADIUS",
            "x(tau)=log(R4(tau))",
            "CANONICAL_HISTORY_COORDINATE",
            "BHSM_ONTOLOGY",
            "The single current scalar history coefficient after proper-time reduction.",
            "maximal regular forward history with R4>0",
            [p_proper],
            equivalent_forms=["R4^-1=exp(-x)", "R4^-2=exp(-2*x)"],
            downstream_consumers=["FIXED_CHANNEL_OPERATOR", "ACTION_VERTEX"],
        ),
        record(
            "PROPER_TIME",
            "d_tau=N_boundary*dt, N_boundary>0, dt>0",
            "ORIENTED_TIME_REPARAMETRIZATION",
            "BHSM_ONTOLOGY",
            "One positive physical time orientation.",
            "positive-lapse regular forward domain",
            [p_proper],
            dimensions="TIME",
            forbidden_interpretations=["Formal reflection is a second physical time."],
            downstream_consumers=["TEMPORAL_LAPLACIAN", "FIXED_CHANNEL_OPERATOR"],
        ),
        record(
            "TEMPORAL_LAPLACIAN",
            "Delta_tau=D_tau^dagger*D_tau",
            "FACTORIZED_NONNEGATIVE_OPERATOR",
            "MATHEMATICAL_OBJECT",
            "Canonical temporal second-order operator; not independent of D_tau.",
            "AE2 physical operator domain",
            [p_proper],
            downstream_consumers=["FIXED_CHANNEL_OPERATOR"],
        ),
        record(
            "FIXED_CHANNEL_OPERATOR",
            "mathcal_K_C-z=-D_tau^2*I+V(x(tau))-z*I",
            "FIXED_SPATIAL_CHANNEL_OPERATOR",
            "MATHEMATICAL_OBJECT",
            "Nonperiodic forward source operator on fixed round-spatial eigenspaces.",
            "AE2 glued birth domain and maximal forward far-end domain",
            [p_fixed, p_weyl],
            equivalent_forms=["2x2 transfer system", "Riccati equation", "Weyl admittance", "Mobius transfer"],
            downstream_consumers=["RESOLVENT", "WEYL_MAP", "SOURCE_RESPONSE"],
            forbidden_interpretations=["Generic moving operator-valued spatial history."],
        ),
        record(
            "NEUTRAL_SPECTRAL_PARAMETER",
            "z in C\\sigma(mathcal_K_C)",
            "RESOLVENT_PARAMETER",
            "MATHEMATICAL_OBJECT",
            "Neutral spectral parameter with no action-owned momentum interpretation.",
            "resolvent set of mathcal_K_C",
            [p_weyl],
            forbidden_interpretations=["z=p^2", "periodic S1 Fourier readout"],
            downstream_consumers=["RESOLVENT", "WEYL_MAP"],
        ),
        record(
            "RESOLVENT",
            "script_R_C(z)=(mathcal_K_C-z)^(-1)",
            "OPERATOR_RESOLVENT",
            "MATHEMATICAL_OBJECT",
            "Physical AE2 forward resolvent.",
            "z in resolvent set",
            [p_weyl],
            equivalent_forms=["Schur-compressed core resolvent with Weyl/Calderon exterior response"],
            downstream_consumers=["SOURCE_RESPONSE", "E1_FIRST_VARIATION"],
        ),
        record(
            "WEYL_MAP",
            "M_C^Weyl(z)*a=Gamma1_birth(gamma_C(z)*a)",
            "BOUNDARY_WEYL_CALDERON_MAP",
            "MATHEMATICAL_OBJECT",
            "Exterior response pulled to the AE2 birth interface.",
            "fixed channel maximal forward domain",
            [p_weyl, p_fixed],
            equivalent_forms=["channel admittance m_j(z)", "Mobius-pulled far-end admittance"],
            downstream_consumers=["SOURCE_RESPONSE", "ZERO_SOURCE_FORCE"],
        ),
        record(
            "AE2_SEAM_OPERATOR",
            "S_AE2(z)=M_event(z)+U_R^dagger*M_child(z)*U_R+W_phys",
            "TWO_SIDED_CALDERON_WENTZELL_SEAM",
            "MATHEMATICAL_OBJECT",
            "Physical AE2 event-child response; neither arm may be omitted from the force domain.",
            "finite encapsulation event glued immediately to child decay/evolution",
            [p_ae2, p_weyl, p_seam, p_seam_enclosure, p_seam_family],
            current_status="BROADLY_ENCLOSED_FULL_NEGATIVE_AXIS_ACTUAL_TRACE_OPEN",
            equivalent_forms=["B_event=U_R^dagger*M_child*U_R+W_phys after child-arm elimination"],
            forbidden_interpretations=["M(0,z)=W_phys alone is the physical AE2 seam datum", "W_phys=0 implies zero child response"],
            downstream_consumers=["SOURCE_RESPONSE", "ZERO_SOURCE_FORCE"],
        ),
        record(
            "SOURCE_RESPONSE",
            "H_ij(z)=<a_i,script_R_C(z)a_j>+H_ij^contact(z)",
            "PAIR_PLUS_CONTACT_RESPONSE",
            "OBSERVABLE_REPRESENTATION",
            "Action-weighted pair plus retained contact response; not a bare eigenvalue.",
            "AE2 source domain",
            [p_weyl, p_e1],
            equivalent_forms=["heat Frechet/Duhamel representation"],
            source_weighting_required=True,
            observable_status="PRE_OBSERVABLE_REQUIRES_SCALAR_MAP",
            downstream_consumers=["E1_FIRST_VARIATION", "PAIR_CONTACT_HESSIAN"],
        ),
        record(
            "E1_FIRST_VARIATION",
            "E1=D_Phi Gamma_Q[deltaPhi]",
            "SOURCE_CONTRACTED_FIRST_VARIATION",
            "BHSM_ONTOLOGY",
            "First physical source/geometry variation, not an absolute infinite-volume determinant.",
            "zero-source AE2 maximal forward reference history",
            [p_e1],
            source_weighting_required=True,
            downstream_consumers=["ZERO_SOURCE_FORCE", "SAME_ACTION_SADDLE"],
            forbidden_interpretations=["absolute determinant is required", "unweighted density is the E1 measure"],
        ),
        record(
            "CONSTRAINT_PROJECTED_REPLACEMENT_FORCE",
            "N_phys^dagger*q_rep=0, q_rep=D_Gamma_heat-D_Gamma_SM_zeta, range(N_phys)=ker(D_C)/G_exact with the physical common-scale center retained",
            "CONSTRAINT_TANGENT_STATIONARITY_CRITERION",
            "MATHEMATICAL_OBJECT",
            "The same-action replacement force must vanish on the constraint tangent after exact gauge and whole-system time equivalences; the common-scale center remains physical, and a constraint-normal component is a KKT-multiplier shift.",
            "finite event-child constraint surface at the zero-source replacement saddle",
            [p_projected_saddle],
            current_status="DERIVED_CRITERION_ACTUAL_PROJECTED_FORCE_AND_JOINT_SADDLE_OPEN",
            equivalent_forms=["q_rep+D_C^dagger*(lambda_rep-lambda_class)=0 before the retained symmetry quotient"],
            downstream_consumers=["G7_08_FORCE", "G7_09_SADDLE"],
            forbidden_interpretations=["ambient q_rep=0 is necessary", "choose a reset-fiber representative by hand", "geometry KKT Hessian is the pair-plus-contact source Hessian"],
        ),
        record(
            "RESET_FIBER_RADIUS_CAUCHY_JET",
            "A(delta_y)=(delta_log_R4,delta_D_tau_log_R4), rank(A|ker(D_C))=2 and rank after any one time quotient is at least 1",
            "QUOTIENT_ROBUST_GEOMETRY_JET",
            "MATHEMATICAL_OBJECT",
            "At least one fixed-channel coefficient-history direction survives the retained one-dimensional whole-system time quotient; common scale is a physical modulation center, not an exact full-action gauge.",
            "certified fixed-event complete-child reset tangent",
            [p_radius_jet],
            current_status="DERIVED_PARAMETRIC_EXTERIOR_ORACLE_STILL_OPEN",
            downstream_consumers=["PARAMETRIC_RESET_FIBER_EXTERIOR_ORACLE", "G7_08_FORCE"],
            forbidden_interpretations=["time translation removes the whole radius history jet", "common scale is an exact gauge of the complete retained action", "the leading weight-seven center may be deleted from the replacement saddle"],
        ),
        record(
            "FINITE_STRATUM_WEYL_JET_SOLVER",
            "P_ii X=P_ib, P_ii X'=K_ib'-K_ii'X, P_ii X''=K_ib''-K_ii''X-2K_ii'X'",
            "INVERSE_FREE_SCHUR_WEYL_JET_SOLVER",
            "MATHEMATICAL_OBJECT",
            "Stable block-covariant Weyl value and first/second geometry-jet evaluation once the action-owned finite-stratum operator family is supplied.",
            "fixed regular finite endpoint or canonical-stop stratum with coercive negative probe",
            [p_executable_oracle],
            current_status="DERIVED_ACTUAL_PARAMETRIC_FINITE_STRATUM_DATA_OPEN",
            downstream_consumers=["PARAMETRIC_RESET_FIBER_EXTERIOR_ORACLE", "G7_08_FORCE", "G7_09_SADDLE"],
            forbidden_interpretations=["the two-chord validation cutoff is a physical force endpoint", "an explicit matrix inverse is required", "solver availability supplies missing action data"],
        ),
        record(
            "PARAMETRIC_RESET_FIBER_EXTERIOR_ORACLE",
            "xi -> (M_C(z;xi),D_xi*M_C(z;xi),D_xi^2*M_C(z;xi)) on each fixed regular finite endpoint stratum of mathfrak_C/G_exact with common scale retained",
            "STRATIFIED_OPERATOR_FAMILY_AND_GEOMETRY_JET",
            "MATHEMATICAL_OBJECT",
            "The action-owned exterior value and two quotient-geometry jets needed to evaluate the replacement force and joint saddle without choosing a reset member.",
            "regular finite completed-encapsulation or canonical-stop strata of the physical reset quotient",
            [p_parametric_oracle],
            current_status="REGULARITY_THEOREM_DERIVED_ACTUAL_PARAMETRIC_ORACLE_OR_FIBER_INVARIANCE_OPEN",
            downstream_consumers=["G7_08_FORCE", "G7_09_SADDLE"],
            forbidden_interpretations=["one reset representative determines the fiber force", "smoothness across endpoint outcome switches is automatic", "infinite nonencapsulating histories are physical readout histories"],
        ),
        record(
            "EXACT_FIXED_S_C2_FIELD",
            "F_s=(s*qdot,b_psi*Psi+s*V_hard)/(c_psi*b_psi+s*Dlambda[V_hard]), Dlambda[F_s]=1",
            "DESINGULARIZED_ACTION_VECTOR_FIELD_ORACLE",
            "MATHEMATICAL_OBJECT",
            "Exact cancellation-preserving C2 generator on every regular simple selected-line chart; only the hard complement is solved.",
            "regular C2 selected-line chart with s>=0 and positive denominator",
            [p_exact_field],
            current_status="CERTIFIED_FINITE_CORE_PARAMETRIC_EXISTENCE_NUMERICAL_OR_INTERVAL_REALIZATION_OPEN",
            downstream_consumers=["PARAMETRIC_RESET_FIBER_EXTERIOR_ORACLE", "G7_08_FORCE"],
            forbidden_interpretations=["invert the full Euler-Dirac block", "promote proof centers to physical histories", "select one reset member by hand"],
        ),
        record(
            "RESET_GENERATED_C2_LAUNCH_CHART",
            "T_launch=D_pi_event(ker D_Creset) direct_sum span{F_0}, dim(T_launch)=72+1=73",
            "NO_SELECTOR_LOCAL_FORWARD_LAUNCH_MANIFOLD",
            "MATHEMATICAL_OBJECT",
            "The forward-swapped reset event image supplies 72 outgoing seed directions and the exact action field supplies one transverse descriptor direction; the resulting local C2 launch family has the full constrained-child dimension without selecting a reset member.",
            "certified double-event reset root, regular branch-24 selected-line chart, s>=0",
            [p_launch_chart],
            current_status="CERTIFIED_LOCAL_73_DIMENSIONAL_MAXIMAL_TAIL_OPEN",
            downstream_consumers=["PARAMETRIC_RESET_FIBER_EXTERIOR_ORACLE", "G7_08_FORCE"],
            forbidden_interpretations=["139 arbitrary outgoing C2 launch dimensions are required", "the numerical proof center is a selected physical member", "the 67-dimensional fixed-seed lift kernel annihilates the full two-sided seam force", "the local launch theorem controls the maximal C2 tail"],
        ),
        record(
            "C2_LAUNCH_ADJOINT_AND_SEAM_SPLIT",
            "g_total=Z^dagger*d_upstream_interface+B^dagger*p_0; K^dagger*B^dagger*p_0=0; g_launch=(Q^dagger*p_0,<F_0,p_0>)",
            "RESET_TANGENT_COTANGENT_FACTOR_AND_KERNEL_COMPATIBILITY",
            "MATHEMATICAL_OBJECT",
            "The downstream C2 force factors through the 72-dimensional seed image and one exact transverse launch direction, while stationarity on the 67-dimensional fixed-seed lift kernel belongs to the complete upstream-history and retained-interface force block.",
            "certified reset tangent and local branch-24 C2 launch chart",
            [p_launch_adjoint],
            current_status="DERIVED_ACTUAL_JOINT_HISTORY_ADJOINT_OPEN",
            downstream_consumers=["G7_08_FORCE", "G7_09_SADDLE"],
            forbidden_interpretations=["discard the 67 fixed-seed kernel from the full saddle", "invent a new local seam force for the 67 kernel", "propagate 73 forward Jacobi columns for one scalar force", "a broad seam enclosure supplies its signed covector", "the algebraic split evaluates the zero-source force"],
        ),
        record(
            "C2_FIXED_SEED_UPSTREAM_FORCE_OWNER",
            "K_fixedC2={0}_C2 direct_sum ker(J_E1), dim(K_fixedC2)=98-rank(J_E1)=67",
            "FORWARD_HISTORY_TANGENT_AND_FORCE_PROVENANCE_IDENTITY",
            "MATHEMATICAL_OBJECT",
            "The C2 fixed-seed kernel is exactly the raw preceding-event tangent. Its force owner is the complete upstream C1-to-E1 heat-minus-zeta history plus retained interface contacts, not a new surface force; one joint history adjoint is the equivalent assembly.",
            "certified forward-swapped reset stratum and AE2 full-history operator domain",
            [p_fixed_seed_owner],
            current_status="DERIVED_ACTUAL_JOINT_BASE_AND_ADJOINT_OPEN",
            downstream_consumers=["G7_08_FORCE", "G7_09_SADDLE"],
            forbidden_interpretations=["the 67 directions are new local seam degrees of freedom", "the zero AE2 fermion surface action makes the upstream force vanish", "M_f invertibility supplies the full incoming heat force", "project the child flow by hand to define the time quotient"],
        ),
        record(
            "GATE7_MAXIMAL_TAIL_SUPPORT_REDUCTION",
            "ker(P_C2 Z)=K_fixedC2, dim K_fixedC2=67; tail_noncompact is supported on range(P_C2 Z) direct_sum span{F0}, dim<=72+1=73",
            "PHYSICAL_COTANGENT_CAUCHY_SUPPORT_DECOMPOSITION",
            "MATHEMATICAL_OBJECT",
            "The full-graded maximal tail is Cauchy on the entire fixed-C2 upstream/interface block and on the separate fixed-terminal incoming-amplitude coordinate; only the outgoing 72+1 C2 launch block retains a noncompact coefficient-Jacobi tail.",
            "certified forward-swapped reset stratum, fixed maximal C2 Friedrichs history, and one internal AE2 seam",
            [p_tail_support],
            current_status="FIXED_C2_AND_INCOMING_TAILS_CLOSED_OUTGOING_73_BLOCK_OPEN",
            downstream_consumers=["G7_08_FORCE", "G7_09_SADDLE"],
            forbidden_interpretations=["the incoming amplitude spans the fixed-seed reset kernel", "all physical cotangent directions are now closed", "an internal seam component is zero", "the 73-dimensional outgoing tail is convergent without proof"],
        ),
        record(
            "GATE7_OUTGOING_FLOW_TAIL_CLOSURE",
            "D_s M_C2^max=(d tau/ds)*(L_spatial-zI-(M_C2^max)^2) along D_sY=F_s; remaining noncompact tail=range(P_C2 Z), rank 72",
            "LOCAL_RICCATI_LIE_DERIVATIVE_AND_TAIL_SUPPORT_REDUCTION",
            "MATHEMATICAL_OBJECT",
            "The transverse F0 launch direction moves the birth section along one exact action orbit. Its maximal Weyl and zeta jets are local moving-boundary terms, so only the 72 reset-generated outgoing seed-image directions retain a noncompact coefficient-Jacobi tail.",
            "regular branch-24 outgoing descriptor chart and maximal C2 Friedrichs form-core exhaustion",
            [p_flow_tail],
            current_status="OUTGOING_FLOW_TAIL_CLOSED_SEED_IMAGE_RANK_72_OPEN",
            downstream_consumers=["G7_08_FORCE", "G7_09_SADDLE"],
            forbidden_interpretations=["F0 is discarded from the local force", "F0 is declared a new gauge direction", "the superseded one-sided W_phys initialization is restored", "the rank-72 seed-image tail is convergent without proof"],
        ),
        record(
            "GATE7_SEED_IMAGE_WARD_GAUGE_AUDIT",
            "range(B_seed)=ker(J_reset[0:26,0:98]), dim=72; BRST_longitudinal+ghost=0 but physical leading heat coefficient=-5 sqrt(pi)",
            "RESET_SEED_IMAGE_AND_WARD_GAUGE_NONREDUCTION_THEOREM",
            "MATHEMATICAL_OBJECT",
            "The complete outgoing seed image is the 72-dimensional constraint-and-ordered-event tangent. No tracked global 98-state gauge generator is available, and neither the principal Calderon slice nor BRST grading annihilates this geometric seed image, so the rank-72 projected Cauchy tail remains the exact owner.",
            "certified N12 reset Jacobian, launch image, principal-gauge audit, BRST ledger, and intrinsic time-root theorem",
            [p_seed_ward_gauge],
            current_status="WARD_GAUGE_SHORTCUTS_CLOSED_INVALID_RANK_72_TAIL_OPEN",
            downstream_consumers=["G7_08_FORCE", "G7_09_SADDLE"],
            forbidden_interpretations=["subtract a gauge dimension by count", "promote the principal delta-w delta-beta slice to a global Cauchy quotient", "use BRST grading as a universal zero-force identity", "infer tail convergence from time-root equivalence"],
        ),
        record(
            "GATE7_RANK72_RELATIVE_FORM_TAIL",
            "g_T-g_S=integral_S^T (U(t,0)B_seed)^dagger q_rep(t) dt+d_T-d_S; common-scale D_a integral(d_tau/R4)=0",
            "SOURCE_CONTRACTED_HEAT_SMOOTHED_RELATIVE_FORM_CAUCHY_CRITERION",
            "MATHEMATICAL_OBJECT",
            "The exact remaining maximal owner is a 72-vector heat-smoothed relative-form tail, not an ambient adjoint norm. The separate common-scale zeta optical-tail obligation is superseded by the moving-duration Ward identity, while the non-scale joint tail remains open.",
            "certified rank-72 reset seed image, complete closed-system heat-minus-zeta seed, and maximal Friedrichs core exhaustion",
            [p_rank72_relative_form],
            current_status="SHARP_CRITERION_DERIVED_COMMON_SCALE_ZETA_TAIL_CLOSED_RANK72_JOINT_TAIL_OPEN",
            downstream_consumers=["G7_08_FORCE", "G7_09_SADDLE"],
            forbidden_interpretations=["require convergence of the full ambient adjoint", "remove a seed-image dimension without a generator-membership theorem", "delete the nonzero common-scale heat trace", "treat fixed-channel Dini or a finite prefix as a maximal temporal tail bound"],
        ),
        record(
            "GATE7_RANK72_MAXIMAL_TAIL_ROUTE_ADJUDICATION",
            "finite-core Poincare rate pi/(2T)->0; current low-axis Weyl decrement>0.99; rank(position block of B_seed)=37",
            "MAXIMAL_TAIL_ROUTE_EXHAUSTION_THEOREM",
            "MATHEMATICAL_OBJECT",
            "Finite-core heat suppression is not uniform under a maximal Friedrichs exhaustion, the exact 1064-to-1222 Weyl net is not converged, gap plus Friedrichs data do not identify the exterior oracle, and the finite-optical NHIM does not supply the absolute graded force domain. The only live routes are the signed rank-72 relative-form Cauchy theorem or an actual later event/canonical stop.",
            "certified nested cores, maximal-exterior counterfamily, reset seed basis, and finite-N12 asymptotic NHIM",
            [p_rank72_route_adjudication],
            current_status="FINITE_PREFIX_AND_FINITE_OPTICAL_SHORTCUTS_EXHAUSTED_RANK72_PROJECTED_TAIL_OR_LATER_STOP_OPEN",
            downstream_consumers=["G7_08_FORCE", "G7_09_SADDLE"],
            forbidden_interpretations=["extrapolate a finite-core Poincare gap to the maximal end", "treat another artificial Dirichlet edge as a physical stop", "infer convergence from a small finite-core heat value", "declare the signed relative-trace route impossible from the absolute NHIM no-go"],
        ),
        record(
            "AE2_CHILD_BOUNDARY_HAMILTONIAN_NON_SUPERSESSION",
            "S_Sigma,F^AE2=0 and delta H_xi^child=integral_boundary(delta Q_xi-i_xi Theta_retained)-delta B_xi^child remains non-executable",
            "ACTION_VERSION_DEPENDENCY_NON_SUPERSESSION_THEOREM",
            "MATHEMATICAL_OBJECT",
            "AE2 closes the fermion transmission domain but adds no complete child covariant symplectic potential, Noether charge assembler, differentiability counterterm/ensemble, or coercive boundary charge; the earlier child-Hamiltonian ownership no-go therefore remains current.",
            "BHSM-AE-2.0.0 global spin-reset action and retained child boundary ownership ledger",
            [p_ae2_boundary_hamiltonian],
            current_status="AE2_FERMION_DOMAIN_CLOSED_CHILD_BOUNDARY_HAMILTONIAN_NOT_ACTION_EXECUTABLE",
            downstream_consumers=["G7_08_FORCE", "G7_09_SADDLE"],
            forbidden_interpretations=["relabel the zero reduced constraint energy as H_xi", "treat the global Dirac domain as a localized seam charge", "add a child boundary ensemble for positivity", "zero an internal child or contact response"],
        ),
        record(
            "GATE7_CAPTURED_NHIM_RANK72_RELATIVE_TAIL",
            "epsilon<=epsilon_0 exp(-H0*t), Ds_mu=O(mu exp(-H0*t/2)), DV_mu=O(mu^2 exp(-H0*t)); g_T-g_S->0 on captured families",
            "CAPTURED_FAMILY_SOURCE_CONTRACTED_RELATIVE_TAIL_THEOREM",
            "MATHEMATICAL_OBJECT",
            "On every open finite-N12 family captured by the retained analytic NHIM, bounded center Jacobi fields and decaying normal fields make all fixed-channel coefficient jets temporally integrable; the certified first C2 collar then makes the full graded rank-72 relative tail angularly summable. The absolute NHIM heat-trace no-go is preserved.",
            "regular finite-N12 post-event C2 families contained in the open NHIM capture basin",
            [p_nhim_rank72_relative_tail],
            current_status="CAPTURED_RANK72_TAIL_CLOSED_RESET_TO_CAPTURE_CONNECTION_OPEN",
            downstream_consumers=["G7_08_FORCE", "G7_09_SADDLE"],
            forbidden_interpretations=["the AE2 reset image is already proved to enter the basin", "the absolute infinite-volume heat trace converges", "all arbitrary maximal histories are controlled", "select a favorable reset member by hand"],
        ),
        record(
            "C2_1222_PARAMETRIC_BASE_FAMILY",
            "Y(s;theta)=Phi_s(R_AE2_local(theta)), D_s J_theta=D_Y F_s J_theta",
            "FINITE_CORE_SMOOTH_FLOW_FAMILY_THEOREM",
            "MATHEMATICAL_OBJECT",
            "A nonempty local 73-parameter family of exact reset-generated C2 histories and first Jacobi fields exists through every prefix of the 1222-segment regular finite core; proof centers remain enclosure data.",
            "regular simple-line positive-Delta fixed-s chart through finite core 1222",
            [p_parametric_base],
            current_status="DERIVED_SIGNED_PARAMETRIC_OR_INTERVAL_ADJOINT_OPEN",
            downstream_consumers=["G7_08_FORCE", "G7_09_SADDLE"],
            forbidden_interpretations=["select a proof center as the physical history", "the 1222 proof edge is an event or stop", "finite-core family existence supplies the graded force value", "finite-core smooth dependence closes the maximal tail"],
        ),
        record(
            "C2_1222_SIGNED_ADJOINT_ASSEMBLY",
            "p_N=C_x,N*x_Y,N+g_T; p_j=C_x,j*x_Y,j+C_h,j*h_Y,j+Phi_Y,j^dagger*p_(j+1); g_reset=Z^dagger*d_upstream_interface+B^dagger*p_0",
            "INVERSE_FREE_SIGNED_HISTORY_COTANGENT_PULLBACK",
            "MATHEMATICAL_OBJECT",
            "On every exact finite-core family member, one reverse sweep pulls the signed radius and moving-duration coefficient cotangent to the C2 seed and then through the reset seam; the complete upstream covector remains part of the same joint force.",
            "exact member of the regular 1222-segment C2 family with action-owned segment-map and duration first jets",
            [p_signed_adjoint],
            current_status="DERIVED_NUMERICAL_PARAMETRIC_OR_INTERVAL_JOINT_SOURCE_ADJOINT_OPEN",
            downstream_consumers=["G7_08_FORCE", "G7_09_SADDLE"],
            forbidden_interpretations=["73 forward Jacobi columns are required for one scalar force", "proof-center coefficient paths evaluate the physical signed force", "the downstream adjoint replaces the complete upstream history covector", "the signed recurrence supplies the graded heat-minus-zeta source"],
        ),
        record(
            "C2_SIGNED_DURATION_INCIDENCE_OWNER",
            "q_tau=N_boundary*s/Delta; D_Y q_tau=q_tau*(D_Y log N_boundary-D_Y Delta/Delta)",
            "ACTION_OWNED_MOVING_DURATION_FIRST_VARIATION",
            "MATHEMATICAL_OBJECT",
            "The signed log-radius and log-lapse covectors and the moving-duration incidence formula are exact; a signed selected-line/hard-complement D_Y Delta partial plus controlled remainder ball is certified at the reference center, and transport of that ball onto the exact parametric family is the minimal local duration gap.",
            "regular positive-lapse positive-Delta C2 fixed-s family",
            [p_duration_incidence],
            current_status="DERIVED_REFERENCE_D_Y_DELTA_BALL_CERTIFIED_FAMILY_TRANSPORT_AND_SEGMENT_ACTION_OPEN",
            downstream_consumers=["C2_1222_SIGNED_ADJOINT_ASSEMBLY", "G7_08_FORCE"],
            forbidden_interpretations=["a norm bound supplies the sign of D_Y Delta", "differentiate the adaptive proof-center algorithm as a physical history", "proper duration is an independent fitted coefficient", "the zero-DDelta formula witness is a BHSM value"],
        ),
        record(
            "C2_SIGNED_DDELTA_SEED_TRANSPORT_AUDIT",
            "DDelta(Y_exact) in DDelta(Y_1214)+Ball(0,r_seed+B_D2Delta*r_tube)",
            "CANCELLATION_RESOLUTION_AUDIT",
            "MATHEMATICAL_OBJECT",
            "The retained product majorants certify a valid local D2Delta transport ball, but that ball contains zero already across the node-1214 exact-state tube; this is a proof-resolution artifact and does not define a physical stop.",
            "first matrix-Lohner chart around stored proof node 1214",
            [p_ddelta_transport],
            current_status="COARSE_TRANSPORT_CERTIFIED_DIRECT_CANCELLATION_PRESERVING_D2DELTA_OR_TIGHTER_LOCALIZATION_OPEN",
            downstream_consumers=["C2_SIGNED_DURATION_INCIDENCE_OWNER", "G7_08_FORCE"],
            forbidden_interpretations=["the coarse D2Delta ball is the physical signed force", "a ball containing zero proves the force vanishes", "coarse transport failure is an event or canonical stop", "proof node 1214 is an exact physical history"],
        ),
        record(
            "C2_DIRECT_DDELTA_ROW_RECONNAISSANCE",
            "b_Psi=<Psi,f>; Delta=Dlambda[b_Psi*Psi+s*V_hard]; D_ih(cb)=b*c_ih+b_i*c_h+c_i*b_h+c*b_ih; D3S[h,Psi,SQ*r]=<Psi_h,r> eliminates w3,w5,wI,wN,wVI,wfi",
            "CANCELLATION_PRESERVING_ONE_ROW_REDUCTION",
            "MATHEMATICAL_OBJECT",
            "The selected-line coefficient is the inverse-free local contraction <Psi,f>, the hard response is confined to the spectral complement, and the signed denominator recombines exactly before norms. Zero exclusion needs only the dominant action-coordinate Hessian row. The mixed second eigenline is first replaced by one small hard adjoint; self-adjointness then eliminates every nested hard adjoint w3,w5,wI,wN,wVI,wfi, leaving only finite local action/source jets, Psi, the existing first eigenline Jacobi matrix Psi_h, its decisive column Psi_i, z, and V_hard. The fully reduced center replay preserves the row norm near 1.69e-5, about 8.6e5 below the rigorous ceiling, but it is not an interval remainder theorem.",
            "first matrix-Lohner chart around stored proof node 1214",
            [p_ddelta_row],
            current_status="ALL_NESTED_HARD_ADJOINTS_ELIMINATED_RIGOROUS_ROW_86_REMAINDER_OPEN",
            downstream_consumers=["C2_SIGNED_DURATION_INCIDENCE_OWNER", "G7_08_FORCE"],
            forbidden_interpretations=["two-mesh agreement or the center hard adjoint is an interval certificate", "the diagnostic row closes signed D_Y Delta", "a full 98 by 98 D2Delta norm or any nested hard-adjoint tube remains necessary for the bc row", "proof node 1214 is an exact physical history"],
        ),
        record(
            "C2_FULLY_REDUCED_SIGNED_ROW_CERTIFICATE",
            "sup_t ||row_86(D2(cb))||_2 <= B_cb < 14.622464650642785 after D3S[h,Psi,SQ*r]=<Psi_h,r> eliminates w3,w5,wI,wN,wVI,wfi",
            "OUTWARD_ROUNDED_CANCELLATION_PRESERVING_ROW_CERTIFICATE",
            "MATHEMATICAL_OBJECT",
            "The retained 96-point action is replayed with primitive-level outward rounding on the exact node-1214 state tube. The complete dominant selected-line product row is certified below its resolving ceiling after a separate whole-matrix correction for the first eigenline Jacobi motion. This closes the dominant bc row only; the s-suppressed hard-response row remains open and Gate 7 is not promoted.",
            "first matrix-Lohner chart around stored proof node 1214",
            [p_reduced_row],
            current_status="DOMINANT_bc_ROW_CERTIFIED_s_HARD_ROW_OPEN",
            downstream_consumers=["C2_SIGNED_DURATION_INCIDENCE_OWNER", "G7_08_FORCE"],
            forbidden_interpretations=["small signed descriptor s makes the hard row zero without a bound", "the bc-row certificate alone closes signed D_Y Delta", "the interval proof center selects a physical history", "Gate 7 or Gate 8 is closed by this row alone"],
        ),
        record(
            "C2_COMPLETE_SIGNED_D2DELTA_ROW_CERTIFICATE",
            "sup_t ||row_86(D2 Delta)||_2 <= 2.684118590455544 < 14.622464650642785, with ||s row_86(D2 R)||_2 <= 0.005348168974427062",
            "OUTWARD_ROUNDED_COMPLETE_SIGNED_DENOMINATOR_ROW_CERTIFICATE",
            "MATHEMATICAL_OBJECT",
            "The ten-term product rule for R=D3S[Qdot+E*V_hard,Psi,Psi] is enclosed on the exact node-1214 tube. Certified second variations bound the response and eigenline first-matrix motions, including their bilinear cross term. The fixed positive descriptor suppresses the raw hard row enough that the complete signed D2Delta row stays strictly below the unchanged resolving ceiling. This zero-excludes the local signed D_Y Delta component on the exact family; the transposed exact segment-map action and complete physical force remain open.",
            "first matrix-Lohner chart around stored proof node 1214",
            [p_suppressed_row],
            current_status="LOCAL_SIGNED_DURATION_DENOMINATOR_CERTIFIED_FORCE_PULLBACK_OPEN",
            downstream_consumers=["C2_SIGNED_DURATION_INCIDENCE_OWNER", "G7_08_FORCE"],
            forbidden_interpretations=["descriptor suppression permits omitting the hard row", "local D_Y Delta zero exclusion is the complete upstream force", "the proof center selects a physical history", "Gate 7, Gate 8, or chord 3 is promoted by this local certificate"],
        ),
        record(
            "CORE_TRANSMISSION_NONSELECTION",
            "T_core_to_reset=NOT_ACTION_DERIVED",
            "PROVENANCE_AND_DOMAIN_NONEXISTENCE_AUDIT",
            "BHSM_ONTOLOGY",
            "AE2 U_R glues regular event and child traces but supplies no pregeometric core-to-reset population projector or extra quotient reduction.",
            "BHSM-AE-2.0.0 regular event-child domain",
            [p_core_audit],
            current_status="OWNER_HYPOTHESIS_NOT_ACTION_DERIVED_NO_SELECTOR_AUTHORITY",
            downstream_consumers=["PARAMETRIC_RESET_FIBER_EXTERIOR_ORACLE", "G7_08_FORCE"],
            forbidden_interpretations=["U_R is a pregeometric core transfer", "core ontology reduces the 139/73/67/66 ledger", "a=1/118 selects a reset state"],
        ),
        record(
            "WEIGHT_SEVEN_TRANSVERSE_DESCRIPTOR",
            "sigma_phys in {0,-7*sqrt(kappa0/42)} with multiplicities 25 and 25 after the 12-chain local time/lapse quotient",
            "CONSTRAINT_REDUCED_GENERALIZED_DESCRIPTOR_PENCIL",
            "MATHEMATICAL_OBJECT",
            "The round expanding dominant system has 25 physical centers and 25 stable velocity transients, with the common-scale center retained and no weight-seven unstable finite mode.",
            "nonrealized round expanding weight-seven mathematical branch",
            [p_w7_descriptor],
            current_status="DERIVED_LOWER_WEIGHT_R_MINUS_2_CENTER_FORCE_OPEN",
            equivalent_forms=["74x74 bordered KKT pencil with 24 algebraic infinite modes", "constraint-solved physical quadratic pencil"],
            downstream_consumers=["WEIGHT_FIVE_CENTER_MODULATION"],
            forbidden_interpretations=["R^-2 numerical roots are weight-seven eigenvalues", "the common-scale center is an exact full-action gauge", "this mathematical branch is a realized particle readout"],
        ),
        record(
            "WEIGHT_FIVE_CENTER_MODULATION",
            "(A7+2*H0*E7)X5=(0,-D_q_phys*L5,-D_m*L5), epsilon=R4^-2",
            "SINGULAR_FESHBACH_BORDERED_KKT_CENTER_LIFT",
            "MATHEMATICAL_OBJECT",
            "Exact first lower-weight center-force operator; its complete 74-component leading modulation vector now has a directed Arb enclosure, while the uniform full retained remainder remains open.",
            "round expanding mathematical branch on the weight-seven physical tangent quotient",
            [p_w5_modulation],
            current_status="DERIVED_OPERATOR_AND_DIRECTED_LEADING_VECTOR_UNIFORM_REMAINDER_OPEN",
            downstream_consumers=["INTERVAL_WEIGHT_FIVE_CENTER_LIFT", "FULL_RETAINED_ASYMPTOTIC_BRANCH"],
            forbidden_interpretations=["float64 R^-2 coefficients are certified eigenvalues", "formal H4 limit is a full retained-history theorem", "the infinite branch is a realized particle"],
        ),
        record(
            "WEIGHT_FIVE_MULTIPRECISION_AUDIT",
            "high_precision_nodes+15_digit_generic_action_jet+70_digit_solve; superseded",
            "REPRODUCIBILITY_NONPROMOTION_CERTIFICATE",
            "MATHEMATICAL_OBJECT",
            "Historical generic-jet rows conservatively withheld promotion but used only default 15-digit action arithmetic and are superseded.",
            "N12 weight-five physical quotient coefficient representation",
            [p_w5_mp_audit],
            current_status="SUPERSEDED_PRECISION_SCOPE_CORRECTED",
            downstream_consumers=["WEIGHT_FIVE_CENTER_MODULATION"],
            forbidden_interpretations=["small solve residual certifies quadrature", "empirically stable sign is an action theorem", "more brute-force nodes replace an enclosure"],
        ),
        record(
            "ANALYTIC_WEIGHT_FIVE_LOCAL_BLOCK_LIFT",
            "exact_local_H7^(10x10)+exact_local_D_L5^(8) -> 74x74 bordered physical lift",
            "ANALYTIC_PRECONDITIONED_FESHBACH_ASSEMBLY",
            "MATHEMATICAL_OBJECT",
            "Genuine high-precision local-block integration converges the represented coefficient and agrees with the independent 98-variable jet; its value is enclosed by the downstream directed Arb certificate.",
            "N12 round expanding mathematical branch physical tangent quotient",
            [p_w5_analytic],
            current_status="DERIVED_CONVERGED_AND_INDEPENDENTLY_CROSSCHECKED_INTERVAL_CERTIFICATE_DOWNSTREAM",
            downstream_consumers=["INTERVAL_WEIGHT_FIVE_CENTER_LIFT"],
            forbidden_interpretations=["empirical 40-digit convergence is directed rounding", "negative correction proves H4 tends to zero", "the mathematical infinite branch is a realized particle"],
        ),
        record(
            "INTERVAL_WEIGHT_FIVE_CENTER_LIFT",
            "X5 in solve_ball(A7+2*H0*E7,(0,-D_q_phys*L5,-D_m*L5)); Gauss remainder <= exact rational E_128",
            "DIRECTED_ARB_BORDERED_CENTER_MODULATION_CERTIFICATE",
            "MATHEMATICAL_OBJECT",
            "Certified Legendre balls, an exact rational quadrature remainder, and a preconditioned 74 by 74 Arb solve rigorously enclose the complete leading center modulation vector and make its common-scale rate correction strictly negative.",
            "N12 round expanding mathematical branch physical tangent quotient",
            [p_w5_interval],
            current_status="DIRECTED_LEADING_WEIGHT_FIVE_VECTOR_CERTIFIED_FULL_ASYMPTOTIC_BRANCH_DOWNSTREAM",
            downstream_consumers=["FULL_RETAINED_ASYMPTOTIC_BRANCH"],
            forbidden_interpretations=["the leading negative rate alone proves nonlinear H4 decay", "the mathematical infinite branch is a realized particle", "the interval certificate closes the finite-history zero-source force"],
        ),
        record(
            "FULL_RETAINED_ASYMPTOTIC_BRANCH",
            "Z(epsilon)=epsilon*X5+epsilon^2*R(epsilon), H4=H0+epsilon*h1+epsilon^2*r_H(epsilon), epsilon=R4^-2",
            "ANALYTIC_BRIOT_BOUQUET_FULL_ACTION_BRANCH_THEOREM",
            "MATHEMATICAL_OBJECT",
            "Exact retained scale weights, the rigorously invertible algebraic block, first-order gauge compatibility, and positive-integer descriptor nonresonance give a local analytic full-action branch with uniformly bounded remainder and H4 tending to H0>0.",
            "nonrealized forever-expanding N12 mathematical formation branch near epsilon=0",
            [p_full_asymptotic],
            current_status="CLOSED_OUTCOME_A_H4_TO_H0_POSITIVE_NONREALIZED_SCOPE",
            downstream_consumers=["PHYSICAL_FINITE_HISTORY_ZERO_SOURCE_FORCE"],
            forbidden_interpretations=["local infinity analyticity proves backward event reachability", "the nonrealized branch is a physical particle", "outcome A closes the finite-history zero-source force", "a lower-weight coefficient is a new eigenvalue"],
        ),
        record(
            "SOURCE_WEIGHTED_THRESHOLD_MEASURE",
            "integral_(0,1]_lambda^(-1)*d|nu_h|(lambda)<infinity",
            "SOURCE_CONTRACTED_SPECTRAL_MEASURE_BOUND",
            "BHSM_ONTOLOGY",
            "Exact source-Dini criterion; compact-source factorization closes every admissible positive far tail.",
            "each realized factorized AE2 Weyl channel near lambda=0",
            [p_e1, p_fac],
            equivalent_forms=["dnu_h(lambda)=lambda*dmu_C_h(lambda) with C_h trace class", "integral lambda^-1*d|nu_h|<=norm_1(C_h)", "|nu_h|([0,Lambda])<=C*Lambda^(1+epsilon), epsilon>0", "|nu_h|([0,Lambda])=O(Lambda/abs(log Lambda)^2)"],
            source_weighting_required=True,
            current_status="DINI_CLOSED_ALL_ADMISSIBLE_TAILS_BY_COMPACT_VOL_TERRA_TRACE_CLASS",
            downstream_consumers=["E1_SOURCE_MEASURE_FINITE", "HIGH_ENERGY_ANGULAR_TAIL"],
            forbidden_interpretations=["strict spectral gap is necessary", "zero resonance automatically diverges"],
        ),
        record(
            "NONFERMION_THRESHOLD_CLOSURE",
            "nonfermion_zero_threshold_obstruction=closed",
            "SECTORWISE_THRESHOLD_THEOREM",
            "BHSM_ONTOLOGY",
            "Scalar/de Rham/ghost and transverse-gauge AE2 threshold obstruction is closed in theorem scope.",
            "certified AE2 nonfermion seam blocks",
            [p_nf],
            source_weighting_required=True,
            current_status="CLOSED_DO_NOT_REOPEN_WITHOUT_CONTRADICTION",
            downstream_consumers=["FACTORIZED_WEYL_THRESHOLD"],
        ),
    ]


def _historical() -> list[dict[str, Any]]:
    gauge = "artifacts/BHSM_alpha_i_update_v4_2.json"
    pred = "theory/bhsm_prediction_ledger.json"
    frozen = "artifacts/frozen_constants_v2.json"
    rho = "artifacts/BHSM_rho_ch_action_audit_v1_9.json"
    energy = "artifacts/intrinsic_state_selection/BHSM_N12_CONSTRAINT_REDUCED_ENERGY_IDENTITY_GATE.json"
    rows = [
        ("GAUGE_127_PATTERN", "alpha_i=w_i/(6*pi^2), w=(1,2,7)", gauge, "HISTORICAL_NOT_ACTION_DERIVED"),
        ("CKM_FROZEN_OUTPUT", "V_CKM=V_CKM^frozen", pred, "FROZEN_OUTPUT_NOT_ACTION_INPUT"),
        ("CKM_EXPONENT_1_16", "s23_candidate=s23_frozen*(Z_virt^(u,2))^(1/16)", pred, "CANDIDATE_NOT_DERIVED"),
        ("CHARGED_ETA_L", "eta_l", rho, "CONDITIONAL_OR_FITTED_NOT_DERIVED"),
        ("CHARGED_RHO_CH", "rho_ch", rho, "OPEN_LOCALIZABLE_NOT_DERIVED"),
        ("Z_VIRT_U2", "Z_virt^(u,2)=1/2", frozen, "FROZEN_CONDITIONAL_OUTPUT"),
        ("LOCAL_ENERGY", "E_energy=Legendre_energy_on_constraint_surface", energy, "ACTION_DERIVED_LOCAL_ENERGY_NOT_MASS"),
        ("PHYSICAL_MASS", "m_phys=observable_map(scale_map,geometric_response)", pred, "NOT_DERIVED_UNTIL_OBSERVABLE_AND_SCALE_MAP"),
        ("NEUTRINO_PHYSICAL_SCALE", "m_nu[eV/GeV]", pred, "NOT_DERIVED"),
    ]
    return [
        record(
            cid,
            formula,
            "HISTORICAL_OR_DOWNSTREAM_FORMULA",
            "SM_EXPERIMENTAL_INTERPRETATION",
            status.replace("_", " ").lower(),
            "historical prediction ledger only",
            [source],
            current_status=status,
            observable_status="HISTORICAL_OR_UNVALIDATED_OBSERVABLE_MAP",
            frozen_output_status="FROZEN_OUTPUT" if "FROZEN" in status else "NOT_FROZEN_OUTPUT",
            forbidden_interpretations=["Use as a current AE2 action input."],
            downstream_consumers=[],
        )
        for cid, formula, source, status in rows
    ]


def _symbols() -> list[dict[str, Any]]:
    definitions = [
        ("SYMBOL_MATHCAL_K_C", "mathcal_K_C", "SOURCE_OPERATOR"),
        ("SYMBOL_K_HIT", "K_hit=c_psi*b_psi", "SINGULAR_HITTING_PRODUCT"),
        ("SYMBOL_K_GEOM", "K_geom", "CURVATURE_ONLY"),
        ("SYMBOL_RESET", "mathcal_R_reset", "RESET_RELATION"),
        ("SYMBOL_RESOLVENT", "script_R_C(z)", "RESOLVENT"),
        ("SYMBOL_R4", "R4", "QUOTIENT_RADIUS"),
        ("SYMBOL_WEYL", "M_C^Weyl(z)", "WEYL_MAP"),
        ("SYMBOL_ADMITTANCE", "m_j(z)", "CHANNEL_ADMITTANCE"),
        ("SYMBOL_MASS", "m_phys", "PHYSICAL_MASS_AFTER_OBSERVABLE_MAP"),
        ("SYMBOL_EVENT", "e_ord", "ORDERED_EVENT_COORDINATE"),
        ("SYMBOL_EVENT_SQUARED", "u_evt=e_ord^2", "SQUARED_EVENT_COORDINATE"),
        ("SYMBOL_SPECTRAL_MEASURE", "E_spec(lambda)", "SPECTRAL_MEASURE"),
        ("SYMBOL_ENERGY", "E_energy", "ENERGY"),
        ("SYMBOL_PARAMETER", "z", "NEUTRAL_SPECTRAL_PARAMETER"),
    ]
    source = "artifacts/flagship_integration/BHSM_N12_FORWARD_GAUGE_WEYL_READOUT_FAMILY.json"
    return [
        record(
            cid, symbol, "CANONICAL_SYMBOL", "MATHEMATICAL_OBJECT", meaning,
            "current AE2 notation", [source], current_status="CANONICAL_UNIQUE_NAMESPACE",
            forbidden_interpretations=["Reuse this symbol for a different object class."],
        )
        for cid, symbol, meaning in definitions
    ]


def _equivalences() -> list[dict[str, Any]]:
    source = "artifacts/flagship_integration/BHSM_N12_FORWARD_FIXED_CHANNEL_TRANSFER.json"
    rows = [
        ("EQ_RADIUS_INVERSE", "R4^-1 <=> exp(-x)", ["R4^-1", "exp(-x)"]),
        ("EQ_RADIUS_SQUARED_INVERSE", "R4^-2 <=> exp(-2*x)", ["R4^-2", "exp(-2*x)"]),
        ("EQ_CHANNEL_DYNAMICS", "second_order <=> transfer_2x2 <=> Riccati <=> Weyl_admittance <=> Mobius_transfer", ["second-order channel equation", "2x2 trace-zero transfer", "Riccati equation", "Weyl admittance", "Mobius transfer"]),
        ("EQ_EXTERIOR_RESPONSE", "bulk_resolvent <=> Schur_core_resolvent <=> Weyl_Calderon_response", ["bulk resolvent", "Schur-compressed core resolvent", "Weyl/Calderon exterior response"]),
        ("EQ_SOURCE_VARIATION", "source_Frechet_derivative <=> resolvent_insertion <=> heat_Duhamel", ["source Frechet derivative", "resolvent insertion", "heat Duhamel representation"]),
    ]
    return [
        record(cid, formula, "MATHEMATICAL_EQUIVALENCE_CLASS", "MATHEMATICAL_OBJECT",
               "Equivalent proof/computation representations of one physical law.", "overlap of stated representation domains", [source],
               equivalent_forms=forms, current_status="EQUIVALENT_NOT_INDEPENDENT_PHYSICS",
               forbidden_interpretations=["Count equivalent forms as independent laws."])
        for cid, formula, forms in rows
    ]


def _deprecations() -> list[dict[str, Any]]:
    source = "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_THRESHOLD_SUPERSESSION.json"
    seam_source = "artifacts/flagship_integration/BHSM_N12_EVENT_NORMAL_TWO_SIDED_SEAM_CORRECTION.json"
    birth_source = "artifacts/flagship_integration/BHSM_N12_GATE7_EXTERNAL_BIRTH_SOURCE_ROLE_SUPERSESSION.json"
    rows = [
        ("DEPRECATE_STRICT_GAP", "strict universal threshold gap", "SUPERSEDED_AS_NECESSARY", "source-weighted threshold measure"),
        ("DEPRECATE_ZERO_RESONANCE_DIVERGENCE", "zero resonance => infrared divergence", "FALSE_IN_GENERAL", "source vertex determines weighted response"),
        ("DEPRECATE_P2", "z=p^2", "FORBIDDEN_WITHOUT_ACTION_MAP", "neutral z"),
        ("DEPRECATE_PERIODIC_READOUT", "periodic S1 Fourier readout", "HISTORICAL", "nonperiodic forward resolvent"),
        ("DEPRECATE_TERMINAL_RETURN", "mandatory terminal return", "NOT_REQUIRED", "conditional event reset or canonical stop"),
        ("DEPRECATE_GENERIC_OPERATOR_HISTORY", "generic operator-valued exterior history", "SUPERSEDED_IN_FIXED_CHANNEL_SCOPE", "x(tau) fixed-channel coefficients"),
        ("DEPRECATE_D5_NATIVE_BLOCKER", "D5/Kato interval sign as native Gate7 blocker", "OPTIONAL_ENDPOINT_ROUTE", "factorized source-weighted LAP"),
        ("DEPRECATE_STRICT_POWER_EXCESS", "epsilon_h>0 power excess is compulsory", "SUFFICIENT_NOT_NECESSARY_AFTER_CRITICAL_BESSEL_THEOREM", "exact source-Dini integrability"),
        ("DEPRECATE_FAR_END_BIRTH_SELECTION", "far Friedrichs closure selects birth graph", "FORBIDDEN", "AE2 glued birth domain"),
        ("DEPRECATE_LOCAL_ENERGY_MASS", "local energy=m_phys", "FORBIDDEN", "observable plus physical scale map"),
    ]
    return [
        record(cid, old, "DEPRECATION_RECORD", "BHSM_ONTOLOGY", replacement,
               "current AE2/Gate7", [source], current_status=status,
               superseded_meanings=[old], forbidden_interpretations=[old])
        for cid, old, status, replacement in rows
    ] + [
        record(
            "DEPRECATE_W_ONLY_EVENT_INITIALIZATION",
            "M(0,z)=W_phys as the physical AE2 event datum",
            "DEPRECATION_RECORD",
            "MATHEMATICAL_OBJECT",
            "Use U_R^dagger*M_child(z)*U_R+W_phys after opposite-arm elimination, or solve the joint two-sided seam.",
            "physical AE2 finite event-child operator",
            [seam_source],
            current_status="SUPERSEDED_BY_TWO_SIDED_AE2_SEAM",
            superseded_meanings=["one-sided W-only terminal wall"],
            forbidden_interpretations=["W_phys=0 implies zero child Calderon response"],
            downstream_consumers=["G7_08_FORCE"],
        ),
        record(
            "DEPRECATE_DYNAMIC_BIRTH_TRACE_MF_REDUCTION",
            "Treat the external birth trace as a dynamical integrated E0 seam and require B_birth or M_E0",
            "DEPRECATION_RECORD",
            "MATHEMATICAL_OBJECT",
            "At fixed external birth trace, differentiate the complete E1/C2 functional and then set the trace to zero; the nonzero internal response is M_f=M11.",
            "physical Gate-7 zero-external-source joint operator",
            [birth_source],
            current_status="SUPERSEDED_BY_EXTERNAL_BIRTH_TRACE_ROLE",
            superseded_meanings=["the external Cauchy source is an integrated dynamical birth seam"],
            forbidden_interpretations=["Reopen M_f by inventing a pre-E0 response arm."],
            downstream_consumers=["G7_08_FORCE"],
        ),
    ]


def _dimensions() -> list[dict[str, Any]]:
    source = "artifacts/flagship_integration/BHSM_N12_FORWARD_PROPER_TIME_FORM_OWNERSHIP.json"
    rows = [
        ("DIM_R4", "[R4]=L", "LENGTH"),
        ("DIM_X", "[x]=1", "DIMENSIONLESS_LOG_RADIUS"),
        ("DIM_TAU", "[tau]=T", "TIME"),
        ("DIM_DTAU", "[D_tau]=T^-1", "INVERSE_TIME"),
        ("DIM_KC", "[mathcal_K_C]=T^-2", "INVERSE_TIME_SQUARED"),
        ("DIM_Z", "[z]=[mathcal_K_C]", "OPERATOR_SPECTRAL_DIMENSION"),
        ("DIM_RESOLVENT", "[script_R_C]=[mathcal_K_C]^-1", "INVERSE_OPERATOR"),
        ("DIM_E_SPEC", "[E_spec]=1", "PROJECTION_MEASURE"),
        ("DIM_E_ENERGY", "[E_energy]=ENERGY", "ENERGY"),
        ("DIM_M_PHYS", "[m_phys]=MASS", "PHYSICAL_MASS_AFTER_SCALE_MAP"),
    ]
    return [
        record(cid, formula, "DIMENSION_SCALE_RECORD", "MATHEMATICAL_OBJECT", meaning,
               "current AE2 units", [source], dimensions=meaning, current_status="DIMENSIONALLY_NORMALIZED")
        for cid, formula, meaning in rows
    ]


def _ontology() -> list[dict[str, Any]]:
    ae2 = "artifacts/action_extension/BHSM_ACTION_AE2_GLOBAL_SPIN_RESET_ACTION.json"
    owner = "theory/norman_owner_ontology_recovered.md"
    finite = "artifacts/flagship_integration/BHSM_N12_GATE7_FINITE_ENCAPSULATION_PHYSICAL_DOMAIN_AUDIT.json"
    source_ontology = "artifacts/flagship_integration/BHSM_N12_GATE7_EXTERNAL_BIRTH_SOURCE_ROLE_SUPERSESSION.json"
    rows = [
        ("ONTOLOGY_MAXIMAL_FORWARD_HISTORY", "H_max^+", "Primary dynamical object is a maximal forward geometric history.", "ACTION_REQUIRED"),
        ("ONTOLOGY_SINGLE_TIME", "dt>0 and d_tau>0", "Physical time has one orientation.", "INTERNAL_CONSISTENCY_REQUIRED"),
        ("ONTOLOGY_REFLECTION", "reflection(H^+) != physical second orientation", "Formal reflection is a non-gauge Cauchy-state pairing.", "INTERPRETIVE_CORRECTION"),
        ("ONTOLOGY_CONDITIONAL_RESET", "event_hit => mathcal_R_reset := forward_event_to_new_child_glue", "The historical reset relation is physically a forward event-to-new-child gluing relation.", "ACTION_REQUIRED_WITH_NORMALIZED_FORWARD_SEMANTICS"),
        ("ONTOLOGY_AE2_DOMAIN", "Spin x G_SM event-child-glued bundle", "Owner-authorized AE2 global forward event/new-child matter domain.", "OWNER_AUTHORIZED_THEORY_VERSION_DECISION"),
        ("ONTOLOGY_AE2_TRANSMISSION", "delta S_AE2=0 => transmission law", "Transmission laws derived on AE2 may be action-derived within AE2.", "ACTION_DERIVED_WITHIN_AE2"),
        ("ONTOLOGY_FAR_END", "new_event_to_new_child_glue if hit; Friedrichs otherwise where applicable", "Far-end completion does not return to or select the birth event.", "ACTION_DOMAIN_REQUIRED"),
        ("ONTOLOGY_GEOMETRY_FIRST", "geometry -> emergent SM interpretation", "Geometry is microscopic and Standard Model language is downstream.", "OWNER_AUTHORIZED_ONTOLOGY"),
        ("ONTOLOGY_NO_OBSERVABLE_UPSTREAM", "action -> theorem -> observable -> frozen comparison", "Advertised observables must be derived and never inserted upstream.", "OWNER_AUTHORIZED_DEPENDENCY_DIRECTION"),
        ("ONTOLOGY_PARTICLE_CLASS", "particle=[persistent geometric mode/history]", "Particles are persistent geometric mode/history equivalence classes.", "OWNER_AUTHORIZED_ONTOLOGY"),
        ("ONTOLOGY_GENERATIONS", "generation_slots=(base,excitation_1,excitation_2)", "Three generations are one base mode plus two excitation slots of one architecture.", "OWNER_AUTHORIZED_ONTOLOGY"),
        ("ONTOLOGY_MASS_READOUT", "m_phys=action_owned_response_plus_universal_scale_map", "Mass is a geometric propagation/boundary response readout, not primitive or local energy.", "OWNER_AUTHORIZED_OBSERVABLE_SEMANTICS"),
        ("ONTOLOGY_UNIVERSAL_SCALE", "physical_scale=universal_action_derived_origin", "Sector differences reside in dimensionless geometric responses, not free sector scales.", "OWNER_AUTHORIZED_DIMENSIONAL_SEMANTICS"),
        ("ONTOLOGY_NEUTRINO_MASS", "m_nu=propagation_locked_curvature_response", "Neutrino mass is a propagation response rather than primitive static rest mass.", "OWNER_AUTHORIZED_OBSERVABLE_SEMANTICS"),
        ("ONTOLOGY_CKM", "V_CKM=relative_orientation(up_response_basis,down_response_basis)", "CKM is the mismatch of action-selected up/down geometric response sectors.", "OWNER_AUTHORIZED_OBSERVABLE_SEMANTICS"),
        ("ONTOLOGY_GAUGE_127", "1:2:7=frozen_candidate_geometric_structure", "The gauge pattern is important but is not an action axiom.", "OWNER_AUTHORIZED_CANDIDATE_STATUS"),
        ("ONTOLOGY_FINE_STRUCTURE_CANDIDATE", "a_UV?=1/(12*pi^2) approximately 1/118.435; historical shorthand a?=1/118", "The fine-structure number is a historical geometric candidate only; its exact AE2 attachment, coupling normalization, and bare-to-dressed running remain underived.", "OWNER_AUTHORIZED_CANDIDATE_QUARANTINED"),
        ("ONTOLOGY_AE2_NO_CHILD_SELECTION", "AE2_glue != arbitrary_child_Cauchy_selector", "AE2 unifies event/child matter traces without selecting a child state by hand.", "OWNER_AUTHORIZED_DOMAIN_SEMANTICS"),
        ("ONTOLOGY_BARE_DRESSED", "dressed=derived_dressing_map(bare)", "Bare and dressed quantities are separate layers and dressing is not fitting freedom.", "OWNER_AUTHORIZED_LAYER_SEPARATION"),
        ("ONTOLOGY_FROZEN_NO_RETUNE", "new_derivation_disagreement => audit", "Frozen predictions never retune.", "OWNER_AUTHORIZED_FREEZE_RULE"),
        ("ONTOLOGY_FULL_COMPLETION", "complete=all_claimed_sectors+scale+domains+BRST+continuum+frozen_reproduction", "Full completion requires reproducible closure from one coherent current action.", "OWNER_AUTHORIZED_COMPLETION_RULE"),
        ("ONTOLOGY_FINITE_ENCAPSULATION", "realized_particle => 0<T_enc<infinity", "A realized particle completes encapsulation in finite positive physical time; infinite nonencapsulating histories remain mathematical but nonrealized.", "OWNER_AUTHORIZED_PHYSICAL_DOMAIN"),
        ("ONTOLOGY_ENCAPSULATION_CHRONOLOGY", "pre_encapsulation -> E0 -> C1 -> forward_evolution -> E1 -> C2", "Encapsulation completes at E0, which creates C1; after positive-duration forward evolution a later collision/de-encapsulation is a distinct event E1 creating a distinct child C2. There is no physical reset or return.", "OWNER_AUTHORIZED_PHYSICAL_DOMAIN"),
        ("ONTOLOGY_GATE7_ZERO_EXTERNAL_SOURCE", "D_xi Gamma_closed[P_joint;j_birth] at fixed j_birth, then j_birth=0", "Only the external BRST-quotiented Cauchy/birth trace is zero. Incoming M_f, transported M_C2, U_R, W_phys, and retained contact/incidence blocks remain nonzero internal responses, assembled and differentiated exactly once. Zero external source selects the retained Dirichlet reference at E0, so M_f=M11; it does not set M_f or any internal child/contact block to zero and does not add a pre-E0 response arm.", "OWNER_AUTHORIZED_PHYSICAL_SOURCE_SEMANTICS"),
    ]
    return [
        record(cid, formula, "ONTOLOGY_RECORD", "BHSM_ONTOLOGY", meaning,
               "current BHSM ontology", [source_ontology] if cid == "ONTOLOGY_GATE7_ZERO_EXTERNAL_SOURCE" else [finite] if cid in {
                   "ONTOLOGY_FINITE_ENCAPSULATION", "ONTOLOGY_ENCAPSULATION_CHRONOLOGY"
               } else [owner] if cid.startswith("ONTOLOGY_") and cid not in {
                   "ONTOLOGY_MAXIMAL_FORWARD_HISTORY", "ONTOLOGY_SINGLE_TIME", "ONTOLOGY_REFLECTION",
                   "ONTOLOGY_CONDITIONAL_RESET", "ONTOLOGY_AE2_DOMAIN", "ONTOLOGY_AE2_TRANSMISSION", "ONTOLOGY_FAR_END"
               } else [ae2], current_status=status,
               forbidden_interpretations=(
                   ["Set an internal response block to zero.", "Add an independent seam source or force.", "Treat the external birth trace as a dynamical integrated seam.", "Add a pre-E0 response arm."] if cid == "ONTOLOGY_GATE7_ZERO_EXTERNAL_SOURCE" else
                   ["Call owner-authorized AE2 ontology itself action-derived."] if cid == "ONTOLOGY_AE2_DOMAIN" else
                   ["Insert downstream Standard Model observables into the action."] if cid == "ONTOLOGY_NO_OBSERVABLE_UPSTREAM" else
                   ["Treat particles as primitive point substances."] if cid == "ONTOLOGY_PARTICLE_CLASS" else
                   ["Use independent freely chosen sector scales."] if cid == "ONTOLOGY_UNIVERSAL_SCALE" else
                   ["Use dressing as fitting freedom."] if cid == "ONTOLOGY_BARE_DRESSED" else
                   ["Retune a frozen prediction."] if cid == "ONTOLOGY_FROZEN_NO_RETUNE" else
                   ["Insert 1/118 or 1/(12*pi^2) into AE2.", "Fit the dressing map to alpha inverse 137.036.", "Use the candidate as a reset selector."] if cid == "ONTOLOGY_FINE_STRUCTURE_CANDIDATE" else []
               ))
        for cid, formula, meaning, status in rows
    ]


GATE_CHAIN = [
    ("G7_01_AE2_DOMAIN", "AE2 glued matter domain", "CLOSED"),
    ("G7_02_FIXED_CHANNEL", "fixed-channel forward operator", "CLOSED"),
    ("G7_03_SECTOR_CLASS", "sectorwise threshold classification", "CLOSED"),
    ("G7_04_NONFERMION", "nonfermionic threshold closure", "CLOSED"),
    ("G7_05_FACTORIZED_LAP", "all admissible positive far tails source-Dini by compact Volterra trace-class theorem", "CLOSED"),
    ("G7_06_E1_FINITE", "fixed-channel E1 source-measure finiteness", "CLOSED"),
    ("G7_07_ANGULAR_TAIL", "finite-endpoint compact-resolvent/source-trace control on the realized finite-encapsulation domain; infinite nonencapsulating tails remain nonrealized mathematical histories", "CLOSED_BY_OWNER_PHYSICAL_SCOPE_AND_LOCAL_ACTION_EXISTENCE"),
    ("G7_08_FORCE", "heat-minus-zeta functional, physical quotient criterion, finite-stratum regularity, moving-endpoint chain rules, inverse-free Weyl solver, and nested channel/Euler-Dirac adjoint pullback are derived; fixed-channel source-Dini and high-energy trace control remain closed; infinite nonencapsulating NHIM histories are preserved as nonrealized mathematics; the analytic full 57 by 196 historical reset Jacobian has rank 57 and its event block has certified rank 32, so the projection onto the 73-dimensional constrained child manifold is submersive; the certified incoming child germ therefore lifts to a nonempty local family with forward chronology E0 -> C1 ->[T>0] E1 -> C2, where E1 is a new event and C2 a new child; after the forward swap, the reset tangent projects to 72 outgoing C2 seed directions with a 67-dimensional fixed-seed lift kernel, and the exact action field Dlambda[F_0]=1 adds the transverse descriptor direction, certifying a 72+1=73 local C2 launch chart without selecting a member; the kernel statement is not full two-sided seam-force invariance: the downstream C2 covector annihilates that kernel exactly, and the kernel is exactly {0}_C2 direct sum ker(J_E1), the already-known raw preceding-event tangent; its force owner is therefore the complete upstream C1-to-E1 heat-minus-zeta history plus retained AE2 interface contacts, not a new local seam force; the AE2 fermion surface action is exactly zero, but this does not make the upstream force vanish, and M_f value or seam invertibility does not supply the full incoming bulk functional; the efficient exact assembly is one joint full-history forward-adjoint KKT solve, with the retained 66-dimensional time quotient handled intrinsically until its hybrid generator is derived; the launch chart, exact C2 fixed-s field, strict regular margins, and compact 1222-segment cover imply a nonempty local 73-parameter family of exact C2 histories and Jacobi fields through every finite-core prefix, so absence of any parametric base history is no longer the blocker; on every exact family member the signed node-radius and moving-duration coefficient cotangents now pull back by one inverse-free reverse state sweep and compose with the reset launch and complete upstream covectors, so 73 forward Jacobi columns and a new C2 response theory are unnecessary; the exact signed log-radius and log-lapse covectors and D(Ns/Delta)=Ns/Delta*(DlogN-DDelta/Delta) incidence are explicit, and the selected-line/hard-complement calculation now certifies a signed D_Y Delta partial plus a relative 2.79e-3 remainder ball at the reference center; the coarse full-operator transport ball contains zero, but Delta recombines exactly as Dlambda[b_Psi*Psi+s*V_hard], and preserving that cancellation reduces the exact-family zero-exclusion task to a rigorous enclosure of action Hessian row 86 below 14.6225 rather than a full 98 by 98 D2Delta norm; self-adjointness now removes every nested hard adjoint w3,w5,wI,wN,wVI,wfi from that row, leaving only local action/source jets, the existing first eigenline Jacobi matrix, its decisive column, z, and V_hard; two direct meshes and the fully reduced center replay give a stable row norm near 1.69e-5, about 8.6e5 below the ceiling, but these center calculations are not promoted to an interval theorem; the rigorous complete signed D2Delta row and all 1222 interval transposed exact moving-duration actions are now certified; only the external BRST-quotiented birth trace is set to zero after differentiation at fixed source, selecting the E0 Dirichlet reference while leaving the nonzero internal response M_f=M11 and every child/contact block intact; the pre-E0 M_E0 arm and B_birth reduction are therefore not current Gate-7 dependencies; the single joint heat cotangent seed and signed reverse equation are derived; the exact retained graded level weights are +24(m^2-1) for transverse gauge, -48(n+1)(n+2) for Weyl, and +4m^2 for HS, with longitudinal/complex-ghost cancellation, so neither grading nor multiplicity is missing; on the 1222 finite core the direct zeta node-radius and moving-duration cotangent is componentwise closed and the complete graded heat seed is retained as a nonzero log-space enclosure below 10^(-1.9e54); the accumulated node actions and all transposed duration actions certify the C2 zeta reset-cotangent norm ball without a transition matrix, while its signed center, the suppressed-heat geometry contraction, complete upstream C1 covector, and maximal projected tail remain open; the historical reset API is only the forward event-to-new-child glue, and no recurrence, universal reachability, or physical child selector is introduced; positive-duration local existence is now closed; the unique maximal M_C2 family is instantiated on the one certified C2 enclosure class, and the exact current owner is the quotient-Cauchy tail of the finite-core physical force net, or a finite later event/canonical stop; the ambient absolute weighted norm is sufficient but not necessary; after the fixed-C2 block and descriptor-flow direction are closed, the exact remaining owner is the 72-vector heat-smoothed relative-form tail on the reset-generated seed image; the moving-duration Ward identity makes the separate common-scale zeta core net identically zero, superseding its old optical-tail obligation, but it does not delete the nonzero common-scale heat trace, remove a seed direction, or close the non-scale joint tail; the stored finite-core heat suppression is not uniform under maximal exhaustion, the exact 1064-to-1222 low-axis Weyl net is not converged, and the finite-optical NHIM supplies no absolute graded-force shortcut, leaving exactly the signed rank-72 relative-form Cauchy theorem or an actual later event/canonical stop", "OPEN_CURRENT_OWNER"),
    ("G7_09_SADDLE", "same-action finite-endpoint forward-adjoint quotient KKT equations are derived but unsolved; a nonempty local positive-duration E0 -> C1 ->[T>0] E1 -> C2 family is certified, so the saddle route awaits the actual quotient-Cauchy heat-minus-zeta force limit or a finite later endpoint and remains mathematically coupled to G7_08 without adding a gate", "PENDING_COUPLED_TO_G7_08"),
    ("G7_10_HESSIAN", "pair-plus-contact Hessian", "PENDING"),
    ("G7_11_WARD_TRACE", "Ward/BRST and source-contracted relative trace", "PENDING"),
    ("G7_12_SCALAR_MAP", "basis-independent physical scalar map", "PENDING"),
    ("G7_13_CLOSE", "Gate 7 closure", "PENDING"),
]


def _gates() -> list[dict[str, Any]]:
    sources = {
        "G7_01_AE2_DOMAIN": "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_GLOBAL_SPIN_MATTER_DOMAIN.json",
        "G7_02_FIXED_CHANNEL": "artifacts/flagship_integration/BHSM_N12_FORWARD_FIXED_CHANNEL_TRANSFER.json",
        "G7_03_SECTOR_CLASS": "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_THRESHOLD_SUPERSESSION.json",
        "G7_04_NONFERMION": "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_NONFERMION_THRESHOLD_MARGIN.json",
        "G7_05_FACTORIZED_LAP": "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_COMPACT_SOURCE_DINI_CLOSURE.json",
        "G7_06_E1_FINITE": "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_COMPACT_SOURCE_DINI_CLOSURE.json",
        "G7_07_ANGULAR_TAIL": "artifacts/flagship_integration/BHSM_N12_GATE7_FINITE_ENCAPSULATION_PHYSICAL_DOMAIN_AUDIT.json",
        "G7_08_FORCE": [
            "artifacts/flagship_integration/BHSM_N12_PARAMETRIC_EXTERIOR_ORACLE_EXECUTABLE_INTERFACE.json",
            "artifacts/flagship_integration/BHSM_N12_FINITE_ENDPOINT_FORCE_SIGN_SHORTCUT_NO_GO.json",
            "artifacts/flagship_integration/BHSM_N12_NEGATIVE_AXIS_SEAM_HEAT_SYNTHESIS_NO_GO.json",
            "artifacts/flagship_integration/BHSM_N12_ACTION_OWNED_ENDPOINT_LOAD_REDUCTION.json",
            "artifacts/flagship_integration/BHSM_N12_RESET_STRATUM_MOVING_ENDPOINT_JETS.json",
            "artifacts/flagship_integration/BHSM_N12_FORCE_FIRST_JET_CRITICAL_PATH.json",
            "artifacts/flagship_integration/BHSM_N12_FORCE_ADJOINT_PULLBACK.json",
            "artifacts/flagship_integration/BHSM_N12_FINITE_ENDPOINT_FORWARD_ADJOINT_KKT.json",
            "artifacts/flagship_integration/BHSM_N12_FORWARD_ADJOINT_KKT_EXISTENCE_GATE.json",
            "artifacts/flagship_integration/BHSM_N12_SAME_ACTION_CONTINUATION_PRECONDITIONS.json",
            "artifacts/flagship_integration/BHSM_N12_DIRECT_KKT_EXISTENCE_PRECONDITIONS.json",
            "artifacts/flagship_integration/BHSM_N12_GATE7_FORMATION_DECAY_CHRONOLOGY_SUPERSESSION.json",
            "artifacts/flagship_integration/BHSM_N12_ASYMPTOTIC_CHILD_EXTERIOR_CONNECTION_PRECONDITIONS.json",
            "artifacts/flagship_integration/BHSM_N12_ASYMPTOTIC_NHIM_CAPTURE_BASIN.json",
            "artifacts/flagship_integration/BHSM_N12_MAXIMAL_FRIEDRICHS_WEYL_EXHAUSTION.json",
            "artifacts/flagship_integration/BHSM_N12_MAXIMAL_FORWARD_ADJOINT_EXHAUSTION.json",
            "artifacts/flagship_integration/BHSM_N12_C2_CLASS_REDUCED_MAXIMAL_RESPONSE.json",
            "artifacts/flagship_integration/BHSM_N12_C2_PROJECTED_ADJOINT_CAUCHY_CRITERION.json",
            "artifacts/flagship_integration/BHSM_N12_C2_INFINITE_HEAT_ZETA_COMPATIBILITY.json",
            "artifacts/flagship_integration/BHSM_N12_C2_EXACT_FIXED_S_FIELD_ORACLE.json",
            "artifacts/flagship_integration/BHSM_N12_C2_RESET_GENERATED_LAUNCH_CHART.json",
            "artifacts/flagship_integration/BHSM_N12_C2_RESET_LAUNCH_ADJOINT_INTERFACE.json",
            "artifacts/flagship_integration/BHSM_N12_C2_FIXED_SEED_UPSTREAM_FORCE_OWNER.json",
            "artifacts/flagship_integration/BHSM_N12_GATE7_MAXIMAL_TAIL_SUPPORT_REDUCTION.json",
            "artifacts/flagship_integration/BHSM_N12_GATE7_OUTGOING_FLOW_TAIL_CLOSURE.json",
            "artifacts/flagship_integration/BHSM_N12_GATE7_SEED_IMAGE_WARD_GAUGE_AUDIT.json",
            "artifacts/flagship_integration/BHSM_N12_GATE7_RANK72_RELATIVE_FORM_TAIL.json",
            "artifacts/flagship_integration/BHSM_N12_GATE7_RANK72_MAXIMAL_TAIL_ROUTE_ADJUDICATION.json",
            "artifacts/flagship_integration/BHSM_N12_AE2_CHILD_BOUNDARY_HAMILTONIAN_NON_SUPERSESSION.json",
            "artifacts/flagship_integration/BHSM_N12_GATE7_NHIM_RANK72_RELATIVE_TAIL_THEOREM.json",
            "artifacts/flagship_integration/BHSM_N12_C2_1222_PARAMETRIC_BASE_FAMILY.json",
            "artifacts/flagship_integration/BHSM_N12_C2_1222_SIGNED_ADJOINT_ASSEMBLY.json",
            "artifacts/flagship_integration/BHSM_N12_C2_1222_TRANSPOSED_DURATION_ACTION_COVERAGE.json",
            "artifacts/flagship_integration/BHSM_N12_GATE7_CLOSED_SYSTEM_ZERO_EXTERNAL_SOURCE_ONTOLOGY.json",
            "artifacts/flagship_integration/BHSM_N12_GATE7_BIRTH_TRACE_MF_SUPERSESSION_AUDIT.json",
            "artifacts/flagship_integration/BHSM_N12_GATE7_BIRTH_GRAPH_LOAD_MATCHING_AUDIT.json",
            "artifacts/flagship_integration/BHSM_N12_GATE7_TWO_SEAM_CLOSED_OPERATOR_ASSEMBLY.json",
            "artifacts/flagship_integration/BHSM_N12_GATE7_E0_EVENT_SIDE_RESPONSE_PROVENANCE_AUDIT.json",
            "artifacts/flagship_integration/BHSM_N12_GATE7_EXTERNAL_BIRTH_SOURCE_ROLE_SUPERSESSION.json",
            "artifacts/flagship_integration/BHSM_N12_GATE7_JOINT_HEAT_COTANGENT_REVERSE_SEED.json",
            "artifacts/flagship_integration/BHSM_N12_GATE7_1222_CORE_DIAGRAM_MATCHING_AUDIT.json",
            "artifacts/flagship_integration/BHSM_N12_GATE7_MAXIMAL_GRADED_COTANGENT_MATCHING_AUDIT.json",
            "artifacts/flagship_integration/BHSM_N12_GATE7_ONE_SEAM_FULL_GRADED_FINITE_CORE_HEAT_BOUND.json",
            "artifacts/flagship_integration/BHSM_N12_GATE7_DIRECT_ZETA_COEFFICIENT_COTANGENT.json",
            "artifacts/flagship_integration/BHSM_N12_GATE7_C2_FINITE_CORE_ZETA_RESET_COTANGENT_ENCLOSURE.json",
            "artifacts/flagship_integration/BHSM_N12_GATE7_JOINT_KKT_INFORMATION_GATE.json",
            "artifacts/flagship_integration/BHSM_N12_GATE7_INCOMING_AMPLITUDE_ZETA_COTANGENT.json",
            "artifacts/flagship_integration/BHSM_N12_GATE7_INCOMING_COMPLIANCE_REGULAR_CHART.json",
            "artifacts/flagship_integration/BHSM_N12_GATE7_INCOMING_GRADED_HEAT_DIFFERENTIABILITY.json",
            "artifacts/flagship_integration/BHSM_N12_GATE7_INCOMING_ZERO_AMPLITUDE_HEAT_ZETA_COMPARISON.json",
            "artifacts/flagship_integration/BHSM_N12_C2_SIGNED_DURATION_INCIDENCE_OWNER.json",
            "artifacts/flagship_integration/BHSM_N12_C2_SIGNED_DDELTA_SEED_TRANSPORT_AUDIT.json",
            "artifacts/flagship_integration/BHSM_N12_C2_DIRECT_DDELTA_ROW_RECONNAISSANCE.json",
            "artifacts/flagship_integration/BHSM_N12_C2_FULLY_REDUCED_SIGNED_ROW_CERTIFICATE.json",
            "artifacts/flagship_integration/BHSM_N12_C2_SUPPRESSED_HARD_RESPONSE_ROW_CERTIFICATE.json",
            "artifacts/flagship_integration/BHSM_N12_CORE_TRANSMITTED_PHYSICAL_MANIFOLD_AUDIT.json",
            "artifacts/flagship_integration/BHSM_N12_ASYMPTOTIC_NHIM_ANGULAR_FORCE_NO_GO.json",
            "artifacts/flagship_integration/BHSM_N12_LOCAL_RESET_TERMINAL_TRANSVERSALITY_AUDIT.json",
            "artifacts/flagship_integration/BHSM_N12_CANONICAL_MOMENTUM_ACTION_JACOBIAN.json",
            "artifacts/flagship_integration/BHSM_N12_FULL_RESET_ACTION_JACOBIAN.json",
            "artifacts/flagship_integration/BHSM_N12_FINITE_TERMINAL_RESET_STRATUM_CANDIDATE.json",
            "artifacts/flagship_integration/BHSM_N12_FINITE_TERMINAL_DIRECTED_CENTER.json",
            "artifacts/flagship_integration/BHSM_N12_FINITE_TERMINAL_RADII_CERTIFICATE.json",
            "artifacts/flagship_integration/BHSM_N12_FINITE_TERMINAL_MARGIN_TRANSFER.json",
            "artifacts/flagship_integration/BHSM_N12_FINITE_TERMINAL_ORIENTATION_CERTIFICATE.json",
            "artifacts/flagship_integration/BHSM_N12_FINITE_TERMINAL_FORWARD_COMPONENT_COMPATIBILITY.json",
            "artifacts/flagship_integration/BHSM_N12_FINITE_TERMINAL_EVENT_EIGENLINE_SOLUTION_BALL.json",
            "artifacts/flagship_integration/BHSM_N12_FINITE_TERMINAL_TWO_SIDED_FORWARD_INTERFACE.json",
        ],
        "G7_09_SADDLE": [
            "artifacts/flagship_integration/BHSM_N12_CONSTRAINT_PROJECTED_REPLACEMENT_SADDLE.json",
            "artifacts/flagship_integration/BHSM_N12_FINITE_ENDPOINT_FORWARD_ADJOINT_KKT.json",
            "artifacts/flagship_integration/BHSM_N12_FORWARD_ADJOINT_KKT_EXISTENCE_GATE.json",
            "artifacts/flagship_integration/BHSM_N12_SAME_ACTION_CONTINUATION_PRECONDITIONS.json",
            "artifacts/flagship_integration/BHSM_N12_DIRECT_KKT_EXISTENCE_PRECONDITIONS.json",
            "artifacts/flagship_integration/BHSM_N12_GATE7_FORMATION_DECAY_CHRONOLOGY_SUPERSESSION.json",
            "artifacts/flagship_integration/BHSM_N12_ASYMPTOTIC_CHILD_EXTERIOR_CONNECTION_PRECONDITIONS.json",
            "artifacts/flagship_integration/BHSM_N12_ASYMPTOTIC_NHIM_ANGULAR_FORCE_NO_GO.json",
            "artifacts/flagship_integration/BHSM_N12_LOCAL_RESET_TERMINAL_TRANSVERSALITY_AUDIT.json",
            "artifacts/flagship_integration/BHSM_N12_FINITE_TERMINAL_RESET_STRATUM_CANDIDATE.json",
            "artifacts/flagship_integration/BHSM_N12_FINITE_TERMINAL_RADII_CERTIFICATE.json",
            "artifacts/flagship_integration/BHSM_N12_FINITE_TERMINAL_ORIENTATION_CERTIFICATE.json",
        ],
    }
    fallback = "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_THRESHOLD_SUPERSESSION.json"
    rows = []
    for index, (cid, meaning, status) in enumerate(GATE_CHAIN):
        if cid == "G7_08_FORCE":
            meaning += (
                "; superseding the earlier center-only row status, the outward-"
                "rounded retained-action replay certifies the complete dominant "
                "bc row by 2.6787704214811163 < 14.622464650642785, leaving "
                "11.943694229161668 for the sole local s-suppressed hard-response "
                "row; the complete ten-term hard-response enclosure now bounds that "
                "row by 0.005348168974427062 and the combined signed D2Delta row by "
                "2.684118590455544, zero-excluding the local D_Y Delta component; "
                "the 98-to-73 orthogonal launch projection preserves the certified "
                "C2 zeta-ball radius and contains both zero and nonzero covectors; "
                "under the closed-system source ontology this retires every separate "
                "zero or zero-exclusion requirement on an internal component, so Gate 7 "
                "remains open for one combined signed heat-zeta-upstream-interface "
                "covector and the maximal projected tail or an actual finite stop; "
                "on the fixed-terminal incoming amplitude family the formation-zeta "
                "covector has an exact strict sign for every positive amplitude; the "
                "equivalent compliance chart C_f=M_f^-1=b/d removes the apparent "
                "M_f Laurent-jet singularity and makes each fixed-channel heat jet "
                "O(lambda); the finite-core Gaussian angular weights dominate the "
                "fixed polynomial transfer-jet loss, certifying differentiation "
                "through the full graded supertrace; at zero amplitude the exact "
                "rank-one Schur-pencil derivative and child mass bound make the "
                "finite-core heat coefficient strictly smaller than the zeta "
                "coefficient, proving positive joint amplitude sign on an "
                "unquantified punctured neighborhood; the full-box remainder, "
                "projected KKT root, and maximal tail remain open; the 67-dimensional "
                "fixed-C2 upstream/interface block and the separate incoming-amplitude "
                "coordinate now have full-graded maximal Cauchy tails by boundary-local "
                "functional calculus, so the remaining noncompact coefficient-Jacobi "
                "tail is supported only on the outgoing 72+1 C2 launch block"
                "; the extra F0 launch direction is the exact descriptor flow along "
                "one maximal child orbit, so its Weyl derivative is the local "
                "Riccati/Lie derivative and its zeta derivative is a moving-boundary "
                "term; the remaining noncompact tail is therefore the rank-72 reset-"
                "generated outgoing C2 seed image; AE2 closes only the fermion "
                "transmission domain and supplies no complete child boundary "
                "Hamiltonian or coercive charge; on every open family actually "
                "captured by the analytic finite-N12 NHIM, its bounded center and "
                "decaying normal Jacobi fields combine with the exact exp(-x) and "
                "exp(-2x) weights and the first-C2-collar Agmon factor to make the "
                "signed rank-72 relative tail Cauchy, so the current geometric "
                "owner is reset-to-capture connection or an actual later stop"
            )
        predecessor = [] if index == 0 else [GATE_CHAIN[index - 1][0]]
        provenance = sources.get(cid, fallback)
        if isinstance(provenance, str):
            provenance = [provenance]
        rows.append(record(
            cid, f"{predecessor or ['START']} -> {cid}", "GATE_DAG_NODE", "BHSM_ONTOLOGY", meaning,
            "current AE2 Gate7", provenance, current_status=status,
            source_weighting_required=cid in {"G7_05_FACTORIZED_LAP", "G7_06_E1_FINITE", "G7_11_WARD_TRACE"},
            downstream_consumers=[] if index == len(GATE_CHAIN) - 1 else [GATE_CHAIN[index + 1][0]],
            forbidden_interpretations=["Universal terminal return is a prerequisite.", "Chord 3 is a prerequisite."],
        ))
    return rows


def build_registries(input_hashes: Mapping[str, str]) -> dict[str, dict[str, Any]]:
    """Build all nine deterministic current registries from verified disk lineage."""

    basis = _with_hashes(_basis(), input_hashes)
    historical = _with_hashes(_historical(), input_hashes)
    gates = _with_hashes(_gates(), input_hashes)
    registries = {
        "BHSM_CURRENT_MATHEMATICAL_BASIS.json": {"records": basis},
        "BHSM_CURRENT_FORMULA_REGISTRY.json": {"records": basis + historical},
        "BHSM_FORMULA_EQUIVALENCE_GRAPH.json": {"records": _with_hashes(_equivalences(), input_hashes)},
        "BHSM_SYMBOL_NAMESPACE_REGISTRY.json": {"records": _with_hashes(_symbols(), input_hashes)},
        "BHSM_FORMULA_DEPRECATION_LEDGER.json": {"records": _with_hashes(_deprecations(), input_hashes)},
        "BHSM_DIMENSION_SCALE_LEDGER.json": {"records": _with_hashes(_dimensions(), input_hashes)},
        "BHSM_CURRENT_ONTOLOGY_REGISTRY.json": {"records": _with_hashes(_ontology(), input_hashes)},
        "BHSM_CURRENT_GATE_LEDGER.json": {"records": gates},
        "BHSM_CURRENT_COMPLETION_DAG.json": {"records": gates},
    }
    for name, payload in registries.items():
        payload.update({
            "artifact": name.removesuffix(".json"),
            "action_version": ACTION_VERSION,
            "ontology_version": ONTOLOGY_VERSION,
            "schema": "BHSM_CURRENT_SEMANTIC_RECORD_V1",
            "input_hashes": dict(sorted(input_hashes.items())),
            "validation_passed": False,
            "FULL_BHSM_COMPLETE": False,
        })
    validate_registries(registries)
    for payload in registries.values():
        payload["validation_passed"] = True
    return registries


def _active_text(registries: Mapping[str, Mapping[str, Any]]) -> str:
    parts = []
    active_names = {
        "BHSM_CURRENT_MATHEMATICAL_BASIS.json",
        "BHSM_CURRENT_FORMULA_REGISTRY.json",
        "BHSM_CURRENT_GATE_LEDGER.json",
        "BHSM_CURRENT_COMPLETION_DAG.json",
    }
    for name, payload in registries.items():
        if name not in active_names:
            continue
        for row in payload["records"]:
            parts.extend([
                str(row["formula"]), str(row["physical_meaning"]), str(row["current_status"]),
                " ".join(row["downstream_consumers"]),
            ])
    return "\n".join(parts).lower()


def validate_registries(registries: Mapping[str, Mapping[str, Any]]) -> None:
    """Fail on incomplete records or a forbidden current semantic regression."""

    expected = {
        "BHSM_CURRENT_MATHEMATICAL_BASIS.json", "BHSM_CURRENT_FORMULA_REGISTRY.json",
        "BHSM_FORMULA_EQUIVALENCE_GRAPH.json", "BHSM_SYMBOL_NAMESPACE_REGISTRY.json",
        "BHSM_FORMULA_DEPRECATION_LEDGER.json", "BHSM_DIMENSION_SCALE_LEDGER.json",
        "BHSM_CURRENT_ONTOLOGY_REGISTRY.json", "BHSM_CURRENT_GATE_LEDGER.json",
        "BHSM_CURRENT_COMPLETION_DAG.json",
    }
    if set(registries) != expected:
        raise ValueError("exactly nine current registries are required")
    ids: dict[str, str] = {}
    for name, payload in registries.items():
        for row in payload.get("records", []):
            missing = set(REQUIRED_RECORD_FIELDS) - set(row)
            if missing:
                raise ValueError(f"{name}:{row.get('canonical_id')} missing {sorted(missing)}")
            cid = row["canonical_id"]
            if name == "BHSM_SYMBOL_NAMESPACE_REGISTRY.json":
                symbol = row["formula"]
                prior = ids.get(symbol)
                if prior is not None and prior != row["physical_meaning"]:
                    raise ValueError(f"symbol collision: {symbol}")
                ids[symbol] = row["physical_meaning"]

    current = _active_text(registries)
    forbidden_active = {
        "z=p^2": "z may not be identified with p^2",
        "strict gap required": "strict gap may not be a Gate7 requirement",
        "zero resonance => infrared divergence": "zero resonance is not automatic divergence",
        "terminal return required": "terminal recurrence is not required",
        "d5/kato interval sign ->": "D5/Kato is not the native Gate7 owner",
        "periodic fourier object required": "periodic Fourier objects are not current Gate7 inputs",
        "far friedrichs selects birth": "far-end closure cannot select the birth graph",
        "ae2 ontology is action-derived": "AE2 ontology is owner-authorized, not action-derived",
        "local energy is physical mass": "local energy is not physical mass",
        "full trace-class theorem required": "source-contracted relative trace control is sufficient",
        "generic operator-valued history required": "fixed-channel reduction is canonical",
        "equivalent forms are independent laws": "equivalent representations are not independent physics",
    }
    for phrase, message in forbidden_active.items():
        if phrase in current:
            raise ValueError(message)

    formula_rows = registries["BHSM_CURRENT_FORMULA_REGISTRY.json"]["records"]
    by_id = {row["canonical_id"]: row for row in formula_rows}
    if by_id["SOURCE_WEIGHTED_THRESHOLD_MEASURE"]["current_status"] != "DINI_CLOSED_ALL_ADMISSIBLE_TAILS_BY_COMPACT_VOL_TERRA_TRACE_CLASS":
        raise ValueError("factorized source-measure reduction status regressed")
    if by_id["NONFERMION_THRESHOLD_CLOSURE"]["current_status"] != "CLOSED_DO_NOT_REOPEN_WITHOUT_CONTRADICTION":
        raise ValueError("nonfermion threshold closure was reopened")
    if any(row["current_status"] == "CURRENT_ACTION_INPUT" for row in formula_rows if row["canonical_id"] in {
        "GAUGE_127_PATTERN", "CKM_FROZEN_OUTPUT", "CKM_EXPONENT_1_16", "CHARGED_ETA_L", "CHARGED_RHO_CH", "Z_VIRT_U2"
    }):
        raise ValueError("historical/frozen output became an AE2 action input")
    ontology = {row["canonical_id"]: row for row in registries["BHSM_CURRENT_ONTOLOGY_REGISTRY.json"]["records"]}
    if ontology["ONTOLOGY_AE2_DOMAIN"]["current_status"] != "OWNER_AUTHORIZED_THEORY_VERSION_DECISION":
        raise ValueError("AE2 ontology was misclassified as action-derived")
    required_owner_ontology = {
        "ONTOLOGY_GEOMETRY_FIRST", "ONTOLOGY_NO_OBSERVABLE_UPSTREAM", "ONTOLOGY_PARTICLE_CLASS",
        "ONTOLOGY_GENERATIONS", "ONTOLOGY_MASS_READOUT", "ONTOLOGY_UNIVERSAL_SCALE",
        "ONTOLOGY_NEUTRINO_MASS", "ONTOLOGY_CKM", "ONTOLOGY_GAUGE_127",
        "ONTOLOGY_AE2_NO_CHILD_SELECTION", "ONTOLOGY_BARE_DRESSED",
        "ONTOLOGY_FROZEN_NO_RETUNE", "ONTOLOGY_FULL_COMPLETION",
        "ONTOLOGY_FINITE_ENCAPSULATION", "ONTOLOGY_ENCAPSULATION_CHRONOLOGY",
        "ONTOLOGY_GATE7_ZERO_EXTERNAL_SOURCE",
    }
    if not required_owner_ontology <= set(ontology):
        raise ValueError("recovered Norman owner ontology is incomplete")
    if any(not ontology[cid]["current_status"].startswith("OWNER_AUTHORIZED") for cid in required_owner_ontology):
        raise ValueError("owner ontology was downgraded or reclassified as action-derived")
    source_ontology = ontology["ONTOLOGY_GATE7_ZERO_EXTERNAL_SOURCE"]
    if not (
        source_ontology["formula"]
        == "D_xi Gamma_closed[P_joint;j_birth] at fixed j_birth, then j_birth=0"
        and "Only the external BRST-quotiented Cauchy/birth trace is zero."
        in source_ontology["physical_meaning"]
        and "M_f=M11"
        in source_ontology["physical_meaning"]
    ):
        raise ValueError("Gate7 zero-external-source ontology regressed")
    equivalences = registries["BHSM_FORMULA_EQUIVALENCE_GRAPH.json"]["records"]
    if any(row["current_status"] != "EQUIVALENT_NOT_INDEPENDENT_PHYSICS" for row in equivalences):
        raise ValueError("equivalent forms were promoted to independent laws")
    dag = registries["BHSM_CURRENT_COMPLETION_DAG.json"]["records"]
    open_nodes = [row["canonical_id"] for row in dag if row["current_status"] == "OPEN_CURRENT_OWNER"]
    if open_nodes != ["G7_08_FORCE"]:
        raise ValueError("completion DAG has the wrong current owner")
