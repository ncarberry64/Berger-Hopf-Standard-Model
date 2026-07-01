"""Repository source search for normalized-action adjoint-pair provenance."""

from __future__ import annotations

from .common import input_guard, repository_root


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
    "normalized action",
    "boundary action",
    "charged current",
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
    "charged-current",
    "W+",
    "W-",
    "weak doublet",
    "left-handed",
    "up down",
    "down up",
    "Hom(V_u,V_d)",
    "Hom(V_d,V_u)",
    "V_u",
    "V_d",
    "CKM",
    "mixing",
    "transport",
    "bilinear",
    "response",
    "unitary",
    "anti-Hermitian connection",
    "covariant derivative",
    "sector projector",
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
    hits = []
    lowered_terms = [(term, term.lower()) for term in SEARCH_TERMS]
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


def search_normalized_action_adjoint_pair_sources(max_hits: int = 160) -> dict[str, object]:
    files = _candidate_files()
    hits: list[dict[str, object]] = []
    for path in files:
        hits.extend(_scan_file(path))
    evidence_for_adjoint_pair = [
        "artifacts/BHSM_chiral_current_attachment_map_v0_6.json records a CKM charged-current target with + h.c.",
        "artifacts/BHSM_ckm_bidirectional_channel_count_v2_3.json records Hom(V_u,V_d) plus Hom(V_d,V_u) as a 16-dimensional candidate.",
        "artifacts/BHSM_ckm_adjoint_pair_selection_v2_3.json records the target-level adjoint-pair candidate while leaving action selection open.",
    ]
    evidence_for_normalized_action_rule = [
        "normalized-action and boundary-action sources exist elsewhere in the repository",
        "Hermitian/real-action language is present in the source corpus",
    ]
    evidence_against_action_derivation = [
        "the located CKM charged-current target is labeled STANDARD_HEP_TARGET_CONVENTION in the chiral-current attachment artifact",
        "the v2.3 adjoint-pair audit explicitly records no complete BHSM action selecting the adjoint-pair subspace",
        "no located normalized-action artifact proves CKM transport space equals Hom(V_u,V_d) direct_sum Hom(V_d,V_u)",
    ]
    return {
        "audit": "normalized_action_adjoint_pair_source_search",
        "files_scanned": len(files),
        "hits": hits[:max_hits],
        "total_hits": len(hits),
        "evidence_for_adjoint_pair": evidence_for_adjoint_pair,
        "evidence_for_normalized_action_rule": evidence_for_normalized_action_rule,
        "evidence_against_action_derivation": evidence_against_action_derivation,
        "missing_sources": [
            "normalized charged-current action term identifying the CKM transport operator",
            "action-derived proof that off-diagonal up/down charged-current transport closes as Hom(V_u,V_d) plus Hom(V_d,V_u)",
            "artifact-backed theorem excluding one-way 8, maximal self-response 16, sector self-response 21, and total charged endomorphism 49 as CKM transport spaces",
        ],
        "status": "OPEN_MISSING_NORMALIZED_ACTION_ADJOINT_PAIR_SELECTION",
        "claim_boundary": "Source hits locate relevant language and target-level Hermitian evidence, but do not prove normalized-action CKM transport-space selection.",
        **input_guard(),
    }

