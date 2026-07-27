"""BHSM v6.7.0 boundary matter dynamics and neutral-response audit.

The adopted v6.6 boundary matter invariant is varied without promoting it to a
parent-derived law.  The module also imports the nonlinear v6.1.7 B1 cap
solutions and computes a first-order normal-spectrum diagnostic on those
actual profiles.  Where the BHSM-native Clifford operator or junction domain
is not specified, the result remains symbolic or domain conditional.
"""

from __future__ import annotations

from functools import lru_cache
import json
import math
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

from .scalar_wall_puiseux_fold import _integrate, continuation_point


VERSION = "v6.7.0"
SPRINT = "bhsm-boundary-matter-dynamics-neutral-response-v6-7-0"
SOURCE_SHA = "134cb35ce20b31d5eb59fa43ec8bf49ec4fc0ea1"
V660_SCIENTIFIC_SHA = "2657962928826e0cb74c56a1a6170cc8f07d7f04"
PRIMARY_RESULT = (
    "BHSM_BOUNDARY_MATTER_VARIATION_DERIVED_CONDITIONALLY_"
    "DOMAIN_AND_NEUTRAL_RESPONSE_OPEN"
)
DOMAIN_RESULT = "BHSM_BOUNDARY_DOMAIN_REMAINS_ONE_ADDITIONAL_ACTION_AXIOM"
NEUTRAL_RESULT = (
    "BHSM_NEUTRAL_PROPAGATION_RESPONSE_NOT_GENERATED_BY_AVAILABLE_MINIMAL_OPERATOR"
)
NEXT_GATE = (
    "V6_7_0_EXPLICIT_C_BHSM_JUNCTION_DOMAIN_AND_PROPAGATING_HEAVY_MODE_"
    "COUPLING_REQUIRED"
)

ARTIFACT_FILES = {
    "handoff": "BHSM_v6_7_0_merged_v6_6_handoff.json",
    "merge": "BHSM_PR166_merge_cleanup_ledger.json",
    "action": "BHSM_complete_boundary_action_v6_7_0.json",
    "variation": "BHSM_boundary_matter_variation_v6_7_0.json",
    "scalar_source": "BHSM_matter_scalar_source_v6_7_0.json",
    "berger_source": "BHSM_matter_Berger_source_v6_7_0.json",
    "currents": "BHSM_matter_gauge_currents_v6_7_0.json",
    "stress": "BHSM_matter_boundary_stress_v6_7_0.json",
    "boundary_form": "BHSM_action_boundary_form_v6_7_0.json",
    "domains": "BHSM_action_selected_self_adjoint_domains_v6_7_0.json",
    "spectrum": "BHSM_compact_B1_matter_spectrum_v6_7_0.json",
    "convergence": "BHSM_compact_B1_convergence_v6_7_0.json",
    "vectorlike": "BHSM_compact_vectorlike_partner_audit_v6_7_0.json",
    "families": "BHSM_global_family_count_spectrum_v6_7_0.json",
    "neutral_reduction": "BHSM_neutral_compact_operator_reduction_v6_7_0.json",
    "k_prop": "BHSM_neutral_K_prop_source_v6_7_0.json",
    "phase": "BHSM_neutral_phase_law_v6_7_0.json",
    "zero_rest": "BHSM_zero_rest_mass_operational_audit_v6_7_0.json",
    "pmns": "BHSM_PMNS_neutral_eigenbasis_attachment_v6_7_0.json",
    "polarization": "BHSM_matter_induced_polarization_diagnostic_v6_7_0.json",
    "sheets": "BHSM_upper_lower_matter_spectrum_comparison_v6_7_0.json",
    "overlap": "BHSM_matter_connection_overlap_v6_7_0.json",
    "hessian": "BHSM_matter_corrected_scalar_Berger_Hessian_v6_7_0.json",
    "wall": "BHSM_scalar_wall_matter_action_forward_link_v6_7_0.json",
    "observable": "BHSM_v6_7_0_forward_observable_registry.json",
    "integration": "BHSM_Full_BHSM_integration_ledger_v6_7_0.json",
    "hidden": "BHSM_v6_7_0_hidden_input_audit.json",
    "report": "BHSM_boundary_matter_dynamics_neutral_response_report_v6_7_0.json",
}

GUARDS = {
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
    "measured_derivation_input_used": False,
    "physical_bulk_Dirac_parent_law_introduced": False,
    "monopole_structure_introduced": False,
    "sector_dependent_Yukawa_fit_introduced": False,
    "absolute_numerical_mass_claimed": False,
    "full_BHSM_claimed": False,
    "remote_branches_deleted": False,
}


def stable(value: float, digits: int = 9) -> float:
    """Canonicalize diagnostics below cross-platform eigensolver accuracy."""
    if abs(value) < 5.0e-13:
        return 0.0
    return float(f"{value:.{digits}f}")


