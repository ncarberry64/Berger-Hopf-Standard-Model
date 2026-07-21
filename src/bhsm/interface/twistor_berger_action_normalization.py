"""BHSM v6.0.9 P1 action normalization on the twistor--Berger geometry.

The module is deliberately off shell.  It normalizes the fixed P1 branch and
records the Lorentzian lapse constraint that prevents a spatial-potential
critical point from being advertised as a parent vacuum.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Iterable

from .twistor_berger_associated_bundle import branching_row


VERSION = "v6.0.9"
SPRINT = "bhsm-twistor-berger-action-normalization-v6-0-9"
PRIMARY_RESULT = "BHSM_TWISTOR_BERGER_ACTION_NORMALIZATION_DERIVED_CONDITIONALLY"

ARTIFACT_FILES = {
    "conventions": "BHSM_twistor_berger_normalization_convention_ledger_v6_0_9.json",
    "measure": "BHSM_physical_fiber_measure_v6_0_9.json",
    "curvature": "BHSM_P1_twistor_berger_curvature_reduction_v6_0_9.json",
    "connection": "BHSM_connection_kinetic_matrix_v6_0_9.json",
    "connection_map": "BHSM_canonical_connection_field_map_v6_0_9.json",
    "moduli": "BHSM_modulus_kinetic_potential_reduction_v6_0_9.json",
    "multiplets": "BHSM_canonical_multiplet_normalization_v6_0_9.json",
    "cubic": "BHSM_cubic_overlap_tensor_v6_0_9.json",
    "quartic": "BHSM_quartic_overlap_tensor_v6_0_9.json",
    "selection": "BHSM_overlap_selection_rules_v6_0_9.json",
    "gap": "BHSM_berger_tower_spectral_gap_v6_0_9.json",
    "tower": "BHSM_tree_level_tower_integration_v6_0_9.json",
    "eft": "BHSM_tower_EFT_error_bound_v6_0_9.json",
    "action": "BHSM_normalized_twistor_berger_effective_action_v6_0_9.json",
    "lovelock": "BHSM_P2_P3_correction_ledger_v6_0_9.json",
    "parent_v5": "BHSM_parent_to_v5_normalized_coefficient_map_v6_0_9.json",
    "sigma": "BHSM_sigma_parent_identification_audit_v6_0_9.json",
    "gauge": "BHSM_gauge_sector_normalization_readiness_v6_0_9.json",
    "fermion": "BHSM_fermion_sector_normalization_readiness_v6_0_9.json",
    "scale": "BHSM_scale_stationarity_audit_v6_0_9.json",
    "stability": "BHSM_reduced_stability_hessian_v6_0_9.json",
    "hidden": "BHSM_action_normalization_hidden_input_audit_v6_0_9.json",
    "report": "BHSM_twistor_berger_action_normalization_report_v6_0_9.json",
}

GUARDS = {
    "fixed_parent_branch": "P1",
    "p2_p3_used_to_repair_p1": False,
    "v6_0_8_architecture_preserved": True,
    "v6_0_7_topological_obstruction_preserved": True,
    "s4_identified_as_observed_spacetime": False,
    "standard_model_gauge_group_derived": False,
    "physical_gauge_coupling_derived": False,
    "particle_or_generation_identification_made": False,
    "measured_input_used": False,
    "absolute_scale_derived": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
    "full_bhsm_completion_claimed": False,
}


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _positive(*values: float) -> None:
    if not values or any(value <= 0 for value in values):
        raise ValueError("all scales and kinetic coefficients must be positive")


def volumes(L4: float, L2: float, L1: float) -> dict[str, float]:
    """Physical volumes in the repository Maurer--Cartan convention."""
    _positive(L4, L2, L1)
    return {
        "S1": 4 * math.pi * L1,
        "S2": 4 * math.pi * L2**2,
        "S3": 16 * math.pi**2 * L2**2 * L1,
        "S4": 8 * math.pi**2 * L4**4 / 3,
        "CP3": 32 * math.pi**3 * L4**4 * L2**2 / 3,
        "S7": 128 * math.pi**4 * L4**4 * L2**2 * L1 / 3,
    }


def fiber_scalar_curvature(L2: float, L1: float) -> float:
    _positive(L2, L1)
    return 2 / L2**2 - L1**2 / (2 * L2**4)


def p1_scalar_curvature(L4: float, L2: float, L1: float) -> float:
    """Constant-modulus scalar curvature including Hopf-connection curvature."""
    _positive(L4, L2, L1)
    return (
        12 / L4**2
        + fiber_scalar_curvature(L2, L1)
        - (2 * L2**2 + L1**2) / L4**4
    )


def connection_kinetic_matrix(kappa1: float, L2: float, L1: float) -> list[list[float]]:
    """K_ab in -1/4 K_ab F^a F^b after physical S3 integration."""
    _positive(kappa1, L2, L1)
    vf = volumes(1.0, L2, L1)["S3"]
    values = [kappa1 * vf * L2**2 / 2, kappa1 * vf * L2**2 / 2, kappa1 * vf * L1**2 / 2]
    return [[values[i] if i == j else 0.0 for j in range(3)] for i in range(3)]


def canonical_connection_scales(kappa1: float, L2: float, L1: float) -> tuple[float, float, float]:
    matrix = connection_kinetic_matrix(kappa1, L2, L1)
    return tuple(math.sqrt(matrix[i][i]) for i in range(3))


def canonical_multiplet_coefficient(Z_parent: float, L2: float, L1: float) -> float:
    _positive(Z_parent, L2, L1)
    return Z_parent * volumes(1.0, L2, L1)["S3"]


def canonical_interaction_coefficient(
    g_parent: float, degree: int, normalized_overlap: float, Z_parent: float, L2: float, L1: float
) -> float:
    if not isinstance(degree, int) or isinstance(degree, bool) or degree < 3:
        raise ValueError("interaction degree must be an integer at least three")
    _positive(Z_parent, L2, L1)
    vf = volumes(1.0, L2, L1)["S3"]
    return g_parent * normalized_overlap * Z_parent ** (-degree / 2) * vf ** (1 - degree / 2)


def _valid_mode(two_j: int, weight: int) -> None:
    if not isinstance(two_j, int) or isinstance(two_j, bool) or two_j < 0:
        raise ValueError("two_j must be a nonnegative integer")
    if not isinstance(weight, int) or isinstance(weight, bool):
        raise ValueError("weight must be integral")
    if abs(weight) > two_j or (two_j - weight) % 2:
        raise ValueError("invalid U(1) weight for the representation")


def cubic_channel_allowed(modes: Iterable[tuple[int, int]]) -> bool:
    rows = list(modes)
    if len(rows) != 3:
        raise ValueError("exactly three modes are required")
    for mode in rows:
        _valid_mode(*mode)
    js = [row[0] for row in rows]
    return (
        sum(row[1] for row in rows) == 0
        and max(js) <= sum(js) - max(js)
        and sum(js) % 2 == 0
    )


def quartic_channel_allowed(modes: Iterable[tuple[int, int]]) -> bool:
    rows = list(modes)
    if len(rows) != 4:
        raise ValueError("exactly four modes are required")
    for mode in rows:
        _valid_mode(*mode)
    if sum(row[1] for row in rows) != 0 or sum(row[0] for row in rows) % 2:
        return False
    possible_12 = set(range(abs(rows[0][0] - rows[1][0]), rows[0][0] + rows[1][0] + 1, 2))
    possible_34 = set(range(abs(rows[2][0] - rows[3][0]), rows[2][0] + rows[3][0] + 1, 2))
    return bool(possible_12 & possible_34)


def spectral_gap(L2: float, L1: float) -> dict[str, Any]:
    """Exact vertical gap above the retained scalar singlet."""
    _positive(L2, L1)
    half_spin = 1 / (2 * L2**2) + 1 / (4 * L1**2)
    spin_one_zero_weight = 2 / L2**2
    ratio2 = (L1 / L2) ** 2
    if math.isclose(ratio2, 1 / 6, rel_tol=1e-12, abs_tol=1e-12):
        channel = "degenerate (J=1/2,|m|=1/2) and (J=1,m=0)"
    elif ratio2 > 1 / 6:
        channel = "(J=1/2,|m|=1/2)"
    else:
        channel = "(J=1,m=0)"
    return {
        "gap": min(half_spin, spin_one_zero_weight),
        "half_spin_candidate": half_spin,
        "spin_one_zero_weight_candidate": spin_one_zero_weight,
        "lowest_channel": channel,
        "crossing_ratio_squared": 1 / 6,
    }


def tower_error_bound(energy_squared: float, gap: float, source_scale: float = 0.0) -> dict[str, float | bool]:
    if energy_squared < 0 or source_scale < 0 or gap <= 0:
        raise ValueError("energy/source scales must be nonnegative and the gap positive")
    controlled = energy_squared < gap and source_scale < gap
    return {
        "controlled": controlled,
        "epsilon": max(energy_squared / gap, source_scale / gap),
        "resolvent_norm_bound": math.inf if energy_squared >= gap else 1 / (gap - energy_squared),
        "derivative_remainder_bound": math.inf if energy_squared >= gap else energy_squared / (gap - energy_squared),
    }


def dewit_log_metric() -> list[list[int]]:
    """ADM DeWitt form for block dimensions (4,2,1), after GHY."""
    return [[-12, -8, -4], [-8, -2, -2], [-4, -2, 0]]


def shape_log_metric() -> list[list[float]]:
    """Metric in rho=(4u4+2u2+u1)/7, beta=u1-u2, gamma=u2-u4."""
    return [[-42.0, 0.0, 0.0], [0.0, 6 / 7, 4 / 7], [0.0, 4 / 7, 12 / 7]]


def fixed_lapse_stationary_branches(kappa0: float, kappa1: float) -> list[dict[str, Any]]:
    _positive(kappa0, kappa1)
    return [
        {"name": "round", "L2_over_L4": 1.0, "L1_over_L4": 1.0, "L4_squared": 15 * kappa1 / (2 * kappa0)},
        {"name": "Jensen-squashed", "L2_over_L4": 1 / math.sqrt(5), "L1_over_L4": 1 / math.sqrt(5), "L4_squared": 27 * kappa1 / (2 * kappa0)},
    ]


def _common(name: str) -> dict[str, Any]:
    return {
        "artifact": name,
        "version": VERSION,
        "sprint": SPRINT,
        "primary_result": PRIMARY_RESULT,
        "claim_boundary": "Exact normalization statements are off-shell or explicitly conditioned. No observed-spacetime, particle, coupling, absolute-unit, or full-BHSM claim follows.",
        **GUARDS,
    }


def build_artifact_payloads(repo_root: Path | None = None) -> dict[str, dict[str, Any]]:
    _ = repo_root
    convention = {
        **_common("BHSM_twistor_berger_normalization_convention_ledger_v6_0_9"),
        "status": "BHSM_TWISTOR_BERGER_CONVENTIONS_FROZEN",
        "parent_action": "S_P1=1/2 integral_M8 sqrt(-G)(kappa1 R-kappa0)+GHY+declared fields",
        "domain": "M8=R_t x S7, Lorentzian signature (-,+,+,+,+,+,+,+)",
        "maurer_cartan": "d sigma1=-sigma2 wedge sigma3 cyclically",
        "generator_convention": "[T_a,T_b]=epsilon_abc T_c; tr_fund(T_a T_b)=-delta_ab/2",
        "u1_weight": "q=2m integral",
        "laplacian": "-Delta is nonnegative",
        "orientation": "vol7=vol4 wedge sigma1 wedge sigma2 wedge sigma3",
        "standard_to_repository_radius_bridge": "R_standard=2 L_repository at the round point",
    }
    measure = {
        **_common("BHSM_physical_fiber_measure_v6_0_9"),
        "status": "BHSM_PHYSICAL_FIBER_MEASURE_DERIVED",
        "physical_volumes": {"S1": "4 pi L1", "S2": "4 pi L2^2", "S3": "16 pi^2 L2^2 L1", "S4": "8 pi^2 L4^4/3", "CP3": "32 pi^3 L4^4 L2^2/3", "S7": "128 pi^4 L4^4 L2^2 L1/3"},
        "normalized_Haar": "dnu_F=dmu_F/Vol(F)",
        "round_check": "L4=L2=L1=R/2 gives Vol(S7)=pi^4 R^7/3",
        "pushforward_composes": "Vol(S1) Vol(S2)=Vol(S3)",
    }
    curvature = {
        **_common("BHSM_P1_twistor_berger_curvature_reduction_v6_0_9"),
        "status": "BHSM_P1_TWISTOR_BERGER_CURVATURE_REDUCTION_DERIVED",
        "connection_metric_identity": "R7=R4+R_F-(1/4) h_ab F^a_mn F^(b,mn)",
        "fiber_scalar": "R_F=2/L2^2-L1^2/(2 L2^4)",
        "hopf_curvature_norm": "|F^a|^2=4/L4^4 for each a in the frozen convention",
        "scalar_curvature": "R7=12/L4^2+2/L2^2-L1^2/(2L2^4)-(2L2^2+L1^2)/L4^4",
        "round_check": "L4=L2=L1=R/2 gives R7=42/R^2",
        "variable_moduli": "after adding GHY and integrating by parts, base derivatives are governed by the displayed ADM/DeWitt log-modulus matrix",
        "boundary_completion": "GHY cancels the normal metric-derivative variation on an actual M8 boundary; internal Hopf fibers are not boundaries",
    }
    connection = {
        **_common("BHSM_connection_kinetic_matrix_v6_0_9"),
        "status": "BHSM_HOPF_CONNECTION_KINETIC_NORMALIZATION_DERIVED",
        "definition": "L_5 contains -(1/4)K_ab F^a F^b",
        "matrix": "K=(kappa1 Vol(F)/2) diag(L2^2,L2^2,L1^2)",
        "entries": ["8 pi^2 kappa1 L2^4 L1", "8 pi^2 kappa1 L2^4 L1", "8 pi^2 kappa1 L2^2 L1^3"],
        "positivity": "positive and nondegenerate iff kappa1,L1,L2>0",
        "s1_first_composition": "(2 pi kappa1 L1^3)(4 pi L2^2)=K_33",
        "bundle_roles": {
            "Sp1": "quaternionic Hopf transport on S3->S7->S4; K_ab is its connection-metric coefficient matrix",
            "U1": "right-circle connection on S1->S7->CP3; the a=3 coefficient is recovered by S1-first then S2 pushforward",
            "twistor_S2": "associated homogeneous directions transported by the Sp1 connection; not an independent principal gauge field in P1",
        },
    }
    connection_map = {
        **_common("BHSM_canonical_connection_field_map_v6_0_9"),
        "status": "BHSM_CANONICAL_CONNECTION_FIELD_MAP_DERIVED",
        "map": "A_can^a=sqrt(K_aa) A^a (no sum)",
        "representation_map": "rho_can(T_a)=rho(T_a)/sqrt(K_aa)",
        "structure_constants": "f_can^a_bc=sqrt(K_aa) f^a_bc/[sqrt(K_bb)sqrt(K_cc)]",
        "anisotropy_warning": "For L1!=L2 this is not one Sp(1)-invariant gauge coupling; the metric preserves only right U(1).",
        "physical_coupling": None,
    }
    moduli = {
        **_common("BHSM_modulus_kinetic_potential_reduction_v6_0_9"),
        "status": "BHSM_P1_MODULUS_REDUCTION_DERIVED_OFF_SHELL",
        "log_variables": ["u4=ln L4", "u2=ln L2", "u1=ln L1"],
        "dewit_matrix": dewit_log_metric(),
        "nonredundant_variables": ["rho=(4u4+2u2+u1)/7", "beta=u1-u2", "gamma=u2-u4"],
        "transformed_matrix": shape_log_metric(),
        "shape_eigenvalues": [2, 4 / 7],
        "conformal_mode": "negative rho direction is lapse-constrained, not by itself a propagating ghost",
        "potential": "U=(Vol(S7)/2)[kappa0-kappa1 R7] in the fixed-lapse spatial reduction",
        "einstein_frame_dependency": "fully canonical lower-dimensional moduli require a declared Weyl frame",
    }
    multiplets = {
        **_common("BHSM_canonical_multiplet_normalization_v6_0_9"),
        "status": "BHSM_BERGER_MULTIPLET_CANONICAL_NORMALIZATION_DERIVED",
        "mode_norm": "integral_F dnu conjugate(Y_A)Y_B=delta_AB",
        "raw_kinetic": "Z_(J,m)=Z_parent Vol(F)",
        "canonical_field": "phi_can=sqrt(Z_parent Vol(F)) phi",
        "p_point_coupling": "g_can=g_parent I_p Z_parent^(-p/2) Vol(F)^(1-p/2)",
        "unit_kinetic_assumed_early": False,
    }
    cubic = {
        **_common("BHSM_cubic_overlap_tensor_v6_0_9"),
        "status": "BHSM_CUBIC_OVERLAP_TENSOR_DERIVED",
        "basis": "Y^J_nm=sqrt(2J+1) D^J_nm under normalized Haar",
        "formula": "I3=sqrt(prod_i(2Ji+1)) (3j[n1,n2,n3])(3j[m1,m2,m3])",
        "exact_low_modes": {"I_000": 1, "I_0_A_Abar": 1},
        "physical_basis_values": {"C_000": "Vol(F)^(-1/2)"},
    }
    quartic = {
        **_common("BHSM_quartic_overlap_tensor_v6_0_9"),
        "status": "BHSM_QUARTIC_OVERLAP_TENSOR_DERIVED",
        "formula": "recoupling sum over common intermediate spin using two Clebsch-Gordan pairs",
        "exact_low_modes": {"I_0000": 1, "I_00_A_Abar": 1},
        "physical_basis_values": {"Q_0000": "Vol(F)^(-1)"},
        "derivative_overlaps": "same representation/weight rules; values are action-specific Casimir contractions",
    }
    selection = {
        **_common("BHSM_overlap_selection_rules_v6_0_9"),
        "status": "BHSM_OVERLAP_SELECTION_RULES_DERIVED",
        "cubic": ["q1+q2+q3=0", "triangle inequalities", "J1+J2+J3 integer", "left magnetic weights sum to zero"],
        "quartic": ["sum q_i=0", "tensor product contains a singlet", "a common pair-coupling intermediate spin exists"],
        "forbidden_channels_vanish": True,
        "low_mode_diagnostics": [
            {"modes": [[0, 0], [1, 1], [1, -1]], "cubic_allowed": True},
            {"modes": [[1, 1], [1, 1], [2, 0]], "cubic_allowed": False},
            {"modes": [[1, 1], [1, -1], [1, 1], [1, -1]], "quartic_allowed": True},
        ],
    }
    gap = {
        **_common("BHSM_berger_tower_spectral_gap_v6_0_9"),
        "status": "BHSM_BERGER_TOWER_SPECTRAL_GAP_DERIVED",
        "retained_sector": "(J,m)=(0,0) scalar singlet",
        "gap": "Delta_spec=min[1/(2L2^2)+1/(4L1^2), 2/L2^2]",
        "level_crossing": "(L1/L2)^2=1/6",
        "positivity": "strict for finite positive L1,L2 for the minimally coupled scalar vertical Laplacian",
        "scaling": "Delta_spec -> alpha^-2 Delta_spec",
        "curvature_caveat": "representation-dependent endomorphisms can change a non-scalar full operator",
    }
    tower = {
        **_common("BHSM_tree_level_tower_integration_v6_0_9"),
        "status": "BHSM_CONTROLLED_TOWER_INTEGRATION_DERIVED_CONDITIONALLY",
        "heavy_equation": "O_H Phi_H=J_H[Phi_L]",
        "tree_correction": "Delta S_tree=-(1/2)<J_H,O_H^(-1)J_H>",
        "resolvent_bound": "||O_H^(-1)|| <= 1/(Delta_spec-E^2) for E^2<Delta_spec in the elliptic/Euclidean low-energy sector",
        "outside_regime": "the infinite harmonic tower is dynamically required",
        "one_loop_computed": False,
    }
    eft = {
        **_common("BHSM_tower_EFT_error_bound_v6_0_9"),
        "status": "BHSM_TOWER_EFT_ERROR_BOUND_DERIVED_CONDITIONALLY",
        "control": "epsilon=max(E^2/Delta_spec, source_scale/Delta_spec, modulus_rate^2/Delta_spec, connection_curvature_scale/Delta_spec)",
        "remainder": "E^2/(Delta_spec-E^2)",
        "validity": "all displayed ratios much less than one and overlap-weighted amplitudes perturbative",
        "unconditional_truncation_claimed": False,
    }
    action = {
        **_common("BHSM_normalized_twistor_berger_effective_action_v6_0_9"),
        "status": PRIMARY_RESULT,
        "base": "B5=R_t x S4 is a diagnostic lower-dimensional base, not observed spacetime",
        "terms": ["Vol(F)(kappa1 R5-kappa0+kappa1 R_F)/2", "-(1/4)K_ab F^a F^b", "canonical covariant multiplet kinetic and Berger spectral terms", "normalized overlap interactions", "modulus kinetic/potential terms", "conditional tree-level heavy-tower correction"],
        "parent_fields": "the frozen provisional P1 declared chi and sigma carriers retain kappa0,kappa1,Z_chi,Z_sigma,A0,G0,g as primitives",
        "full_lorentzian_background_derived": False,
    }
    lovelock = {
        **_common("BHSM_P2_P3_correction_ledger_v6_0_9"),
        "status": "BHSM_P2_P3_SEPARATE_CORRECTION_LEDGER",
        "P2": "quadratic Lovelock/Gauss-Bonnet with independent kappa2 of dimension L^-4 in D=8",
        "P3": "cubic Lovelock with independent kappa3 of dimension L^-2 in D=8",
        "role": "possible higher-curvature correction study only",
        "included_in_P1_result": False,
    }
    parent_v5 = {
        **_common("BHSM_parent_to_v5_normalized_coefficient_map_v6_0_9"),
        "status": "BHSM_PARENT_TO_V5_COEFFICIENT_MAP_ADVANCED_CONDITIONALLY",
        "mapped": ["physical fiber measure", "canonical singlet normalization", "quadratic spectral/parent Hessian split", "quartic volume scaling"],
        "unmapped": ["legacy (k,j) intertwiner", "v5 topographic coefficient values", "boundary/collar coefficients", "particle-sector assignment"],
        "reverse_engineering_used": False,
        "coefficient_audit": {
            "boundary_geometry": "unresolved: requires a physical M8 boundary/collar action",
            "scalar_topographic_kinetic": "conditional: Z_sigma Vol(F) before canonicalization",
            "A_ST": "unresolved: A0 and modulus/Hessian mixing are primitive",
            "G_ST": "conditional structural map: G0 times the singlet quartic overlap and canonical volume factors",
            "sigma_scale": "unresolved: no Lorentzian vacuum branch",
            "gauge_kinetic": "geometric K_ab derived; physical gauge map open",
            "charged_current": "unresolved: fermion current and aperture map absent",
            "neutral_response": "unresolved: no physical response operator map",
            "fermion_kinetic": "unresolved: parent spinor action absent",
            "scale_RG": "unresolved: primitive scale and quantum framework absent",
            "recycling": "unresolved: no parent reduction source",
        },
    }
    sigma = {
        **_common("BHSM_sigma_parent_identification_audit_v6_0_9"),
        "status": "BHSM_SIGMA_PARENT_CANDIDATE_SELECTED",
        "candidate": "the normalized (J,m)=(0,0) mode of the already declared bulk sigma carrier",
        "why": "it is the unique scalar fiber singlet within the frozen declared sigma field and exists at sigma=0",
        "not_derived": ["identification with the v5 topographic sigma", "A0 and G0 from geometry", "sigma vacuum", "boundary response map"],
        "new_field_added": False,
    }
    gauge = {
        **_common("BHSM_gauge_sector_normalization_readiness_v6_0_9"),
        "status": "BHSM_GEOMETRIC_CONNECTION_NORMALIZATION_READY_PHYSICAL_GAUGE_MAP_OPEN",
        "derived": ["K_ab", "canonical connection rescaling", "representation-generator rescaling", "anisotropy condition"],
        "open": ["physical gauge algebra map", "observed-spacetime reduction", "matter current normalization", "renormalized coupling"],
        "standard_model_coupling": None,
    }
    fermion = {
        **_common("BHSM_fermion_sector_normalization_readiness_v6_0_9"),
        "status": "BHSM_FERMION_NORMALIZATION_NOT_YET_DERIVED",
        "available": ["physical measure", "spin-connection geometry", "representation branching inputs"],
        "required": ["eight-dimensional spinor action", "spin structure/chirality convention", "twisted Dirac spectrum", "fermion overlap tensors", "index-to-light-mode proof"],
        "fermion_masses_derived": False,
    }
    scale = {
        **_common("BHSM_scale_stationarity_audit_v6_0_9"),
        "status": "BHSM_P1_FIXED_LAPSE_STATIONARY_RATIOS_DERIVED_FULL_BACKGROUND_OPEN",
        "fixed_lapse_branches": ["round: L1/L4=L2/L4=1 and (kappa0/kappa1)L4^2=15/2", "Jensen-squashed: L1/L4=L2/L4=1/sqrt(5) and (kappa0/kappa1)L4^2=27/2"],
        "primitive_scale": "both scales depend on the unfixed primitive ratio kappa1/kappa0",
        "lorentzian_constraint": "vacuum R_t x S7 violates the simultaneous lapse/tt and spatial Einstein equations for positive-curvature S7 unless an explicit stress source is solved",
        "absolute_unit_anchor": None,
        "common_rescaling": {
            "fiber_volume": "alpha^3",
            "S7_volume": "alpha^7",
            "connection_K": "alpha^5 times kappa1 when all nested lengths scale together",
            "spectral_eigenvalues": "alpha^-2",
            "canonical_scalar_factor": "alpha^(3/2) at fixed Z_parent",
            "canonical_p_overlap": "alpha^[3(1-p/2)] at fixed parent coupling",
            "P1_curvature_potential_integrand": "kappa1 alpha^5 versus kappa0 alpha^7",
        },
    }
    stability = {
        **_common("BHSM_reduced_stability_hessian_v6_0_9"),
        "status": "BHSM_FIXED_LAPSE_REDUCED_HESSIAN_CLASSIFIED_NOT_PHYSICAL_STABILITY",
        "round_log_hessian_proportional": [[24, 4, 2], [4, 10, 1], [2, 1, 4.5]],
        "round_leading_principal_minors": [24, 224, 960],
        "squashed_determinant_proportional": "-22464 sqrt(5)/15625",
        "classification": "round is a fixed-lapse spatial-potential minimum; Jensen-squashed is a saddle",
        "promotion_blocker": "the lapse constraint and declared-field stress background have not been solved",
        "connection_modes": "K_ab is positive for kappa1,L1,L2>0; gauge zero modes require gauge fixing before a physical Hessian count",
        "retained_multiplet": "minimal scalar singlet stability additionally depends on the declared parent Hessian",
        "heavy_tower": "vertical scalar Laplacian is positive with the displayed gap; nonminimal curvature endomorphisms remain action-specific",
    }
    hidden = {
        **_common("BHSM_action_normalization_hidden_input_audit_v6_0_9"),
        "status": "BHSM_ACTION_NORMALIZATION_HIDDEN_INPUTS_EXPOSED",
        "primitive_dimensional": ["kappa0", "kappa1", "Z_chi", "Z_sigma", "A0", "G0"],
        "primitive_dimensionless_or_convention_dependent": ["g", "generator trace normalization", "field normalization conventions"],
        "not_imported": ["Planck length", "Hubble rate", "CMB temperature", "measured masses", "PDG values", "W calibration", "CKM fitting", "neutrino limits", "cosmological parameters"],
        "normalization_bridge_hidden": False,
    }
    report = {
        **_common("BHSM_twistor_berger_action_normalization_report_v6_0_9"),
        "status": PRIMARY_RESULT,
        "central_answer": "The fixed P1 action supplies an exact physical measure, constant-modulus curvature reduction, positive connection kinetic matrix, canonical multiplet and overlap normalization, an exact scalar vertical gap, and a controlled tree-level tower regime. It does not yet supply a full Lorentzian stationary parent background: the fixed-lapse extrema fail promotion until declared-field stress and the lapse constraint are solved. Their dimensional scale also remains the unfixed primitive ratio kappa1/kappa0.",
        "derived": ["physical nested volumes", "P1 off-shell curvature and connection coefficients", "canonical scalar multiplet factors", "cubic/quartic selection rules", "singlet-to-tower spectral gap", "conditional resolvent/error bounds", "fixed-lapse stationary ratios and Hessian classification"],
        "conditional": ["low-energy tower integration", "sigma singlet parent candidate", "parent-to-v5 coefficient bridge", "fixed-lapse extrema"],
        "invalidated_or_downgraded": ["a fixed-lapse extremum is not a Lorentzian P1 vacuum", "anisotropic K_ab is not one physical Sp(1) gauge coupling", "finite nonlinear multiplets are not unconditionally closed"],
        "remaining_blockers": ["solve the Lorentzian lapse and declared-field stress equations", "derive a physical parent sigma/topographic map", "derive fermion action/spectrum", "derive physical gauge and particle maps", "select primitive coefficients or an action-native absolute anchor"],
        "completion_gate": "V6_0_9_CONTINUE_TO_P1_LORENTZIAN_BACKGROUND_CONSTRAINT_CLOSURE",
        "recommended_next_branch": "bhsm-p1-lorentzian-background-constraint-closure-v6-0-10",
        "full_bhsm_status": "FULL_BHSM_NOT_COMPLETE",
    }
    payloads = [convention, measure, curvature, connection, connection_map, moduli, multiplets, cubic, quartic, selection, gap, tower, eft, action, lovelock, parent_v5, sigma, gauge, fermion, scale, stability, hidden, report]
    return dict(zip(ARTIFACT_FILES, payloads, strict=True))


def branching_checks(max_ell: int = 12) -> list[dict[str, Any]]:
    if not isinstance(max_ell, int) or isinstance(max_ell, bool) or max_ell < 0:
        raise ValueError("max_ell must be a nonnegative integer")
    return [branching_row(ell) for ell in range(max_ell + 1)]


def materialize_artifacts(root: Path) -> list[Path]:
    target = root / "artifacts"
    target.mkdir(parents=True, exist_ok=True)
    built = build_artifact_payloads(root)
    paths = []
    for key, filename in ARTIFACT_FILES.items():
        path = target / filename
        path.write_text(deterministic_json(built[key]), encoding="utf-8")
        paths.append(path)
    return paths


def action_normalization_status_report(repo_root: Path | None = None) -> dict[str, Any]:
    report = build_artifact_payloads(repo_root)["report"]
    report["artifacts"] = {key: f"artifacts/{name}" for key, name in ARTIFACT_FILES.items()}
    return report


def action_normalization_status_to_markdown(report: dict[str, Any]) -> str:
    return "\n".join([
        "# BHSM v6.0.9 Twistor--Berger Action Normalization",
        "",
        f"Primary result: `{report['primary_result']}`.",
        "",
        report["central_answer"],
        "",
        f"Next gate: `{report['completion_gate']}`.",
        "",
        "`FULL_BHSM_NOT_COMPLETE`.",
    ]) + "\n"
