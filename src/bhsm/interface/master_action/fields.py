"""Configuration-space and bundle ledgers."""

from __future__ import annotations

from .common import envelope


def _field(
    field_id: str,
    symbol: str,
    manifold: str,
    bundle: str,
    representation: str,
    reality: str,
    chirality: str,
    mass_dimension: str,
    regularity: str,
    activity: str,
    gauge_transform: str,
    diffeo_transform: str,
    variation_domain: str,
) -> dict[str, str]:
    return {
        "field_id": field_id,
        "symbol": symbol,
        "manifold": manifold,
        "bundle": bundle,
        "representation": representation,
        "reality_condition": reality,
        "chirality": chirality,
        "mass_dimension": mass_dimension,
        "boundary_regularity": regularity,
        "activity": activity,
        "gauge_transformation": gauge_transform,
        "diffeomorphism_transformation": diffeo_transform,
        "variation_domain": variation_domain,
    }


def field_rows() -> list[dict[str, str]]:
    return [
        _field("bulk_metric", "G_AB", "M8=R_t x S7", "Sym2(T*M8)", "gauge singlet", "real Lorentz metric", "n/a", "0", "H2_loc; fixed endpoint trace", "ACTIVE_IN_S8", "invariant", "pullback tensor", "compact temporal support or Dirichlet endpoint metric"),
        _field("bulk_carrier", "chi", "M8", "trivial real line", "singlet", "real", "n/a", "3", "H1", "ACTIVE_IN_S8", "invariant", "scalar", "smooth normalizable"),
        _field("bulk_scalar", "sigma", "M8 and cap pullback", "real line", "singlet", "real; wall Z2", "n/a", "3", "H1 with cap regularity", "ACTIVE", "invariant", "scalar", "D0 uses regular pole and fixed boundary trace"),
        _field("cap_metrics", "g_+-,", "M5_+ disjoint_union M5_-", "Sym2(T*M5)", "singlet", "real Lorentz metric", "n/a", "0", "H2", "ACTIVE_IN_RELATIVE_ACTION", "invariant", "pullback tensor", "fixed-h D0 or declared larger domain"),
        _field("induced_metric", "gamma_+-,", "B1=partial M5_+=partial M5_-", "Sym2(T*B1)", "singlet", "real Lorentz metric", "n/a", "0", "H3/2 trace", "DEPENDENT_TRACE", "invariant", "pullback tensor", "determined by cap traces"),
        _field("intrinsic_metric", "h_ab", "B1", "Sym2(T*B1)", "singlet", "real Lorentz metric", "n/a", "0", "H2", "FIXED_IN_D0_ACTIVE_IN_PARENT_DOMAIN", "invariant", "pullback tensor", "fixed h in D0; independent before matcher"),
        _field("matcher", "Lambda_+-^ab", "B1", "Sym2(TB1) density", "singlet", "real", "n/a", "4", "H-1/2", "AUXILIARY_ACTIVE", "invariant", "tensor density", "unrestricted finite-energy multiplier"),
        _field("lapse_shift", "N,N^a", "M5 caps", "R plus TB1", "singlet", "real", "n/a", "0", "H1", "ACTIVE_CONSTRAINT_FIELDS", "invariant", "ADM variables", "regular lapse; tangent shift with declared endpoint support"),
        _field("gauge_connections", "A_i", "B1 or effective M4", "T*M4 tensor ad(P_i)", "SU3 x SU2 x U1 adjoint", "anti-Hermitian connection", "n/a", "1", "H1 with absolute/relative boundary choice", "ACTIVE_IN_S4", "A->uAu^-1-u du^-1", "one-form pullback", "gauge quotient; coexact slice for Hessian"),
        _field("fermion_multiplet", "Psi", "B1 or effective M4", "S_h tensor E_rep tensor C3_family", "retained SM representation ledger", "Lorentz adjoint reality", "P_L/P_R by representation", "3/2", "H1/2 with maximal-isotropic boundary pairing", "ACTIVE_IN_S4", "Psi->rho(u)Psi", "spinor pullback", "self-adjoint/maximal-isotropic Dirac domain remains input"),
        _field("triality_projectors", "P_r", "finite family fiber", "End(C3_family)", "Z3 spectral projectors", "Hermitian idempotents", "commute with chirality", "0", "finite dimensional", "FIXED_REPRESENTATION_DATA", "covariant constant", "scalar", "exact Spin8 triality algebra"),
        _field("sector_projectors", "P_f", "finite representation fiber", "End(E_rep)", "sector dependent", "Hermitian idempotents", "chirality compatible", "0", "finite dimensional", "INDEPENDENT_INPUT", "intertwiner", "scalar", "fixed orthogonal ranges"),
        _field("mode_projectors", "Pi_f,n", "Berger/collar spectral fiber", "finite-rank End(H)", "sector and generation", "orthogonal", "chirality compatible", "0", "spectral-domain preserving", "INDEPENDENT_INPUT", "gauge intertwiner", "scalar", "mode ledger fixed before comparison"),
        _field("neutral_response", "N_neu", "B1/collar", "real rank-3 response bundle", "neutral", "real", "n/a", "1", "H1 on declared cone", "ACTIVE_EFFECTIVE_FIELD", "invariant", "scalar/vector by model", "nonnegative normalized cone is conditional"),
        _field("charged_current", "W_mu^+-", "effective M4", "T*M4 tensor su2_C", "charged weak adjoint", "W^-=(W^+)dagger", "couples left chirality", "1", "H1", "DEPENDENT_GAUGE_COMPONENT", "non-Abelian connection law", "one-form", "contained in SU2 connection"),
        _field("berger_shape", "a", "internal Berger S3 datum", "R_+", "geometric modulus", "real positive", "n/a", "0", "fixed", "INDEPENDENT_THEORY_INPUT", "invariant", "scalar", "not varied without a reduction/source law"),
        _field("physical_scale", "ell_*", "global unit bridge", "R_+", "singlet", "real positive", "n/a", "-1", "n/a", "ABSENT_OPEN_TIER_B", "invariant", "scalar", "no calibration exercised"),
    ]


def configuration_space_payload() -> dict:
    return envelope(
        "BHSM_master_configuration_space_v7_0",
        configuration_space=field_rows(),
        architecture_levels=["M8_PROVISIONAL", "M5_TWO_CAP_RELATIVE", "M4_EFFECTIVE"],
        single_configuration_space_exists=False,
        reason="No sourced reduction functor identifies the fields and domains across all three levels.",
    )


def bundle_ledger_payload() -> dict:
    rows = [
        {"bundle_id": "B8_tensor", "base": "M8", "fiber": "Lorentz metrics and real scalars", "status": "PROVISIONAL_PARENT"},
        {"bundle_id": "B5_cap_tensor", "base": "M5_+ disjoint_union M5_-", "fiber": "cap metrics, lapse/shift, sigma", "status": "FROZEN_RELATIVE_PROBLEM"},
        {"bundle_id": "B4_spin_gauge", "base": "B1 or M4", "fiber": "S_h tensor E_SM tensor C3_family", "status": "CONDITIONAL_EFFECTIVE"},
        {"bundle_id": "B4_response", "base": "B1/collar", "fiber": "neutral response and scalar/topographic modes", "status": "CONDITIONAL_EFFECTIVE"},
    ]
    return envelope(
        "BHSM_master_field_bundle_ledger_v7_0",
        bundles=rows,
        cross_level_bundle_isomorphism=None,
        missing_object="COVARIANT_BULK_BOUNDARY_REDUCTION_FUNCTOR",
    )
