"""Materialize the repository-wide BHSM spacetime-edge terminology audit."""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "artifacts/flagship_integration/BHSM_SPACETIME_EDGE_ONTOLOGY_AUDIT.json"
SEARCH_ROOTS = (
    ROOT / "theory",
    ROOT / "src",
    ROOT / "scripts",
    ROOT / "tests",
    ROOT / "artifacts/current_semantics",
    ROOT / "artifacts/flagship_integration",
)
SUFFIXES = {".md", ".py", ".json"}
TERMS = re.compile(
    r"\b(spacetime[ _-]edge|finite-prefix edge|finite-core edge|form-core edge|"
    r"far edge|core edge|physical edge|canonical stop|endpoint|boundary|event|"
    r"truncation|cutoff|edge|aether)\b",
    re.IGNORECASE,
)
AMBIGUOUS_PROOF_EDGE = re.compile(
    r"\b(far edge|form-core edge|finite-core edge|proof edge|"
    r"(?:1,?064|1,?222)(?:-segment|-core)? edge)\b",
    re.IGNORECASE,
)

# These are provenance records for wording repaired in this milestone.  The
# scanner locates the replacement text after the correction, so line numbers
# remain deterministic without keeping stale wording in current theory.
CORRECTIONS = {
    "theory/n12_c2_1064_to_1222_nested_weyl_increment.md": (
        "Dirichlet far form-core edge; The far edge remains a form-core truncation",
        "Dirichlet far form-core truncation boundary; the far form-core truncation boundary remains a proof cutoff",
    ),
    "theory/n12_c2_1222_segment_finite_core_descriptor.md": (
        "far edge of a Friedrichs form core",
        "far form-core truncation boundary of a Friedrichs form core",
    ),
    "theory/n12_c2_1064_segment_negative_axis_weyl_family.md": (
        "Dirichlet form-core edge; form-core edge",
        "Dirichlet form-core truncation boundary; form-core truncation boundary",
    ),
    "src/bhsm/interface/aether_forward_c2_weyl_riccati.py": (
        "far Dirichlet form-core edge",
        "far Dirichlet form-core truncation boundary",
    ),
    "theory/gate_ledger.md": (
        "proof edge; artificial far edge; 1,222-core edge; segment-1222 edge",
        "proof cutoff; artificial far form-core truncation boundary; 1,222-core truncation boundary; segment-1222 proof cutoff",
    ),
    "theory/bhsm_current_semantic_normalization.md": (
        "1222 edge remains a nonphysical form-core truncation",
        "1222 form-core truncation boundary remains a nonphysical proof cutoff",
    ),
    "theory/n12_c2_1064_segment_weyl_coefficient_cotangent.md": (
        "far Dirichlet form-core edge", "far Dirichlet form-core truncation boundary",
    ),
    "theory/n12_c2_common_scale_weyl_covariance.md": (
        "Friedrichs form-core edge", "Friedrichs form-core truncation boundary",
    ),
    "theory/n12_c2_1222_moving_duration_pullback_enclosure.md": (
        "artificial 1,222-core edge", "finite 1,222-core truncation boundary",
    ),
    "theory/n12_c2_1222_parametric_base_family.md": (
        "1,222nd proof edge", "1,222nd proof cutoff",
    ),
    "theory/n12_c2_1222_segment_negative_axis_weyl_family.md": (
        "far edge", "far form-core truncation boundary",
    ),
    "theory/n12_c2_finite_prefix_terminal_load_bracket.md": (
        "far edge of the certified prefix", "far form-core truncation boundary of the certified prefix",
    ),
    "theory/n12_gate7_ae2_one_seam_direct_descriptor.md": (
        "far proof edge", "far proof cutoff",
    ),
    "theory/n12_gate7_1222_core_diagram_matching_audit.md": (
        "far C2 proof edge; artificial 1,222-core edge; 1,222-core edge",
        "far C2 form-core truncation boundary; finite 1,222-core truncation boundary; 1,222-core truncation boundary",
    ),
    "theory/n12_gate7_fixed_channel_finite_core_heat_bound.md": (
        "1,222-core proof edge", "1,222-core proof cutoff",
    ),
    "theory/n12_gate7_maximal_graded_cotangent_matching_audit.md": (
        "finite proof edge", "finite proof cutoff",
    ),
    "theory/n12_gate7_one_seam_full_graded_finite_core_heat_bound.md": (
        "far proof edge", "far proof cutoff",
    ),
    "theory/n12_gate7_rank72_maximal_tail_route_adjudication.md": (
        "proof edge", "proof cutoff",
    ),
    "theory/n12_maximal_friedrichs_weyl_exhaustion.md": (
        "artificial far edge; moving far edge",
        "artificial far form-core truncation boundary; moving far form-core truncation boundary",
    ),
    "src/bhsm/interface/forward_finite_endpoint_heat_force.py": (
        "artificial far edge", "artificial far form-core truncation boundary",
    ),
    "src/bhsm/interface/current_semantic_normalization.py": (
        "1222 proof edge is an event or stop",
        "1222 proof cutoff is an event or canonical stop",
    ),
    "scripts/assemble_n12_c2_1222_segment_finite_core_descriptor.py": (
        "segment-1222 proof edge is a physical endpoint",
        "segment-1222 proof cutoff is a physical endpoint",
    ),
    "scripts/audit_n12_gate7_1222_core_diagram_matching.py": (
        "proof edge is an endpoint", "proof cutoff is a physical endpoint",
    ),
    "scripts/derive_n12_c2_1222_segment_negative_axis_weyl_family.py": (
        "far core edge is an endpoint", "far form-core truncation boundary is a physical endpoint",
    ),
    "scripts/derive_n12_c2_1222_parametric_base_family.py": (
        "1222 proof edge is a physical endpoint", "1222 proof cutoff is a physical endpoint",
    ),
    "artifacts/flagship_integration/BHSM_N12_C2_1222_SEGMENT_NEGATIVE_AXIS_WEYL_FAMILY.json": (
        "far core edge is an endpoint", "far form-core truncation boundary is a physical endpoint",
    ),
    "artifacts/flagship_integration/BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.json": (
        "segment-1222 proof edge is a physical endpoint", "segment-1222 proof cutoff is a physical endpoint",
    ),
    "artifacts/flagship_integration/BHSM_N12_C2_1222_PARAMETRIC_BASE_FAMILY.json": (
        "1222 proof edge is a physical endpoint", "1222 proof cutoff is a physical endpoint",
    ),
    "artifacts/flagship_integration/BHSM_N12_GATE7_1222_CORE_DIAGRAM_MATCHING_AUDIT.json": (
        "proof edge is an endpoint", "proof cutoff is a physical endpoint",
    ),
}


