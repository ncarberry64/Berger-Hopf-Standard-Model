"""Exact checks of the dated amendment's restricted mathematical deductions.

This verifies algebra and records source provenance. It runs no coupled solve,
prediction, calibration ensemble, proof campaign or physical terminal model.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
BASE = "00614fa0d479a2de78460ca061cc5304cdb610cf"
AMENDMENT = "docs/BHSM_NORMAN_CORE_SURFACE_AMENDMENT_20261022.md"
OUTPUT = "artifacts/current_semantics/BHSM_NORMAN_CORE_SURFACE_AMENDMENT_20261022.json"
SOURCES = [
    "docs/BHSM_AETHER_PREGEOMETRIC_PARENT_CALCULUS_V15_0.md",
    "docs/BHSM_AETHER_DYNAMICAL_CORRESPONDENCE_V15_1.md",
    "docs/BHSM_AETHER_MICROSCOPIC_CORE_ACTION_V15_3.md",
    "docs/BHSM_AETHER_FOUNDATIONAL_EVENT_ALGEBRA_STATE_V15_4.md",
    "docs/BHSM_GLOBAL_PREGEOMETRIC_MASTER_CLOSURE_V15_5.md",
    "docs/BHSM_RECIPROCAL_CORE_SURFACE_ATTACHMENT_v11_3.md",
    "docs/BHSM_AETHER_CORE_SURFACE_TRACE_V15_11.md",
    "docs/BHSM_AETHER_MOVING_INTERFACE_TRANSFER_V15_12.md",
    "docs/BHSM_AETHER_MATERIAL_SKIN_VARIATION_V15_15.md",
    "docs/BHSM_AETHER_ETA_SIGMA_RESPONSE_CONSTRAINT_V15_40.md",
    "docs/BHSM_AETHER_POST_CUT_SELF_SIMILAR_PERSISTENCE_V15_47.md",
    "docs/BHSM_N3_FIREWALL_CORE_CHILD_OWNERSHIP_V17_98.md",
    "theory/ae4_current_c2_physical_enclosure_state_integration.md",
    "theory/ae4_event_response_jet_integration.md",
    "theory/ae31_c2_intrinsic_m4_lepton_action.md",
    "theory/bhsm_covariant_bubble_interface_mechanics.md",
    "theory/collective_curvature_dark_matter_interpretation.md",
]


def exact_checks() -> dict[str, bool]:
    k, f0 = sp.symbols("kappa1 f0", positive=True)
    tau, s, z, x = sp.symbols("tau s z x", real=True)
    X = s**2 - tau**2
    F = k * X / 2 + X**4 / 8
    A = k + X**3
    grad = sp.Matrix([-tau, s])
    G = A * sp.diag(-1, 1) + 6 * X**2 * grad * grad.T
    checks = {
        "principal_symbol_from_polynomial_Hessian": all(
            sp.simplify(v) == 0 for v in sp.hessian(F, (tau, s)) - G),
        "principal_determinant": sp.simplify(G.det() + A * (k + 7 * X**3)) == 0,
        "positive_time_kinetic_implies_hyperbolic_factor": sp.simplify(
            (k + 7 * X**3) - (-G[0, 0]) - 6 * X**2 * s**2) == 0,
    }
    # Differentiate the characteristic polynomial before setting tau=0.
    v = sp.symbols("v", positive=True)
    characteristic = G[0, 0] * v**2 - 2 * G[0, 1] * v + G[1, 1]
    dv_tau = (-sp.diff(characteristic, tau) / sp.diff(characteristic, v)).subs(tau, 0)
    dv_s = (-sp.diff(characteristic, s) / sp.diff(characteristic, v)).subs(tau, 0)
    A0, C0 = k + s**6, k + 7 * s**6
    directional = sp.factor(v * (-v * dv_tau + dv_s))
    directional = sp.factor(directional.subs(v**2, C0 / A0))
    checks["genuine_nonlinearity_directional_derivative"] = sp.simplify(
        directional - 6 * s**5 * (2 * k - 7 * s**6) / A0**2) == 0
    checks["stationary_flux_strict_monotone_polynomial"] = sp.diff((k + s**6) * s, s) == k + 7 * s**6
    checks["stationary_gradient_flux_derivative_on_positive_branch"] = sp.simplify(
        sp.diff(A * s, s) - A - 6 * s**2 * X**2) == 0
    hamiltonian_density = tau * sp.diff(-f0 * F, tau) + f0 * F
    checks["null_wave_nonzero_energy"] = sp.simplify(
        hamiltonian_density.subs({tau: -z, s: z}) - f0 * k * z**2) == 0
    W = sp.sin(x)**2 * sp.cos(x)**2
    dW = sp.sin(4 * x) * sp.sin(2 * x) / 2
    Z = sp.integrate(W, (x, 0, sp.pi / 2))
    dZ = sp.integrate(dW, (x, 0, sp.pi / 2))
    dA = sp.integrate(dW, (x, 0, sp.pi / 4))
    derivative = (dZ / 2 - dA) / W.subs(x, sp.pi / 4)
    checks["regular_carrier_weighted_median_at_identity"] = sp.simplify(
        sp.integrate(W, (x, 0, sp.pi / 4)) - Z / 2) == 0
    checks["regular_carrier_variation_integrals"] = Z == sp.pi / 16 and dZ == 0 and dA == sp.Rational(1, 6)
    checks["regular_carrier_shape_derivative_minus_two_thirds"] = derivative == -sp.Rational(2, 3)
    R, gamma, p = sp.symbols("R gamma p", positive=True)
    speed, acceleration = sp.symbols("speed acceleration", real=True)
    L = -gamma * R**p * sp.sqrt(1 - speed**2)
    momentum = sp.diff(L, speed)
    EL = (sp.diff(momentum, R) * speed + sp.diff(momentum, speed) * acceleration - sp.diff(L, R)) / R**p
    expected = gamma * (acceleration / (1 - speed**2)**sp.Rational(3, 2)
                        + p / (R * sp.sqrt(1 - speed**2)))
    checks["regular_radial_membrane_Euler_equation"] = sp.simplify(EL - expected) == 0
    nu, m, omega, rotation = sp.symbols("nu m omega rotation", real=True)
    checks["rigid_relabeling_keeps_frequency_differential"] = sp.expand(
        (nu - m * rotation) - m * (omega - rotation) - (nu - m * omega)) == 0
    return checks


def payload() -> dict:
    checks = exact_checks()
    if not all(checks.values()):
        raise AssertionError({k: v for k, v in checks.items() if not v})
    # The source checkout may use CRLF; canonical LF matches the Git blobs
    # and makes this text ledger portable across Windows and Linux.
    digest = lambda p: hashlib.sha256((ROOT / p).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    return {
        "schema_version": 1,
        "artifact": "BHSM_NORMAN_CORE_SURFACE_AMENDMENT_20261022",
        "date": "2026-10-22", "hypothesis_author": "Norman P. Carberry",
        "status": "ATTRIBUTED_HYPOTHESIS_WITH_SCOPED_MATHEMATICAL_DEDUCTIONS",
        "source_base_commit": BASE,
        "source_hash_basis": "UTF-8 text with CRLF normalized to LF; scientific source hashes equal the stated base Git blobs",
        "amendment": {"path": AMENDMENT, "sha256": digest(AMENDMENT)},
        "verification_tool": {"path": "tools/check_norman_core_surface_consequences.py",
            "sha256": digest("tools/check_norman_core_surface_consequences.py")},
        "author_handoff": {"label": "CODEX HANDOFF — UPDATE BHSM CORE/SURFACE THEORY AND THE BLACK HOLE TRACKER",
            "date": "2026-10-22", "sha256": "d604c8c48f66d6753bbf0b95bbb3d0953fd7d5e0d2d134b4288e2eeed38c5240"},
        "sources": [{"path": p, "sha256": digest(p), "commit": BASE} for p in SOURCES],
        "exact_symbolic_checks": checks,
        "symbolic_check_scope": "Exact identities under explicit regular/scalar restrictions; no physical validation or full coupled solution",
        "claim_ledger": [
            {"id": "core_harmonic_language", "class": "DEFINITION_POSTULATE", "status": "AUTHOR_SUPPLIED",
             "consequence": "No primitive ordinary spacetime or hertz-valued core spectrum"},
            {"id": "baton_and_boundary_dominance", "class": "DEFINITION_POSTULATE", "status": "AUTHOR_SUPPLIED",
             "consequence": "Inherited configuration; formation, maintenance and terminal transition are separate"},
            {"id": "regimes_and_daughters", "class": "DEFINITION_POSTULATE", "status": "AUTHOR_SUPPLIED",
             "consequence": "Envelopes produce daughters; exceptional terminal core route may have zero spacetime daughters"},
            {"id": "core_event_algebra", "class": "EXACT_MODEL_RESULT", "status": "COMPOSITION_DERIVED_POSITIVE_COMPLETION_NOT_SELECTED"},
            {"id": "regular_incidence_and_Haar", "class": "EXACT_MODEL_RESULT", "status": "REGULAR_MATCHER_AND_POSITIVE_CAPACITY_OBSTRUCTION_DERIVED"},
            {"id": "regular_material_matching", "class": "EXACT_MODEL_RESULT", "status": "TRANSMITTING_SAME_SPACETIME_LAW_DERIVED_NOT_CORE_TRANSFER"},
            {"id": "regular_covariant_mechanics", "class": "CONDITIONAL_DEDUCTION", "status": "OWNER_SELECTED_ACTION_VARIATION_DERIVED_FULL_IVP_REQUIRED"},
            {"id": "weighted_median_shape_response", "class": "CONDITIONAL_DEDUCTION", "status": "EXACT_FIXED_DOMAIN_VARIATION_MINUS_TWO_THIRDS"},
            {"id": "scalar_front_restriction", "class": "EXACT_MODEL_RESULT", "status": "PRINCIPAL_SYMBOL_STEEPENING_NO_STATIONARY_JUMP_NULL_ENERGY_SCOPED"},
            {"id": "hard_channels", "class": "CONDITIONAL_DEDUCTION", "status": "BILATERAL_PROJECTED_RESPONSE_VANISHING_REQUIRED_NOT_EVALUATED"},
            {"id": "terminal_charge_accounting", "class": "CONDITIONAL_DEDUCTION", "status": "REGULAR_SIDE_DEFICIT_DEFINED_CORE_IMAGE_REQUIRES_CORRESPONDENCE"},
            {"id": "black_hole_quiet_neutron_star_quantum", "class": "DEFINITION_POSTULATE", "status": "PROPOSED_APPLICATION_NOT_DERIVED_TRANSITION"},
            {"id": "double_slit_three_quarks", "class": "ILLUSTRATION", "status": "NOT_INTERFERENCE_CUTOFF_OR_COMPLETE_SPACETIME_ISOLATION_PROOF"},
            {"id": "interference_examples", "class": "OBSERVATIONAL_CLAIM", "status": "PRIMARY_LITERATURE_CONSTRAINT_NOT_BHSM_CONFIRMATION"},
            {"id": "galaxy_extension", "class": "DEFINITION_POSTULATE", "status": "POPULATION_HISTORY_BALANCE_PRESSURE_SUPPORTED_AND_LENSING_TESTS_REQUIRED"},
        ],
        "unrecovered_historical_deliverables": {"count_named_in_handoff": 2,
            "filenames": [None, None], "status": "FILENAMES_BLANK_ORIGINALS_NOT_IDENTIFIED",
            "recovery_scope": "Targeted repository text and Downloads filenames; recent Galaxy dark matter explanation conversation; no drive-wide inventory or duplicate archive scan",
            "preserved_scope": "Handoff's sextic persistence and conditional radial-law statements remain conditional, without invented coefficients or claimed recovered editable source"},
        "terminal_requirement": "Selected core representation/event domain and trace correspondence with variational transfer, charge projections, post-contact topology/gauge/phase and receiving/reconstruction data",
        "no_new_coefficients_or_rates": True, "numerical_prediction_changed": False,
        "core_metric_assigned": False, "terminal_core_transfer_derived": False,
        "hard_boundary_derived": False, "FULL_BHSM_COMPLETE": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Materialize the deterministic ledger")
    args = parser.parse_args()
    result = payload()
    encoded = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.write:
        (ROOT / OUTPUT).write_text(encoded, encoding="utf-8", newline="\n")
    elif (ROOT / OUTPUT).read_text(encoding="utf-8") != encoded:
        raise ValueError("The committed claim/source ledger differs; regenerate it from reviewed sources")
    print(json.dumps({"passed": True, "checks": result["exact_symbolic_checks"],
                      "artifact": OUTPUT, "written": args.write}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
