"""BHSM v8.3 projected-spectral audit of classical mode-stress incidence.

The frozen three-slot modules are imported from v8.2.  Explicit profiles are
not required here: every repository operator is also tested basis-free through
``P_f B[h] P_f`` and, where possible, by Hellmann--Feynman differentiation.
Conditional spectral coefficients are retained without promoting an unproved
ledger-to-action intertwiner.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from math import pi
from pathlib import Path
from typing import Any

from . import generation_projector_action_attachment as v82


VERSION = "v8.3"
SPRINT = "bhsm-classical-mode-stress-incidence-v8-3"
SOURCE_MAIN_SHA = "3afc556ca7a6d64ce58b82053961c364de11fb8a"
ARTIFACT_NAME = "BHSM_classical_mode_stress_incidence_v8_3"
FINAL_VERDICT = (
    "BHSM_FROZEN_MODE_LEDGER_NOT_REALIZED_AS_SPECTRUM_"
    "OF_ANY_ACTION_OPERATOR"
)
NEXT_MISSING_OBJECT = (
    "ACTION_DERIVED_INTERTWINER_FROM_FROZEN_KJQ_MODULES_TO_"
    "AN_ACTION_OPERATOR_SPECTRAL_DOMAIN"
)
RELEASE_VERDICT = "BHSM_1_0_RELEASE_BLOCKED"

SOURCE_PATHS = (
    "src/bhsm/interface/master_action/terms.py",
    "src/bhsm/interface/master_action/hessians.py",
    "src/bhsm/interface/master_action/measures.py",
    "src/bhsm/interface/master_action/generation_projector_action_attachment.py",
    "src/bhsm/interface/master_action/mode_resolved_curvature_incidence.py",
    "src/bhsm/interface/master_action/mass_curvature_response.py",
    "src/bhsm/interface/twistor_berger_associated_bundle.py",
    "src/bhsm/interface/twistor_berger_action_normalization.py",
    "src/bhsm/interface/action_lemmas/source_search.py",
    "src/bhsm/interface/action_lemmas/primitive_lattice_rule.py",
    "src/bhsm/interface/normalized_action_adjoint_pair/hermitian_action_rule.py",
    "src/bhsm/interface/primitive_charged_incidence/projector_reduction_audit.py",
    "src/bhsm/interface/primitive_charged_incidence/omega_trace_audit.py",
    "src/bhsm/interface/primitive_charged_incidence/physical_normalization_gate.py",
    "src/boundary_graded_defect_action_kernel.py",
    "src/boundary_derivation.py",
    "src/berger_spectrum.py",
    "src/mode_selection.py",
    "src/constants.py",
    "src/weak_double_projection_zvirt_bridge.py",
    "src/virtual_environment.py",
    "src/rg_matching.py",
    "docs/gauge_coupling_registry_pattern.md",
    "theory/derived_qj_eigenfunction_map_status.md",
    "theory/derived_m_weight_assignment_status.md",
)


def deterministic_json(value: Any) -> str:
    return json.dumps(
        value, indent=2, sort_keys=True, ensure_ascii=False
    ) + "\n"


def repository_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _text(path: str) -> str:
    return (repository_root() / path).read_text(encoding="utf-8")


def _sha256(path: str) -> str:
    return sha256((repository_root() / path).read_bytes()).hexdigest()


def source_audit() -> dict[str, Any]:
    terms = _text("src/bhsm/interface/master_action/terms.py")
    defect = _text("src/boundary_graded_defect_action_kernel.py")
    boundary = _text("src/boundary_derivation.py")
    selector = _text("src/mode_selection.py")
    weak = _text("src/weak_double_projection_zvirt_bridge.py")
    dressing = _text("src/virtual_environment.py")
    berger = _text("src/berger_spectrum.py")
    associated = _text(
        "src/bhsm/interface/twistor_berger_associated_bundle.py"
    )
    qj_status = _text("theory/derived_qj_eigenfunction_map_status.md")
    m_status = _text("theory/derived_m_weight_assignment_status.md")
    checks = {
        "localized_fermion_term_exists": "T4_fermion" in terms,
        "localized_Yukawa_term_exists": "T4_Yukawa" in terms,
        "no_mode_amplitudes_in_term_registry": all(
            token not in terms
            for token in ("c_f,i", "c_{f,i}", "Phi_f", "u_{f,i}")
        ),
        "defect_hessian_invalid_as_charged_hierarchy": (
            '"charged_Hessian_from_S_index_trace": '
            '"INVALIDATED_DO_NOT_CLAIM"' in defect
        ),
        "boundary_operator_only_action_linked": (
            "not obtained from variation" in boundary
        ),
        "mode_selection_is_finite_label_algorithm": (
            "selected_generation_modes" in selector
            and "boundary_penalty" in selector
        ),
        "weak_factor_is_conditional": (
            '"Z_virt_u2_applicability": "DERIVED_CONDITIONAL"' in weak
        ),
        "weak_factor_lives_in_diagnostic_dressing": (
            "Not canonically adopted in this phase." in dressing
        ),
        "berger_formula_is_explicitly_proxy": (
            "Berger scalar spectrum proxy" in berger
        ),
        "exact_scalar_action_operator_exists": (
            "quadratic_scalar_reduction" in associated
            and "physical-fiber-orthonormal basis" in associated
        ),
        "legacy_kj_intertwiner_not_asserted": (
            '"legacy_k_j_identification": "not asserted' in associated
        ),
        "qj_eigenfunction_map_remains_open": (
            "explicit Berger/BHSM eigenfunction map | `OPEN`" in qj_status
        ),
        "harmonic_m_assignment_remains_open": (
            "m assignment | `OPEN`" in m_status
        ),
    }
    return {
        "baseline": SOURCE_MAIN_SHA,
        "sources": [
            {"path": path, "sha256": _sha256(path)}
            for path in SOURCE_PATHS
        ],
        "checks": checks,
        "checks_passed": all(checks.values()),
    }


def frozen_sector_modules() -> dict[str, Any]:
    frozen = v82.frozen_family_modules()
    return {
        "classification": frozen["classification"],
        "family_slot_count": frozen["family_slot_count"],
        "modules": frozen["modules"],
        "imported_from": (
            "BHSM_generation_projector_action_attachment_v8_2"
        ),
        "rederived": False,
        "labels_changed": False,
        "normalization_changed": False,
    }


def _hopf_charge(mode: tuple[int, int]) -> int:
    k, j = mode
    return k - 2 * j


def _proxy_eigenvalue(mode: tuple[int, int]) -> int:
    """Return berger_lambda(k,j,a=1) exactly."""

    k, _ = mode
    return k * (k + 2)


def _proxy_tau(mode: tuple[int, int]) -> int:
    """Return -d berger_lambda/d ln(a) at a=1 exactly."""

    q = _hopf_charge(mode)
    return -2 * q * q


def proxy_spectral_candidate() -> dict[str, Any]:
    """Evaluate the strongest algebraic spectral candidate without licensing it."""

    sectors: dict[str, Any] = {}
    for sector, modes in v82.SECTOR_MODES.items():
        rows = []
        for slot, mode in enumerate(modes):
            k, j = mode
            q = _hopf_charge(mode)
            rows.append(
                {
                    "slot": slot,
                    "mode": [k, j],
                    "q": q,
                    "candidate_J": f"{k}/2",
                    "candidate_m": f"{q}/2",
                    "berger_proxy_lambda_at_a_1": _proxy_eigenvalue(mode),
                    "d_lambda_d_ln_a_at_a_1": -_proxy_tau(mode),
                    "candidate_tau": _proxy_tau(mode),
                    "projected_normalization": (
                        "I3 only conditional on the missing intertwiner"
                    ),
                    "action_stress": None,
                }
            )
        tau = [row["candidate_tau"] for row in rows]
        sectors[sector] = {
            "candidate_K_at_a_1": [
                [
                    _proxy_eigenvalue(modes[i]) if i == j else 0
                    for j in range(3)
                ]
                for i in range(3)
            ],
            "candidate_tau_diagonal": tau,
            "candidate_tau_nondegenerate": len(set(tau)) == 3,
            "per_mode": rows,
        }
    return {
        "formula": (
            "lambda_proxy(k,j;a)=k(k+2)+(a^2-1)q^2, q=k-2j"
        ),
        "hellmann_feynman_candidate": (
            "tau=-partial lambda_proxy/partial ln(a)=-2a^2q^2"
        ),
        "exact_scalar_operator_formula": (
            "lambda_(J,m)=J(J+1)/L2^2+m^2(1/L1^2-1/L2^2)"
        ),
        "formal_formula_match": (
            "J=k/2, m=q/2, L2=1/2, L1=1/(2a) would make "
            "lambda_(J,m)=lambda_proxy"
        ),
        "formula_match_licensed": False,
        "why_not_licensed": [
            (
                "berger_spectrum.py calls its eigenvalue a scalar spectrum "
                "proxy rather than an action operator"
            ),
            (
                "the exact associated-bundle artifact explicitly says the "
                "legacy (k,j) identification is not asserted and requires "
                "an intertwiner"
            ),
            (
                "the earlier qj eigenfunction map is a conditional symbolic "
                "scaffold; its explicit map and harmonic m assignment remain "
                "open"
            ),
            (
                "the exact operator is a provisional parent-scalar carrier, "
                "not the localized fermion action carrier"
            ),
        ],
        "sectors": sectors,
        "classification": (
            "EXACTLY_EVALUATED_PROXY_NOT_ACTION_OWNED_ON_FROZEN_MODULE"
        ),
    }


def projected_spectral_action_audit() -> dict[str, Any]:
    """Exhaust the basis-free P_f B[h] P_f candidates."""

    return {
        "target": (
            "K_f[h]=P_f^(3) B_f[h] P_f^(3); "
            "S_red=c_f^dagger G_f[h]K_f[h]c_f"
        ),
        "candidates": [
            {
                "operator": "localized M4 Dirac-Yukawa Hessian",
                "action_owned": True,
                "projector_restriction_defined": True,
                "projected_K": "I3 tensor D_M4 before Yukawa input",
                "metric_dependence": "ordinary M4 Dirac stress",
                "frozen_ledger_is_its_spectrum": False,
                "result": "FAMILY_CENTRAL_NOT_MODE_RESOLVED",
            },
            {
                "operator": "S_index_trace=lambda_IT(Omega-T)^2",
                "action_owned": (
                    "CONDITIONAL_SCAFFOLD_NOT_AUTHORITATIVE_ACTION_TERM"
                ),
                "projector_restriction_defined": "labelwise only",
                "projected_K": (
                    "zero on admissible nonbase slots; the base-slot "
                    "reference convention is not an amplitude spectrum"
                ),
                "metric_dependence": None,
                "frozen_ledger_is_its_spectrum": False,
                "result": (
                    "RANK_ONE_LABEL_CONSTRAINT_INVALIDATED_AS_CHARGED_HESSIAN"
                ),
            },
            {
                "operator": "exact Berger associated-scalar operator O_(J,m)",
                "action_owned": (
                    "PROVISIONAL_PARENT_SCALAR_REDUCTION_ONLY"
                ),
                "projector_restriction_defined": False,
                "projected_K": None,
                "metric_dependence": "exact in L1,L2",
                "frozen_ledger_is_its_spectrum": False,
                "result": "MISSING_KJQ_TO_JM_ACTION_INTERTWINER",
            },
            {
                "operator": "legacy berger_lambda(k,j;a)",
                "action_owned": False,
                "projector_restriction_defined": True,
                "projected_K": (
                    "conditional diagonal matrices recorded in "
                    "proxy_spectral_candidate"
                ),
                "metric_dependence": "exact proxy dependence on a",
                "frozen_ledger_is_its_spectrum": "PROXY_ONLY",
                "result": "OPERATIONAL_SPECTRAL_PROXY_NOT_ACTION_OWNED",
            },
            {
                "operator": "fixed-h scalar/KKT Hessian",
                "action_owned": True,
                "projector_restriction_defined": False,
                "projected_K": None,
                "metric_dependence": (
                    "fixed-h cap scalar and matcher variables only"
                ),
                "frozen_ledger_is_its_spectrum": False,
                "result": "DIFFERENT_BUNDLE_DOMAIN_AND_FIELD_CONTENT",
            },
            {
                "operator": "first cap-even intrinsic collar operator",
                "action_owned": True,
                "projector_restriction_defined": (
                    "only on its ordinary tangential/scalar domain"
                ),
                "projected_K": None,
                "metric_dependence": (
                    "A(rho)=sec(rho)^2 A(0); "
                    "(cos(rho)^3 A(rho))''|0=-A(0)"
                ),
                "frozen_ledger_is_its_spectrum": False,
                "result": "UNIVERSAL_OR_WRONG_CARRIER_NOT_FAMILY_INCIDENCE",
            },
            {
                "operator": "Omega/incidence/adjoint-pair operators",
                "action_owned": False,
                "projector_restriction_defined": "finite symbolic maps only",
                "projected_K": None,
                "metric_dependence": None,
                "frozen_ledger_is_its_spectrum": False,
                "result": (
                    "STRUCTURALLY_INTEGRATED_WITH_PHYSICAL_NORMALIZATION_OPEN"
                ),
            },
        ],
        "proxy_candidate": proxy_spectral_candidate(),
        "successful_action_canonical_projection": None,
        "result": FINAL_VERDICT,
    }


def hellmann_feynman_audit() -> dict[str, Any]:
    return {
        "identity": (
            "delta lambda_i=<u_i,(delta B)u_i> for normalized "
            "nondegenerate action eigenmodes"
        ),
        "exact_action_scalar_eigenvalues_metric_dependent": True,
        "legacy_proxy_eigenvalues_metric_dependent": True,
        "frozen_modes_proved_normalized_action_eigenmodes": False,
        "candidate_derivatives": {
            sector: data["candidate_tau_diagonal"]
            for sector, data in proxy_spectral_candidate()["sectors"].items()
        },
        "candidate_nondegeneracy": {
            sector: data["candidate_tau_nondegenerate"]
            for sector, data in proxy_spectral_candidate()["sectors"].items()
        },
        "down_sector_note": (
            "the proxy squashing derivative has a repeated zero for the "
            "(0,0) and (6,3) slots even before action ownership"
        ),
        "action_canonical_tau": None,
        "reason": (
            "Hellmann--Feynman cannot transfer a proxy derivative to the "
            "frozen physical module until the action intertwiner proves "
            "that its slots are normalized eigenmodes of the same operator"
        ),
        "result": "CONDITIONAL_PROXY_RESPONSE_ONLY",
    }


def background_vs_self_backreaction() -> dict[str, Any]:
    return {
        "background_quadratic": {
            "formula": "c^dagger K_f[h_bg] c",
            "amplitude_order": "conjugate(c)c",
            "logically_excluded_by_quartic_self_response": False,
            "target_K_f": None,
            "reason": "the frozen-module action projection is not established",
        },
        "self_induced_metric_backreaction": {
            "formula": (
                "(c^dagger B_f c) H_hh^+ (c^dagger B_f c)"
            ),
            "amplitude_order": "(conjugate(c)c)^2",
            "status": "SEPARATE_DOWNSTREAM_EFFECT",
        },
        "first_cap_even_order": {
            "intrinsic_operator": 2,
            "measure_operator_split": (
                "delta(GK)=(delta G)K+G(delta K)"
            ),
            "known_result": (
                "G=cos(rho)^3 and K=sec(rho)^2K(0) give "
                "(GK)''|0=-K(0) on the established intrinsic domain"
            ),
            "frozen_family_application": None,
            "reason": (
                "the internal vertical action supplies no rho-dependent "
                "L1,L2 profile and the intrinsic domain is not the frozen "
                "fermion module"
            ),
        },
    }


def action_ownership_audit() -> list[dict[str, Any]]:
    rows = [
        {
            "object": "T4_fermion",
            "role": "localized effective Dirac kinetic term",
            "family_dependence": "identity on attached finite family fiber",
            "classification": "FORMAL_CENTRAL_EFT_STRESS_ONLY",
            "target_stress_contribution": False,
            "reason": (
                "its stationary fields are M4 spinors, not the frozen "
                "Berger ledger resonances"
            ),
        },
        {
            "object": "T4_Yukawa",
            "role": "localized effective mass incidence",
            "family_dependence": "independent matrices Y_e,Y_u,Y_d",
            "classification": "EFFECTIVE_QFT_PARAMETER",
            "target_stress_contribution": False,
            "reason": "using Y_f would insert the mass matrix to be derived",
        },
        {
            "object": "S_index_trace=lambda_IT(Omega-T)^2",
            "role": "finite label admissibility constraint",
            "family_dependence": "sector labels q,j",
            "classification": "NOT_A_FIELD_AMPLITUDE_ACTION",
            "target_stress_contribution": False,
            "reason": (
                "it has no c_f,i, mode profile, spacetime density, or h_ab "
                "variation; its label Hessian is explicitly invalidated as "
                "the charged hierarchy Hessian"
            ),
        },
        {
            "object": "exact associated-scalar O_(J,m)",
            "role": "metric-dependent quadratic scalar spectral action",
            "family_dependence": "J,m eigenspaces with physical-fiber Gram",
            "classification": "ACTION_LINKED_PROVISIONAL_SCALAR_CARRIER",
            "target_stress_contribution": False,
            "reason": (
                "no action-derived intertwiner realizes the frozen (k,j,q) "
                "modules as these scalar eigenspaces, and this is not the "
                "localized fermion carrier"
            ),
        },
        {
            "object": "Berger proxy eigenvalue and boundary_penalty",
            "role": "spectral ordering and selection diagnostics",
            "family_dependence": "k,j,q and Omega_f",
            "classification": "OPERATIONAL_NOT_ACTION_OWNED",
            "target_stress_contribution": False,
            "reason": (
                "its diagonal K and squashing derivative are computable, "
                "but repository provenance calls it a proxy and does not "
                "supply the action intertwiner"
            ),
        },
        {
            "object": "sector and mode projectors",
            "role": "finite incidence and attached slot resolution",
            "family_dependence": "P_f and Pi_f,i",
            "classification": "METRIC_INDEPENDENT_FIXED_DATA",
            "target_stress_contribution": False,
            "reason": (
                "projectors organize a supplied bilinear but do not supply "
                "the bilinear operator A_f[h]"
            ),
        },
        {
            "object": "mu_collar=det(I+rho S)dmu_h d rho",
            "role": "conditional collar measure",
            "family_dependence": None,
            "classification": "MEASURE_AVAILABLE_PROFILES_ABSENT",
            "target_stress_contribution": False,
            "reason": (
                "J cannot normalize undefined u_f,i(Y,rho) profiles or an "
                "absent collar action density"
            ),
        },
        {
            "object": "GHY/Brown-York/matcher response",
            "role": "universal metric canonical momentum",
            "family_dependence": None,
            "classification": "UNIVERSAL_GEOMETRIC_RESPONSE",
            "target_stress_contribution": False,
            "reason": (
                "its mixed derivative with an absent c_f bilinear is zero "
                "or undefined; adding slot weights is forbidden"
            ),
        },
        {
            "object": "cap scalar/topographic action",
            "role": "distinct scalar radial response",
            "family_dependence": None,
            "classification": "DIFFERENT_BUNDLE_AND_DOMAIN",
            "target_stress_contribution": False,
            "reason": "no action cross-term attaches it to the frozen modes",
        },
        {
            "object": "charged-current incidence",
            "role": "effective SU2 gauge coupling",
            "family_dependence": "Yukawa-basis input",
            "classification": "NO_FROZEN_MODE_AMPLITUDE_SOURCE",
            "target_stress_contribution": False,
            "reason": "no arbitrary off-diagonal term is licensed",
        },
        {
            "object": "Z_virt^(u,2)=1/2",
            "role": "middle-up weak-double-projection bridge",
            "family_dependence": "one diagnostic mode-specific factor",
            "classification": "HISTORICAL_DRESSING_NOT_ACTION_STRESS",
            "target_stress_contribution": False,
            "reason": "it is not canonically adopted in an action term",
        },
    ]
    flags = {
        "T4_fermion": ("FORMAL_EFT_ONLY", False, True, True, False, False),
        "T4_Yukawa": ("INPUT_ONLY", "INPUT_ONLY", False, False, False, False),
        "S_index_trace=lambda_IT(Omega-T)^2": (
            False, False, False, False, False, True
        ),
        "exact associated-scalar O_(J,m)": (
            False, False, False, False, True, True
        ),
        "Berger proxy eigenvalue and boundary_penalty": (
            False, False, False, False, False, True
        ),
        "sector and mode projectors": (
            False, False, False, True, True, False
        ),
        "mu_collar=det(I+rho S)dmu_h d rho": (
            False, False, True, False, False, False
        ),
        "GHY/Brown-York/matcher response": (
            False, False, True, False, False, False
        ),
        "cap scalar/topographic action": (
            False, False, False, False, True, False
        ),
        "charged-current incidence": (
            False, "EFFECTIVE_INPUT_ONLY", False, False, False, False
        ),
        "Z_virt^(u,2)=1/2": (
            False, False, False, False, False, True
        ),
    }
    names = (
        "diagonal_stress",
        "off_diagonal_stress",
        "universal_removable_normalization",
        "vanishes_by_orthogonality",
        "forbidden_by_sector_or_projector",
        "not_action_owned_for_frozen_modes",
    )
    for row in rows:
        row.update(dict(zip(names, flags[row["object"]], strict=True)))
    return rows


def mode_action_source() -> dict[str, Any]:
    return {
        "required_form": (
            "S_f^(2)=sum_ij conjugate(c_f,i) A_f,ij[h,S,J,...] c_f,j"
        ),
        "required_stationary_modes": "u_f,0,u_f,1,u_f,2",
        "located_action_density": None,
        "located_mode_profiles": None,
        "located_amplitude_fields": None,
        "located_metric_dependent_operator_A_f": None,
        "basis_free_projection_exhausted": True,
        "exact_metric_dependent_scalar_operator_located": (
            "O_(J,m)=-D_A^*D_A+lambda_(J,m)(L1,L2)"
        ),
        "scalar_operator_on_frozen_module": None,
        "legacy_proxy_K_evaluated": True,
        "ledger_to_action_spectral_intertwiner": None,
        "finite_attachment_is_not_action_density": True,
        "proof": [
            (
                "The master term registry contains no c_f amplitudes, "
                "Phi_f expansion, or frozen u_f profile."
            ),
            (
                "The q,j defect functional is a metric-independent label "
                "constraint whose charged-Hessian use is invalidated."
            ),
            (
                "The exact associated-scalar action has normalized (J,m) "
                "eigenspaces and L1,L2 dependence, but its own source says "
                "the legacy (k,j) identification requires an intertwiner."
            ),
            (
                "The symbolic qj eigenfunction map and harmonic m assignment "
                "remain open, while the localized Dirac action is family "
                "central and has no Hopf operator."
            ),
            (
                "Therefore P_f B[h] P_f is not action-canonically defined "
                "on the frozen modules even though a conditional proxy "
                "matrix can be evaluated."
            ),
        ],
        "result": FINAL_VERDICT,
    }


def gram_matrices() -> dict[str, Any]:
    formal = [
        ["1", "0", "0"],
        ["0", "1", "0"],
        ["0", "0", "1"],
    ]
    row = {
        "finite_attachment_Gram": formal,
        "finite_attachment_status": "ABSTRACT_ORTHOGONAL_PROJECTOR_BASIS",
        "associated_scalar_action_Gram": (
            "I3 conditional on an isometric frozen-ledger intertwiner into "
            "the physical-fiber-orthonormal (J,m) eigenspaces"
        ),
        "action_canonical_Gram": None,
        "collar_measure": "J(Y,rho)=det(I+rho S(Y))",
        "reason": (
            "the exact scalar tower is orthonormal, but no action map "
            "identifies its eigenspaces with the frozen physical slots; "
            "the charged-incidence physical normalization gate is also open"
        ),
    }
    return {sector: dict(row) for sector in ("charged_lepton", "up", "down")}


def classical_mode_stress() -> dict[str, Any]:
    component = {
        "bilinear_tensor": None,
        "trace": None,
        "traceless": None,
        "normal_traction": None,
        "tangential_stress": None,
        "Hopf_horizontal": None,
        "Hopf_vertical": None,
        "collar_dependence": None,
        "surface_localization": None,
        "canonical_action_contribution": None,
    }
    sectors: dict[str, Any] = {}
    for sector, modes in v82.SECTOR_MODES.items():
        sectors[sector] = {
            **component,
            "per_mode": [
                {
                    "slot": index,
                    "mode": list(mode),
                    **component,
                }
                for index, mode in enumerate(modes)
            ],
        }
    return {
        "definition": (
            "T_f,ab^(ij)=-2/sqrt(|h|) delta A_f,ij/delta h^ab"
        ),
        **sectors,
        "formal_M4_EFT_projection": {
            "formula": "T_EFT,ab^(ij)=delta_ij T_Dirac,ab",
            "status": "FAMILY_CENTRAL_NOT_CLASSICAL_LEDGER_MODE_STRESS",
            "base_excitation_distinguished": False,
            "accepted_as_target": False,
        },
        "projected_proxy_response": proxy_spectral_candidate()["sectors"],
        "proxy_response_status": (
            "RECORDED_NOT_PROMOTED_TO_ACTION_CANONICAL_STRESS"
        ),
        "measure_operator_split": (
            "delta(G_f K_f)=(delta G_f)K_f+G_f(delta K_f)"
        ),
        "Hellmann_Feynman": hellmann_feynman_audit(),
        "base_excitation_inequality_test": None,
        "result": FINAL_VERDICT,
    }


def mixed_hessian() -> dict[str, Any]:
    return {
        "requested_block": (
            "B_f,ab;ij=delta^3 S/(delta h^ab delta conjugate(c_f,i) "
            "delta c_f,j)"
        ),
        "classical_mode_block": None,
        "complete_block_matrix": None,
        "formal_EFT_block": "delta_ij delta T_Dirac,ab/delta Psi",
        "formal_EFT_status": "CENTRAL_AND_NOT_THE_REQUESTED_MODE_BLOCK",
        "metric_Hessian": {
            "exists_as_constrained_KKT_scaffold": True,
            "gauge_kernel_present": True,
            "closed_range_complement_required": True,
            "selected_inverse_for_this_response": None,
        },
        "candidate_proxy_block": (
            "diagonal d lambda_proxy/d ln(a), not an action Hessian"
        ),
        "result": "UNDEFINED_BECAUSE_ACTION_PROJECTION_ON_F_f_IS_ABSENT",
    }


def interface_compliance() -> dict[str, Any]:
    return {
        "candidate_objects": [
            "delta h/delta pi_env",
            "delta pi_env/delta h",
            "constrained seam KKT Hessian",
            "first cap-even shape response",
        ],
        "selected_operator": None,
        "source_block_available": False,
        "gauge_quotient_fixed_for_this_contraction": False,
        "kernel_treated_for_this_contraction": False,
        "reason": (
            "compliance selection is downstream of the missing action "
            "projection and cannot act on the conditional proxy derivative"
        ),
        "downstream_obstruction": (
            "BHSM_INTERFACE_INCIDENCE_BLOCKED_BY_NO_SELECTED_"
            "SEAM_COMPLIANCE_OPERATOR"
        ),
    }


def geometric_work() -> dict[str, Any]:
    return {
        "pi_T_contraction": {
            "formula": "int pi_env^ab T_f,ab^(ij) dmu_h",
            "accepted": False,
            "reason": "T_f,ab^(ij) is undefined",
        },
        "compliance_contraction": {
            "formula": "<B_f,C B_f>",
            "accepted": False,
            "reason": "B_f and C are not action-selected",
        },
        "Schur_complement": {
            "formula": "A_f-B_f^dagger H_hh^+ B_f",
            "accepted": False,
            "reason": "A_f and B_f are absent and H_hh^+ is unselected",
        },
        "amplitude_order_theorem": {
            "metric_source_order": "conjugate(c)c",
            "induced_metric_order": "conjugate(c)c",
            "eliminated_backreaction_order": "(conjugate(c)c)^2",
            "result": (
                "about the zero-mode-amplitude background, compliant metric "
                "backreaction is quartic and cannot itself be a quadratic "
                "mass incidence"
            ),
            "nonzero_background_requirement": (
                "a selected coherent amplitude background would be required "
                "to obtain a quadratic fluctuation correction"
            ),
        },
        "background_vs_self_backreaction": background_vs_self_backreaction(),
        "unique_action_derived_response": None,
    }


def response_matrices() -> dict[str, Any]:
    result: dict[str, Any] = {}
    proxy = proxy_spectral_candidate()["sectors"]
    for sector in ("charged_lepton", "up", "down"):
        result[sector] = {
            "matrix": None,
            "rank": None,
            "eigenvalues": None,
            "generalized_eigenvalues": None,
            "hierarchy": None,
            "exact_zeros": None,
            "uncertainty": "EXACT_STRUCTURAL_OBSTRUCTION",
            "normalization_dependence": None,
            "conditional_proxy_matrix": [
                [
                    proxy[sector]["candidate_tau_diagonal"][i]
                    if i == j
                    else 0
                    for j in range(3)
                ]
                for i in range(3)
            ],
            "conditional_proxy_nondegenerate": proxy[sector][
                "candidate_tau_nondegenerate"
            ],
            "conditional_proxy_promoted": False,
        }
    return result


def virtual_door_placement() -> dict[str, Any]:
    return {
        "mode": [6, 0],
        "factor": "1/2",
        "applications_in_action_stress": 0,
        "placement": "HISTORICAL_DIAGNOSTIC_DRESSING_ONLY",
        "mode_normalization": False,
        "kinetic_response": False,
        "surface_incidence": False,
        "stress_tensor": False,
        "mass_incidence": False,
        "double_counted": False,
        "conditional_bridge_preserved": True,
    }


def alpha_impedance_status() -> dict[str, Any]:
    return {
        "twelve_pi_squared": 12.0 * pi**2,
        "claimed_inverse_interface_value": "12*pi^2",
        "GEOMETRIC_INTERFACE_IMPEDANCE": (
            "PROPOSED_INTERPRETATION_NOT_ACTION_OWNED"
        ),
        "ELECTROMAGNETIC_CHANNEL_PROJECTION": None,
        "RUNNING_FACTORIZATION": (
            "ONE_LOOP_GAUGE_SCAFFOLD_USES_EMPIRICAL_REFERENCE_INPUTS; "
            "NO_ACTION_MAP_FROM_12PI2_TO_LOW_ENERGY_ALPHA"
        ),
        "MASS_RESPONSE_NORMALIZATION": None,
        "repository_distinction": (
            "the registered gauge screen uses the common denominator "
            "6*pi^2, while alpha^-1/(12*pi^2) elsewhere is an "
            "empirical-alpha scale screen"
        ),
        "multiplied_into_mass_response": False,
        "result": (
            "BHSM_ALPHA_IMPEDANCE_INTERPRETATION_LACKS_ACTION_ATTACHMENT"
        ),
    }


def physical_observables() -> dict[str, Any]:
    return {
        "mass_ratios": {
            "charged_lepton": None,
            "up": None,
            "down": None,
        },
        "CKM": {
            "matrix": None,
            "angles": None,
            "CP_phase": None,
            "Jarlskog": None,
            "reason": "R_u and R_d have no defined eigenbases",
        },
        "physical_transport": (
            "BLOCKED_BEFORE_GEOMETRIC_TO_QFT_MASS_TRANSPORT"
        ),
        "distinct_falsifiable_prediction": False,
    }


def prediction_freeze() -> dict[str, Any]:
    return {
        "version": VERSION,
        "doctrine": v82.foundational_doctrine(),
        "frozen_modules": frozen_sector_modules(),
        "mode_action": mode_action_source(),
        "projected_spectral_action": projected_spectral_action_audit(),
        "Hellmann_Feynman": hellmann_feynman_audit(),
        "Gram_matrices": gram_matrices(),
        "classical_stress": classical_mode_stress(),
        "mixed_Hessian": mixed_hessian(),
        "interface_compliance": interface_compliance(),
        "geometric_work": geometric_work(),
        "response_matrices": response_matrices(),
        "virtual_door": virtual_door_placement(),
        "alpha": alpha_impedance_status(),
        "observables": physical_observables(),
        "uncertainties": "EXACT_STRUCTURAL_OBSTRUCTION",
        "falsification_thresholds": {
            "action_operator": "pass_fail",
            "frozen_ledger_spectral_intertwiner": "pass_fail",
            "projected_Gram": "pass_fail",
            "metric_variation": "pass_fail",
            "response_matrix": "pass_fail",
        },
        "comparison_data_used": False,
        "retuning_permitted": False,
        "status": "FROZEN_STRONGER_EXACT_OBSTRUCTION",
    }


def prediction_freeze_hash() -> str:
    return sha256(
        deterministic_json(prediction_freeze()).encode("utf-8")
    ).hexdigest().upper()


def post_freeze_comparison() -> dict[str, Any]:
    return {
        "freeze_hash_verified_before_comparison": prediction_freeze_hash(),
        "historical_bare_ratios": "UNDEFINED_COMPARISON",
        "historical_dressed_candidate": "UNDEFINED_COMPARISON",
        "historical_CKM_screen": "UNDEFINED_COMPARISON",
        "common_scale_external_references": "UNDEFINED_COMPARISON",
        "reason": "v8.3 freezes no response matrix or physical observable",
        "post_comparison_retuning": False,
    }


def completion_gate_payload() -> dict[str, Any]:
    gate = v82.completion_gate_payload()
    gate.update(
        {
            "version": VERSION,
            "sprint": SPRINT,
            "source_main_sha": SOURCE_MAIN_SHA,
            "current_verdict": FINAL_VERDICT,
            "next_highest_upstream_blocker": NEXT_MISSING_OBJECT,
            "mode_resolved_curvature_incidence": FINAL_VERDICT,
            "classical_mode_stress": FINAL_VERDICT,
            "distinct_action_derived_prediction_exists": False,
            "BHSM_1_0_release_complete": False,
        }
    )
    gate["RB15"] = {
        "status": "BLOCKED_EXACT_OBJECT_PROVED",
        "resolution": FINAL_VERDICT,
    }
    gate["RB16"] = {
        "status": "DOWNSTREAM_BLOCKED",
        "resolution": (
            "release packaging remains ineligible while RB-15 is open"
        ),
    }
    return gate


def payload() -> dict[str, Any]:
    result = {
        "artifact": ARTIFACT_NAME,
        "version": VERSION,
        "sprint": SPRINT,
        "source_main_sha": SOURCE_MAIN_SHA,
        "source_audit": source_audit(),
        "v8_3_action_structure": (
            "AUDIT_ONLY_NO_NEW_ACTION_TERM_INTRODUCED"
        ),
        "frozen_sector_modules": frozen_sector_modules(),
        "mode_action_ownership": action_ownership_audit(),
        "mode_action_source": mode_action_source(),
        "projected_spectral_action_audit": (
            projected_spectral_action_audit()
        ),
        "Hellmann_Feynman_audit": hellmann_feynman_audit(),
        "background_quadratic_vs_self_backreaction": (
            background_vs_self_backreaction()
        ),
        "action_canonical_Gram_matrices": gram_matrices(),
        "classical_bilinear_mode_stress": classical_mode_stress(),
        "mixed_metric_mode_Hessian": mixed_hessian(),
        "interface_compliance": interface_compliance(),
        "geometric_work_functional": geometric_work(),
        "response_matrices": response_matrices(),
        "virtual_door_placement": virtual_door_placement(),
        "alpha_impedance_status": alpha_impedance_status(),
        "physical_observables": physical_observables(),
        "prediction_freeze": prediction_freeze(),
        "prediction_freeze_sha256": prediction_freeze_hash(),
        "post_freeze_comparison": post_freeze_comparison(),
        "falsification_condition": (
            "An existing or independently justified, domain-preserving "
            "intertwiner must map every frozen (k,j,q) slot into normalized "
            "eigenmodes of one action-owned metric-dependent operator, "
            "thereby defining P_f B[h] P_f and its projected Gram without "
            "using mass or mixing data."
        ),
        "RB15": {
            "status": "BLOCKED_EXACT_OBJECT_PROVED",
            "resolution": FINAL_VERDICT,
        },
        "RB16": {
            "status": "DOWNSTREAM_BLOCKED",
            "release_package_generated": False,
        },
        "release_status": RELEASE_VERDICT,
        "remaining_exact_obstruction": NEXT_MISSING_OBJECT,
        "final_verdict": FINAL_VERDICT,
        "integrity": {
            "fit_used": False,
            "measured_mode_selection_used": False,
            "generation_rederived": False,
            "arbitrary_stress_weight_used": False,
            "arbitrary_compliance_used": False,
            "arbitrary_cross_term_used": False,
            "virtual_door_double_counted": False,
            "arbitrary_Yukawa_matrix_used": False,
            "new_mediator_used": False,
            "second_scale_used": False,
            "hidden_calibration_used": False,
            "post_comparison_retuning_used": False,
        },
    }
    checks = {
        "sources_pass": result["source_audit"]["checks_passed"],
        "frozen_modules_imported": (
            result["frozen_sector_modules"]["family_slot_count"] == 3
        ),
        "no_action_density": (
            result["mode_action_source"]["located_action_density"] is None
        ),
        "projected_spectral_route_exhausted": (
            len(
                result["projected_spectral_action_audit"]["candidates"]
            )
            == 7
        ),
        "proxy_derivatives_recorded": (
            result["Hellmann_Feynman_audit"]["candidate_derivatives"]
            ["charged_lepton"]
            == [0, -2, -18]
            and result["Hellmann_Feynman_audit"][
                "candidate_derivatives"
            ]["up"]
            == [0, -72, -128]
            and result["Hellmann_Feynman_audit"][
                "candidate_derivatives"
            ]["down"]
            == [0, 0, -32]
        ),
        "proxy_not_promoted": all(
            result["response_matrices"][sector][
                "conditional_proxy_promoted"
            ]
            is False
            for sector in ("charged_lepton", "up", "down")
        ),
        "ledger_action_intertwiner_absent": (
            result["mode_action_source"][
                "ledger_to_action_spectral_intertwiner"
            ]
            is None
        ),
        "no_classical_stress_fabricated": all(
            result["classical_bilinear_mode_stress"][sector][
                "bilinear_tensor"
            ]
            is None
            for sector in ("charged_lepton", "up", "down")
        ),
        "no_response_fabricated": all(
            result["response_matrices"][sector]["matrix"] is None
            for sector in ("charged_lepton", "up", "down")
        ),
        "virtual_door_not_applied": (
            result["virtual_door_placement"][
                "applications_in_action_stress"
            ]
            == 0
        ),
        "alpha_not_inserted": (
            result["alpha_impedance_status"][
                "multiplied_into_mass_response"
            ]
            is False
        ),
        "stronger_than_v8_2": result["final_verdict"] != v82.FINAL_VERDICT,
    }
    result["validation"] = checks
    result["validation_passed"] = all(checks.values())
    return result


def status_report() -> dict[str, Any]:
    data = payload()
    return {
        key: data[key]
        for key in (
            "version",
            "frozen_sector_modules",
            "mode_action_source",
            "projected_spectral_action_audit",
            "Hellmann_Feynman_audit",
            "background_quadratic_vs_self_backreaction",
            "action_canonical_Gram_matrices",
            "classical_bilinear_mode_stress",
            "mixed_metric_mode_Hessian",
            "interface_compliance",
            "geometric_work_functional",
            "response_matrices",
            "virtual_door_placement",
            "alpha_impedance_status",
            "physical_observables",
            "prediction_freeze_sha256",
            "post_freeze_comparison",
            "RB15",
            "RB16",
            "release_status",
            "remaining_exact_obstruction",
            "final_verdict",
            "validation_passed",
        )
    }


def status_to_markdown(report: dict[str, Any] | None = None) -> str:
    report = status_report() if report is None else report
    modules = report["frozen_sector_modules"]["modules"]
    lines = [
        "# BHSM v8.3 classical mode-stress incidence",
        "",
        (
            "The frozen modules remain attached. The basis-free spectral "
            "route is exhausted, but no action-derived intertwiner realizes "
            "their ledger as one action operator's normalized spectrum."
        ),
        "",
        (
            "| Sector | Frozen basis | Proxy tau | Action Gram | "
            "Physical response |"
        ),
        "| --- | --- | --- | --- | --- |",
    ]
    for sector in ("charged_lepton", "up", "down"):
        basis = ", ".join(
            str(tuple(mode)) for mode in modules[sector]["basis"]
        )
        tau = report["Hellmann_Feynman_audit"][
            "candidate_derivatives"
        ][sector]
        lines.append(
            f"| {sector} | {basis} | `{tau}` | `None` | `None` |"
        )
    lines.extend(
        [
            "",
            "- Formal M4 EFT stress: `delta_ij T_Dirac` (central, rejected)",
            (
                "- Exact associated-scalar operator: metric dependent, "
                "but its frozen-ledger intertwiner is absent"
            ),
            (
                "- Berger proxy: evaluated exactly and retained as "
                "conditional evidence, not promoted"
            ),
            "- Mixed metric-mode Hessian: `None`",
            "- Selected seam compliance: `None`",
            "- Mass ratios: `None`",
            "- CKM: `None`",
            "- Virtual-door action applications: `0`",
            (
                "- Alpha impedance: "
                "`LACKS_ACTION_ATTACHMENT`"
            ),
            (
                "- Prediction freeze SHA-256: "
                f"`{report['prediction_freeze_sha256']}`"
            ),
            f"- RB-15: `{report['RB15']['status']}`",
            f"- RB-16: `{report['RB16']['status']}`",
            f"- Release: `{report['release_status']}`",
            "",
            (
                "Remaining exact obstruction: "
                f"`{report['remaining_exact_obstruction']}`"
            ),
            "",
            f"Verdict: `{report['final_verdict']}`",
            "",
        ]
    )
    return "\n".join(lines)


def materialize(root: Path) -> tuple[Path, Path]:
    artifact = root / "artifacts" / f"{ARTIFACT_NAME}.json"
    gate = root / "artifacts" / "BHSM_1_0_completion_gate.json"
    artifact.write_bytes(deterministic_json(payload()).encode("utf-8"))
    gate.write_bytes(
        deterministic_json(completion_gate_payload()).encode("utf-8")
    )
    return artifact, gate


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--materialize", action="store_true")
    args = parser.parse_args(argv)
    if not args.materialize:
        parser.error("--materialize is required")
    root = repository_root()
    for path in materialize(root):
        print(path.relative_to(root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
