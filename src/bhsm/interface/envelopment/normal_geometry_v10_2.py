"""Covariant normal geometry and action-domain audit for BHSM v10.2."""

from __future__ import annotations

from typing import Any

import numpy as np


VERSION = "v10.2"
GEOMETRY_VERDICT = "BHSM_PHYSICAL_NORMAL_DISPLACEMENT_ABSENT_FROM_CURRENT_ACTION_DOMAIN"


def induced_geometry(metric: np.ndarray, normal: np.ndarray) -> dict[str, np.ndarray | float]:
    """Return the normalized hypersurface projectors for a non-null normal."""

    g = np.asarray(metric, dtype=float)
    n = np.asarray(normal, dtype=float)
    if g.ndim != 2 or g.shape[0] != g.shape[1] or n.shape != (g.shape[0],):
        raise ValueError("metric must be square and normal must match its dimension")
    n_cov = g @ n
    norm = float(n @ n_cov)
    if not np.isclose(abs(norm), 1.0, atol=1.0e-12):
        raise ValueError("normal must have unit norm")
    epsilon = 1.0 if norm > 0 else -1.0
    h_cov = g - epsilon * np.outer(n_cov, n_cov)
    h_mixed = np.eye(g.shape[0]) - epsilon * np.outer(n, n_cov)
    return {
        "normal_norm": norm,
        "epsilon": epsilon,
        "normal_covector": n_cov,
        "induced_metric": h_cov,
        "mixed_projector": h_mixed,
    }


def gaussian_collar_jacobian(radial_lapse: float, induced_metric: np.ndarray) -> float:
    """Return sqrt(|det G|)=|N_rho| sqrt(|det h|) for a block collar metric."""

    if radial_lapse == 0:
        raise ValueError("radial lapse must be nonzero")
    determinant = float(np.linalg.det(np.asarray(induced_metric, dtype=float)))
    return abs(float(radial_lapse)) * float(np.sqrt(abs(determinant)))


def domain_ledger() -> list[dict[str, Any]]:
    return [
        {
            "domain": "M8",
            "dimension": 8,
            "metric": "G_AB",
            "normal_object": "rho-normal only after a local collar/foliation is selected",
            "action_owner": "S8^env",
        },
        {
            "domain": "lifted seam",
            "dimension": 7,
            "metric": "S3_fiber x M4 pullback, locally",
            "normal_object": "I_rho",
            "action_owner": None,
        },
        {
            "domain": "M5 caps",
            "dimension": 5,
            "metric": "radial ADM (N,N^mu,h_mu_nu)",
            "normal_object": "cap normal to B1",
            "action_owner": "S5+S_GHY",
        },
        {
            "domain": "M4=B1",
            "dimension": 4,
            "metric": "independent h_mu_nu with matcher h=iota^*g",
            "normal_object": "fixed embedding iota in the frozen action",
            "action_owner": "S4,intrinsic+S_compatibility+S_current",
        },
    ]


def metric_ansatz_audit() -> dict[str, Any]:
    return {
        "candidate_local_form": (
            "ds8^2=N_rho^2 d rho^2+g_mu_nu dx^mu dx^nu+"
            "a_F^2 gamma_ab(theta^a+A^a_mu dx^mu)(theta^b+A^b_nu dx^nu)"
        ),
        "accepted_parts": {
            "radial_lapse": "M5 cap ADM only",
            "M4_metric": "intrinsic seam plus matcher",
            "Hopf_connection": "canonical Sp(1) connection in the M8 reduction",
            "Hopf_radion": "homogeneous M8 invariant metric sector",
        },
        "not_proved": [
            "one off-shell metric simultaneously realizes the independent S8, S5, and S4 action owners",
            "the M5 rho-normal is the normal to the seven-dimensional lifted seam in M8",
            "the M4 gauge connection is the Kaluza-Klein connection A^a_mu",
        ],
        "adopted_as_global_parent_metric": False,
    }


def normal_variation_ledger() -> dict[str, Any]:
    return {
        "candidate_deformation": "delta X^A=psi n^A",
        "identities": {
            "delta_h_ij": "2 psi K_ij",
            "delta_sqrt_abs_h": "psi K sqrt|h|",
            "delta_K": "-Delta_h psi-(K_ij K^ij+Ric(n,n))psi",
            "delta_K_ij": "-D_iD_j psi+psi(K_i^k K_kj-R_ninj)",
            "collar_measure": "delta(J dmu_h d rho)=J(K psi+delta log J)dmu_h d rho plus endpoint terms",
        },
        "GHY_role": "cancels normal derivatives of delta g for Dirichlet metric variation; it does not create a varied embedding",
        "prior_exact_results": [
            "v5.12 standard normal-variation identities",
            "v6.10 no independent junction density in the minimal well-posed action",
            "v6.13 zeta is not an action variable",
            "v6.15 interface threading is a presymplectic null trace",
            "v6.25 dynamical embedding domain was not reached",
        ],
        "embedding_fixed": True,
        "psi_in_configuration_space": False,
        "delta_S_delta_psi": None,
        "shape_equation_from_current_action": None,
        "coordinate_rho_shift_is_physical_displacement": False,
        "verdict": GEOMETRY_VERDICT,
    }


def geometry_payload() -> dict[str, Any]:
    example = induced_geometry(np.diag([-1.0, 1.0, 1.0]), np.array([0.0, 1.0, 0.0]))
    projector = np.asarray(example["mixed_projector"])
    validation = {
        "unit_normal": bool(np.isclose(example["normal_norm"], 1.0)),
        "projector_idempotent": bool(np.allclose(projector @ projector, projector)),
        "projector_annihilates_normal": bool(np.allclose(projector @ np.array([0.0, 1.0, 0.0]), 0.0)),
        "domain_dimensions": [row["dimension"] for row in domain_ledger()] == [8, 7, 5, 4],
        "rho_not_promoted": not normal_variation_ledger()["coordinate_rho_shift_is_physical_displacement"],
        "psi_fails_closed": normal_variation_ledger()["delta_S_delta_psi"] is None,
    }
    return {
        "artifact": "BHSM_normal_radion_geometry_v10_2",
        "version": VERSION,
        "domains": domain_ledger(),
        "metric_ansatz": metric_ansatz_audit(),
        "normal_variation": normal_variation_ledger(),
        "verdict": GEOMETRY_VERDICT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
