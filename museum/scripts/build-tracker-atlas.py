"""Render a small, deterministic Museum view of the reviewed candidate inventory.

This reads metadata only. It never fits, ranks, classifies, or changes observations.
The complete inventory and provenance remain in the downloadable metadata package.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INVENTORY_SHA256 = "4a76300f0e0e3883a0c9c343e1e0c5fbead595c9b4f333aaa01ec05c9ec9debc"
CODE_COMMIT = "8ca349fa8eb5c54c661a022790ae915d05060b59"
REPOSITORY = "https://github.com/ncarberry64/Berger-Hopf-Standard-Model"


def build():
    path = "products/blackhole_tracker/bhtracker/web/atlas_data.json"
    content = (ROOT / path).read_bytes()
    if hashlib.sha256(content).hexdigest() != INVENTORY_SHA256:
        raise ValueError("The reviewed inventory bytes changed; review a new version first.")
    inventory = json.loads(content)
    counts = inventory["metadata"]["counts"]
    assert counts["unique_events"] == 155 == 100 + 59 - 4
    assert counts["tier_counts"] == {
        "REVIEW_REQUIRED": 94, "SUPPORTED_LENSING_EVENT": 58,
        "BLACK_HOLE_SEARCH_TARGET": 3, "BLACK_HOLE_CANDIDATE": 0,
        "STRONGLY_SUPPORTED_BLACK_HOLE_IDENTIFICATION": 0,
    }
    targets = []
    for event in inventory["events"]:
        assert all(value is None for value in event["lens"].values())
        if event["tier"] != "BLACK_HOLE_SEARCH_TARGET":
            continue
        targets.append({key: event[key] for key in (
            "event_id", "known_aliases", "source_direction", "lens", "tier",
            "classification_basis", "quality_flags", "next_actions",
        )})
    benchmark, = inventory["benchmarks"]
    assert benchmark["classification_source"] == "LITERATURE"
    assert benchmark["tracker_recovery_status"].startswith("NOT_ESTABLISHED")
    return {
        "schema": "bhsm.museum.candidate_atlas_view.v1",
        "repository_url": REPOSITORY,
        "formal_product_revision": CODE_COMMIT,
        "source_inventory": path,
        "inventory_utf8_sha256": INVENTORY_SHA256,
        "scientific_as_of": inventory["metadata"]["scientific_as_of"],
        "role": "STATIC_METADATA_VIEW_NOT_AN_INFERENCE_OR_NEW_RANKING",
        "counts": counts,
        "targets": targets,
        "benchmark": {key: benchmark[key] for key in (
            "event_id", "classification_source", "benchmark_status",
            "tracker_recovery_status", "source_direction", "lens",
        )},
        "scope": "Source/event directions, not present lens positions. Unavailable physical quantities stay null. All155 cohort outcomes, including failed or unavailable cases, remain in the complete inventory. One published benchmark is separate from cohort counts; tracker recovery is open. No new black-hole interpretation.",
        "BHSM_interpretation": "One Einstein/GHY optical exterior counted once. Core, membrane, horizon and deformation are not measured by this inventory.",
    }


if __name__ == "__main__":
    rendered = (json.dumps(build(), indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
    destinations = [
        ROOT / "museum/lib/blackhole-tracker-atlas.json",
        ROOT / "museum/public/research/blackhole-tracker/candidate-atlas-20261023-v3/ATLAS_PROVENANCE.json",
    ]
    for destination in destinations:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(rendered)
    print(json.dumps({"sha256": hashlib.sha256(rendered).hexdigest(), "bytes": len(rendered), "targets": 3, "cohort_events": 155, "separate_benchmarks": 1}))