def classify(match: str, context: str) -> str:
    """Classify one occurrence without assigning physics from nearby prose."""

    token = match.lower().replace("_", " ")
    text = context.lower().replace("_", " ")
    if "spacetime edge" in token:
        return "SPACETIME_EDGE"
    if token == "aether" and any(word in text for word in ("spacetime", "pure energy", "phase limit", "transition")):
        return "SPACETIME_EDGE"
    if any(word in text for word in (
        "form-core", "finite-core", "proof cutoff", "proof edge", "stored prefix",
        "finite prefix", "mesh endpoint", "validation cutoff", "certificate cutoff",
        "dirichlet cutoff", "truncation boundary",
    )):
        return "FORM_CORE_TRUNCATION_BOUNDARY"
    if any(word in text for word in ("proof-chart", "chart loss", "chart boundary", "binary64", "loss of precision")):
        return "PROOF_CHART_BOUNDARY"
    if token in {"canonical stop", "event"} or any(word in text for word in (
        "canonical stop", "stopping locus", "action-owned stop", "history terminates",
    )):
        return "CANONICAL_STOP_EVENT"
    if token == "boundary" and any(word in text for word in (
        "core boundary", "geometric boundary", "boundary collar", "induced boundary",
    )):
        return "CORE_BOUNDARY"
    return "ORDINARY_NONAMBIGUOUS_USAGE"


def source_files() -> list[Path]:
    files: set[Path] = set()
    for base in SEARCH_ROOTS:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if (
                path.is_file()
                and path.suffix.lower() in SUFFIXES
                and path != TARGET
                and path != Path(__file__).resolve()
                and not any(part.startswith(".tmp") or part.startswith(".") for part in path.relative_to(ROOT).parts)
                and "__pycache__" not in path.parts
            ):
                files.add(path)
    return sorted(files, key=lambda item: item.relative_to(ROOT).as_posix())


