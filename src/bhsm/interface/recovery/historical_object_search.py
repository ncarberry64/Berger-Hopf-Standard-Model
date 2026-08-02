"""Canonical recovery question and searched-resource ledger."""

from __future__ import annotations

from typing import Any


SYNONYMS = [
    "support weight", "sector weight", "depth character", "spacetime-removal weight",
    "boundary incidence", "carrier weight", "representation charge", "measure scaling",
    "fiber incidence", "wall incidence", "support coupling", "upsilon exponent",
    "q_D coupling", "Haar character", "dimensional support factor", "primitive coframe",
    "active-generator weight", "normalized boundary measure",
]


def recovery_question(object_name: str = "support representation functor") -> dict[str, Any]:
    return {
        "canonical_current_name": object_name,
        "mathematical_type": "strong monoidal functor C_BHSM^strat -> Rep(G_D), modulo physical natural/canonical equivalence",
        "domain": "stratified S8/S5/S4/regular-core BHSM action category",
        "codomain": "continuous representations of G_D=(R_{>0}, multiplication)",
        "defining_property": "assign primitive characters and equivariant morphisms preserving the complete local action, boundary/core variation, symplectic form, and reduction",
        "required_inputs": ["primitive GD action", "supported derivative couplings", "measure characters", "boundary/core canonical domain"],
        "required_outputs": ["physical equivalence class", "canonical representative", "invariant w/lambda_D ratios"],
        "symmetries": ["diffeomorphism", "gauge", "triality", "GD monoidal naturality"],
        "normalization": "one primitive character or a proof that generator rescaling is representation gauge",
        "upstream_dependencies": ["v11.0 multiplicative support", "v7.1 reduction", "v10.4 support action class"],
        "downstream_claims_blocked": ["core transfer", "three-mode action", "cycles", "masses", "mixing", "M4", "quantum"],
        "historical_synonyms": SYNONYMS,
    }


def search_ledger() -> dict[str, Any]:
    return {
        "current_tree_searched": True,
        "git_content_history_searched": True,
        "local_and_remote_branches_searched": True,
        "tags_searched": True,
        "github_prs_searched": True,
        "github_issues_searched": True,
        "artifacts_searched": True,
        "tests_searched": True,
        "canonical_resources_searched": True,
        "author_attachments_searched": True,
        "preservation_bundles": [
            {"path": "D:/Carberry_Greatest_Works_Curated_FINAL_2026-06-26/01_BHSM/Berger-Hopf-Standard-Model_v8.3_2026-07-30.bundle", "verified": True, "main": "0721ee6a79f97cae5b3ac5bf040fa07ef9584678"},
            {"path": "D:/Carberry_Greatest_Works_Curated_FINAL_2026-06-26/01_BHSM/Berger-Hopf-Standard-Model_v10.4_2026-08-01.bundle", "verified": True, "main": "04a38d962e32613ff4486f6ef068a01d24a9e4ac"},
            {"path": "D:/Carberry_Greatest_Works_Curated_FINAL_2026-06-26/01_BHSM/BHSM_v11.0_2026-08-02_76ca770.bundle", "verified": True, "main": "76ca770729d73805e79e2e6528fc735dcdd559ec"},
        ],
        "usb_mirror_searched_read_only": True,
        "search_complete": True,
    }
