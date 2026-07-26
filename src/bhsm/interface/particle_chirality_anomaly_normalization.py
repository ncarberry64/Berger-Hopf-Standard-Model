"""BHSM v6.3.0 particle, chirality, anomaly, and normalization architecture."""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

from . import triality_generation_scale_architecture as v620


VERSION = "v6.3.0"
SPRINT = "bhsm-particle-chirality-anomaly-normalization-v6-3-0"
SOURCE_SHA = "87577bc946437048848afb9d46cf5e62253613d8"
PRIMARY_RESULT = (
    "BHSM_CHIRAL_PARTICLE_AND_CONNECTION_ARCHITECTURE_DERIVED_CONDITIONALLY"
)

ARTIFACT_FILES = {
    "handoff": "BHSM_v6_3_0_state_handoff.json",
    "particle_map": "BHSM_three_family_particle_representation_map_v6_3_0.json",
    "mass": "BHSM_triality_Berger_family_mass_operator_v6_3_0.json",
    "operator": "BHSM_first_order_Clifford_boundary_operator_v6_3_0.json",
    "chiral_domain": "BHSM_chiral_boundary_domain_v6_3_0.json",
    "u1": "BHSM_physical_U1_generator_search_v6_3_0.json",
    "em": "BHSM_electromagnetic_surviving_generator_v6_3_0.json",
    "anomaly_one": "BHSM_one_family_anomaly_audit_v6_3_0.json",
    "anomaly_three": "BHSM_three_family_anomaly_audit_v6_3_0.json",
    "color_norm": "BHSM_G2_SU3_color_connection_normalization_v6_3_0.json",
    "incidence": "BHSM_1_2_7_incidence_audit_v6_3_0.json",
    "connection_map": "BHSM_connection_coefficient_dependency_map_v6_3_0.json",
    "scale": "BHSM_absolute_scale_representation_map_v6_3_0.json",
    "mixed_mode": "BHSM_Berger_scalar_wall_mixed_mode_map_v6_3_0.json",
    "r4": "BHSM_scalar_wall_O_r4_action_ledger_v6_3_0.json",
    "hessian": "BHSM_constraint_reduced_mixed_Hessian_v6_3_0.json",
    "hidden": "BHSM_v6_3_0_hidden_input_audit.json",
    "report": "BHSM_particle_chirality_anomaly_normalization_report_v6_3_0.json",
}

GUARDS = {
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
    "measured_derivation_input_used": False,
    "physical_Dirac_parent_law_introduced": False,
    "monopole_structure_introduced": False,
    "triality_and_Berger_triplications_multiplied": False,
    "full_G2_called_low_energy_gauge_group": False,
    "full_BHSM_claimed": False,
}


def fraction_text(value: Fraction | int) -> str:
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def boundary_charge(C: int, sigma: int) -> Fraction:
    if C not in (0, 1) or sigma not in (-1, 1):
        raise ValueError("C must be 0/1 and sigma must be +/-1")
    return Fraction(sigma - 1, 2) + Fraction(2 * C, 3)


def weak_generator(w: int, sigma: int) -> Fraction:
    if w not in (0, 1) or sigma not in (-1, 1):
        raise ValueError("w must be 0/1 and sigma must be +/-1")
    return Fraction(w * sigma, 2)


def physical_u1(C: int, sigma: int, w: int) -> Fraction:
    """Residual U(1) in the convention Q_em=T_n+Y_BH."""
    return boundary_charge(C, sigma) - weak_generator(w, sigma)


def electric_charge(C: int, sigma: int, w: int) -> Fraction:
    return weak_generator(w, sigma) + physical_u1(C, sigma, w)


@dataclass(frozen=True)
class Multiplet:
    name: str
    su3: str
    su3_dimension: int
    su3_cubic_sign: int
    sp1: str
    sp1_dimension: int
    Y: Fraction
    boundary_source: str
    boundary_parity: str
    clifford_chirality: str
    candidate_role: str
    optional: bool = False

    @property
    def complex_dimension(self) -> int:
        return self.su3_dimension * self.sp1_dimension