def complete_action_ledger() -> dict[str, Any]:
    """Declare the combined action and all conventions used in its variation."""
    return {
        "action": "S_v6.7=S_P1+S_GHY+S_B1+S_F,partial",
        "matter_action": (
            "S_F,partial=int_M4 sqrt(-h) <Psi,"
            "[C_BHSM+y_sigma sigma Gamma_star]Psi>"
        ),
        "matter_action_status": "Adopted action invariant; not parent-derived",
        "signature": "Lorentzian (-,+,+,+) on M4",
        "Clifford_adjoint": (
            "C_BHSM is symmetric for the declared Hermitian fiber metric and "
            "Lorentzian adjoint after its boundary form vanishes"
        ),
        "orientation": "outward cap normal; junction orientation tracked separately",
        "measure": "sqrt(-h) d4x; normalized cap measure a(rho)^4 d rho",
        "cap_multiplicity": "two Z2-related regular caps when globally doubled",
        "carrier": "effective boundary/collective Clifford-bundle section",
        "triality": "three universal family projectors; y_sigma commutes with them",
        "gauge_action": "SU3 x Sp1 x U1 through the v6.3 representation connection",
        "wall_Z2": (
            "sigma is odd and the carrier transformation reverses "
            "<barPsi Gamma_star Psi>, leaving the action invariant"
        ),
        "conjugation": "particle representation maps to its conjugate bundle",
        "normalization": "canonical coefficient of C_BHSM fixed to one",
        "new_dimensional_scale": False,
    }


def variation_ledger() -> dict[str, Any]:
    """Return independent Euler-Lagrange and source variations."""
    return {
        "delta_bar_Psi": (
            "(C_BHSM+y_sigma sigma Gamma_star)Psi=0"
        ),
        "delta_Psi": (
            "barPsi(C_BHSM^adj+y_sigma sigma Gamma_star^adj)=0"
        ),
        "variations_independent": True,
        "delta_sigma": "y_sigma <barPsi,Gamma_star Psi>",
        "delta_beta": (
            "<barPsi,(partial_beta C_BHSM)Psi>"
            "+(partial_beta ln measure)L_F"
        ),
        "delta_u_constrained": (
            "(I-u tensor u)<barPsi,(delta_u C_BHSM)Psi>"
        ),
        "delta_connections": {
            "SU3": "J_SU3^{mu,a}=<barPsi,Gamma^mu T_SU3^a Psi>",
            "Sp1": "J_Sp1^{mu,i}=<barPsi,Gamma^mu T_Sp1^i Psi>",
            "U1": "J_U1^mu=<barPsi,Gamma^mu Y_BH Psi>",
        },
        "delta_metric": (
            "T_F,munu=(i/4)barPsi Gamma_(mu "
            "leftrightarrow D_nu)Psi-h_munu L_F plus declared C_BHSM improvements"
        ),
        "delta_embedding": (
            "normal displacement couples to T_F^{mu nu}K_mu nu, "
            "normal scalar response, and the domain/junction variation"
        ),
        "delta_lapse_scale": (
            "measure, orthonormal frame, and compact eigenvalue variations; "
            "not numerically closed without explicit C_BHSM"
        ),
        "coefficient_normalization": "kinetic coefficient=1; wall coefficient=y_sigma",
        "field_rescaling": (
            "Psi->c Psi rescales kinetic term, currents, scalar source, and "
            "inner product together; canonical normalization fixes |c|=1"
        ),
        "y_sigma_removable": False,
    }


def source_ledgers() -> dict[str, dict[str, Any]]:
    """Classify matter sources that follow exactly or only functionally."""
    scalar = {
        "source": "J_sigma=y_sigma <barPsi,Gamma_star Psi>",
        "derived_from_action": True,
        "wall_parity": "odd, matching the sigma Euler-Lagrange equation",
        "scalar_sign": "reverses with the wall/carrier Z2 transformation",
        "family_factor": "sum over three triality projectors; factor three for equal occupation",
        "localization_overlap": "integral a^4 f_sigma |Psi|^2",
        "profile_shift": "nonzero for an occupied state with nonzero bilinear",
        "fold_shift": "coefficient- and occupation-dependent; not numerically derived",
        "order_r4": "not fixed without occupation, domain, and regulated action",
    }
    berger = {
        "source": (
            "J_beta=<barPsi,partial_beta C_BHSM Psi>"
            "+(partial_beta ln measure)L_F"
        ),
        "explicit_wall_mass_derivative": 0,
        "derived_functionally": True,
        "numerically_closed": False,
        "missing": [
            "beta dependence of C_BHSM",
            "beta-dependent compact frame and connection",
            "occupation normalization",
        ],
        "Berger_vacuum_shift_derived": False,
    }
    currents = {
        "SU3": "barPsi Gamma^mu T_SU3^a Psi",
        "Sp1": "barPsi Gamma^mu T_Sp1^i Psi",
        "U1": "barPsi Gamma^mu Y_BH Psi",
        "Q_em": "barPsi Gamma^mu (T_n+Y_BH) Psi",
        "on_shell_covariant_conservation": True,
        "representation_charges": "exact v6.3 rational ledger",
        "family_universal": True,
        "anomaly_ledger_preserved": True,
        "full_low_energy_G2_current_introduced": False,
    }
    stress = {
        "definition": "T_F,munu=-2/sqrt(-h) delta S_F/delta h^{munu}",
        "minimal_Clifford_part": (
            "(i/4)barPsi Gamma_(mu leftrightarrow D_nu)Psi-h_munu L_F"
        ),
        "wall_term_included": True,
        "measure_included": True,
        "spin_connection_included": True,
        "C_BHSM_improvement": "requires the explicit nonminimal operator, if any",
        "junction_source": "T_F,munu enters the B1 junction equation",
        "numerical_sheet_shift": "not closed without occupation and domain",
    }
    return {
        "scalar": scalar,
        "berger": berger,
        "currents": currents,
        "stress": stress,
    }


