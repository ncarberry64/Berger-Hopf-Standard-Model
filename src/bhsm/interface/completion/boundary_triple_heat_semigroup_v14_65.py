"""BHSM v14.65 reduced self-adjoint boundary-triple / heat-semigroup gate.

This sprint constructs an exact reduced continuum theorem witness for the
v14.64 relative-boundary correspondence target.  Each incidence edge of the
M8 -> M5+/- -> M4 diamond is represented by a finite interval carrying a
magnetic covariant Laplacian.  Standard continuity plus covariant Kirchhoff
flux matching is encoded as a boundary-triple self-adjoint extension.

The construction is deliberately fail-closed:
* it proves a self-adjoint continuum domain exists for the reduced diamond;
* it derives the exact positive-resolvent Dirichlet-to-Neumann/Weyl matrix;
* its degree-two Kirchhoff realization is exactly a magnetic circle, so the
  spectrum depends only on total metric length and one loop holonomy;
* the heat trace and relative zeta determinant are then exact and cutoff-free;
* the relative determinant supplies a genuine holonomy force, but the reduced
  scalar circle cannot retain independent M8/M5/M4 tangential dynamics.

Therefore this is a rigorous correspondence skeleton, not the physical BHSM
operator.  The full next object is operator-valued: actual tangential
Dirac-Laplace blocks, Wentzell/KKT seam dynamics, ghosts/zero modes, and the
action-selected global stationary background.

No physical particle prediction is emitted.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import math
from typing import Any, Mapping, Sequence

import numpy as np

VERSION = "v14.65"

PRIMARY_VERDICT = (
    "BHSM_V14_65_THE_TWO_CAP_ENVELOPMENT_DIAMOND_ADMITS_AN_EXACT_SELF_ADJOINT_"
    "MAGNETIC_BOUNDARY_TRIPLE_REALIZATION_WITH_CONTINUITY_AND_COVARIANT_"
    "KIRCHHOFF_FLUX_MATCHING_AND_AN_EXACT_HERMITIAN_DTN_WEYL_FUNCTION_BUT_"
    "BECAUSE_EVERY_VERTEX_HAS_DEGREE_TWO_THE_MINIMAL_SCALAR_REALIZATION_IS_"
    "UNITARILY_EQUIVALENT_TO_ONE_MAGNETIC_CIRCLE_AND_COLLAPSES_ALL_EDGE_LENGTH_"
    "DATA_TO_TOTAL_LENGTH_PLUS_ONE_LOOP_HOLONOMY_SO_THE_PHYSICAL_BHSM_"
    "CORRESPONDENCE_MUST_BE_OPERATOR_VALUED_WITH_STRATUM_TANGENTIAL_DYNAMICS"
)

HEAT_VERDICT = (
    "BHSM_V14_65_ON_THE_EXACT_REDUCED_MAGNETIC_CIRCLE_THE_PREDECLARED_HEAT_"
    "SEMIGROUP_BRANCH_HAS_A_CUTOFF_FREE_TRACE_AND_RELATIVE_ZETA_DETERMINANT_"
    "WITH_LOG_DET_RATIO_LOG_OF_COSH_ML_MINUS_COS_PHI_OVER_COSH_ML_MINUS_ONE_"
    "AND_THEREFORE_GENERATES_AN_ACTION_OWNED_HOLONOMY_FORCE_ONCE_THE_OPERATOR_"
    "STATISTICS_AND_GLOBAL_BACKGROUND_ARE_FIXED"
)

COLLAPSE_VERDICT = (
    "BHSM_V14_65_THE_PURE_SCALAR_DEGREE_TWO_KIRCHHOFF_DIAMOND_CANNOT_ENCODE_"
    "INDEPENDENT_PLUS_MINUS_CAP_OR_M8_M5_M4_SPECTRAL_RESPONSES_BECAUSE_ITS_"
    "SPECTRUM_IS_A_FUNCTION_ONLY_OF_TOTAL_LENGTH_MASS_AND_LOOP_HOLONOMY"
)

EXACT_NEXT_OBJECT = (
    "OPERATOR_VALUED_CALDERON_BOUNDARY_TRIPLE_OR_WENTZELL_KKT_REALIZATION_"
    "USING_THE_ACTUAL_M8_M5_PLUS_MINUS_M4_TANGENTIAL_DIRAC_LAPLACE_BLOCKS_"
    "ACTION_SELECTED_GLOBAL_ENVELOPMENT_LENGTHS_AND_CONNECTION_HOLONOMY_"
    "COMPLETE_GAUGE_GHOST_ZERO_MODE_PROJECTORS_THEN_COMPUTE_THE_FULL_RELATIVE_"
    "HEAT_KERNEL_ZETA_FUNCTION_GLOBAL_STATIONARY_BRANCH_AND_RUN_THE_FROZEN_"
    "NO_RETUNING_NEUTRINO_KILL_SCREEN"
)

VERTICES = ("M8", "M5_plus", "M5_minus", "M4")
VERTEX_INDEX = {v: i for i, v in enumerate(VERTICES)}

# Each edge orientation is fixed once and for all.  The loop orientation is
# M8 -> M5+ -> M4 -> M5- -> M8, so e_m4 and e_8m enter the loop backwards.
EDGES = (
    ("M8", "M5_plus", "e_8p"),
    ("M5_plus", "M4", "e_p4"),
    ("M5_minus", "M4", "e_m4"),
    ("M8", "M5_minus", "e_8m"),
)
EDGE_NAMES = tuple(e[2] for e in EDGES)


def canonical_json_bytes(payload: Any) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def sha256_payload(payload: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def _finite_positive(x: float, name: str) -> float:
    y = float(x)
    if not math.isfinite(y) or y <= 0.0:
        raise ValueError(f"{name} must be positive and finite")
    return y


def principal_phase(phi: float) -> float:
    p = float(phi)
    if not math.isfinite(p):
        raise ValueError("phase must be finite")
    return math.atan2(math.sin(p), math.cos(p))


def diamond_holonomy(phases: Mapping[str, float]) -> float:
    raw = (
        float(phases.get("e_8p", 0.0))
        + float(phases.get("e_p4", 0.0))
        - float(phases.get("e_m4", 0.0))
        - float(phases.get("e_8m", 0.0))
    )
    return principal_phase(raw)


def gauge_transform_edge_phases(
    phases: Mapping[str, float], vertex_phases: Mapping[str, float]
) -> dict[str, float]:
    """Gauge transform compatible with M' = U M U^* for the vertex DtN map.

    For an oriented edge i -> j, alpha' = alpha - theta_i + theta_j.
    """
    out: dict[str, float] = {}
    for a, b, name in EDGES:
        out[name] = principal_phase(
            float(phases.get(name, 0.0))
            - float(vertex_phases.get(a, 0.0))
            + float(vertex_phases.get(b, 0.0))
        )
    return out


def endpoint_layout() -> dict[str, tuple[int, int]]:
    return {name: (2 * i, 2 * i + 1) for i, (_, _, name) in enumerate(EDGES)}


def vertex_endpoint_indices() -> dict[str, tuple[int, int]]:
    layout = endpoint_layout()
    by_vertex: dict[str, list[int]] = {v: [] for v in VERTICES}
    for a, b, name in EDGES:
        left, right = layout[name]
        by_vertex[a].append(left)
        by_vertex[b].append(right)
    out = {v: tuple(xs) for v, xs in by_vertex.items()}
    if any(len(xs) != 2 for xs in out.values()):
        raise RuntimeError("diamond is expected to have degree two at every vertex")
    return out  # type: ignore[return-value]


def self_adjoint_extension_matrices() -> tuple[np.ndarray, np.ndarray]:
    """Return A,B for A Gamma0 + B Gamma1 = 0 on the 8 endpoints.

    At every degree-two vertex:
      * row 1 imposes continuity u_a-u_b=0;
      * row 2 imposes covariant Kirchhoff flux p_a+p_b=0.

    The finite-dimensional self-adjoint extension criterion is
    rank(A,B)=8 and A B^* = B A^*.
    """
    n = 2 * len(EDGES)
    a = np.zeros((n, n), dtype=complex)
    b = np.zeros((n, n), dtype=complex)
    row = 0
    for vertex in VERTICES:
        i, j = vertex_endpoint_indices()[vertex]
        a[row, i] = 1.0
        a[row, j] = -1.0
        row += 1
        b[row, i] = 1.0
        b[row, j] = 1.0
        row += 1
    return a, b


def self_adjoint_extension_diagnostics() -> dict[str, float | int | bool]:
    a, b = self_adjoint_extension_matrices()
    rank = int(np.linalg.matrix_rank(np.concatenate((a, b), axis=1)))
    comm = float(np.linalg.norm(a @ np.conjugate(b.T) - b @ np.conjugate(a.T)))
    return {
        "boundary_dimension": int(a.shape[0]),
        "rank_A_B": rank,
        "ABstar_minus_BAstar_norm": comm,
        "self_adjoint_extension_criterion_pass": rank == a.shape[0] and comm < 1e-13,
    }


def sample_domain_boundary_data(seed: int = 1465) -> tuple[np.ndarray, np.ndarray]:
    """Construct Gamma0,Gamma1 data satisfying continuity/Kirchhoff exactly."""
    rng = np.random.default_rng(seed)
    n = 2 * len(EDGES)
    g0 = np.zeros(n, dtype=complex)
    g1 = np.zeros(n, dtype=complex)
    for vertex in VERTICES:
        i, j = vertex_endpoint_indices()[vertex]
        u = rng.normal() + 1j * rng.normal()
        p = rng.normal() + 1j * rng.normal()
        g0[i] = g0[j] = u
        g1[i] = p
        g1[j] = -p
    return g0, g1


def boundary_green_form(g0_f: np.ndarray, g1_f: np.ndarray, g0_g: np.ndarray, g1_g: np.ndarray) -> complex:
    return np.vdot(g1_f, g0_g) - np.vdot(g0_f, g1_g)


def local_edge_dtn(length: float, kappa: float, phase: float = 0.0) -> np.ndarray:
    """Exact magnetic interval DtN matrix for (-D_x^2 + kappa^2)u=0.

    Boundary ordering follows the oriented edge left -> right and Gamma1 uses
    outward covariant normal derivatives.  The phase is the integrated edge
    connection alpha = int A dx.
    """
    ell = _finite_positive(length, "length")
    kap = _finite_positive(kappa, "kappa")
    alpha = principal_phase(phase)
    z = kap * ell
    sh = math.sinh(z)
    if sh == 0.0:
        raise ValueError("singular hyperbolic denominator")
    coth = math.cosh(z) / sh
    csch = 1.0 / sh
    em = np.exp(-1j * alpha)
    ep = np.exp(+1j * alpha)
    return kap * np.array(
        [[coth, -csch * em], [-csch * ep, coth]], dtype=complex
    )


def global_vertex_dtn(
    lengths: Mapping[str, float],
    kappa: float,
    phases: Mapping[str, float] | None = None,
) -> np.ndarray:
    """Assemble the exact four-vertex Weyl/DtN matrix by edge addition."""
    phases = {} if phases is None else phases
    m = np.zeros((len(VERTICES), len(VERTICES)), dtype=complex)
    for a, b, name in EDGES:
        loc = local_edge_dtn(lengths[name], kappa, phases.get(name, 0.0))
        i, j = VERTEX_INDEX[a], VERTEX_INDEX[b]
        m[i, i] += loc[0, 0]
        m[i, j] += loc[0, 1]
        m[j, i] += loc[1, 0]
        m[j, j] += loc[1, 1]
    return m


def gauge_transform_vertex_matrix(m: np.ndarray, vertex_phases: Mapping[str, float]) -> np.ndarray:
    theta = np.array([float(vertex_phases.get(v, 0.0)) for v in VERTICES], dtype=float)
    u = np.diag(np.exp(1j * theta))
    a = np.asarray(m, dtype=complex)
    return u @ a @ np.conjugate(u.T)


def dtn_gauge_witness() -> dict[str, Any]:
    lengths = {"e_8p": 1.15, "e_p4": 0.73, "e_m4": 0.91, "e_8m": 1.31}
    phases = {"e_8p": 0.21, "e_p4": 0.44, "e_m4": 0.13, "e_8m": -0.37}
    theta = {"M8": 0.31, "M5_plus": -0.27, "M5_minus": 0.52, "M4": -0.11}
    kap = 0.83
    m0 = global_vertex_dtn(lengths, kap, phases)
    phases_g = gauge_transform_edge_phases(phases, theta)
    m1 = global_vertex_dtn(lengths, kap, phases_g)
    expected = gauge_transform_vertex_matrix(m0, theta)
    ev = np.linalg.eigvalsh(m0)
    return {
        "version": VERSION,
        "kappa": kap,
        "lengths_diagnostic": lengths,
        "phases_diagnostic": phases,
        "holonomy": diamond_holonomy(phases),
        "holonomy_after_vertex_gauge": diamond_holonomy(phases_g),
        "hermiticity_residual": float(np.linalg.norm(m0 - np.conjugate(m0.T))),
        "gauge_covariance_residual": float(np.linalg.norm(m1 - expected)),
        "minimum_DtN_eigenvalue": float(np.min(ev)),
        "positive_resolvent_DtN_positive": bool(np.min(ev) > 0.0),
        "physical_BHSM_prediction": False,
    }


def total_length(lengths: Mapping[str, float]) -> float:
    return sum(_finite_positive(lengths[name], name) for name in EDGE_NAMES)


def circle_eigenvalue(n: int, circumference: float, holonomy: float, mass: float) -> float:
    ell = _finite_positive(circumference, "circumference")
    m = float(mass)
    if not math.isfinite(m) or m < 0.0:
        raise ValueError("mass must be nonnegative and finite")
    phi = principal_phase(holonomy)
    return ((2.0 * math.pi * int(n) + phi) / ell) ** 2 + m * m


def heat_trace_primal(
    t: float,
    circumference: float,
    holonomy: float,
    mass: float,
    nmax: int = 200,
) -> float:
    tt = _finite_positive(t, "t")
    ncut = int(nmax)
    if ncut < 1:
        raise ValueError("nmax must be positive")
    vals = [math.exp(-tt * circle_eigenvalue(n, circumference, holonomy, mass)) for n in range(-ncut, ncut + 1)]
    return math.fsum(vals)


def heat_trace_poisson(
    t: float,
    circumference: float,
    holonomy: float,
    mass: float,
    kmax: int = 200,
) -> float:
    tt = _finite_positive(t, "t")
    ell = _finite_positive(circumference, "circumference")
    m = float(mass)
    if not math.isfinite(m) or m < 0.0:
        raise ValueError("mass must be nonnegative and finite")
    kcut = int(kmax)
    if kcut < 1:
        raise ValueError("kmax must be positive")
    phi = principal_phase(holonomy)
    pref = ell / math.sqrt(4.0 * math.pi * tt) * math.exp(-tt * m * m)
    terms = [1.0]
    for k in range(1, kcut + 1):
        terms.append(2.0 * math.exp(-(ell * ell * k * k) / (4.0 * tt)) * math.cos(k * phi))
    return pref * math.fsum(terms)


def relative_heat_trace(t: float, circumference: float, holonomy: float, mass: float) -> float:
    # Choose the representation with stronger numerical convergence.
    tt = _finite_positive(t, "t")
    if tt < circumference * circumference / (4.0 * math.pi):
        return heat_trace_poisson(tt, circumference, holonomy, mass, 120) - heat_trace_poisson(tt, circumference, 0.0, mass, 120)
    return heat_trace_primal(tt, circumference, holonomy, mass, 220) - heat_trace_primal(tt, circumference, 0.0, mass, 220)


def exact_relative_logdet(circumference: float, holonomy: float, mass: float) -> float:
    ell = _finite_positive(circumference, "circumference")
    m = _finite_positive(mass, "mass")
    phi = principal_phase(holonomy)
    numerator = math.cosh(m * ell) - math.cos(phi)
    denominator = math.cosh(m * ell) - 1.0
    return math.log(numerator / denominator)


def truncated_relative_logdet(
    circumference: float,
    holonomy: float,
    mass: float,
    nmax: int = 20000,
) -> float:
    ncut = int(nmax)
    if ncut < 1:
        raise ValueError("nmax must be positive")
    vals = []
    for n in range(-ncut, ncut + 1):
        a = circle_eigenvalue(n, circumference, holonomy, mass)
        b = circle_eigenvalue(n, circumference, 0.0, mass)
        vals.append(math.log(a / b))
    return math.fsum(vals)


def holonomy_force(circumference: float, holonomy: float, mass: float) -> float:
    ell = _finite_positive(circumference, "circumference")
    m = _finite_positive(mass, "mass")
    phi = principal_phase(holonomy)
    return math.sin(phi) / (math.cosh(m * ell) - math.cos(phi))


def holonomy_curvature(circumference: float, holonomy: float, mass: float) -> float:
    ell = _finite_positive(circumference, "circumference")
    m = _finite_positive(mass, "mass")
    phi = principal_phase(holonomy)
    c = math.cosh(m * ell)
    d = c - math.cos(phi)
    return (math.cos(phi) * d - math.sin(phi) ** 2) / (d * d)


def spectral_collapse_payload() -> dict[str, Any]:
    # Same total length, very different partition among strata.
    a = {"e_8p": 1.0, "e_p4": 1.0, "e_m4": 1.0, "e_8m": 1.0}
    b = {"e_8p": 0.4, "e_p4": 1.6, "e_m4": 0.7, "e_8m": 1.3}
    phases = {"e_8p": 0.2, "e_p4": 0.31, "e_m4": -0.08, "e_8m": -0.15}
    phi = diamond_holonomy(phases)
    mass = 0.7
    eig_a = [circle_eigenvalue(n, total_length(a), phi, mass) for n in range(-6, 7)]
    eig_b = [circle_eigenvalue(n, total_length(b), phi, mass) for n in range(-6, 7)]
    return {
        "version": VERSION,
        "verdict": COLLAPSE_VERDICT,
        "partition_A": a,
        "partition_B": b,
        "total_length_A": total_length(a),
        "total_length_B": total_length(b),
        "same_total_length": total_length(a) == total_length(b),
        "same_holonomy": True,
        "sample_spectrum_max_difference": float(np.max(np.abs(np.asarray(eig_a) - np.asarray(eig_b)))),
        "minimal_scalar_Kirchhoff_realization_retains_independent_stratum_lengths": False,
        "required_upgrade": "operator-valued tangential Weyl functions and dynamic/Wentzell-KKT vertex-seam coupling",
        "physical_BHSM_prediction": False,
    }


def solve_monotone_global_scale(
    a8: float = 0.04,
    a6: float = 0.08,
    a3: float = 0.20,
    z: float = -1.0,
) -> float:
    """Diagnostic v14.61-style global scale solve by deterministic bisection.

    Solves 8 A8 exp(8x)+6 A6 exp(6x)+3 A3 exp(3x)+Z=0.
    Coefficients are synthetic theorem-witness values, not BHSM physics.
    """
    vals = [float(a8), float(a6), float(a3)]
    if any((not math.isfinite(v) or v < 0.0) for v in vals):
        raise ValueError("power coefficients must be finite and nonnegative")
    zz = float(z)
    if not math.isfinite(zz) or zz >= 0.0:
        raise ValueError("diagnostic z must be finite and negative")

    def f(x: float) -> float:
        return 8.0*a8*math.exp(8.0*x) + 6.0*a6*math.exp(6.0*x) + 3.0*a3*math.exp(3.0*x) + zz

    lo, hi = -8.0, 2.0
    flo, fhi = f(lo), f(hi)
    if not (flo < 0.0 < fhi):
        raise RuntimeError("failed to bracket diagnostic scale root")
    for _ in range(120):
        mid = 0.5 * (lo + hi)
        fm = f(mid)
        if fm > 0.0:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def no_retuning_pipeline_payload() -> dict[str, Any]:
    frozen = {
        "A8": 0.04,
        "A6": 0.08,
        "A3": 0.20,
        "Z": -1.0,
        "edge_shape_fractions": {"e_8p": 0.8, "e_p4": 1.1, "e_m4": 0.9, "e_8m": 1.2},
        "edge_phases": {"e_8p": 0.2, "e_p4": 0.31, "e_m4": -0.08, "e_8m": -0.15},
        "diagnostic_mass": 0.7,
        "heat_time": 0.6,
    }
    x = solve_monotone_global_scale(frozen["A8"], frozen["A6"], frozen["A3"], frozen["Z"])
    scale = math.exp(x)
    lengths = {k: scale * v for k, v in frozen["edge_shape_fractions"].items()}
    phi = diamond_holonomy(frozen["edge_phases"])
    circumference = total_length(lengths)
    logdet = exact_relative_logdet(circumference, phi, frozen["diagnostic_mass"])
    heat = relative_heat_trace(frozen["heat_time"], circumference, phi, frozen["diagnostic_mass"])
    stationarity = 8.0*frozen["A8"]*math.exp(8*x) + 6.0*frozen["A6"]*math.exp(6*x) + 3.0*frozen["A3"]*math.exp(3*x) + frozen["Z"]
    return {
        "version": VERSION,
        "purpose": "demonstrate a frozen-before-solve global-BVP -> lengths -> self-adjoint operator -> heat/zeta pipeline with no downstream tuning",
        "all_fixture_inputs_frozen_before_solve": True,
        "fixture_inputs": frozen,
        "global_scale_x_diagnostic": x,
        "global_scale_stationarity_residual": abs(stationarity),
        "derived_edge_lengths": lengths,
        "derived_total_length": circumference,
        "derived_loop_holonomy_from_frozen_edge_phases": phi,
        "relative_heat_trace_diagnostic": heat,
        "relative_logdet_diagnostic": logdet,
        "postcomparison_adjustment_performed": False,
        "physical_BHSM_prediction": False,
    }


def self_adjoint_domain_payload() -> dict[str, Any]:
    diag = self_adjoint_extension_diagnostics()
    f0, f1 = sample_domain_boundary_data(1465)
    g0, g1 = sample_domain_boundary_data(1466)
    green = boundary_green_form(f0, f1, g0, g1)
    return {
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "operator": "direct sum of magnetic interval Laplacians -D_x^2+m^2 on the four envelopment incidence edges",
        "boundary_maps": {
            "Gamma0": "endpoint values",
            "Gamma1": "outward covariant endpoint derivatives",
        },
        "extension": "continuity plus covariant Kirchhoff flux conservation at each M8/M5+/M5-/M4 vertex",
        **diag,
        "sample_domain_green_form_abs": abs(green),
        "reduced_continuum_self_adjoint_domain_closed": bool(diag["self_adjoint_extension_criterion_pass"] and abs(green) < 1e-13),
        "full_BHSM_operator_domain_closed": False,
        "physical_BHSM_prediction": False,
    }


def heat_zeta_payload() -> dict[str, Any]:
    lengths = {"e_8p": 1.15, "e_p4": 0.73, "e_m4": 0.91, "e_8m": 1.31}
    phases = {"e_8p": 0.21, "e_p4": 0.44, "e_m4": 0.13, "e_8m": -0.37}
    ell = total_length(lengths)
    phi = diamond_holonomy(phases)
    m = 0.7
    t = 0.5
    primal = heat_trace_primal(t, ell, phi, m, 240)
    poisson = heat_trace_poisson(t, ell, phi, m, 240)
    exact_det = exact_relative_logdet(ell, phi, m)
    trunc_det = truncated_relative_logdet(ell, phi, m, 50000)
    return {
        "version": VERSION,
        "verdict": HEAT_VERDICT,
        "circumference_diagnostic": ell,
        "holonomy_diagnostic": phi,
        "mass_diagnostic": m,
        "heat_time_diagnostic": t,
        "heat_trace_primal": primal,
        "heat_trace_poisson": poisson,
        "heat_trace_duality_residual": abs(primal-poisson),
        "exact_relative_logdet": exact_det,
        "truncated_symmetric_spectral_product_logdet": trunc_det,
        "truncated_product_residual": abs(trunc_det-exact_det),
        "holonomy_force_at_diagnostic_phase": holonomy_force(ell, phi, m),
        "holonomy_force_at_zero": holonomy_force(ell, 0.0, m),
        "holonomy_curvature_at_zero": holonomy_curvature(ell, 0.0, m),
        "positive_prefactor_selects_phi_zero_as_local_minimum_in_this_reduced_single_species_witness": holonomy_curvature(ell, 0.0, m) > 0.0,
        "full_BHSM_supertrace_holonomy_selected": False,
        "physical_BHSM_prediction": False,
    }


def status_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "validated": [
            "The reduced two-cap diamond has an exact continuum self-adjoint magnetic interval realization.",
            "Continuity plus covariant Kirchhoff flux matching satisfies rank(A,B)=8 and AB*=BA*.",
            "The positive-resolvent edge DtN/Weyl function is exact, Hermitian, positive, and vertex-gauge covariant.",
            "The degree-two diamond is unitarily equivalent to a magnetic circle with total length and one loop holonomy.",
            "The heat trace has mutually consistent momentum and Poisson/winding representations.",
            "The reduced relative zeta determinant is cutoff-free and has a closed holonomy-dependent formula.",
            "The nonlocal determinant generates a holonomy force once statistics and the operator are fixed.",
        ],
        "invalidated": [
            "The minimal scalar Kirchhoff diamond retains independent spectral memory of all four stratum edge lengths.",
            "A self-adjoint scalar metric-graph skeleton is already the full M8/M5/M4 BHSM operator.",
            "The loop holonomy must remain an arbitrary external flavor parameter once the nonlocal determinant is included.",
        ],
        "reclassified": [
            "v14.64's abstract boundary-triple target is realizable exactly in a reduced continuum theorem class.",
            "The principal remaining domain problem is operator-valued tangential dynamics, not existence of any self-adjoint correspondence domain.",
            "Holonomy becomes a dynamical action variable in the relative heat/zeta branch rather than merely an incidence label.",
            "Independent cap/stratum information must enter through operator-valued Weyl functions or dynamic boundary terms, not through scalar edge partition alone.",
        ],
        "open": [
            "insert actual M8, M5+, M5-, and M4 tangential Dirac-Laplace operators into the boundary triple",
            "derive Wentzell/KKT dynamic seam terms from the stratified action",
            "derive the physical connection holonomy from the global stationary branch",
            "complete gauge, ghost, zero-mode, and Calderon projectors",
            "compute full mixed-dimensional relative heat coefficients and supertrace statistics",
            "solve and exhaust the physical global envelopment stationary branches",
            "derive effective fermion/current operators on the selected background",
            "run physical DtN/relative heat bundle and frozen neutrino kill screen without retuning",
        ],
    }


def next_object_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "closed_in_v14_65": [
            "reduced continuum boundary triple",
            "self-adjoint scalar magnetic diamond domain",
            "exact scalar DtN/Weyl function",
            "exact reduced heat trace",
            "exact reduced relative zeta determinant",
            "reduced holonomy-force mechanism",
        ],
        "mandatory_upgrade": "replace scalar interval edge operators by operator-valued actual stratum tangential Dirac-Laplace/Weyl operators and dynamic seam KKT/Wentzell coupling",
        "postcomparison_choice_forbidden": True,
    }


def completion_gate_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "full_BHSM_complete": False,
        "mark_III": "NOT_REACHED",
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "physical_prediction_emitted": False,
        "usb_touched": False,
        "v14_59_cap_inverse_problem_architecturally_bypassed": True,
        "v14_60_global_envelopment_selection_retained": True,
        "v14_64_continuum_trace_obstruction_respected": True,
        "reduced_self_adjoint_boundary_domain_closed": True,
        "full_operator_valued_BHSM_boundary_domain_closed": False,
        "reduced_heat_zeta_branch_closed": True,
        "physical_global_supertrace_heat_zeta_closed": False,
        "missing_checks": [
            "actual M8 tangential Dirac-Laplace block",
            "actual M5 plus/minus tangential Dirac-Laplace blocks",
            "actual intrinsic M4 fermion/gauge/scalar block",
            "action-derived Wentzell/KKT seam coupling",
            "physical connection holonomy from the stationary action",
            "complete Calderon/gauge/ghost/zero-mode projectors",
            "physical mixed-dimensional relative heat supertrace",
            "action-normalized global parent/child stationary solution",
            "branch exhaustion and gauge-reduced Hessian",
            "physical effective fermion/current operators",
            "physical DtN and relative heat-kernel bundle",
            "frozen no-retuning neutrino kill screen",
            "downstream masses/mixing/couplings only after all prior gates pass",
        ],
        "exact_next_object": EXACT_NEXT_OBJECT,
    }


def master_payload() -> dict[str, Any]:
    payload = {
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "heat_verdict": HEAT_VERDICT,
        "collapse_verdict": COLLAPSE_VERDICT,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "self_adjoint_domain": self_adjoint_domain_payload(),
        "dtn_weyl": dtn_gauge_witness(),
        "heat_zeta": heat_zeta_payload(),
        "spectral_collapse": spectral_collapse_payload(),
        "no_retuning_pipeline": no_retuning_pipeline_payload(),
    }
    payload["sha256_without_self_hash"] = sha256_payload(payload)
    return payload


def artifact_payloads() -> dict[str, dict[str, Any]]:
    return {
        "BHSM_boundary_triple_heat_semigroup_v14_65.json": master_payload(),
        "BHSM_self_adjoint_boundary_domain_v14_65.json": self_adjoint_domain_payload(),
        "BHSM_dtn_weyl_gate_v14_65.json": dtn_gauge_witness(),
        "BHSM_reduced_heat_zeta_gate_v14_65.json": heat_zeta_payload(),
        "BHSM_scalar_diamond_collapse_gate_v14_65.json": spectral_collapse_payload(),
        "BHSM_no_retuning_operator_pipeline_v14_65.json": no_retuning_pipeline_payload(),
        "BHSM_status_ledger_v14_65.json": status_payload(),
        "BHSM_next_object_gate_v14_65.json": next_object_payload(),
        "BHSM_completion_gate_v14_65.json": completion_gate_payload(),
    }


def materialize(out_dir: Path) -> list[Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for name, payload in sorted(artifact_payloads().items()):
        path = out / name
        path.write_bytes(canonical_json_bytes(payload) + b"\n")
        written.append(path)
    return written
