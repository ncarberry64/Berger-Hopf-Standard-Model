"""Canonical AE2/Gate-7 semantic registries and regression guardrails."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Iterable, Mapping


ACTION_VERSION = "BHSM-AE-2.0.0"
ONTOLOGY_VERSION = "BHSM-AE2-ONTOLOGY-1.0.0"
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
        )
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
    rows = [
        ("ONTOLOGY_MAXIMAL_FORWARD_HISTORY", "H_max^+", "Primary dynamical object is a maximal forward geometric history.", "ACTION_REQUIRED"),
        ("ONTOLOGY_SINGLE_TIME", "dt>0 and d_tau>0", "Physical time has one orientation.", "INTERNAL_CONSISTENCY_REQUIRED"),
        ("ONTOLOGY_REFLECTION", "reflection(H^+) != physical second orientation", "Formal reflection is a non-gauge Cauchy-state pairing.", "INTERPRETIVE_CORRECTION"),
        ("ONTOLOGY_CONDITIONAL_RESET", "event_hit => mathcal_R_reset", "Reset is applied if the certified event is reached.", "ACTION_REQUIRED"),
        ("ONTOLOGY_AE2_DOMAIN", "Spin x G_SM reset-glued bundle", "Owner-authorized AE2 global event-child matter domain.", "OWNER_AUTHORIZED_THEORY_VERSION_DECISION"),
        ("ONTOLOGY_AE2_TRANSMISSION", "delta S_AE2=0 => transmission law", "Transmission laws derived on AE2 may be action-derived within AE2.", "ACTION_DERIVED_WITHIN_AE2"),
        ("ONTOLOGY_FAR_END", "event reset if hit; Friedrichs otherwise where applicable", "Far-end completion does not select the birth graph.", "ACTION_DOMAIN_REQUIRED"),
        ("ONTOLOGY_GEOMETRY_FIRST", "geometry -> emergent SM interpretation", "Geometry is microscopic and Standard Model language is downstream.", "OWNER_AUTHORIZED_ONTOLOGY"),
        ("ONTOLOGY_NO_OBSERVABLE_UPSTREAM", "action -> theorem -> observable -> frozen comparison", "Advertised observables must be derived and never inserted upstream.", "OWNER_AUTHORIZED_DEPENDENCY_DIRECTION"),
        ("ONTOLOGY_PARTICLE_CLASS", "particle=[persistent geometric mode/history]", "Particles are persistent geometric mode/history equivalence classes.", "OWNER_AUTHORIZED_ONTOLOGY"),
        ("ONTOLOGY_GENERATIONS", "generation_slots=(base,excitation_1,excitation_2)", "Three generations are one base mode plus two excitation slots of one architecture.", "OWNER_AUTHORIZED_ONTOLOGY"),
        ("ONTOLOGY_MASS_READOUT", "m_phys=action_owned_response_plus_universal_scale_map", "Mass is a geometric propagation/boundary response readout, not primitive or local energy.", "OWNER_AUTHORIZED_OBSERVABLE_SEMANTICS"),
        ("ONTOLOGY_UNIVERSAL_SCALE", "physical_scale=universal_action_derived_origin", "Sector differences reside in dimensionless geometric responses, not free sector scales.", "OWNER_AUTHORIZED_DIMENSIONAL_SEMANTICS"),
        ("ONTOLOGY_NEUTRINO_MASS", "m_nu=propagation_locked_curvature_response", "Neutrino mass is a propagation response rather than primitive static rest mass.", "OWNER_AUTHORIZED_OBSERVABLE_SEMANTICS"),
        ("ONTOLOGY_CKM", "V_CKM=relative_orientation(up_response_basis,down_response_basis)", "CKM is the mismatch of action-selected up/down geometric response sectors.", "OWNER_AUTHORIZED_OBSERVABLE_SEMANTICS"),
        ("ONTOLOGY_GAUGE_127", "1:2:7=frozen_candidate_geometric_structure", "The gauge pattern is important but is not an action axiom.", "OWNER_AUTHORIZED_CANDIDATE_STATUS"),
        ("ONTOLOGY_AE2_NO_CHILD_SELECTION", "AE2_glue != arbitrary_child_Cauchy_selector", "AE2 unifies event/child matter traces without selecting a child state by hand.", "OWNER_AUTHORIZED_DOMAIN_SEMANTICS"),
        ("ONTOLOGY_BARE_DRESSED", "dressed=derived_dressing_map(bare)", "Bare and dressed quantities are separate layers and dressing is not fitting freedom.", "OWNER_AUTHORIZED_LAYER_SEPARATION"),
        ("ONTOLOGY_FROZEN_NO_RETUNE", "new_derivation_disagreement => audit", "Frozen predictions never retune.", "OWNER_AUTHORIZED_FREEZE_RULE"),
        ("ONTOLOGY_FULL_COMPLETION", "complete=all_claimed_sectors+scale+domains+BRST+continuum+frozen_reproduction", "Full completion requires reproducible closure from one coherent current action.", "OWNER_AUTHORIZED_COMPLETION_RULE"),
        ("ONTOLOGY_FINITE_ENCAPSULATION", "realized_particle => 0<T_enc<infinity", "A realized particle completes encapsulation in finite positive physical time; infinite nonencapsulating histories remain mathematical but nonrealized.", "OWNER_AUTHORIZED_PHYSICAL_DOMAIN"),
        ("ONTOLOGY_ENCAPSULATION_CHRONOLOGY", "formation -> singular_event -> complete_child_reset -> decay_or_evolution", "Encapsulation is completed by the pre-event history at the singular event; the reset image is post-encapsulation child data and is not required to return.", "OWNER_AUTHORIZED_PHYSICAL_DOMAIN"),
    ]
    return [
        record(cid, formula, "ONTOLOGY_RECORD", "BHSM_ONTOLOGY", meaning,
               "current BHSM ontology", [finite] if cid in {
                   "ONTOLOGY_FINITE_ENCAPSULATION", "ONTOLOGY_ENCAPSULATION_CHRONOLOGY"
               } else [owner] if cid.startswith("ONTOLOGY_") and cid not in {
                   "ONTOLOGY_MAXIMAL_FORWARD_HISTORY", "ONTOLOGY_SINGLE_TIME", "ONTOLOGY_REFLECTION",
                   "ONTOLOGY_CONDITIONAL_RESET", "ONTOLOGY_AE2_DOMAIN", "ONTOLOGY_AE2_TRANSMISSION", "ONTOLOGY_FAR_END"
               } else [ae2], current_status=status,
               forbidden_interpretations=(
                   ["Call owner-authorized AE2 ontology itself action-derived."] if cid == "ONTOLOGY_AE2_DOMAIN" else
                   ["Insert downstream Standard Model observables into the action."] if cid == "ONTOLOGY_NO_OBSERVABLE_UPSTREAM" else
                   ["Treat particles as primitive point substances."] if cid == "ONTOLOGY_PARTICLE_CLASS" else
                   ["Use independent freely chosen sector scales."] if cid == "ONTOLOGY_UNIVERSAL_SCALE" else
                   ["Use dressing as fitting freedom."] if cid == "ONTOLOGY_BARE_DRESSED" else
                   ["Retune a frozen prediction."] if cid == "ONTOLOGY_FROZEN_NO_RETUNE" else []
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
    ("G7_08_FORCE", "heat-minus-zeta functional, physical quotient criterion, fixed-stratum oracle regularity, and quotient-robust radius-jet variation derived; actual parametric exterior oracle remains open", "OPEN_CURRENT_OWNER"),
    ("G7_09_SADDLE", "same-action joint constrained saddle, mathematically coupled to G7_08 without adding a gate", "PENDING_COUPLED_TO_G7_08"),
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
        "G7_08_FORCE": "artifacts/flagship_integration/BHSM_N12_RESET_FIBER_RADIUS_JET_AND_SCALE_CENTER_AUDIT.json",
    }
    fallback = "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_THRESHOLD_SUPERSESSION.json"
    rows = []
    for index, (cid, meaning, status) in enumerate(GATE_CHAIN):
        predecessor = [] if index == 0 else [GATE_CHAIN[index - 1][0]]
        rows.append(record(
            cid, f"{predecessor or ['START']} -> {cid}", "GATE_DAG_NODE", "BHSM_ONTOLOGY", meaning,
            "current AE2 Gate7", [sources.get(cid, fallback)], current_status=status,
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
    }
    if not required_owner_ontology <= set(ontology):
        raise ValueError("recovered Norman owner ontology is incomplete")
    if any(not ontology[cid]["current_status"].startswith("OWNER_AUTHORIZED") for cid in required_owner_ontology):
        raise ValueError("owner ontology was downgraded or reclassified as action-derived")
    equivalences = registries["BHSM_FORMULA_EQUIVALENCE_GRAPH.json"]["records"]
    if any(row["current_status"] != "EQUIVALENT_NOT_INDEPENDENT_PHYSICS" for row in equivalences):
        raise ValueError("equivalent forms were promoted to independent laws")
    dag = registries["BHSM_CURRENT_COMPLETION_DAG.json"]["records"]
    open_nodes = [row["canonical_id"] for row in dag if row["current_status"] == "OPEN_CURRENT_OWNER"]
    if open_nodes != ["G7_08_FORCE"]:
        raise ValueError("completion DAG has the wrong current owner")