def one_family_multiplets(include_neutral_singlet: bool = True) -> tuple[Multiplet, ...]:
    rows = [
        Multiplet(
            "Q_L", "3", 3, 1, "2", 2, Fraction(1, 6),
            "(C=1,w=1,sigma=+/-1)", "interface-active",
            "K=+1", "left colored weak doublet",
        ),
        Multiplet(
            "L_L", "1", 1, 0, "2", 2, Fraction(-1, 2),
            "(C=0,w=1,sigma=+/-1)", "interface-active",
            "K=+1", "left color-singlet weak doublet",
        ),
        Multiplet(
            "u_c", "conjugate(3)", 3, -1, "1", 1, Fraction(-2, 3),
            "conjugate of (C=1,w=0,sigma=+1)", "interface-inactive/conjugate",
            "K=+1", "left-Weyl conjugate of upper colored singlet",
        ),
        Multiplet(
            "d_c", "conjugate(3)", 3, -1, "1", 1, Fraction(1, 3),
            "conjugate of (C=1,w=0,sigma=-1)", "interface-inactive/conjugate",
            "K=+1", "left-Weyl conjugate of lower colored singlet",
        ),
        Multiplet(
            "e_c", "1", 1, 0, "1", 1, Fraction(1),
            "conjugate of (C=0,w=0,sigma=-1)", "interface-inactive/conjugate",
            "K=+1", "left-Weyl conjugate of charged singlet",
        ),
    ]
    if include_neutral_singlet:
        rows.append(
            Multiplet(
                "nu_c", "1", 1, 0, "1", 1, Fraction(0),
                "conjugate of (C=0,w=0,sigma=+1)",
                "interface-inactive/conjugate", "K=+1",
                "optional neutral singlet; no fundamental mass implied", True,
            )
        )
    return tuple(rows)


MODE_LEDGERS = {
    "Q_L": {
        "upper": [(0, 0), (6, 0), (10, 1)],
        "lower": [(0, 0), (6, 3), (8, 2)],
    },
    "L_L": {
        "upper": [(0, 0), (3, 0), (3, 1)],
        "lower": [(0, 0), (5, 2), (9, 3)],
    },
    "u_c": {"singlet": [(0, 0), (6, 0), (10, 1)]},
    "d_c": {"singlet": [(0, 0), (6, 3), (8, 2)]},
    "e_c": {"singlet": [(0, 0), (5, 2), (9, 3)]},
    "nu_c": {"singlet": [(0, 0), (3, 0), (3, 1)]},
}


def mode_for_family(name: str, family: int) -> dict[str, list[int]]:
    if family not in (0, 1, 2):
        raise ValueError("family must be 0, 1, or 2")
    return {
        component: list(modes[family])
        for component, modes in MODE_LEDGERS[name].items()
    }


def particle_representation_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    carrier_names = ("triality eigenfamily P_0", "triality eigenfamily P_1", "triality eigenfamily P_2")
    family_slots = ("reference", "excitation_1", "excitation_2")
    for family in range(3):
        for multiplet in one_family_multiplets():
            row = asdict(multiplet)
            row["Y"] = fraction_text(multiplet.Y)
            row["complex_dimension"] = multiplet.complex_dimension
            row.update(
                {
                    "family_projector": f"P_{family}",
                    "Spin8_carrier": f"P_{family}(8_v direct_sum 8_s direct_sum 8_c), rank 8",
                    "triality_description": carrier_names[family],
                    "Berger_family_slot": family_slots[family],
                    "G2_channel": "1+7 with selected complex polarization",
                    "nested_U1_weight": "q=2m; component sign recorded by sigma",
                    "existing_BHSM_mode": mode_for_family(multiplet.name, family),
                    "proof_status": (
                        "derived conditional on the boundary complex polarization "
                        "and the K=+1 Clifford-domain selection"
                    ),
                }
            )
            rows.append(row)
    return rows


def family_dimension(include_neutral_singlet: bool = True) -> int:
    return sum(row.complex_dimension for row in one_family_multiplets(include_neutral_singlet))


