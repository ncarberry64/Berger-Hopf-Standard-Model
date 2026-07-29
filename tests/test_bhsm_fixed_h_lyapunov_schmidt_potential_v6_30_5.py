from __future__ import annotations

import hashlib
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bhsm.interface import fixed_h_lyapunov_schmidt_potential as ls


def test_source_main_and_all_parent_shas_are_pinned():
    assert ls.SOURCE_MAIN_SHA.startswith("7c8b8b7")
    assert set(ls.PARENT_SCIENTIFIC_SHAS) == {
        "v6.30.2",
        "v6.30.3",
        "v6.30.4",
        "v6.30.4_serialization_fix",
    }


def test_exact_KKT_projector_and_normalization():
    ledger = ls.projector_ledger()
    assert ledger["normalization_N"] == 1
    assert "4 sin(rho)^4" in ledger["pairing"]
    assert all(ls.projector_identities().values())
    assert ledger["domain_preservation"]["matcher_reaction"] is True


def test_amplitude_phase_condition_fixes_all_higher_kernel_parts():
    ledger = ls.amplitude_ledger()
    assert "P Phi_n=0" in ledger["higher_orders"]
    assert ledger["action_multiplier_added"] is False
    assert ledger["reflection"] == "q->-q at fixed tau"


def test_phi2_is_reproduced_without_D2_import():
    assert "tan(rho)**2" in str(ls.v6304.second_order_lapse_response())
    assert ls.v6304.fredholm_projection_exact() == 0
    assert ls.GUARDS["historical_D2_coefficient_imported"] is False


def test_complete_third_order_source_has_all_surviving_terms():
    ledger = ls.third_order_source_ledger()
    assert ledger["components"]["scalar"] == "S3_sigma=-6 r3"
    origins = " ".join(row["origin"] for row in ledger["term_ledger"])
    assert "G5 sigma^4" in origins
    assert "quadratic potential" in origins
    assert "kinetic" in origins
    assert "GHY+B1+matcher" in origins


def test_third_order_noether_and_matcher_compatibility():
    ledger = ls.noether_ledger()
    assert "a' E_a" in ledger["off_shell_identity"]
    assert "E_a=-(sigma'/a')" in ledger[
        "nonlinear_cokernel_representative"
    ]
    assert ledger["matcher_trace_compatible"] is True
    assert ledger["endpoint_reaction_compatible"] is True


def test_projection_coefficients_and_exact_branch_condition():
    projection = ls.projection_formula()
    assert abs(ls.M4 - 21.690130229412136) < 1.0e-12
    assert abs(ls.C_GRAV - 394.70598844295543) < 1.0e-11
    assert abs(ls.G3_GAMMA - 6 * ls.M4) < 1.0e-12
    assert abs(ls.G3_ZETA - 6 * ls.C_GRAV) < 1.0e-11
    assert "=-Omega3" in projection["g3"]
    assert "G5/Z5=-18.197" in projection["exact_zero_condition"]


def test_two_independent_projection_and_phi3_methods():
    diagnostics = ls.numerical_diagnostics()
    assert len(diagnostics["methods"]) == 2
    assert abs(diagnostics["projection"]["M4"] - ls.M4) < 2.0e-12
    assert abs(
        diagnostics["projection"]["C_grav"] - ls.C_GRAV
    ) < 1.0e-10
    assert diagnostics["Phi3"]["regular_pole"] is True
    assert diagnostics["Phi3"]["Dirichlet_endpoint"] is True
    assert diagnostics["Phi3"]["KKT_orthogonal"] is True


def test_cross_platform_serialization_uses_certified_bounds():
    agreement = ls.numerical_diagnostics()["agreement"]
    assert "certified" in agreement["serialization_policy"]
    for key, row in agreement.items():
        if key == "serialization_policy":
            continue
        assert row["relation"] == "<"
        assert isinstance(row["certified_upper_bound"], float)


def test_fourth_order_source_parity_constraint_and_reaction():
    source = ls.fourth_order_ledger()
    assert source["Omega4"] == 0
    assert source["Noether_compatible"] is True
    assert "A4" in source["expansion"]
    assert "eta4=" in source["S4_components"]["matcher_reaction"]
    phi4 = ls.phi4_ledger()
    assert phi4["P_Phi4"] == 0
    assert phi4["sigma4"] == 0
    assert phi4["matcher_recurrence"] is True