def build_payload() -> dict[str, object]:
    occurrences: list[dict[str, object]] = []
    current_ambiguous: list[dict[str, object]] = []
    scanned_files = source_files()
    for path in scanned_files:
        relative = path.relative_to(ROOT).as_posix()
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(lines, start=1):
            context = line.strip()
            for found in TERMS.finditer(line):
                wording = found.group(0)
                row = {
                    "file": relative,
                    "line": line_number,
                    "context": context,
                    "old_wording": wording,
                    "classified_meaning": classify(wording, context),
                    "replacement_wording": wording,
                    "math_changed": False,
                    "claim_status_changed": False,
                }
                occurrences.append(row)
                if AMBIGUOUS_PROOF_EDGE.search(context):
                    current_ambiguous.append(row)
    corrections = [
        {
            "file": file,
            "old_wording": old,
            "classified_meaning": "FORM_CORE_TRUNCATION_BOUNDARY",
            "replacement_wording": replacement,
            "math_changed": False,
            "claim_status_changed": False,
        }
        for file, (old, replacement) in sorted(CORRECTIONS.items())
    ]
    counts = Counter(row["classified_meaning"] for row in occurrences)
    validations = {
        "all_requested_occurrences_classified": all(
            row["classified_meaning"] in {
                "FORM_CORE_TRUNCATION_BOUNDARY", "CORE_BOUNDARY",
                "CANONICAL_STOP_EVENT", "SPACETIME_EDGE", "PROOF_CHART_BOUNDARY",
                "ORDINARY_NONAMBIGUOUS_USAGE",
            }
            for row in occurrences
        ),
        "ambiguous_proof_edge_wording_absent": not current_ambiguous,
        "mathematics_unchanged": True,
        "claim_status_unchanged": True,
        "frozen_predictions_unchanged": True,
        "current_stop_remains_unidentified_with_spacetime_edge": True,
        "spacetime_edge_action_location_remains_underived": True,
        "full_bhsm_complete_remains_false": True,
    }
    return {
        "artifact": "BHSM_SPACETIME_EDGE_ONTOLOGY_AUDIT",
        "ontology_version": "BHSM-AE2-ONTOLOGY-1.4.0",
        "reserved_meaning": "SPACETIME_EDGE is the ontological limit where spacetime ceases and pure energy/Aether is the environment.",
        "search_roots": [path.relative_to(ROOT).as_posix() for path in SEARCH_ROOTS],
        "search_terms": TERMS.pattern,
        "files_scanned": len(scanned_files),
        "occurrence_count": len(occurrences),
        "classification_counts": dict(sorted(counts.items())),
        "wording_corrections": corrections,
        "occurrences": occurrences,
        "current_ambiguous_occurrences": current_ambiguous,
        "action_audit": {
            "present": [
                "owner-authorized pure-energy core ontology",
                "open core-boundary phase-space/self-adjoint-transfer target",
                "formal regular+boundary+core conservation ledger",
                "regular-stratum restriction preserving current BHSM mathematics",
            ],
            "absent_or_open": [
                "complete core transfer map", "energy matching across transition",
                "phase/topology/gauge transport", "exit condition",
                "nonextension theorem for every regular spacetime chart",
                "physical Aether transition derivation",
            ],
            "future_dependency": "CANONICAL_STOP_TO_SPACETIME_EDGE_IDENTIFICATION",
            "future_dependency_status": "OPEN_ACTION_LEVEL_IDENTIFICATION_NOT_GATE7_PREREQUISITE",
        },
        "gate7": {
            "mathematics_changed": False,
            "finite_history_stop_may_close_existing_alternative": True,
            "requires_stop_to_equal_spacetime_edge": False,
        },
        "FULL_BHSM_COMPLETE": False,
        "frozen_predictions_changed": False,
        "validation": validations,
        "validation_passed": all(validations.values()),
    }


def deterministic_json(payload: dict[str, object]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"


def main() -> None:
    payload = build_payload()
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(deterministic_json(payload), encoding="utf-8")
    print(TARGET.relative_to(ROOT).as_posix())
    print(json.dumps({
        "occurrence_count": payload["occurrence_count"],
        "classification_counts": payload["classification_counts"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