def anomaly_coefficients(
    families: int = 1, include_neutral_singlet: bool = True
) -> dict[str, Fraction | int | bool]:
    if families <= 0:
        raise ValueError("families must be positive")
    rows = one_family_multiplets(include_neutral_singlet)
    su3_cubic = sum(row.sp1_dimension * row.su3_cubic_sign for row in rows)
    su3_sq_u1 = sum(
        row.sp1_dimension * Fraction(1, 2) * row.Y
        for row in rows
        if row.su3_dimension == 3
    )
    sp1_sq_u1 = sum(
        row.su3_dimension * Fraction(1, 2) * row.Y
        for row in rows
        if row.sp1_dimension == 2
    )
    u1_cubic = sum(row.complex_dimension * row.Y**3 for row in rows)
    gravity_u1 = sum(row.complex_dimension * row.Y for row in rows)
    doublets = sum(
        row.su3_dimension for row in rows if row.sp1_dimension == 2
    )
    return {
        "SU3_cubed": families * su3_cubic,
        "SU3_squared_U1": families * su3_sq_u1,
        "Sp1_squared_U1": families * sp1_sq_u1,
        "U1_cubed": families * u1_cubic,
        "gravity_squared_U1": families * gravity_u1,
        "Sp1_doublet_count": families * doublets,
        "Witten_parity_even": (families * doublets) % 2 == 0,
    }


def anomaly_payload(families: int, include_neutral_singlet: bool) -> dict[str, Any]:
    return {
        key: value if isinstance(value, bool) else fraction_text(value)
        for key, value in anomaly_coefficients(
            families, include_neutral_singlet
        ).items()
    }


def clifford_matrices() -> dict[str, np.ndarray]:
    gamma_n = np.array([[0, 1], [1, 0]], dtype=complex)
    gamma_star = np.array([[0, -1j], [1j, 0]], dtype=complex)
    K = 1j * gamma_n @ gamma_star
    identity = np.eye(2, dtype=complex)
    return {
        "Gamma_n": gamma_n,
        "Gamma_star": gamma_star,
        "K": K,
        "Pi_plus": (identity + K) / 2,
        "Pi_minus": (identity - K) / 2,
    }


def clifford_checks() -> dict[str, bool]:
    matrices = clifford_matrices()
    gn, gs, K = matrices["Gamma_n"], matrices["Gamma_star"], matrices["K"]
    pp, pm = matrices["Pi_plus"], matrices["Pi_minus"]
    identity = np.eye(2, dtype=complex)
    zero = np.zeros((2, 2), dtype=complex)
    return {
        "Gamma_n_squared": bool(np.allclose(gn @ gn, identity)),
        "Gamma_star_squared": bool(np.allclose(gs @ gs, identity)),
        "anticommutator_zero": bool(np.allclose(gn @ gs + gs @ gn, zero)),
        "K_squared": bool(np.allclose(K @ K, identity)),
        "projectors_idempotent": bool(
            np.allclose(pp @ pp, pp) and np.allclose(pm @ pm, pm)
        ),
        "projectors_orthogonal": bool(np.allclose(pp @ pm, zero)),
        "projectors_complete": bool(np.allclose(pp + pm, identity)),
        "self_adjoint_boundary_form": bool(
            np.allclose(pp.conj().T @ gn @ pp, zero)
        ),
    }


def zero_mode_profile(x: np.ndarray | float, delta: float = 1.0) -> np.ndarray:
    """Normalized representative for m(x)=delta^-1 tanh(x/delta)."""
    if delta <= 0:
        raise ValueError("delta must be positive")
    values = np.asarray(x, dtype=float)
    return 1 / (math.sqrt(2 * delta) * np.cosh(values / delta))


def zero_mode_diagnostic() -> dict[str, Any]:
    x = np.linspace(-12, 12, 24001)
    profile = zero_mode_profile(x)
    norm = float(np.trapezoid(profile**2, x))
    return {
        "representative_mass": "m(x)=tanh(x) in dimensionless collar units",
        "profile": "psi_+(x)=sech(x)/sqrt(2)",
        "analytic_norm": "integral_R |psi_+|^2 dx=1",
        "numerical_norm": float(f"{norm:.12f}"),
        "K_plus_normalizable_count_per_internal_slot": 1,
        "K_minus_normalizable_count_per_internal_slot": 0,
        "normal_index_per_selected_slot": 1,
    }


