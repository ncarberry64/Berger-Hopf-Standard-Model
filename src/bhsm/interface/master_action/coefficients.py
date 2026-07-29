"""Exhaustive coefficient and input classification."""

from __future__ import annotations

from .common import COEFFICIENT_TYPES, envelope


def _row(
    coefficient_id: str,
    symbol: str,
    sector: str,
    classification: str,
    action_level: str,
    rationale: str,
    *,
    value: str | None = None,
    comparison_input: bool = False,
) -> dict:
    assert classification in COEFFICIENT_TYPES
    return {
        "coefficient_id": coefficient_id,
        "symbol": symbol,
        "sector": sector,
        "classification": classification,
        "action_level": action_level,
        "value": value,
        "comparison_input": comparison_input,
        "fitted": False,
        "rationale": rationale,
    }


def rows() -> list[dict]:
    return [
        _row("bulk_cosmological", "kappa0", "M8 gravity", "INDEPENDENT_THEORY_INPUT", "S8", "Frozen provisional P1 primitive."),
        _row("bulk_einstein", "kappa1", "M8/M5 gravity", "INDEPENDENT_THEORY_INPUT", "S8,S5", "Common positive gravitational normalization input."),
        _row("carrier_kinetic", "Zchi", "M8 carrier", "INDEPENDENT_THEORY_INPUT", "S8", "Frozen primitive."),
        _row("scalar_kinetic", "Zsigma", "scalar", "INDEPENDENT_THEORY_INPUT", "S8", "Frozen primitive; field normalization leaves invariants."),
        _row("scalar_mass", "A0", "scalar", "INDEPENDENT_THEORY_INPUT", "S8", "Parameterized relevant scalar coefficient."),
        _row("scalar_quartic", "G0", "scalar", "INDEPENDENT_THEORY_INPUT", "S8", "Parameterized primitive; no sign or value selected."),
        _row("carrier_scalar", "g", "M8 carrier-scalar", "INDEPENDENT_THEORY_INPUT", "S8", "Frozen provisional interaction."),
        _row("lambda5", "kappa1 G5/Z5^2", "reduced scalar", "INDEPENDENT_THEORY_INPUT", "S5_reduced", "Field-redefinition invariant scalar input."),
        _row("GHY_coefficient", "kappa1", "cap gravity", "ACTION_DERIVED", "S5", "Fixed by Einstein-Hilbert Dirichlet variation."),
        _row("matcher_normalization", "1", "junction", "REMOVED_AS_REDUNDANT", "S5|B1", "Absorbed into the Lagrange multiplier."),
        _row("B1_einstein", "C_partial", "intrinsic boundary gravity", "INDEPENDENT_THEORY_INPUT", "S4_boundary", "Provisional B1 Wilson coefficient."),
        _row("B1_gauge", "tau_A", "boundary gauge", "INDEPENDENT_THEORY_INPUT", "S4_boundary", "Not pushed forward from M8/M5."),
        _row("gauge_trace_rep", "K1,K2,K3=10/3,2,2", "gauge", "REPRESENTATION_DERIVED", "S4_effective", "Exact traces of retained chiral representation."),
        _row("gauge_screen_weights", "w1,w2,w3=1,2,7", "gauge screen", "REJECTED_AS_INCOMPATIBLE", "SCREEN_ONLY", "Active-generator counts are not representation trace coefficients."),
        _row("gauge_couplings", "g1,g2,g3", "gauge", "INDEPENDENT_THEORY_INPUT", "S4_effective", "Finite EFT inputs; not predicted by the current action."),
        _row("fermion_kinetic", "zeta_psi", "fermion", "REMOVED_AS_REDUNDANT", "S4_effective", "Set to one by a common nonzero field rescaling."),
        _row("hypercharge_norm", "Y_H=1/2", "representation", "INDEPENDENT_THEORY_INPUT", "S4_effective", "Conventional normalization input."),
        _row("Yukawa_matrices", "Y_u,Y_d,Y_e", "fermion/scalar", "INDEPENDENT_THEORY_INPUT", "S4_effective", "Finite matrices; frozen overlap screens do not derive them."),
        _row("CKM_matrix", "V=U_u^dagger U_d", "charged current", "ACTION_DERIVED", "S4_effective", "Derived from independent Yukawa matrices after diagonalization."),
        _row("ckm_screen_law", "sqrt(d/s),2s/b,sqrt(u/t)", "screen", "REJECTED_AS_INCOMPATIBLE", "SCREEN_ONLY", "Retained only as a frozen internal-rule screen, not an action consequence."),
        _row("charged_extra_coupling", "g_ch", "charged current", "REMOVED_AS_REDUNDANT", "S4_effective", "Would double count the SU2 covariant derivative."),
        _row("charged_stiffness", "rho_ch", "charged screen", "REJECTED_AS_INCOMPATIBLE", "SCREEN_ONLY", "No action selection; not required once current is in D_mu."),
        _row("charged_lepton_eta", "eta_l", "charged screen", "REJECTED_AS_INCOMPATIBLE", "SCREEN_ONLY", "No normalized action source."),
        _row("neutral_aux_kinetic", "Z_neu", "neutral response", "INDEPENDENT_THEORY_INPUT", "DeltaS4", "Finite effective response coefficient."),
        _row("neutral_aux_mass", "A_neu", "neutral response", "INDEPENDENT_THEORY_INPUT", "DeltaS4", "Finite effective response coefficient; no physical mass without scale."),
        _row("neutral_coupling", "g_neu", "neutral response", "INDEPENDENT_THEORY_INPUT", "DeltaS4", "Finite effective coupling."),
        _row("pmns_screen_rule", "alpha effective rule", "screen", "REJECTED_AS_INCOMPATIBLE", "SCREEN_ONLY", "Effective-extension screen, not action-derived."),
        _row("triality_projectors", "P0,P1,P2", "generations", "REPRESENTATION_DERIVED", "S4_effective", "Exact Spin8 triality projectors conditional on carrier choice."),
        _row("sector_projectors", "P_f", "sectors", "INDEPENDENT_THEORY_INPUT", "S4_effective", "Finite Hermitian intertwiners fixed before comparison."),
        _row("mode_ledger", "Pi_f,n", "generations", "INDEPENDENT_THEORY_INPUT", "SCREEN/EFT", "Finite spectral projector ledger; not predicted."),
        _row("omega_target_rules", "Omega_f target rule", "mode selection", "REMOVED_AS_REDUNDANT", "SCREEN_ONLY", "Implementation route superseded by explicit projector ledger."),
        _row("S_overlap", "1/(4 pi)", "flavor screen", "INDEPENDENT_THEORY_INPUT", "SCREEN_ONLY", "Declared no-fit screen input."),
        _row("geometry_a", "a", "Berger geometry", "INDEPENDENT_THEORY_INPUT", "INTERNAL_GEOMETRY", "Positive dimensionless shape input, not a prediction."),
        _row("alpha_low_energy", "alpha_inv_low_energy", "comparison/screen", "REJECTED_AS_INCOMPATIBLE", "ACTION_EXCLUDED", "Measured alpha cannot source parent geometry; comparison only.", comparison_input=True),
        _row("Planck_energy", "E_P", "scale screen", "REJECTED_AS_INCOMPATIBLE", "ACTION_EXCLUDED", "Measured dimensionful constant is not an exercised universal calibration.", comparison_input=True),
        _row("universal_scale", "ell_*", "physical units", "UNLICENSED_ORIGIN_BLOCKER", "CROSS_LEVEL", "No action-derived scale or declared universal calibration exists."),
        _row("reduction_pushforward", "R_*", "cross-level reduction", "UNLICENSED_ORIGIN_BLOCKER", "S8->S5->S4", "Missing covariant reduction functor fixes no coefficient pushforward."),
    ]


def payload() -> dict:
    data = rows()
    return envelope(
        "BHSM_master_coefficient_input_ledger_v7_0",
        allowed_types=sorted(COEFFICIENT_TYPES),
        coefficients=data,
        every_coefficient_typed=all(r["classification"] in COEFFICIENT_TYPES for r in data),
        comparison_inputs_in_action=[],
        finite_independent_input_count=sum(r["classification"] == "INDEPENDENT_THEORY_INPUT" for r in data),
        unlicensed_inputs=[r["coefficient_id"] for r in data if r["classification"] == "UNLICENSED_ORIGIN_BLOCKER"],
    )
