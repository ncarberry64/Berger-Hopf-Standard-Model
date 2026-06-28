"""Verify the exact incidence identities while retaining their assumptions."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

from .common import Common16IncidenceAudit, repository_root


def audit_common_16_incidence(
    repository: str | Path | None = None,
) -> Common16IncidenceAudit:
    root = repository_root(repository)
    kernel = json.loads(
        (root / "data/charged_suppression_operator_kernel_v1.json").read_text(encoding="utf-8")
    )
    selector = json.loads(
        (root / "data/charged_stiffness_action_selector_v1.json").read_text(encoding="utf-8")
    )
    omega = kernel["incidence_ranks"]
    rho_three = next(row for row in selector["selector_candidates"] if row["rho_ch"] == "3")
    rho_ch = int(rho_three["rho_ch"])
    weights = {sector: value // rho_ch for sector, value in omega.items()}
    weight_sum = sum(weights.values())
    projectors = {sector: Fraction(weight, weight_sum) for sector, weight in weights.items()}
    n_16 = weights["down"] ** 2
    exact = (
        weights == {"lepton": 1, "up": 2, "down": 4}
        and weight_sum == 7
        and projectors == {
            "lepton": Fraction(1, 7),
            "up": Fraction(2, 7),
            "down": Fraction(4, 7),
        }
        and n_16 == 16
    )
    return Common16IncidenceAudit(
        status="CONDITIONAL_COMMON_16_GENERATOR_CANDIDATE",
        omega_values=omega,
        rho_ch=rho_ch,
        sector_weights=weights,
        charged_weight_sum=weight_sum,
        projector_fractions=projectors,
        n_16=n_16,
        epsilon_ckm_candidate=Fraction(1, n_16),
        identities_exact=exact,
        omega_source_status="STRUCTURALLY_INTEGRATED_NOT_ACTION_DERIVED",
        rho_ch_source_status=(
            "OPEN_MISSING_RHO_CH_ACTION_DERIVATION"
            if not rho_three["selected"]
            else "CONDITIONAL_RHO_CH_ACTION_PROVENANCE_CANDIDATE"
        ),
        assumptions=(
            "Omega_l=3, Omega_u=6, and Omega_d=12 are admitted as structural boundary ranks",
            "rho_ch=3 is admitted as the cyclic-weight candidate",
        ),
        claim_boundary=(
            "The fraction identities are exact under the stated structural premises. They do not derive "
            "Omega_f or select rho_ch=3 from the charged action."
        ),
    )