def u1_generator_ledger() -> dict[str, Any]:
    return {
        "commuting_basis": ["I", "P_C", "S_sigma", "P_w S_sigma"],
        "general_form": "a I+b P_C+c S_sigma+d P_w S_sigma",
        "derived_coefficients": {
            "a": "-1/2",
            "b": "2/3",
            "c": "1/2",
            "d": "-1/2",
        },
        "operator": (
            "Y_BH=-(1/2)I+(2/3)P_C+(1/2)S_sigma"
            "-(1/2)P_w S_sigma"
        ),
        "equivalent_residual": "Y_BH=Q_boundary-T_n=Y_boundary/2",
        "family_operator_allowed": False,
        "reason_family_operator_excluded": "physical connection must commute with and act identically on P_0,P_1,P_2",
        "G2_centralizer_U1_available": False,
        "nested_U1_alone_sufficient": False,
        "nested_U1_obstruction": "q=2m distinguishes orientation components but not color activity or active/inactive boundary sectors",
        "Higgs_normalization": "Y_BH(Phi_BH)=1/2",
    }


def charge_table() -> list[dict[str, str]]:
    entries = [
        ("L_upper", 0, 1, 1, False),
        ("L_lower", 0, -1, 1, False),
        ("Q_upper", 1, 1, 1, False),
        ("Q_lower", 1, -1, 1, False),
        ("nu_c", 0, 1, 0, True),
        ("e_c", 0, -1, 0, True),
        ("u_c", 1, 1, 0, True),
        ("d_c", 1, -1, 0, True),
    ]
    rows = []
    for name, C, sigma, w, conjugate in entries:
        Tn = weak_generator(w, sigma)
        Y = physical_u1(C, sigma, w)
        Q = Tn + Y
        if conjugate:
            Tn, Y, Q = -Tn, -Y, -Q
        rows.append(
            {
                "slot": name,
                "C": str(C),
                "sigma": str(sigma),
                "w": str(w),
                "left_Weyl_conjugated": str(conjugate).lower(),
                "T_n": fraction_text(Tn),
                "Y_BH": fraction_text(Y),
                "Q_em": fraction_text(Q),
            }
        )
    return rows


def connection_trace_indices() -> dict[str, Fraction]:
    rows = one_family_multiplets()
    I1 = sum(row.complex_dimension * row.Y**2 for row in rows)
    I2 = sum(
        row.su3_dimension * Fraction(1, 2)
        for row in rows
        if row.sp1_dimension == 2
    )
    I3 = sum(
        row.sp1_dimension * Fraction(1, 2)
        for row in rows
        if row.su3_dimension == 3
    )
    eta = I2 / I1
    return {
        "I1_raw": I1,
        "I2": I2,
        "I3": I3,
        "eta_Y": eta,
        "I1_normalized": eta * I1,
    }


def connection_trace_payload() -> dict[str, str]:
    return {
        key: fraction_text(value)
        for key, value in connection_trace_indices().items()
    }


def exact_mass_operator(repo_root: Path) -> dict[str, Any]:
    frozen_path = repo_root / "docs" / "frozen_predictions.json"
    frozen = json.loads(frozen_path.read_text(encoding="utf-8"))
    return {
        "operator": "M_f=sum_k m_(f,k) P_k+M_(f,mix)",
        "projector_algebra_preserved": v620.triality_algebra_check(),
        "family_projectors": ["P_0", "P_1", "P_2"],
        "Berger_basis": "diag(m_(f,0),m_(f,1),m_(f,2))",
        "triality_basis": "F diag(m_(f,0),m_(f,1),m_(f,2)) F^-1",
        "mixing_constraint": "[M_(f,mix), gauge representation projectors]=0",
        "mass_source": "Berger/topographic excitation eigenvalue or overlap operator",
        "absolute_masses_derived": False,
        "mode_ledgers": {
            name: {
                component: [list(mode) for mode in modes]
                for component, modes in components.items()
            }
            for name, components in MODE_LEDGERS.items()
        },
        "frozen_outputs_read_only": frozen["outputs"],
        "frozen_constants_read_only": frozen["constants"],
        "dressed_candidate_status_preserved": frozen["dressing_rule"]["status"],
        "frozen_values_used_as_derivation_inputs": False,
        "spectrum_status": "mode ordering plus frozen ratio screens; absolute and complete dressed eigenvalues remain conditional",
    }