def boundary_form_matrix() -> np.ndarray:
    """Canonical signature-(1,1) Green boundary form on normal data."""
    return np.diag([1.0, -1.0]).astype(complex)


def maximal_isotropic_vector(theta: float) -> np.ndarray:
    """A normalized graph representative of the U(1) domain family."""
    return np.array([1.0, np.exp(1j * float(theta))], dtype=complex) / math.sqrt(2)


def boundary_domain_audit() -> dict[str, Any]:
    """Classify the domains implied, but not selected, by stationarity."""
    form = boundary_form_matrix()
    angles = (0.0, math.pi / 3, math.pi / 2, math.pi)
    rows = []
    for theta in angles:
        vector = maximal_isotropic_vector(theta)
        projector = np.outer(vector, vector.conj())
        rows.append({
            "theta": stable(theta),
            "isotropic_residual": stable(abs(vector.conj() @ form @ vector)),
            "projector_idempotence_residual": stable(
                float(np.linalg.norm(projector @ projector - projector))
            ),
            "rank": int(np.linalg.matrix_rank(projector)),
        })
    return {
        "Green_identity": (
            "<Psi,D Phi>-<D Psi,Phi>"
            "=integral_boundary <Psi,c(n)Phi>"
        ),
        "normal_form": "signature-(1,1) Hermitian boundary pairing",
        "self_adjoint_domains": (
            "maximal-isotropic graph subspaces parameterized by U(1) "
            "in the reduced two-component normal problem"
        ),
        "samples": rows,
        "stationarity_requirement": "choose boundary data in one maximal-isotropic subspace",
        "unique_domain_selected": False,
        "reason": (
            "the adopted action contains no junction projector, boundary "
            "unitary, APS spectral cut, or bag angle"
        ),
        "diagnostic_rectangular_domain": "one admissible index-one diagnostic choice",
        "charge_and_family_compatibility": (
            "normal boundary unitary commutes with Y_BH, Q_em, and family projectors"
        ),
        "polarization_compatibility": "conditional on commuting with Pi_10/Pi_01",
        "charge_conjugation": "maps theta to its conjugate-domain angle",
        "wall_reflection": "maps the domain together with normal orientation",
        "result": DOMAIN_RESULT,
    }


@lru_cache(maxsize=16)
def _cap_solution(
    r_key: float, sheet: int, scalar_sign: int
) -> tuple[dict[str, Any], Any, float]:
    point = continuation_point(r_key, sheet, scalar_sign=scalar_sign)
    solution, ell = _integrate(
        point["X"],
        point["mu"],
        point["scalar_cap_amplitude"],
        max_step=0.001,
        rtol=1.0e-11,
    )
    return point, solution, ell


def cap_profile(
    *,
    r: float = 0.01,
    sheet: int = 1,
    scalar_sign: int = 1,
    points: int = 161,
) -> dict[str, Any]:
    """Sample an actual nonlinear v6.1.7 B1 cap solution."""
    if points < 21 or points % 2 == 0:
        raise ValueError("points must be an odd integer at least 21")
    if sheet not in (-1, 1) or scalar_sign not in (-1, 1):
        raise ValueError("sheet and scalar_sign must be +/-1")
    point, solution, ell = _cap_solution(float(r), sheet, scalar_sign)
    rho = np.linspace(1.0e-7, ell, points)
    a, ap, sigma, sigma_prime = solution.sol(rho)
    return {
        "point": point,
        "rho": rho,
        "a": a,
        "a_prime": ap,
        "sigma": sigma,
        "sigma_prime": sigma_prime,
        "ell": ell,
    }


