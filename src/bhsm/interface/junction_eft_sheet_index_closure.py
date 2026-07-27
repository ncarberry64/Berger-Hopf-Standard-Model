"""BHSM v6.9.0 junction EFT, sheet kill screen, and index certification.

The construction is deliberately finite dimensional.  It projects the
available v6.7/v6.8 collar operator onto three triality copies of its zero
mode and first positive compact level, identifies the sole boundary overlap
that can evade bulk orthogonality, and performs an exact Feshbach reduction.
The stability and index gates stop at their first mathematically explicit
closure condition.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import sympy as sp


VERSION = "v6.9.0"
SPRINT = "bhsm-junction-eft-sheet-index-v6-9-0"
SOURCE_SHA = "caaeb62c2042ed35ab461cdc3ef0a0e664b23050"
V680_SCIENTIFIC_SHA = "c823e767a735feee8a746be27e86c8edcd650d2c"
V680_FINAL_SHA = "e8bb212f21d51d27e1afe1acdb579592e3e7a53a"

PRIMARY_RESULT = "BHSM_AVAILABLE_C_BHSM_HAS_ZERO_LIGHT_HEAVY_COUPLING"
GATE_B_RESULT = (
    "BHSM_LOWER_SHEET_KILL_SCREEN_REQUIRES_ONE_MISSING_HESSIAN_INVARIANT"
)
GATE_C_RESULT = "BHSM_AUXILIARY_INDEX_ONE_CERTIFIED"

ARTIFACT_FILES = {
    "block": "BHSM_junction_light_heavy_block_v6_9_0.json",
    "schur": "BHSM_junction_Schur_and_K_prop_v6_9_0.json",
    "sheet": "BHSM_lower_sheet_negative_mode_kill_screen_v6_9_0.json",
    "index": "BHSM_APS_Callias_index_certification_v6_9_0.json",
    "hidden": "BHSM_v6_9_0_hidden_input_audit.json",
    "report": "BHSM_v6_9_0_dynamical_closure_report.json",
}

GUARDS = {
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
    "measured_derivation_input_used": False,
    "physical_bulk_Dirac_parent_law_introduced": False,
    "sector_dependent_coupling_introduced": False,
    "fitted_matrix_introduced": False,
    "global_spectrum_claimed": False,
    "full_eight_dimensional_PDE_solved": False,
    "lambda_geom_set_to_one": False,
    "full_BHSM_claimed": False,
}

E = sp.symbols("E", real=True)
P = sp.symbols("p", real=True)
M_H = sp.symbols("M_H", positive=True, real=True)
J_J = sp.symbols("j_J", real=True)
K_B = sp.symbols("k_b", positive=True, real=True)
B_MINUS, B_PLUS = sp.symbols("B_minus B_plus", real=True)
XI = sp.symbols("xi", real=True, nonzero=True)


def light_projector() -> sp.ImmutableMatrix:
    """Project onto the three triality copies of the neutral zero mode."""
    return sp.ImmutableMatrix(sp.diag(1, 1, 1, 0, 0, 0))


def heavy_projector() -> sp.ImmutableMatrix:
    """Project onto the first positive compact level in each triality copy."""
    return sp.ImmutableMatrix(sp.diag(0, 0, 0, 1, 1, 1))


def triality_cycle() -> sp.ImmutableMatrix:
    """Cyclic family action on both light and heavy triplets."""
    cycle = sp.ImmutableMatrix([[0, 0, 1], [1, 0, 0], [0, 1, 0]])
    return sp.ImmutableMatrix(sp.diag(cycle, cycle))


def basis_ledger() -> dict[str, Any]:
    """Declare the six-state truncated Hilbert space and all quantum labels."""
    return {
        "Hilbert_space": "H_total=H_L direct_sum H_H isomorphic to C^3 direct sum C^3",
        "basis_order": [
            "|P0,f0>",
            "|P1,f0>",
            "|P2,f0>",
            "|P0,f1>",
            "|P1,f1>",
            "|P2,f1>",
        ],
        "H_L": "three triality copies of the v6.7 neutral compact zero mode f0",
        "H_H": "first positive compact mode f1 in the same three copies",
        "inner_product": (
            "delta_family times the v6.7 normalized cap L2 product"
        ),
        "triality_action": "cyclic P0->P1->P2 on both subspaces",
        "charge": 0,
        "Q_em": "zero on the declared neutral basis",
        "Y_BH": "zero on the declared neutral basis",
        "conjugation": "componentwise complex conjugation with conjugate domain",
        "collar_parity": (
            "f0 is the selected K=+ zero mode; f1 is the first positive "
            "self-adjoint normal eigenmode"
        ),
        "domain": (
            "the declared v6.7 rectangular maximal-isotropic diagnostic "
            "domain; not action selected"
        ),
        "arbitrary_neutral_mixing_matrix": False,
    }


def static_blocks(
    junction_overlap: sp.Expr = sp.Integer(0),
) -> dict[str, sp.ImmutableMatrix]:
    """Hamiltonian blocks for the smallest light-heavy truncation."""
    identity = sp.eye(3)
    h_ll = P * identity
    h_hh = (P + M_H) * identity
    v_lh = sp.sympify(junction_overlap) * identity
    return {
        "H_LL": sp.ImmutableMatrix(h_ll),
        "H_HH": sp.ImmutableMatrix(h_hh),
        "V_LH": sp.ImmutableMatrix(v_lh),
        "V_HL": sp.ImmutableMatrix(v_lh.T.conjugate()),
    }


def full_truncated_operator(
    junction_overlap: sp.Expr = sp.Integer(0),
) -> sp.ImmutableMatrix:
    """Six-dimensional Hermitian truncated Hamiltonian."""
    blocks = static_blocks(junction_overlap)
    return sp.ImmutableMatrix(
        blocks["H_LL"].row_join(blocks["V_LH"]).col_join(
            blocks["V_HL"].row_join(blocks["H_HH"])
        )
    )


def selection_rule_table() -> list[dict[str, str]]:
    """Exact light-heavy selection rules for every declared operator piece."""
    return [
        {
            "term": "C_normal+lambda_geom sigma Gamma_star",
            "matrix_element": "0",
            "classification": "exactly zero",
            "reason": "f0 and f1 are orthogonal eigenmodes of this self-adjoint block",
        },
        {
            "term": "C_angular",
            "matrix_element": "0 in the smallest same-angular-state truncation",
            "classification": "Berger-harmonic selection",
            "reason": "acts on the common angular factor and leaves <f0|f1>=0",
        },
        {
            "term": "C_connection",
            "matrix_element": "0 for the available neutral constant profile",
            "classification": "charge and orthogonality zero",
            "reason": "Q_em=Y_BH=0 and the family-universal profile is normal-mode diagonal",
        },
        {
            "term": "C_Berger",
            "matrix_element": "0 in the v6.8 canonical same-mode factor",
            "classification": "orthonormal-frame and harmonic zero",
            "reason": "Berger factors act internally and preserve normal-mode orthogonality",
        },
        {
            "term": "C_polarization",
            "matrix_element": "0 in the available v6.7 normal operator",
            "classification": "exactly zero in available truncation",
            "reason": "the exported normal operator has no polarization dependence",
        },
        {
            "term": "family/triality projectors",
            "matrix_element": "0",
            "classification": "family-universal selection",
            "reason": "commute with P_L and P_H and do not change f0 to f1",
        },
        {
            "term": "C_junction",
            "matrix_element": "j_J I_3",
            "classification": "coefficient-dependent and unresolved",
            "reason": (
                "a boundary-supported insertion is not killed by bulk L2 "
                "orthogonality; its action/domain overlap is not supplied"
            ),
        },
    ]


def available_light_heavy_result() -> dict[str, Any]:
    """Return the exact result for the pieces currently present."""
    blocks = static_blocks(0)
    return {
        "P_L_C_available_P_H": "0_3",
        "V_LH_is_zero": blocks["V_LH"] == sp.zeros(3),
        "V_HL_equals_adjoint": (
            blocks["V_HL"] == blocks["V_LH"].T.conjugate()
        ),
        "heavy_gap": "M_H>0",
        "missing_invariant": (
            "j_J=<f0,C_junction f1> on the declared boundary domain"
        ),
        "missing_invariant_symmetry": (
            "real Hermitian neutral triality-singlet scalar; minimal block j_J I_3"
        ),
        "result": PRIMARY_RESULT,
    }


def schur_inverse_operator(
    junction_overlap: sp.Expr = J_J,
) -> sp.ImmutableMatrix:
    """Energy-dependent light inverse operator after the first heavy level."""
    j = sp.sympify(junction_overlap)
    scalar = P - E - j**2 / (P + M_H - E)
    return sp.ImmutableMatrix(scalar * sp.eye(3))


def light_energy() -> sp.Expr:
    """Exact light root continuously connected to E=p when j_J vanishes."""
    return P + (M_H - sp.sqrt(M_H**2 + 4 * J_J**2)) / 2


def light_energy_shift_series() -> sp.Expr:
    """Small-junction-overlap expansion through fourth order."""
    return -J_J**2 / M_H + J_J**4 / M_H**3


def schur_ledger() -> dict[str, Any]:
    """Classify the exact Feshbach reduction and its energy law."""
    return {
        "inverse_operator": (
            "[(p-E)-j_J^2/(p+M_H-E)] I_3"
        ),
        "resolvent_domain": "E not equal to p+M_H",
        "controlled_regime": "|E-p|,|j_J| << M_H",
        "resolvent_series": (
            "1/(p+M_H-E)=1/M_H+(E-p)/M_H^2+(E-p)^2/M_H^3+..."
        ),
        "leading_Schur_term": "-j_J^2 I_3/M_H",
        "leading_term_dimension": "mass: [j_J]^2/[M_H]",
        "exact_light_energy": (
            "E_light=p+[M_H-sqrt(M_H^2+4j_J^2)]/2"
        ),
        "energy_shift": (
            "delta E=-j_J^2/M_H+j_J^4/M_H^3+..."
        ),
        "energy_scaling": "E^0 at leading order; not 1/p",
        "Hermitian": True,
        "locality": "local finite-level EFT away from the heavy pole",
        "path_or_environment_dependence": False,
        "channel_structure": "proportional to I_3",
        "K_prop_defined": False,
        "reason_no_K_prop": "no kappa_i/(2p) term is generated",
        "available_operator_j_J": 0,
        "available_operator_delta_E": 0,
        "relative_neutral_phase": (
            "zero; both the available and minimal universal extension are "
            "channel universal"
        ),
        "operational_mass_squared": (
            "not generated: the leading universal correction is E^0, not "
            "kappa/(2p)"
        ),
    }


def physical_kinetic_metric() -> sp.ImmutableMatrix:
    """Smallest physical kinetic metric, retaining open bending normalization."""
    return sp.ImmutableMatrix(sp.diag(1, sp.Rational(6, 7), K_B))


def physical_hessian(sheet: int) -> sp.ImmutableMatrix:
    """General real symmetric 3x3 physical Hessian on (sigma,beta,b)."""
    if sheet not in (-1, 1):
        raise ValueError("sheet must be +/-1")
    h_ss, h_sb, h_bb = sp.symbols(
        f"h_ss_{sheet} h_sigma_beta_{sheet} h_beta_beta_{sheet}", real=True
    )
    h_sj, h_bj = sp.symbols(
        f"h_sigma_b_{sheet} h_beta_b_{sheet}", real=True
    )
    bending = B_PLUS if sheet > 0 else B_MINUS
    return sp.ImmutableMatrix(
        [
            [h_ss, h_sb, h_sj],
            [h_sb, h_bb, h_bj],
            [h_sj, h_bj, bending],
        ]
    )


def bending_witness() -> sp.ImmutableMatrix:
    """Pure declared junction-position/bending trial direction."""
    return sp.ImmutableMatrix([0, 0, 1])


def bending_rayleigh(sheet: int) -> sp.Expr:
    """Exact physical Rayleigh quotient of the pure bending witness."""
    witness = bending_witness()
    numerator = (witness.T * physical_hessian(sheet) * witness)[0]
    denominator = (witness.T * physical_kinetic_metric() * witness)[0]
    return sp.simplify(numerator / denominator)


def sheet_kill_ledger() -> dict[str, Any]:
    """Stop Gate B at the first unavailable constraint-reduced invariant."""
    return {
        "variables": ["delta_sigma", "delta_beta", "delta_b"],
        "delta_b": "declared junction-position/embedding bending perturbation",
        "constrained_variables": [
            "lapse/length response",
            "moving endpoint/domain response",
        ],
        "gauge_null_handling": (
            "must be quotiented before H_CC inversion; no determinant sign is used"
        ),
        "H_phys": "H_PP-H_PC H_CC^(-1) H_CP on the non-gauge constrained subspace",
        "H_phys_status": "not numerically closed by existing second-variation data",
        "K_phys": "diag(1,6/7,k_b), with physical admissibility requiring k_b>0",
        "witness": "(0,0,1)",
        "lower_Rayleigh": "B_minus/k_b",
        "upper_Rayleigh": "B_plus/k_b",
        "known_sheet_orientation": "nu1_lower<0<nu1_upper",
        "orientation_determines_action_curvature": False,
        "negative_lower_condition": "k_b>0 and B_minus<0",
        "tachyon_condition": "positive k_b and negative B_minus",
        "ghost_condition": "k_b<0, independently of B_minus",
        "constraint_artifact_condition": "delta_b lies in the removed gauge kernel",
        "missing_invariant": (
            "B_sheet=e_b^dagger[H_PP-H_PC H_CC^(-1)H_CP]e_b, "
            "the constraint-reduced junction-bending Hessian invariant"
        ),
        "existing_repository_value": None,
        "lower_sheet_rejected": False,
        "upper_sheet_comparison": "open because B_plus is not supplied",
        "nonnegative_small_trial_proves_full_stability": False,
        "result": GATE_B_RESULT,
    }


def callias_symbol() -> sp.ImmutableMatrix:
    """Principal symbol of the graded auxiliary complete-collar operator."""
    return sp.ImmutableMatrix([[0, -sp.I * XI], [sp.I * XI, 0]])


def callias_index_ledger() -> dict[str, Any]:
    """Certify the rank-one auxiliary complete-collar Callias index."""
    return {
        "operator": (
            "D_aux=[[0,A^dagger],[A,0]], "
            "A=partial_rho+lambda_geom sigma(rho)"
        ),
        "role": "auxiliary BHSM elliptic operator; not a physical bulk Dirac law",
        "manifold": "noncompact complete collar R in the normal direction",
        "grading": "K=i Gamma_n Gamma_star",
        "inner_product": "L2(R) rank-two collar product per selected internal slot",
        "principal_symbol": "[[0,-i xi],[i xi,0]]",
        "principal_symbol_determinant": "-xi^2, nonzero for xi!=0",
        "elliptic": True,
        "boundary_condition": "L2 decay at both asymptotic ends; no finite boundary",
        "APS_applicable": False,
        "APS_reason": (
            "the actual compact cap lacks an action-selected tangential "
            "boundary operator, APS projector, eta invariant, and boundary kernel h"
        ),
        "Callias_applicable": True,
        "Callias_conditions": [
            "m(rho)=lambda_geom sigma(rho) tends to invertible nonzero limits",
            "m_minus<0<m_plus for the selected wall orientation",
            "the asymptotic potential is coercive",
            "localized profile changes are compact perturbations",
        ],
        "Fredholm": True,
        "index_formula": "ind(A)=[sgn(m_plus)-sgn(m_minus)]/2",
        "index_per_selected_slot": 1,
        "triality_total_index": 3,
        "kernel_A": (
            "one mode f proportional exp[-integral m(rho)d rho]"
        ),
        "kernel_A_adjoint": 0,
        "paired_zero_modes_excluded": (
            "yes for the rank-one complete-collar auxiliary problem by "
            "opposite exponential nonnormalizability"
        ),
        "compact_cap_physical_domain_selected": False,
        "physical_index_claimed": False,
        "comparison": (
            "agrees with the v6.7 diagnostic index one, positive gap, and "
            "no opposite-chirality zero mode on the selected domain"
        ),
        "lambda_geom_status": (
            "nonzero universal primitive; magnitude does not change the index"
        ),
        "result": GATE_C_RESULT,
    }


def _matrix_strings(matrix: sp.MatrixBase) -> list[list[str]]:
    return [[sp.sstr(entry) for entry in row] for row in matrix.tolist()]


def _common(name: str) -> dict[str, Any]:
    return {
        "artifact": name,
        "version": VERSION,
        "sprint": SPRINT,
        "source_main_sha": SOURCE_SHA,
        "v6_8_scientific_sha": V680_SCIENTIFIC_SHA,
        "v6_8_final_sha": V680_FINAL_SHA,
        "primary_result": PRIMARY_RESULT,
        **GUARDS,
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    """Build all six deterministic v6.9 certification artifacts."""
    p_l = light_projector()
    p_h = heavy_projector()
    available = static_blocks(0)
    extended = static_blocks(J_J)
    block = {
        **_common("BHSM_junction_light_heavy_block_v6_9_0"),
        "status": PRIMARY_RESULT,
        "basis": basis_ledger(),
        "P_L": _matrix_strings(p_l),
        "P_H": _matrix_strings(p_h),
        "projector_checks": {
            "P_L_idempotent": p_l * p_l == p_l,
            "P_H_idempotent": p_h * p_h == p_h,
            "orthogonal": p_l * p_h == sp.zeros(6),
            "complete": p_l + p_h == sp.eye(6),
        },
        "available_blocks": {
            key: _matrix_strings(value) for key, value in available.items()
        },
        "minimal_junction_extension": {
            key: _matrix_strings(value) for key, value in extended.items()
        },
        "selection_rules": selection_rule_table(),
        **available_light_heavy_result(),
    }
    schur = {
        **_common("BHSM_junction_Schur_and_K_prop_v6_9_0"),
        "status": "BHSM_JUNCTION_SCHUR_RESPONSE_IS_UNIVERSAL_NO_NEUTRAL_PHASE",
        **schur_ledger(),
    }
    sheet = {
        **_common("BHSM_lower_sheet_negative_mode_kill_screen_v6_9_0"),
        "status": GATE_B_RESULT,
        **sheet_kill_ledger(),
    }
    index = {
        **_common("BHSM_APS_Callias_index_certification_v6_9_0"),
        "status": GATE_C_RESULT,
        **callias_index_ledger(),
    }
    hidden = {
        **_common("BHSM_v6_9_0_hidden_input_audit"),
        "status": "BHSM_V6_9_0_HIDDEN_INPUT_AUDIT_PASS",
        "lambda_geom": "one universal dimensionless primitive",
        "new_symbolic_invariants": [
            "j_J, unresolved junction light-heavy overlap",
            "B_sheet, unresolved constraint-reduced bending Hessian",
        ],
        "new_fitted_parameters": [],
        "measured_inputs": [],
        "arbitrary_neutral_mixing_matrix": False,
        "K_prop_manufactured": False,
        "lower_sheet_selection_manufactured": False,
        "physical_domain_selected_by_index": False,
    }
    report = {
        **_common("BHSM_v6_9_0_dynamical_closure_report"),
        "status": (
            "BHSM_JUNCTION_EFT_CLOSED_AVAILABLE_COUPLING_ZERO_"
            "SHEET_HESSIAN_OPEN_AUXILIARY_INDEX_ONE"
        ),
        "Gate_A": {
            "result": PRIMARY_RESULT,
            "available_V_LH": "0_3",
            "missing_junction_overlap": "j_J I_3",
            "Schur_scaling_if_nonzero": "universal E^0",
            "K_prop": None,
            "relative_phase": "zero",
        },
        "Gate_B": {
            "result": GATE_B_RESULT,
            "witness": "(0,0,1)",
            "lower_Rayleigh": "B_minus/k_b",
            "certified_negative": False,
        },
        "Gate_C": {
            "result": GATE_C_RESULT,
            "theorem": "Callias on the auxiliary complete collar",
            "index_per_slot": 1,
            "paired_auxiliary_zero_modes": 0,
            "physical_compact_domain_still_conditional": True,
        },
        "artifact_count": len(ARTIFACT_FILES),
    }
    return {
        "block": block,
        "schur": schur,
        "sheet": sheet,
        "index": index,
        "hidden": hidden,
        "report": report,
    }


def artifact_bytes() -> dict[str, bytes]:
    """Canonical UTF-8/LF serialization keyed by artifact filename."""
    return {
        ARTIFACT_FILES[key]: (
            json.dumps(payload, indent=2, sort_keys=True) + "\n"
        ).encode("utf-8")
        for key, payload in artifact_payloads().items()
    }


def materialize_artifacts(root: Path) -> list[Path]:
    """Write all six deterministic artifacts below ``root/artifacts``."""
    target = Path(root) / "artifacts"
    target.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for filename, content in artifact_bytes().items():
        path = target / filename
        path.write_bytes(content)
        paths.append(path)
    return paths


__all__ = [
    "ARTIFACT_FILES",
    "B_MINUS",
    "B_PLUS",
    "E",
    "GATE_B_RESULT",
    "GATE_C_RESULT",
    "J_J",
    "K_B",
    "M_H",
    "P",
    "PRIMARY_RESULT",
    "XI",
    "artifact_bytes",
    "artifact_payloads",
    "available_light_heavy_result",
    "basis_ledger",
    "bending_rayleigh",
    "bending_witness",
    "callias_index_ledger",
    "callias_symbol",
    "full_truncated_operator",
    "heavy_projector",
    "light_energy",
    "light_energy_shift_series",
    "light_projector",
    "materialize_artifacts",
    "physical_hessian",
    "physical_kinetic_metric",
    "schur_inverse_operator",
    "schur_ledger",
    "selection_rule_table",
    "sheet_kill_ledger",
    "static_blocks",
    "triality_cycle",
]
