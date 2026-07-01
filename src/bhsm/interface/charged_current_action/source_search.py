"""Search local sources for normalized charged-current action evidence."""

from __future__ import annotations

import json

from .common import STATUS_OPEN_ACTION, input_guard, repository_root


SEARCH_PATHS = (
    "artifacts",
    "docs",
    "src",
    "bhsm",
    "tests",
    "manuscript",
    "reports",
    "README.md",
    "STATUS.md",
    "CLAIMS.md",
    "ROADMAP.md",
    "CLI_REFERENCE.md",
)

SEARCH_TERMS = (
    "charged current",
    "charged-current",
    "normalized action",
    "boundary action",
    "action term",
    "finite action",
    "fermion action",
    "Dirac action",
    "Hermitian",
    "hermitian",
    "adjoint",
    "conjugate",
    "h.c.",
    "h.c",
    "Hermitian conjugate",
    "real action",
    "self-adjoint",
    "off-diagonal",
    "weak doublet",
    "left-handed",
    "W+",
    "W-",
    "J_ud",
    "J_du",
    "up down",
    "down up",
    "Hom(V_u,V_d)",
    "Hom(V_d,V_u)",
    "V_u",
    "V_d",
    "transport space",
    "operator domain",
    "operator codomain",
    "sector projector",
    "Pi_u",
    "Pi_d",
    "charged incidence",
    "primitive incidence",
    "s_u",
    "s_d",
    "Omega_u",
    "Omega_d",
    "rho_ch",
    "CKM",
    "mixing",
    "bilinear",
    "response",
    "connection",
    "anti-Hermitian connection",
    "covariant derivative",
    "finite algebra",
    "charged Hessian",
    "bridge",
)

TEXT_SUFFIXES = {
    "",
    ".c",
    ".cc",
    ".cmake",
    ".cpp",
    ".csv",
    ".h",
    ".hpp",
    ".ini",
    ".json",
    ".md",
    ".py",
    ".rst",
    ".tex",
    ".toml",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}


def _candidate_files() -> list[object]:
    root = repository_root()
    files = []
    for relative in SEARCH_PATHS:
        path = root / relative
        if not path.exists():
            continue
        if path.is_file():
            files.append(path)
            continue
        for item in path.rglob("*"):
            if item.is_file() and item.suffix.lower() in TEXT_SUFFIXES:
                files.append(item)
    return sorted(set(files))


def _scan_file(path) -> list[dict[str, object]]:
    root = repository_root()
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return []
    lowered_terms = [(term, term.lower()) for term in SEARCH_TERMS]
    hits = []
    for number, line in enumerate(lines, start=1):
        lower = line.lower()
        for term, lowered in lowered_terms:
            if lowered in lower:
                hits.append(
                    {
                        "path": path.relative_to(root).as_posix(),
                        "line": number,
                        "term": term,
                        "excerpt": line.strip()[:220],
                    }
                )
                break
    return hits


def _load_json(relative: str) -> dict[str, object]:
    return json.loads((repository_root() / relative).read_text(encoding="utf-8"))


def candidate_action_terms() -> list[dict[str, object]]:
    chiral = _load_json("artifacts/BHSM_chiral_current_attachment_map_v0_6.json")
    minimal = _load_json("artifacts/BHSM_minimal_bounded_lagrangian_subset_v1_2.json")
    vertex = _load_json("artifacts/BHSM_production_vertex_table_candidate_v0_9.json")
    chiral_ckm = next(row for row in chiral["entries"] if row["current_family_id"] == "q_charged_current_CKM_BH")
    minimal_ckm = next(row for row in minimal["terms"] if row["term_id"] == "L_CKM_charged_current_bounded")
    vertex_ckm = next(row for row in vertex["entries"] if row["vertex_id"] == "q_charged_current_CKM_BH")
    return [
        {
            "term_id": "q_charged_current_CKM_BH",
            "symbolic_expression": chiral_ckm["target_expression"],
            "source": "artifacts/BHSM_chiral_current_attachment_map_v0_6.json",
            "status": "STANDARD_HEP_TARGET_CONVENTION",
            "limitation": "charged-current Lorentz structure is a target convention, not a normalized BHSM action derivation",
        },
        {
            "term_id": "L_CKM_charged_current_bounded",
            "symbolic_expression": minimal_ckm["symbolic_expression"],
            "source": "artifacts/BHSM_minimal_bounded_lagrangian_subset_v1_2.json",
            "status": "BOUNDED_COLLIDER_INTERFACE_TARGET",
            "limitation": "included in a minimal bounded collider-interface subset; explicitly not the complete BHSM 4D Lagrangian",
        },
        {
            "term_id": "L_CC_q_candidate",
            "symbolic_expression": vertex_ckm["candidate_expression"],
            "source": "artifacts/BHSM_production_vertex_table_candidate_v0_9.json",
            "status": "STRUCTURAL_CANDIDATE_WITH_DERIVED_MIXING_MATRIX",
            "limitation": "production vertex candidate has open coupling, mass-width, and renormalization dependencies",
        },
    ]


def search_charged_current_action_sources(max_hits: int = 180) -> dict[str, object]:
    files = _candidate_files()
    hits: list[dict[str, object]] = []
    for path in files:
        hits.extend(_scan_file(path))
    evidence_against = {
        "one_way_up_down": ["located candidate terms include + h.c.; no normalized action proves a one-way-only map"],
        "bidirectional_adjoint_pair": ["located + h.c. evidence is target/interface level; no normalized action ties both terms as the selected transport space"],
        "sector_self_response_sum": ["sector self-response appears in incidence/accounting contexts, not as the located charged-current action term"],
        "total_charged_endomorphism": ["no located normalized action acts on the full charged endomorphism algebra"],
        "maximal_self_response": ["same dimension 16 appears, but no action evidence identifies End(V_d) as the charged-current source"],
    }
    return {
        "audit": "charged_current_action_source_search",
        "files_scanned": len(files),
        "hits": hits[:max_hits],
        "total_hits": len(hits),
        "candidate_action_terms": candidate_action_terms(),
        "candidate_transport_spaces": [
            "Hom(V_u,V_d)",
            "Hom(V_u,V_d) direct_sum Hom(V_d,V_u)",
            "End(V_l) direct_sum End(V_u) direct_sum End(V_d)",
            "End(V_ch)",
            "End(V_d)",
        ],
        "evidence_for_one_way": ["CKM target has an up/down bilinear factor ubar_i ... d_j before adding h.c."],
        "evidence_for_adjoint_pair": ["CKM charged-current target and bounded term explicitly include + h.c."],
        "evidence_for_sector_self_response": ["primitive charged incidence audits track sector dimensions 1, 2, and 4"],
        "evidence_for_total_endomorphism": ["v2.2/v2.5 audits record End(V_ch) as a competing algebraic assignment"],
        "evidence_for_maximal_self_response": ["v2.2/v2.5 audits record End(V_d) with the same numerical dimension 16"],
        "evidence_against_each_candidate": evidence_against,
        "missing_sources": [
            "normalized charged-current BHSM action term with declared operator domain and codomain",
            "action normalization source that selects one-way, adjoint-pair, sector-self, total-endomorphism, or maximal-self transport",
            "proof that CKM is the transport/mixing law on the action-selected charged-current space",
        ],
        "status": STATUS_OPEN_ACTION,
        "claim_boundary": "Located charged-current terms are target/interface candidates; they do not yet constitute a normalized BHSM charged-current action term selecting transport space.",
        **input_guard(),
    }

