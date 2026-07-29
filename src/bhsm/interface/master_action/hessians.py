"""Quadratic operator and domain map."""

from __future__ import annotations

from .common import envelope


def rows() -> list[dict]:
    return [
        {"block": "M8_gravity_scalar", "operator": "gauge-fixed Lovelock/P1 metric-scalar Hessian", "domain": "H2 metric intersect gauge slice; H1 scalars", "adjoint_domain": "same after endpoint conditions", "kernel": "diffeomorphism zero modes plus background moduli", "positivity": "not established", "status": "PROVISIONAL"},
        {"block": "D0_fixed_h", "operator": "radial Sturm-Liouville plus finite-rank matcher KKT block", "domain": "regular pole, fixed h, scalar Dirichlet trace, matcher reaction", "adjoint_domain": "explicit v6.30.2 KKT domain", "kernel": "one scalar Jacobi mode before amplitude quotient", "positivity": "conditional quartic inequality", "status": "RECOVERED_EXACTLY"},
        {"block": "gauge", "operator": "d_A^dagger d_A plus curvature on coexact adjoint one-forms", "domain": "H2 coexact gauge slice with declared boundary condition", "adjoint_domain": "same for absolute/relative elliptic choice", "kernel": "flat/stabilizer connections", "positivity": "nonnegative principal block", "status": "EFT_LEVEL_ONLY"},
        {"block": "fermion", "operator": "i slashD_A plus Yukawa background", "domain": "H1 maximal-isotropic/self-adjoint Dirac domain", "adjoint_domain": "equals domain by input choice", "kernel": "chiral zero modes representation dependent", "positivity": "indefinite first-order Hermitian", "status": "DOMAIN_FAMILY_NOT_PARENT_SELECTED"},
        {"block": "charged", "operator": "SU2 gauge-fermion Hessian and Yukawa flavor off-diagonal blocks", "domain": "gauge x Dirac domains", "adjoint_domain": "Hermitian adjoint pair", "kernel": "gauge zero modes", "positivity": "indefinite saddle", "status": "EFT_DERIVED"},
        {"block": "neutral_response", "operator": "-Z_neu D2-A_neu on declared cone", "domain": "H2 intersect response cone", "adjoint_domain": "boundary-condition dependent", "kernel": "coefficient dependent", "positivity": "conditional on Z_neu and cone inequality", "status": "EFFECTIVE_CONDITIONAL"},
        {"block": "cross_level", "operator": None, "domain": None, "adjoint_domain": None, "kernel": None, "positivity": None, "status": "MISSING_REDUCTION_INTERTWINER"},
    ]


def payload() -> dict:
    return envelope(
        "BHSM_master_hessian_operator_map_v7_0",
        Hessian_blocks=rows(),
        fixed_h_D0_recovered=True,
        full_master_Hessian_exists=False,
        closed_range_cross_level_unproved=True,
        obstruction="No R_* intertwines levelwise Hessians or their domains.",
    )