def test_reduced_action_identity_has_two_cap_sign_and_direct_crosscheck():
    ledger = ls.action_identity_ledger()
    assert ledger["J0"] == "-2 Z5"
    assert ledger["identity"] == (
        "Gamma4=J0 g3=-2 Z5 g3=2 Z5 Omega3"
    )
    assert ledger["factor_two"] == "two identical caps"
    assert ledger["direct_action_crosscheck"]["agreement"].startswith("exact")


def test_jordan_coefficients_are_same_domain_and_unsubtracted():
    ledger = ls.jordan_ledger()
    assert ledger["F1"] == 0
    assert ledger["VJ0"] == "symbolic and unsubtracted"
    assert ledger["VJ2"] == "12 F2"
    assert ledger["VJ4"] == "12 F4+2 Z5 g3"
    assert ledger["historical_D2_F1_used"] is False


def test_same_family_null_hessian_and_quartic_Einstein_coefficient():
    ledger = ls.einstein_ledger()
    assert ledger["same_family_null_hessian"]["VE2"] == 0
    assert ledger["first_nonzero"]["order"] == 4
    assert "3633.0356624841" in ledger["first_nonzero"]["simplified"]
    assert ledger["reflection"] == "VE is even and independent of tau"


def test_same_domain_kinetic_and_canonical_map_invert():
    ledger = ls.canonical_ledger()
    assert abs(ledger["same_domain_kinetic"]["k0"] - ls.K0) < 1.0e-13
    assert ledger["same_domain_kinetic"]["positive"] is True
    assert "6.935084858283065" in ledger[
        "same_domain_kinetic"
    ]["why_historical_value_rejected"]
    assert "phi/sqrt(k0)" in ledger["canonical_map"]["q_of_phi"]
    assert ledger["first_interaction"]["order"] == 4


def test_first_canonical_interaction_threshold_and_local_stability():
    assert abs(
        ls.CANONICAL_G_OVER_Z2
        - ls.VE4_GAMMA_Z / ls.K0**2
    ) < 1.0e-12
    assert abs(
        ls.CANONICAL_INV_KAPPA
        - ls.VE4_Z2_OVER_KAPPA / ls.K0**2
    ) < 1.0e-12
    stability = ls.stability_ledger()
    assert stability["quadratic"] == stability["cubic"] == 0
    assert stability["classification"]["stable_wall_G5_positive"] == (
        "strict local quartic minimum"
    )
    assert stability["global_stability"] is False


def test_exact_branch_and_reduced_family_verdicts_are_separate():
    ledger = ls.exact_permission_ledger()
    assert ledger["stable_wall_sign_domain"]["exact_branch_continues"] is False
    assert ledger["reduced_effective_family"] == (
        "constructed through fourth order"
    )
    assert ledger["continuous_family_of_exact_vacua_claimed"] is False


def test_scale_phase_is_explicitly_not_permitted():
    ledger = ls.scale_permission_ledger()
    assert ledger["v6_31_permitted"] is False
    assert ledger["result"] == ls.SCALE_RESULT
    assert ledger["unselected_frozen_coefficient"] == "G5"


def test_no_forbidden_method_or_claim_guard_is_enabled():
    for key, value in ls.GUARDS.items():
        assert value is False, key


def test_exactly_fifteen_deterministic_artifacts():
    assert len(ls.ARTIFACT_FILES) == 15
    assert set(ls.artifact_payloads()) == set(ls.ARTIFACT_FILES)
    first = ls.artifact_bytes()
    second = ls.artifact_bytes()
    assert first == second
    assert {
        name: hashlib.sha256(content).hexdigest()
        for name, content in first.items()
    } == {
        name: hashlib.sha256(content).hexdigest()
        for name, content in second.items()
    }


def test_checked_in_artifacts_are_current():
    for name, content in ls.artifact_bytes().items():
        assert (ROOT / "artifacts" / name).read_bytes() == content


def test_materializer_is_idempotent():
    script = (
        ROOT
        / "scripts"
        / "materialize_fixed_h_lyapunov_schmidt_potential_v6_30_5.py"
    )
    subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True)
    first = {
        name: (ROOT / "artifacts" / name).read_bytes()
        for name in ls.ARTIFACT_FILES.values()
    }
    subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True)
    second = {
        name: (ROOT / "artifacts" / name).read_bytes()
        for name in ls.ARTIFACT_FILES.values()
    }
    assert first == second == ls.artifact_bytes()