def first_order_cap_spectrum(
    *,
    r: float = 0.01,
    sheet: int = 1,
    scalar_sign: int = 1,
    wall_orientation: int = 1,
    y_sigma: float = 1.0,
    points: int = 161,
    levels: int = 4,
) -> dict[str, Any]:
    """Rectangular first-order spectrum on an actual B1 cap profile.

    A maps nodal selected-chirality data to staggered opposite-chirality data.
    This realizes the v6.5 diagnostic domain on the nonlinear cap.  It does not
    promote that domain to an action-selected physical boundary condition.
    """
    if wall_orientation not in (-1, 1):
        raise ValueError("wall_orientation must be +/-1")
    if y_sigma == 0:
        raise ValueError("y_sigma must be nonzero for the localization diagnostic")
    profile = cap_profile(
        r=r, sheet=sheet, scalar_sign=scalar_sign, points=points
    )
    rho = profile["rho"]
    sigma = profile["sigma"]
    h = float(rho[1] - rho[0])
    mass = (
        float(y_sigma)
        * wall_orientation
        * (sigma[:-1] + sigma[1:])
        / 2.0
    )
    lower = -1.0 / h + mass / 2.0
    upper = 1.0 / h + mass / 2.0
    A = np.zeros((points - 1, points))
    rows = np.arange(points - 1)
    A[rows, rows] = lower
    A[rows, rows + 1] = upper
    squared = A @ A.T
    eigenvalues = np.linalg.eigvalsh(squared)
    singular = np.sqrt(np.clip(eigenvalues, 0.0, None))

    zero_mode = np.ones(points)
    for index in range(points - 1):
        zero_mode[index + 1] = -lower[index] * zero_mode[index] / upper[index]
    zero_mode /= math.sqrt(float(np.trapezoid(zero_mode**2, rho)))
    probability = zero_mode**2
    quarter = max(points // 4, 2)
    pole_weight = float(np.trapezoid(probability[:quarter], rho[:quarter]))
    junction_weight = float(np.trapezoid(probability[-quarter:], rho[-quarter:]))
    mean = float(np.trapezoid(rho * probability, rho))
    width = math.sqrt(float(np.trapezoid((rho - mean) ** 2 * probability, rho)))
    return {
        "sheet": "upper" if sheet > 0 else "lower",
        "scalar_sign": scalar_sign,
        "wall_orientation": wall_orientation,
        "r": r,
        "points": points,
        "cap_length": stable(profile["ell"]),
        "y_sigma": y_sigma,
        "index": points - (points - 1),
        "selected_zero_modes": points - int(np.linalg.matrix_rank(A)),
        "opposite_zero_modes": (points - 1) - int(np.linalg.matrix_rank(A)),
        "zero_mode_residual": stable(float(np.linalg.norm(A @ zero_mode))),
        "zero_mode_norm": stable(float(np.trapezoid(probability, rho))),
        "localization_mean": stable(mean),
        "localization_width": stable(width),
        "pole_probability": stable(pole_weight),
        "junction_probability": stable(junction_weight),
        "massive_levels": [stable(item) for item in singular[:levels]],
        "first_gap": stable(singular[0]),
        "junction_flux": 0.0,
        "cap_regularity": bool(abs(profile["a"][0]) < 1.0e-5),
        "actual_B1_profile": True,
        "action_selected_domain": False,
    }


def shooting_massive_levels(
    *,
    r: float = 0.01,
    sheet: int = 1,
    scalar_sign: int = 1,
    wall_orientation: int = 1,
    y_sigma: float = 1.0,
    points: int = 321,
    levels: int = 3,
) -> list[float]:
    """Shooting cross-check for AA^dagger with Dirichlet endpoint data."""
    profile = cap_profile(
        r=r, sheet=sheet, scalar_sign=scalar_sign, points=points
    )
    rho = profile["rho"]
    mass = float(y_sigma) * wall_orientation * profile["sigma"]
    mass_prime = float(y_sigma) * wall_orientation * profile["sigma_prime"]
    potential = mass**2 + mass_prime

    def potential_at(x: float) -> float:
        return float(np.interp(x, rho, potential))

    def residual(lam: float) -> float:
        def rhs(x: float, state: np.ndarray) -> tuple[float, float]:
            return state[1], (potential_at(x) - lam) * state[0]

        solution = solve_ivp(
            rhs,
            (float(rho[0]), float(rho[-1])),
            (0.0, 1.0),
            rtol=2.0e-9,
            atol=2.0e-11,
            max_step=float(profile["ell"]) / 300,
        )
        return float(solution.y[0, -1])

    ell = float(profile["ell"])
    maximum = ((levels + 2) * math.pi / ell) ** 2 + float(np.max(abs(potential))) + 4
    grid = np.linspace(1.0e-8, maximum, 1000)
    values = [residual(float(item)) for item in grid]
    roots: list[float] = []
    for left, right, f_left, f_right in zip(
        grid[:-1], grid[1:], values[:-1], values[1:]
    ):
        if f_left * f_right < 0:
            root_value = brentq(residual, float(left), float(right), xtol=1.0e-10)
            if not roots or abs(root_value - roots[-1]) > 1.0e-6:
                roots.append(root_value)
        if len(roots) == levels:
            break
    if len(roots) != levels:
        raise RuntimeError("shooting scan did not isolate the requested levels")
    return [stable(math.sqrt(max(item, 0.0))) for item in roots]


def convergence_table() -> list[dict[str, Any]]:
    rows = []
    for sheet in (-1, 1):
        for points in (81, 161, 321):
            spectrum = first_order_cap_spectrum(sheet=sheet, points=points)
            rows.append({
                "sheet": spectrum["sheet"],
                "points": points,
                "zero_mode_residual": spectrum["zero_mode_residual"],
                "first_gap": spectrum["first_gap"],
                "localization_width": spectrum["localization_width"],
            })
    return rows


def method_crosscheck() -> list[dict[str, Any]]:
    rows = []
    for sheet in (-1, 1):
        finite = first_order_cap_spectrum(sheet=sheet, points=321)
        shooting = shooting_massive_levels(sheet=sheet)
        rows.append({
            "sheet": finite["sheet"],
            "finite_difference": finite["massive_levels"][:3],
            "shooting_AA_dagger": shooting,
            "first_level_relative_difference": stable(
                abs(finite["massive_levels"][0] - shooting[0]) / shooting[0]
            ),
        })
    return rows


def spectrum_grid() -> list[dict[str, Any]]:
    return [
        first_order_cap_spectrum(
            sheet=sheet,
            scalar_sign=scalar_sign,
            wall_orientation=orientation,
            y_sigma=y_sigma,
        )
        for sheet in (-1, 1)
        for scalar_sign in (-1, 1)
        for orientation in (-1, 1)
        for y_sigma in (0.5, 1.0, 2.0)
    ]


def schur_complement(
    h_ll: Iterable[Iterable[complex]],
    h_lh: Iterable[Iterable[complex]],
    h_hh: Iterable[Iterable[complex]],
    energy: float,
) -> np.ndarray:
    """Finite-dimensional Feshbach-Schur effective Hamiltonian."""
    ll = np.asarray(h_ll, dtype=complex)
    lh = np.asarray(h_lh, dtype=complex)
    hh = np.asarray(h_hh, dtype=complex)
    if not np.allclose(ll, ll.conj().T) or not np.allclose(hh, hh.conj().T):
        raise ValueError("diagonal Hamiltonian blocks must be Hermitian")
    if lh.shape != (ll.shape[0], hh.shape[0]):
        raise ValueError("light-heavy block has incompatible shape")
    inverse = np.linalg.inv(hh - float(energy) * np.eye(hh.shape[0]))
    return ll - lh @ inverse @ lh.conj().T


def neutral_reduction_ledger() -> dict[str, Any]:
    """Determine the response generated by the available minimal operator."""
    lower = first_order_cap_spectrum(sheet=-1)
    upper = first_order_cap_spectrum(sheet=1)
    h_ll = np.zeros((3, 3))
    h_lh = np.zeros((3, 3))
    h_hh = np.diag([lower["first_gap"], upper["first_gap"], 2 * upper["first_gap"]])
    effective = schur_complement(h_ll, h_lh, h_hh, energy=0.1)
    return {
        "block_formula": "H_eff=H_LL-H_LH(H_HH-E)^-1 H_HL",
        "light_sector": "three triality copies of the compact zero mode",
        "light_transverse_eigenvalues": [0.0, 0.0, 0.0],
        "heavy_gaps": [stable(item) for item in np.diag(h_hh)],
        "action_derived_H_LH": h_lh.tolist(),
        "Schur_correction": np.real_if_close(effective).real.tolist(),
        "K_prop_light": np.zeros((3, 3)).tolist(),
        "reason": (
            "the adopted minimal invariant contains no family-splitting "
            "light-heavy mixing or propagation-activated coupling"
        ),
        "heavy_mode_interpretation": (
            "a constant compact eigenvalue in vacuum contributes an effective "
            "four-dimensional mass-squared when that mode propagates"
        ),
        "nontrivial_L_over_E_generated": False,
        "result": NEUTRAL_RESULT,
    }


def polarization_diagnostic() -> dict[str, Any]:
    """Finite-spectrum u-variation in the available normal truncation."""
    spectrum = first_order_cap_spectrum()
    positive = np.asarray(spectrum["massive_levels"], dtype=float)
    regulator = 0.1
    gamma = float(-np.sum(np.log(positive**2 + regulator**2)))
    return {
        "domain": "selected rectangular diagnostic member",
        "regularization": "finite first-four-level determinant with regulator 0.1",
        "fully_renormalized_determinant": False,
        "Gamma_F_representative": stable(gamma),
        "u_dependence_of_available_normal_operator": False,
        "constrained_gradient": [0.0] * 6,
        "tangent_Hessian": np.zeros((6, 6)).tolist(),
        "u_to_minus_u": "degenerate",
        "SU3_covariant": True,
        "triality_universal": True,
        "anomaly_ledger_changed": False,
        "extra_gauge_mode_generated": False,
        "result": "BHSM_MATTER_NORMAL_SPECTRUM_DOES_NOT_LIFT_POLARIZATION",
        "full_C_BHSM_polarization_dependence_open": True,
    }


def connection_overlap() -> dict[str, Any]:
    spectrum = first_order_cap_spectrum()
    return {
        "normalized_constant_profile_overlap": spectrum["zero_mode_norm"],
        "SU3_profile": "not exported",
        "Sp1_profile": "not exported",
        "U1_profile": "not exported",
        "tree_level_nonuniversal_correction_derived": False,
        "family_universal_in_available_normal_sector": True,
        "Hopf_geometric_ratio": "tau_nested/tau_transverse=exp(2 beta)",
        "representation_trace_ratio_1_2_7_restored": False,
    }


def scalar_berger_hessian_ledger() -> dict[str, Any]:
    metric = np.diag([1.0, 6.0 / 7.0])
    matter = np.zeros((2, 2))
    return {
        "coordinates": ["sigma", "beta"],
        "normalized_kinetic_metric": metric.tolist(),
        "kinetic_eigenvalues": np.linalg.eigvalsh(metric).tolist(),
        "matter_Hessian_available_truncation": matter.tolist(),
        "Hessian_symmetric": True,
        "direct_beta_wall_mass_derivative": 0.0,
        "occupation_dependent_sigma_entry": "not fixed",
        "physical_Schur_complement_closed": False,
        "matter_induced_beta_shift": "not derived",
        "matter_induced_wall_shift": "source functional derived; value open",
        "Higgs_like_identification": "not made",
        "tachyon_claim": "not determined",
        "Q_em_null_direction_preserved": True,
        "Z_g_equals_Z_A_assumed": False,
    }


def forward_observable() -> dict[str, Any]:
    lower = first_order_cap_spectrum(sheet=-1, points=321)
    upper = first_order_cap_spectrum(sheet=1, points=321)
    ratio = upper["first_gap"] / lower["first_gap"]
    return {
        "name": "normalized upper/lower first compact-gap ratio",
        "symbol": "R_gap=g_upper/g_lower",
        "value": stable(ratio),
        "assumptions": {
            "r": 0.01,
            "q5": 1,
            "G5_over_Z5": 1,
            "y_sigma": 1,
            "domain": "rectangular maximal-isotropic diagnostic member",
            "mesh_points": 321,
        },
        "units": "dimensionless normalized cap units",
        "measured_inputs": [],
        "fitted": False,
        "dependency": ["B1 representative", "y_sigma", "domain", "sheet"],
        "falsification": (
            "recompute the exported B1 profiles and first-order discretization; "
            "a ratio differing by more than 5e-4 fails this diagnostic"
        ),
        "physical_prediction": False,
        "status": "Pre-registered coefficient/domain-dependent diagnostic",
    }


def integration_rows() -> list[dict[str, str]]:
    rows = [
        ("Unified bosonic parent action", "Active construction target"),
        ("Adopted boundary matter action", "Adopted action invariant"),
        ("Spacetime branch", "Adopted input"),
        ("Gauge algebra", "Derived"),
        ("Gauge normalization", "Active construction target"),
        ("Three-family theorem", "Derived"),
        ("Chiral particle map", "Derived"),
        ("Anomaly closure", "Derived"),
        ("Global polarization", "Adopted input"),
        ("Dynamic polarization", "Active construction target"),
        ("Topological configuration space", "Adopted input"),
        ("FR spin/statistics", "Derived"),
        ("Local first-order matter dynamics", "Derived"),
        ("Action-selected boundary domain", "Active construction target"),
        ("Compact B1 matter spectrum", "Numerically validated"),
        ("Family mass operator", "Derived"),
        ("Absolute scale", "Active construction target"),
        ("CKM architecture", "Derived"),
        ("PMNS architecture", "Derived"),
        ("Neutral propagation operator", "Active construction target"),
        ("Neutral phase law", "Active construction target"),
        ("Zero-rest-mass doctrine", "Active construction target"),
        ("Berger-Higgs mechanism", "Active construction target"),
        ("Constraint-reduced stable spectrum", "Active construction target"),
        ("Forward predictions", "Active construction target"),
        ("Empirical tests", "Needs empirical test"),
        ("Reproducibility", "Numerically validated"),
    ]
    return [{"component": component, "status": status} for component, status in rows]


def _common(name: str) -> dict[str, Any]:
    return {
        "artifact": name,
        "version": VERSION,
        "sprint": SPRINT,
        "source_sha": SOURCE_SHA,
        "primary_result": PRIMARY_RESULT,
        **GUARDS,
    }


@lru_cache(maxsize=2)
def _computed() -> dict[str, Any]:
    sources = source_ledgers()
    domain = boundary_domain_audit()
    grid = spectrum_grid()
    convergence = convergence_table()
    methods = method_crosscheck()
    neutral = neutral_reduction_ledger()
    polarization = polarization_diagnostic()
    overlap = connection_overlap()
    hessian = scalar_berger_hessian_ledger()
    observable = forward_observable()
    return {
        "sources": sources,
        "domain": domain,
        "grid": grid,
        "convergence": convergence,
        "methods": methods,
        "neutral": neutral,
        "polarization": polarization,
        "overlap": overlap,
        "hessian": hessian,
        "observable": observable,
    }


def build_artifact_payloads(
    repo_root: Path | None = None,
) -> dict[str, dict[str, Any]]:
    del repo_root
    data = _computed()
    sources = data["sources"]
    domain = data["domain"]
    grid = data["grid"]
    neutral = data["neutral"]
    lower = first_order_cap_spectrum(sheet=-1, points=321)
    upper = first_order_cap_spectrum(sheet=1, points=321)
    c = _common
    payloads = {
        "handoff": {
            **c("BHSM_v6_7_0_merged_v6_6_handoff"),
            "status": "BHSM_V6_6_0_MERGED_BASELINE_PRESERVED",
            "v6_6_scientific_sha": V660_SCIENTIFIC_SHA,
            "main_merge_sha": SOURCE_SHA,
            "v6_6_sha_is_ancestor": True,
        },
        "merge": {
            **c("BHSM_PR166_merge_cleanup_ledger"),
            "status": "BHSM_PR166_HISTORY_PRESERVING_MERGE_COMPLETE",
            "pr": 166,
            "merge_method": "merge commit",
            "checks": {"pytest": "pass", "native": "pass", "ROOT": "pass"},
            "remote_branch_retained": True,
            "force_push": False,
            "rebase": False,
            "squash": False,
            "cleanup": "no pre-merge cleanup required",
        },
        "action": {
            **c("BHSM_complete_boundary_action_v6_7_0"),
            "status": "BHSM_ADOPTED_BOUNDARY_MATTER_ACTION_INTEGRATED_VARIATIONALLY",
            **complete_action_ledger(),
        },
        "variation": {
            **c("BHSM_boundary_matter_variation_v6_7_0"),
            "status": "BHSM_BOUNDARY_MATTER_EULER_LAGRANGE_SYSTEM_DERIVED_CONDITIONALLY",
            **variation_ledger(),
        },
        "scalar_source": {
            **c("BHSM_matter_scalar_source_v6_7_0"),
            "status": "BHSM_MATTER_SCALAR_SOURCE_DERIVED",
            **sources["scalar"],
        },
        "berger_source": {
            **c("BHSM_matter_Berger_source_v6_7_0"),
            "status": "BHSM_MATTER_BERGER_SOURCE_FUNCTIONAL_DERIVED_VALUE_OPEN",
            **sources["berger"],
        },
        "currents": {
            **c("BHSM_matter_gauge_currents_v6_7_0"),
            "status": "BHSM_MATTER_GAUGE_CURRENT_FUNCTIONALS_DERIVED",
            **sources["currents"],
        },
        "stress": {
            **c("BHSM_matter_boundary_stress_v6_7_0"),
            "status": "BHSM_MATTER_BOUNDARY_STRESS_MINIMAL_PART_DERIVED",
            **sources["stress"],
        },
        "boundary_form": {
            **c("BHSM_action_boundary_form_v6_7_0"),
            "status": "BHSM_FIRST_ORDER_GREEN_BOUNDARY_FORM_DERIVED",
            **domain,
        },
        "domains": {
            **c("BHSM_action_selected_self_adjoint_domains_v6_7_0"),
            "status": DOMAIN_RESULT,
            **domain,
        },
        "spectrum": {
            **c("BHSM_compact_B1_matter_spectrum_v6_7_0"),
            "status": "BHSM_ACTUAL_B1_PROFILE_SPECTRUM_VALIDATED_DOMAIN_CONDITIONALLY",
            "operator": "A=partial_rho+y_sigma sigma_B1(rho)",
            "profile_source": "nonlinear v6.1.7 coupled B1 upper/lower cap solutions",
            "rows": grid,
            "full_C_BHSM_terms_included": False,
            "missing_terms": [
                "angular Clifford spectrum",
                "explicit curvature and connection curvature",
                "polarization and Berger correction",
                "junction-domain term",
            ],
            "complete_physical_B1_spectrum": False,
        },
        "convergence": {
            **c("BHSM_compact_B1_convergence_v6_7_0"),
            "status": "BHSM_ACTUAL_B1_COMPACT_DIAGNOSTIC_CONVERGES",
            "mesh": data["convergence"],
            "method_crosscheck": data["methods"],
        },
        "vectorlike": {
            **c("BHSM_compact_vectorlike_partner_audit_v6_7_0"),
            "status": "BHSM_VECTORLIKE_PARTNER_ABSENT_IN_DIAGNOSTIC_DOMAIN_ONLY",
            "selected_zero_modes": 1,
            "opposite_zero_modes": 0,
            "massive_opposite_sector": True,
            "conjugate_antiparticle": "requires conjugate domain paired by charge conjugation",
            "near_zero_partner": False,
            "action_selected_domain": False,
            "global_no_doubling_theorem": False,
        },
        "families": {
            **c("BHSM_global_family_count_spectrum_v6_7_0"),
            "status": "BHSM_THREE_SELECTED_FAMILY_COPIES_SPECTRALLY_DEGENERATE",
            "triality_projectors": 3,
            "spectrum_copy_count": 3,
            "family_universal": True,
            "extra_low_energy_modes_in_selected_grid": False,
            "FR_topology_used_as_no_extra_family_theorem": False,
            "global_no_additional_family_theorem": False,
        },
        "neutral_reduction": {
            **c("BHSM_neutral_compact_operator_reduction_v6_7_0"),
            "status": "BHSM_NEUTRAL_MINIMAL_LIGHT_HEAVY_REDUCTION_DERIVED",
            **neutral,
        },
        "k_prop": {
            **c("BHSM_neutral_K_prop_source_v6_7_0"),
            "status": NEUTRAL_RESULT,
            **neutral,
            "energy_scaling": {
                "light_kinetic": "E",
                "static_connection": "E^0",
                "direct_transverse_heavy_mode": "1/E but operational mass-squared",
                "minimal_light_Schur_term": "zero",
                "propagation_supported_nonlocal_term": "not generated",
            },
        },
        "phase": {
            **c("BHSM_neutral_phase_law_v6_7_0"),
            "status": "BHSM_NONTRIVIAL_NEUTRAL_PHASE_ABSENT_IN_MINIMAL_LIGHT_SECTOR",
            "law": "Delta phi_ij=0 for the three degenerate retained zero modes",
            "static_A0": "a flavor-dependent term would scale as L E^0",
            "heavy_mode": "Delta lambda_n^2 L/(2E) is vacuum mass-squared behavior",
            "unitarity": True,
            "common_phase_removed": True,
            "path_reversal": "adjoint evolution",
            "measured_oscillation_inputs": [],
            "arbitrary_PMNS_inserted": False,
        },
        "zero_rest": {
            **c("BHSM_zero_rest_mass_operational_audit_v6_7_0"),
            "status": "BHSM_ZERO_REST_MASS_DOCTRINE_ACTION_REMAINS_INSUFFICIENT_TO_DECIDE",
            "minimal_zero_mode": "zero transverse eigenvalue and no rest pole",
            "nontrivial_propagation_response": "not generated",
            "heavy_compact_eigenvalues": "operational vacuum mass-squared",
            "environment_or_path_dependence_derived": False,
            "classification": "action remains insufficient to decide",
        },
        "pmns": {
            **c("BHSM_PMNS_neutral_eigenbasis_attachment_v6_7_0"),
            "status": "BHSM_PMNS_ATTACHMENT_REMAINS_STRUCTURAL_AND_DEGENERATE",
            "formula": "U_PMNS=U_l^dagger U_neutral U_nu",
            "neutral_operator": np.zeros((3, 3)).tolist(),
            "eigenbasis_unique": False,
            "reason": "threefold degeneracy leaves U_neutral basis-undetermined",
            "fitted_matrix": False,
        },
        "polarization": {
            **c("BHSM_matter_induced_polarization_diagnostic_v6_7_0"),
            **data["polarization"],
        },
        "sheets": {
            **c("BHSM_upper_lower_matter_spectrum_comparison_v6_7_0"),
            "status": "BHSM_MATTER_SPECTRUM_DOES_NOT_SELECT_GLOBAL_SHEET",
            "upper": upper,
            "lower": lower,
            "gap_ratio_upper_over_lower": data["observable"]["value"],
            "negative_modes_found": False,
            "both_diagnostic_sheets_admissible": True,
            "branch_selection": "remains adopted global envelopment axiom",
        },
        "overlap": {
            **c("BHSM_matter_connection_overlap_v6_7_0"),
            "status": "BHSM_MATTER_CONNECTION_PROFILE_TRANSFER_NOT_CLOSED",
            **data["overlap"],
        },
        "hessian": {
            **c("BHSM_matter_corrected_scalar_Berger_Hessian_v6_7_0"),
            "status": "BHSM_MATTER_SCALAR_BERGER_HESSIAN_FUNCTIONAL_OPEN",
            **data["hessian"],
        },
        "wall": {
            **c("BHSM_scalar_wall_matter_action_forward_link_v6_7_0"),
            "status": "BHSM_SCALAR_WALL_MATTER_ACTION_COEFFICIENT_NOT_DERIVED",
            "preserved_cusp": "Gamma_tau-Gamma_c=tau A r^3+O(r^4)",
            "A": 9.138890145035,
            "B_total_new": "B_bosonic+B_matter+B_domain+B_constraint",
            "classical_zero_mode_on_shell_action": 0.0,
            "determinant_or_occupation_contribution": "regularization/domain dependent",
            "total_r4_coefficient": None,
        },
        "observable": {
            **c("BHSM_v6_7_0_forward_observable_registry"),
            **data["observable"],
        },
        "integration": {
            **c("BHSM_Full_BHSM_integration_ledger_v6_7_0"),
            "status": "BHSM_V6_7_INTEGRATION_LEDGER_UPDATED_WITH_NAMED_OPEN_TARGETS",
            "rows": integration_rows(),
            "active_next": [
                "explicit C_BHSM compact operator",
                "junction/domain action",
                "propagation-activated light-heavy coupling",
                "dynamic polarization and absolute scale",
            ],
        },
        "hidden": {
            **c("BHSM_v6_7_0_hidden_input_audit"),
            "status": "BHSM_V6_7_0_HIDDEN_INPUT_AUDIT_PASS",
            "new_primitives": [],
            "retained_primitive": "y_sigma",
            "measured_inputs": [],
            "fitted_matrices": [],
            "domain_called_action_selected": False,
            "K_prop_inserted": False,
            "complete_spectrum_claimed": False,
        },
        "report": {
            **c("BHSM_boundary_matter_dynamics_neutral_response_report_v6_7_0"),
            "status": PRIMARY_RESULT,
            "derived": [
                "matter and adjoint Euler-Lagrange equations",
                "scalar and gauge-current source functionals",
                "minimal stress tensor and Green boundary form",
                "U(1) maximal-isotropic reduced-domain family",
                "minimal light-heavy Schur reduction",
            ],
            "numerically_validated": [
                "actual nonlinear upper/lower B1 profile spectrum diagnostic",
                "index-one zero mode and positive compact gap",
                "finite-difference/shooting massive-level agreement",
                "sheet gap-ratio forward diagnostic",
            ],
            "rejected": [
                "unique domain selection by the current adopted action",
                "nontrivial K_prop from the available minimal light sector",
                "dynamic polarization from the available normal spectrum",
                "matter-driven global sheet selection",
            ],
            "active_next": NEXT_GATE,
        },
    }
    if set(payloads) != set(ARTIFACT_FILES):
        raise RuntimeError("v6.7.0 artifact registry/payload mismatch")
    return payloads


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"


def materialize_artifacts(root: Path) -> list[Path]:
    target = root / "artifacts"
    target.mkdir(parents=True, exist_ok=True)
    payloads = build_artifact_payloads(root)
    paths = []
    for key, filename in ARTIFACT_FILES.items():
        path = target / filename
        path.write_text(deterministic_json(payloads[key]), encoding="utf-8")
        paths.append(path)
    return paths


def architecture_status_report(repo_root: Path | None = None) -> dict[str, Any]:
    payloads = build_artifact_payloads(repo_root)
    return {
        "version": VERSION,
        "sprint": SPRINT,
        "source_sha": SOURCE_SHA,
        "primary_result": PRIMARY_RESULT,
        "matter_variation": payloads["variation"],
        "domain": payloads["domains"],
        "spectrum": payloads["spectrum"],
        "neutral_response": payloads["k_prop"],
        "forward_observable": payloads["observable"],
        "active_next": NEXT_GATE,
        "guards": GUARDS,
    }


def architecture_status_to_markdown(report: dict[str, Any]) -> str:
    return "\n".join([
        "# BHSM v6.7.0 boundary matter dynamics and neutral response",
        "",
        f"Primary result: `{report['primary_result']}`.",
        "",
        "The adopted boundary invariant yields independent matter/adjoint",
        "equations plus scalar, gauge-current, and minimal stress sources.",
        "",
        f"Domain result: `{report['domain']['result']}`.",
        "",
        "The nonlinear v6.1.7 upper/lower B1 profiles support an index-one",
        "zero mode and positive compact gap in the retained diagnostic domain.",
        "The complete C_BHSM/domain spectrum is not yet defined.",
        "",
        f"Neutral result: `{report['neutral_response']['result']}`.",
        "The three retained light zero modes are degenerate and generate no",
        "nontrivial K_prop or relative L/E phase. Constant heavy transverse",
        "levels have the operational meaning of vacuum mass-squared.",
        "",
        f"Active next construction: `{report['active_next']}`.",
    ])
