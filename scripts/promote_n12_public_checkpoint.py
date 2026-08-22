"""Promote the validated N12 checkpoint into stable public artifacts.

This is a content-preserving provenance promotion.  It does not recompute,
reinterpret, or strengthen any scientific result.  Temporary source names are
mapped to durable repository paths, repository JSON uses canonical LF line
endings, and every promoted file is SHA-256 hashed.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path


TARGET = Path("artifacts/n12_direct_checkpoint")
MANIFEST = TARGET / "BHSM_N12_SCIENTIFIC_CHECKPOINT_MANIFEST.json"

FILES = {
    ".tmp_direct_n12_high_precision_action_center.npz":
        "BHSM_N12_COMPLETE_PERSISTENT_CHILD_STATE.npz",
    ".tmp_direct_n12_high_precision_complete_persistent_child_promotion.json":
        "BHSM_N12_COMPLETE_PERSISTENT_CHILD_CERTIFICATE.json",
    ".tmp_direct_n12_high_precision_root_residual.json":
        "BHSM_N12_EXACT_ROOT_RESIDUAL.json",
    ".tmp_direct_n12_high_precision_root_full_radii_1e11.json":
        "BHSM_N12_FULL_ACTION_RADII_CERTIFICATE.json",
    ".tmp_direct_n12_high_precision_root_directed_center.json":
        "BHSM_N12_DIRECTED_ROUNDING_CERTIFICATE.json",
    ".tmp_direct_n12_high_precision_root_physical_neighborhood.json":
        "BHSM_N12_PHYSICAL_NEIGHBORHOOD_CERTIFICATE.json",
    ".tmp_direct_n12_high_precision_root_persistence_final.json":
        "BHSM_N12_POSITIVE_DURATION_PERSISTENCE.json",
    ".tmp_direct_n12_high_precision_root_ordered_ball_1e11.json":
        "BHSM_N12_ORDERED_EVENT_EIGENLINE_BALL.json",
    ".tmp_direct_n12_high_precision_root_ordered_mixed_1e11.json":
        "BHSM_N12_ORDERED_EVENT_MIXED_MAJORANT.json",
    ".tmp_direct_n12_high_precision_root_bordered_1e11.json":
        "BHSM_N12_BORDERED_LIFT_BALL.json",
    ".tmp_direct_n12_high_precision_root_action_majorants_1e11.json":
        "BHSM_N12_ACTION_MAJORANTS.json",
    ".tmp_direct_n12_high_precision_root_exact_normal_1e20.json":
        "BHSM_N12_EXACT_NORMAL_1E20.json",
    ".tmp_direct_n12_high_precision_root_exact_normal_1e20.npz":
        "BHSM_N12_EXACT_NORMAL_1E20.npz",
    ".tmp_direct_n12_high_precision_root_exact_normal_1e24.json":
        "BHSM_N12_EXACT_NORMAL_1E24.json",
    ".tmp_direct_n12_high_precision_root_exact_normal_1e24.npz":
        "BHSM_N12_EXACT_NORMAL_1E24.npz",
    ".tmp_direct_n12_high_precision_root_third_variations.json":
        "BHSM_N12_THIRD_VARIATIONS.json",
    ".tmp_direct_n12_high_precision_root_third_variations.npz":
        "BHSM_N12_THIRD_VARIATIONS.npz",
    ".tmp_direct_n12_high_precision_root_momentum_one_sided_1e12.json":
        "BHSM_N12_MOMENTUM_ONE_SIDED_1E12.json",
    ".tmp_direct_n12_high_precision_root_momentum_one_sided_1e12.npz":
        "BHSM_N12_MOMENTUM_ONE_SIDED_1E12.npz",
    ".tmp_direct_n12_high_precision_exact_boundary_tail.json":
        "BHSM_N12_EXACT_BOUNDARY_TAIL.json",
    ".tmp_direct_n12_high_precision_principal_coercivity.json":
        "BHSM_N12_PRINCIPAL_COERCIVITY.json",
    ".tmp_direct_n12_high_precision_inverse_square_tail.json":
        "BHSM_N12_INVERSE_SQUARE_TAIL_DIAGNOSTIC.json",
    ".tmp_direct_n12_high_precision_high_shell_dirac_gauge_fixed.json":
        "BHSM_N12_GAUGE_FIXED_HIGH_SHELL_DIAGNOSTIC.json",
    ".tmp_direct_n12_high_precision_event_child_calderon_symbol.json":
        "BHSM_N12_EVENT_CHILD_CALDERON_N12_TO_N32_P96.json",
    ".tmp_direct_n12_high_precision_event_child_calderon_symbol_p192.json":
        "BHSM_N12_EVENT_CHILD_CALDERON_N12_N32_P192.json",
    ".tmp_direct_n12_high_precision_event_child_calderon_symbol_n48.json":
        "BHSM_N12_EVENT_CHILD_CALDERON_N12_TO_N48_P96.json",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def main() -> None:
    missing = [source for source in FILES if not Path(source).is_file()]
    if missing:
        raise FileNotFoundError("missing promotion inputs: " + ", ".join(missing))
    promotion = json.loads(Path(
        ".tmp_direct_n12_high_precision_complete_persistent_child_promotion.json"
    ).read_text(encoding="utf-8"))
    if not promotion.get("DIRECT_N12_COMPLETE_PERSISTENT_CHILD_CERTIFIED"):
        raise RuntimeError("N12 promotion certificate is not validated")
    if promotion.get("CONTINUUM_EVENT_CHILD_CERTIFIED") is not False:
        raise RuntimeError("public checkpoint must retain the open continuum gate")
    if promotion.get("FULL_BHSM_COMPLETE") is not False:
        raise RuntimeError("public checkpoint must retain FULL_BHSM_COMPLETE=false")

    TARGET.mkdir(parents=True, exist_ok=True)
    entries = []
    for source_name, target_name in FILES.items():
        source = Path(source_name)
        target = TARGET / target_name
        if source.suffix.lower() == ".json":
            # Match the repository's canonical JSON representation so hashes
            # remain valid in clean Linux and Windows checkouts.
            target.write_bytes(source.read_bytes().replace(b"\r\n", b"\n"))
        else:
            shutil.copy2(source, target)
        entries.append({
            "source_temporary_path": source.as_posix(),
            "durable_repository_path": target.as_posix(),
            "bytes": target.stat().st_size,
            "SHA256": sha256(target),
            "byte_identical_to_source": sha256(target) == sha256(source),
        })

    manifest = {
        "classification": "BHSM_N12_DIRECT_ROOT_PUBLIC_PROVENANCE_CHECKPOINT",
        "scientific_status": {
            "DIRECT_N12_COMPLETE_PERSISTENT_CHILD_CERTIFIED": True,
            "exact_F12_norm": 2.1479968882829104e-14,
            "certified_action_coordinate_root_ball_radius": 1.0e-11,
            "corrected_ordered_event_branch": "N6_INDEX_12_TO_N12_INDEX_24",
            "N12_event_child_Calderon_symbol_gap": 0.029146859835472938,
            "minimum_zero_padded_probe_symbol_gap_N12_to_N48": (
                0.00912893612489853
            ),
            "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "claim_boundary": (
            "N12 is a certified complete persistent finite-resolution child. "
            "The N16-N48 states in the Calderon artifacts are zero-padded "
            "diagnostic probes, not roots. Their positive finite symbol gaps "
            "do not prove an N-uniform continuum bound. Q_xi, Delta H, "
            "action-selected families, and blind observables remain open."
        ),
        "exact_next_dependency": (
            "DERIVE_AN_EXPLICIT_N12_TO_INFINITY_RETAINED_ACTION_BOUND_ON_"
            "THE_GAUGE_FIXED_EVENT_CHILD_CALDERON_GRAPH_PROJECTOR_TAIL_"
            "AND_CLOSE_THE_NONLINEAR_INVERSE_SQUARE_CORRECTION_RADIUS"
        ),
        "promoted_files": entries,
        "reproduction": {
            "python": "Python 3.10+ with the repository benchmark extra",
            "focused_commands": [
                "python scripts/audit_n12_high_precision_coupled_residual.py",
                "python scripts/derive_n12_exact_normal_jacobian.py",
                "python scripts/certify_n12_full_action_radii.py",
                "python scripts/certify_n12_candidate_positive_duration_persistence.py",
                "python scripts/audit_n12_event_child_calderon_symbol.py",
            ],
            "note": (
                "The public state and certificate inputs are stored in this "
                "directory; scripts accept BHSM_N12_* environment overrides "
                "for durable paths."
            ),
        },
        "new_equation_constraint_gate_scale_fit_or_prediction": False,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "manifest": MANIFEST.as_posix(),
        "files": len(entries),
        "bytes": sum(entry["bytes"] for entry in entries),
        "manifest_SHA256": sha256(MANIFEST),
    }, indent=2))


if __name__ == "__main__":
    main()