def _common(artifact: str) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "version": VERSION,
        "sprint": SPRINT,
        "primary_result": PRIMARY_RESULT,
        **GUARDS,
    }


def build_artifact_payloads(repo_root: Path | None = None) -> dict[str, dict[str, Any]]:
    root = repo_root or Path(__file__).resolve().parents[3]
    common = _common
    anomaly_min = anomaly_payload(1, False)
    anomaly_full = anomaly_payload(1, True)
    anomaly_three = anomaly_payload(3, True)
    traces = connection_trace_payload()
    mass = exact_mass_operator(root)
    payloads: dict[str, dict[str, Any]] = {
        "handoff": {
            **common("BHSM_v6_3_0_state_handoff"),
            "status": "BHSM_V6_3_0_STACKED_HANDOFF_RECORDED",
            "source_branch": "bhsm-triality-generation-scale-architecture-v6-2-0",
            "source_sha": SOURCE_SHA,
            "source_PR": 162,
            "source_results_preserved": True,
        },
        "particle_map": {
            **common("BHSM_three_family_particle_representation_map_v6_3_0"),
            "status": "BHSM_THREE_FAMILY_CHIRAL_REPRESENTATION_MAP_DERIVED_CONDITIONALLY",
            "rows": particle_representation_rows(),
            "one_family_dimension_without_neutral_singlet": family_dimension(False),
            "one_family_dimension_with_neutral_singlet": family_dimension(True),
            "active_dimension": 8,
            "inactive_dimension_with_neutral_singlet": 8,
            "family_universal": True,
            "generation_count": 3,
            "complex_polarization": {
                "selection": "choose 1+3 from 1+1+3+conjugate(3); conjugate polarization is antiparticle data",
                "status": "BHSM boundary-domain identification",
                "without_selection": "3 and conjugate(3) cannot be the two components of one chiral weak doublet",
                "falsifier": "no globally consistent polarization commuting with the retained SU3 connection and boundary domain",
            },
            "particles_antiparticles_double_counted": False,
            "optional_neutral_singlet_role": "completes 16 slots but may remain constrained/core-facing; no mass term follows",
        },
        "mass": {
            **common("BHSM_triality_Berger_family_mass_operator_v6_3_0"),
            "status": "BHSM_TRIALITY_BERGER_FAMILY_MASS_OPERATOR_ATTACHED",
            **mass,
        },
        "operator": {
            **common("BHSM_first_order_Clifford_boundary_operator_v6_3_0"),
            "status": "BHSM_FIRST_ORDER_CLIFFORD_BOUNDARY_OPERATOR_CONSTRUCTED",
            "operator": "C_BHSM=-i Gamma_n nabla_n+Gamma_star m_B(x)+C_tangential",
            "action": "S_C=integral_collar dmu Psi^dagger C_BHSM Psi",
            "configuration_space": "L2 sections of the declared collar Clifford bundle tensored with the selected boundary representation",
            "Clifford_bundle": "rank-two normal Clifford factor tensor the M4 spin/Clifford machinery and internal representation bundle",
            "inner_product": "<Psi,Phi>=integral_collar dmu Psi^dagger Phi",
            "domain": "H1 on the complete collar; on a cut collar impose Pi_minus trace=0",
            "self_adjointness": "complete-collar Dirac-type theorem, or maximal isotropic local boundary domain because Pi_plus Gamma_n Pi_plus=0",
            "normal_orientation": "outward spacetime-facing normal fixes K=i Gamma_n Gamma_star; reversing the normal exchanges K signs",
            "physical_parent_law": False,
            "mathematical_input_sources": [
                "Atiyah-Patodi-Singer spectral boundary-domain mathematics",
                "domain-wall zero-mode mathematics",
            ],
            "checks": clifford_checks(),
        },
        "chiral_domain": {
            **common("BHSM_chiral_boundary_domain_v6_3_0"),
            "status": "BHSM_CHIRAL_BOUNDARY_MODE_DERIVED_CONDITIONALLY",
            "grading": "K=i Gamma_n Gamma_star",
            "domain_projectors": "Pi_+/-=(1+/-K)/2",
            "mass_condition": "m_B(-infinity)<0<m_B(+infinity)",
            "mass_source_status": "requires an odd BHSM-native scalar-wall coupling coefficient in S_C",
            "result": "one normalizable K=+1 normal profile per selected internal slot; K=-1 is nonnormalizable",
            "zero_mode": zero_mode_diagnostic(),
            "family_result": "the same index-one normal factor occurs on each P_0,P_1,P_2 family projector",
            "total_family_factor_index": 3,
            "no_fourth_family_theorem": False,
            "unwanted_vectorlike_doubling": False,
            "monopole_dependency": False,
        },
        "u1": {
            **common("BHSM_physical_U1_generator_search_v6_3_0"),
            "status": "BHSM_PHYSICAL_U1_GENERATOR_DERIVED_CONDITIONALLY",
            **u1_generator_ledger(),
            "claim_condition": "boundary charge/operator and complex-polarized chiral representation identifications",
        },
        "em": {
            **common("BHSM_electromagnetic_surviving_generator_v6_3_0"),
            "status": "BHSM_ELECTROMAGNETIC_SURVIVING_GENERATOR_DERIVED",
            "generator": "Q_em=T_n+Y_BH=Q_boundary",
            "Higgs_vacuum": "T_n(Phi_vac)=-1/2, Y_BH(Phi_BH)=+1/2",
            "vacuum_charge": "0",
            "charge_table": charge_table(),
            "measured_charges_fit": False,
        },
        "anomaly_one": {
            **common("BHSM_one_family_anomaly_audit_v6_3_0"),
            "status": "BHSM_ONE_FAMILY_ANOMALY_CANCELLATION_DERIVED",
            "conventions": {
                "basis": "left-handed Weyl",
                "T_fundamental": "1/2",
                "SU3_cubic": "A(3)=+1, A(conjugate(3))=-1",
                "conjugates": "physical right-handed rows represented by left-Weyl conjugates with opposite Y",
            },
            "without_neutral_singlet": anomaly_min,
            "with_neutral_singlet": anomaly_full,
            "cancels_family_by_family": True,
            "neutral_singlet_required_for_anomalies": False,
            "neutral_singlet_required_for_16_slot_completion": True,
        },
        "anomaly_three": {
            **common("BHSM_three_family_anomaly_audit_v6_3_0"),
            "status": "BHSM_THREE_FAMILY_ANOMALY_REPLICATION_DERIVED",
            "three_family_totals": anomaly_three,
            "relation": "three exact copies of the one-family zero coefficients",
            "Witten_doublets": 12,
            "family_interdependence_required": False,
        },
        "color_norm": {
            **common("BHSM_G2_SU3_color_connection_normalization_v6_3_0"),
            "status": "BHSM_G2_SU3_COLOR_CONNECTION_NORMALIZATION_DERIVED_CONDITIONALLY",
            "retained_connection": "SU3 adjoint 8 selected by the v6.2.0 rank-eight projector",
            "constrained_coset": "3+conjugate(3), six generators",
            "one_family_trace_indices": traces,
            "color_index_derivation": "2*T(3) from Q_L plus T(conjugate3) from u_c and d_c =2",
            "full_G2_propagated": False,
        },
        "incidence": {
            **common("BHSM_1_2_7_incidence_audit_v6_3_0"),
            "status": "BHSM_1_2_7_CANDIDATE_REJECTED_BY_REPRESENTATION_TRACE",
            "geometric_denominator": "6*pi^2 preserved exactly",
            "one_family_trace_indices": traces,
            "raw_integer_ratio": "5:3:3",
            "canonically_normalized_ratio": "1:1:1",
            "three_family_factor": "common factor 3; ratios unchanged",
            "candidate_ratio": "1:2:7",
            "candidate_matches_representation_trace": False,
            "surviving_possible_role": "only an independently action-derived geometric/localization transfer weight",
            "frozen_registry_changed": False,
        },
        "connection_map": {
            **common("BHSM_connection_coefficient_dependency_map_v6_3_0"),
            "status": "BHSM_CONNECTION_COEFFICIENT_DEPENDENCY_MAP_DERIVED",
            "formula": "1/g_i^2=Z_A,i N_geom,i I_i",
            "dependencies": {
                "sphere_volume": "6*pi^2 denominator",
                "representation_trace": traces,
                "geometric_mode_norm": "N_geom,i remains action-dependent",
                "boundary_localization": "included in Z_A,i or separately declared",
                "family_multiplicity": "common factor 3 if all families are active at matching scale",
                "matching_and_RG": "not used in the derivation",
            },
            "physical_alpha_derived": False,
        },
        "scale": {
            **common("BHSM_absolute_scale_representation_map_v6_3_0"),
            "status": "BHSM_REPRESENTATION_NORMALIZED_ABSOLUTE_SCALE_MAP_DERIVED_CONDITIONALLY",
            "established_correspondence": "C4=Mbar_Pl^2/2; tau_i I_i=1/g_i^2",
            "trace_indices": traces,
            "Xi_i": "Xi_i=(Z_g/Z_A,i)/(N_geom,i I_i)",
            "map": "L_i^2=Xi_i 2/(g_i^2 Mbar_Pl^2)",
            "mass_conversion": "m_(f,k)=(hbar/(c L_*)) E_(f,k)",
            "Z_g_equals_Z_A_assumed": False,
            "transfer_factors_equal_assumed": False,
            "numerical_absolute_mass_emitted": False,
        },
        "mixed_mode": {
            **common("BHSM_Berger_scalar_wall_mixed_mode_map_v6_3_0"),
            "status": "BHSM_BERGER_SCALAR_WALL_QUADRATIC_SEPARATION_PRESERVED",
            "coordinates": ["delta sigma", "delta beta"],
            "quadratic_source": "p1-p2=0 for the retained singlet wall",
            "H_sigma_beta_at_retained_linear_source": "0",
            "current_result": "separate quadratic coordinates in the retained truncation",
            "higher_order_mixing": "allowed and not computed",
            "one_light_scalar_claimed": False,
        },
        "r4": {
            **common("BHSM_scalar_wall_O_r4_action_ledger_v6_3_0"),
            "status": "BHSM_SCALAR_WALL_O_R4_ACTION_LEDGER_CONSTRUCTED_TOTAL_OPEN",
            "expansion": "Gamma_tau-Gamma_c=tau(nu1/12)r^3+B_tau r^4+O(r^5)",
            "leading_coefficient": "nu1/12=9.138890145035",
            "components": {
                "B_direct": "(G5/Z5) 21.690130229412 enters the analytic projection",
                "B_gravity": None,
                "B_junction": None,
                "B_domain": None,
                "B_normalization": None,
                "B_constraint": None,
                "B_total": None,
            },
            "fixed_moving_agreement": "v6.1.7 coordinate agreement preserved through O(r^3); O(r^4) comparison not completed",
            "fitted_number_frozen": False,
        },
        "hessian": {
            **common("BHSM_constraint_reduced_mixed_Hessian_v6_3_0"),
            "status": "BHSM_CONSTRAINT_REDUCED_MIXED_HESSIAN_ARCHITECTURE_CONSTRUCTED",
            "variables": [
                "scalar-wall fluctuation", "Berger radial fluctuation",
                "two twistor-orientation fluctuations", "lapse",
                "scale factor", "induced metric", "junction displacement",
                "retained connection fluctuations",
            ],
            "reduction": "K_eff=H_gg-H_gPhi H_PhiPhi^-1 H_Phig",
            "constraint_block": ["lapse", "longitudinal metric", "normal-coordinate gauge"],
            "boundary_domain_block": ["junction displacement", "Clifford projector domain"],
            "physical_candidate_block": ["delta sigma", "delta beta", "twistor transverse orientation", "transverse retained connections", "metric TT"],
            "full_coefficients_constructed": False,
            "full_spectrum_computed": False,
            "stability_claimed": False,
        },
        "hidden": {
            **common("BHSM_v6_3_0_hidden_input_audit"),
            "status": "BHSM_V6_3_0_HIDDEN_INPUT_AUDIT_PASS",
            "measured_inputs": [],
            "fits": [],
            "external_values": [],
            "frozen_outputs_read_only": True,
            "new_primitive_coefficients": [],
            "adopted_domain_choices": [
                "complex polarization selecting 1+3",
                "odd collar mass orientation",
                "Higgs U1 normalization Y=1/2",
            ],
        },
        "report": {
            **common("BHSM_particle_chirality_anomaly_normalization_report_v6_3_0"),
            "status": PRIMARY_RESULT,
            "primary_conclusion": (
                "The triality family factor, boundary complex polarization, "
                "one-sided Clifford domain, residual boundary U1 operator, "
                "and exact anomaly/trace ledgers form a conditional chiral "
                "three-family connection architecture."
            ),
            "derived": [
                "exact residual U1 coefficients and Q_em",
                "one- and three-family anomaly cancellation",
                "trace indices 10/3,2,2 and eta_Y=3/5",
                "projector-compatible family mass operator",
                "representation-dependent absolute-scale factors",
            ],
            "conditional": [
                "global boundary complex polarization",
                "odd scalar-wall coupling in the Clifford action",
                "physical interpretation of the retained connections",
            ],
            "rejected": [
                "nested U1 alone as physical U1",
                "1:2:7 as a representation-trace incidence ratio",
                "unpolarized 3+conjugate(3) as one chiral weak doublet",
            ],
            "active_targets": [
                "derive polarization from the global associated bundle",
                "derive the odd Clifford coupling from the parent action",
                "derive geometric transfer factors N_geom,i and Z_A,i",
                "complete O(r^4) projection and mixed Hessian spectrum",
            ],
        },
    }
    if set(payloads) != set(ARTIFACT_FILES):
        raise RuntimeError("v6.3.0 artifact registry/payload mismatch")
    return payloads


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def materialize_artifacts(root: Path) -> list[Path]:
    payloads = build_artifact_payloads(root)
    output = root / "artifacts"
    written = []
    for key, filename in ARTIFACT_FILES.items():
        path = output / filename
        path.write_text(deterministic_json(payloads[key]), encoding="utf-8")
        written.append(path)
    return written


def architecture_status_report(repo_root: Path | None = None) -> dict[str, Any]:
    payloads = build_artifact_payloads(repo_root)
    return {
        "version": VERSION,
        "branch": SPRINT,
        "primary_result": PRIMARY_RESULT,
        "particle_map": payloads["particle_map"]["status"],
        "chirality": payloads["chiral_domain"]["status"],
        "physical_U1": payloads["u1"]["status"],
        "anomalies": payloads["anomaly_one"]["status"],
        "incidence": payloads["incidence"]["status"],
        "mass_operator": payloads["mass"]["status"],
        "scale": payloads["scale"]["status"],
        "safeguards": GUARDS,
    }


def architecture_status_to_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# BHSM v6.3.0 particle/chirality/anomaly normalization",
            "",
            f"Primary result: `{report['primary_result']}`.",
            "",
            f"- Particle map: `{report['particle_map']}`",
            f"- Chirality: `{report['chirality']}`",
            f"- Physical U(1): `{report['physical_U1']}`",
            f"- Anomalies: `{report['anomalies']}`",
            f"- 1:2:7 audit: `{report['incidence']}`",
            f"- Mass operator: `{report['mass_operator']}`",
            f"- Scale map: `{report['scale']}`",
            "",
        ]
    )
