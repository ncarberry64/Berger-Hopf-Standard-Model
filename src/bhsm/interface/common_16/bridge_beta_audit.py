"""Compare the common-16 refactorization with the existing bridge source."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

from .common import Common16BridgeBetaAudit, repository_root
from .incidence_audit import audit_common_16_incidence


def _fraction(value: str) -> Fraction:
    return Fraction(value)


def audit_common_16_bridge_beta(
    repository: str | Path | None = None,
) -> Common16BridgeBetaAudit:
    root = repository_root(repository)
    incidence = audit_common_16_incidence(root)
    source = json.loads(
        (root / "data/incidence_normalized_overlap_bridge_source.json").read_text(encoding="utf-8")
    )
    values = json.loads(
        (root / "artifacts/charged_boundary_bridge_values_v1.json").read_text(encoding="utf-8")
    )
    common_value = Fraction(
        incidence.n_16,
        incidence.charged_weight_sum * incidence.rho_ch**3,
    )
    source_value = _fraction(source["g_ch_factorization_value"])
    beta = {sector: _fraction(row["beta"]) for sector, row in values["sectors"].items()}
    expected = {
        sector: common_value * incidence.projector_fractions[sector]
        for sector in ("lepton", "up", "down")
    }
    return Common16BridgeBetaAudit(
        status="CONDITIONAL_COMMON_16_GENERATOR_CANDIDATE",
        common_16_bridge_formula="N_16/(S_ch*rho_ch^3)",
        incidence_overlap_bridge_formula="(4/3)^2/21",
        common_16_bridge_value=common_value,
        incidence_overlap_bridge_value=source_value,
        bridge_identity_exact=common_value == source_value == Fraction(16, 189),
        beta_values=beta,
        expected_beta_values=expected,
        beta_identities_exact=beta == expected,
        bridge_source_status=source["statuses"]["charged_bridge_seed_16_over_189"],
        common_generator_artifact_backed=False,
        claim_boundary=(
            "The two bridge formulas are exactly equal after assuming rho_ch=3 and Omega/rho weights "
            "(1,2,4). The existing artifact sources 16/189 through incidence 21 and overlap 4/3; it does "
            "not prove that N_16 is their common physical generator."
        ),
    )
