"""Create the deterministic, metadata-only candidate-atlas walkthrough.

This authoring script uses only the standard library. It executes no notebook
cell, scientific fit, observation importer, download or inference campaign.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from textwrap import dedent
import tomllib

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "notebooks" / "05_candidate_atlas.ipynb"


def cell(kind: str, identifier: str, source: str) -> dict:
    value = {"cell_type": kind, "id": identifier, "metadata": {},
             "source": dedent(source).strip() + "\n"}
    if kind == "code":
        value.update(execution_count=None, outputs=[])
    return value


def build_notebook() -> dict:
    version = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    cells = [
        cell("markdown", "atlas-purpose", r'''
            # BHSM Blackhole Tracker: candidate atlas

            Use the **actual bundled metadata inventory** to locate historical
            events and inspect their evidence without running a new physical fit.
            The 100-event pilot and 59-event published parallax cohort share four
            identities: the atlas retains **155 distinct cohort records** plus a
            **separate published known-system benchmark**.

            The BHSM interpretation uses **one shared Einstein/GHY compact-lens
            exterior optical response, counted once**. No extra core/envelope
            potential is introduced. These records do not identify a membrane
            deformation, core state or horizon.

            A source/event sky direction is not an inferred present-day lens
            position. The J2000 equinox does not supply an observation epoch.
            Unavailable lens position, mass, distance and absolute motion remain
            `None` (JSON `null`); a long event is not a mass measurement.

            Install the matching Blackhole Tracker wheel first. This notebook
            needs no additional notebook-level scientific dependency, raw
            observations, network access or external file location. Formal source
            and citation: [BHSM reviewer repository](https://github.com/ncarberry64/Berger-Hopf-Standard-Model).
            '''),
        cell("code", "atlas-load-inventory", '''
            import json
            from pathlib import Path
            from tempfile import NamedTemporaryFile
            from bhtracker import candidate_atlas as atlas

            inventory, inventory_text = atlas.load_inventory()
            inventory_sha256 = atlas.text_sha256(inventory_text)
            assert inventory_sha256 == "4a76300f0e0e3883a0c9c343e1e0c5fbead595c9b4f333aaa01ec05c9ec9debc"
            assert len(inventory["events"]) == 155
            assert len(inventory["benchmarks"]) == 1
            print(json.dumps(atlas.summary(inventory), indent=2))
            print("Exact bundled inventory UTF-8 SHA-256:", inventory_sha256)
            '''),
        cell("markdown", "atlas-target-evidence", '''
            ## Three search targets with different evidence

            OGLE3-ULENS-0585 and OGLE3-ULENS-3092 passed the frozen historical
            photometric follow-up screen. Their mass and object type remain
            unresolved. PAR-13 is a previously published, disputed,
            population-prior-dependent possibility: unreliable Gaia source
            astrometry and an alternative lower-mass interpretation remain
            explicit. These three records are not three identified black holes,
            and this notebook produces no new ranking or interpretation.
            '''),
        cell("code", "atlas-three-targets", '''
            target_filters = {**atlas.default_filters(), "tier": "BLACK_HOLE_SEARCH_TARGET"}
            targets = atlas.filter_events(inventory, target_filters)
            target_ids = [event["event_id"] for event in targets]
            assert target_ids == ["OGLE3-ULENS-0585", "OGLE3-ULENS-3092", "OGLE3-ULENS-PAR-13"]
            for event in targets:
                print(event["event_id"], "|", event["classification_basis"])
                print("  Frozen photometric follow-up:", event["photometric_assessment"].get("followup_eligible"))
                print("  BH evidence:", event["literature_assessment"]["current_BH_evidence_status"])
                for interpretation in event["literature_assessment"].get("interpretations", []):
                    if interpretation.get("caution"):
                        print("  Published caution:", interpretation["caution"])
            '''),
        cell("markdown", "atlas-localization", '''
            ## Directions to investigate; unresolved physical quantities

            These catalog directions support archival searches and pointing.
            They supply no depth, present-day lens position, lens trajectory or
            error region. Printed catalog precision is not a measured positional
            uncertainty. The complete source attribution stays in each record's
            `provenance` and `source_records` fields and in every replay.
            '''),
        cell("code", "atlas-directions-and-nulls", '''
            direction_fields = ("role", "ra_hms", "dec_dms", "ra_deg", "dec_deg",
                                "frame", "equinox", "epoch", "uncertainty")
            for event in targets:
                assert all(event["lens"][field] is None for field in atlas.LENS_FIELDS)
                print(json.dumps({
                    "event_id": event["event_id"],
                    "source_event_direction": {field: event["source_direction"][field]
                                               for field in direction_fields},
                    "inferred_lens_quantities": event["lens"],
                    "new_black_hole_interpretation": event["new_black_hole_interpretation"]
                }, indent=2))
            '''),
        cell("markdown", "atlas-retain-outcomes", '''
            ## Keep the full cohorts and every failed outcome

            A failed simple fit remains useful for alternative-model assessment;
            it is not erased by the target filter. Published lens designations,
            scalar nonrejection, frozen follow-up eligibility and physical
            classification remain separate. Four verified overlaps are counted
            once. This metadata walkthrough does not refit the parallax cohort.
            '''),
        cell("code", "atlas-cohorts-and-failures", '''
            pilot = atlas.filter_events(inventory, {**atlas.default_filters(),
                "cohort": "FROZEN_100_EVENT_PILOT_V1"})
            parallax = atlas.filter_events(inventory, {**atlas.default_filters(),
                "cohort": "WYRZYKOWSKI_2016_PARALLAX_59"})
            overlaps = sorted({e["event_id"] for e in pilot} & {e["event_id"] for e in parallax})
            inadequate = [e for e in pilot if e["photometric_assessment"]["tracker_status"] == "PHOTOMETRIC_MODEL_INADEQUATE"]
            scalar_nonrejected = [e for e in pilot if e["photometric_assessment"].get("scalar_fit_nonrejected") is True]
            qualified = [e for e in pilot if e["photometric_assessment"].get("followup_eligible") is True]
            assert (len(pilot), len(parallax), len(overlaps), len(inadequate), len(scalar_nonrejected), len(qualified)) == (100, 59, 4, 89, 11, 2)
            print({"pilot": len(pilot), "published_parallax": len(parallax), "overlap_ids": overlaps,
                   "retained_inadequate_simple_fits": len(inadequate),
                   "scalar_nonrejected": len(scalar_nonrejected), "qualified_followups": len(qualified)})
            '''),
        cell("markdown", "atlas-known-benchmark", '''
            ## Published benchmark label versus tracker recovery

            OGLE-2011-BLG-0462 has strong published black-hole evidence. The
            atlas records that literature label separately from the 155 cohort
            events. **The engine's recovery is still not established**; a known
            positive label is not a successful benchmark fit by this software.
            This cell reads the saved status and performs no astrometric fit or
            uncertainty calibration.
            '''),
        cell("code", "atlas-benchmark-status", '''
            benchmark = inventory["benchmarks"][0]
            assert benchmark["classification_source"] == "LITERATURE"
            assert benchmark["tracker_recovery_status"].startswith("NOT_ESTABLISHED")
            assert benchmark["accepted_engine_black_hole"] is False
            print(json.dumps({
                "event_id": benchmark["event_id"],
                "classification_source": benchmark["classification_source"],
                "published_benchmark_status": benchmark["benchmark_status"],
                "tracker_recovery_status": benchmark["tracker_recovery_status"],
                "accepted_engine_black_hole": benchmark["accepted_engine_black_hole"],
                "inferred_lens_quantities": benchmark["lens"]
            }, indent=2))
            '''),
        cell("markdown", "atlas-replay-scope", '''
            ## Export and replay without losing unselected events

            The replay carries the exact original inventory UTF-8 text, its
            SHA-256, filtered records and identities, filters and metadata.
            Hashes establish consistency, not authenticity, scientific adequacy
            or a black-hole identification. The fixed tutorial timestamp below
            is an export label, not an observation epoch.

            First verify in memory, then write and read one uniquely named
            temporary file through the same open handle. It is removed on close;
            no raw observation or existing analysis file is changed. Replay
            restores the inventory and selection, not a physical inference run.
            '''),
        cell("code", "atlas-exact-utf8-replay", '''
            bundle = atlas.create_replay(inventory_text, target_filters,
                origin="05_candidate_atlas notebook", created_utc="2026-10-23T00:00:00Z")
            restored = atlas.validate_replay(bundle)
            assert restored["inventory_json"].encode("utf-8") == inventory_text.encode("utf-8")
            assert restored["inventory_utf8_sha256"] == inventory_sha256
            assert restored["selected_event_ids"] == target_ids
            bundle_bytes = json.dumps(bundle, indent=2, ensure_ascii=False, allow_nan=False).encode("utf-8")
            with NamedTemporaryFile(mode="w+b", prefix="bhsm-atlas-", suffix=".json") as temporary:
                temporary.write(bundle_bytes)
                temporary.flush()
                temporary.seek(0)
                from_file = atlas.validate_replay(atlas.read_json(temporary.read().decode("utf-8")))
                assert from_file["inventory_json"].encode("utf-8") == inventory_text.encode("utf-8")
            assert not Path(temporary.name).exists()
            print({"payload_sha256": bundle["payload_sha256"], "inventory_sha256": inventory_sha256,
                   "retained_cohort_events": len(from_file["inventory"]["events"]),
                   "separate_benchmarks": len(from_file["inventory"]["benchmarks"]),
                   "restored_target_ids": from_file["selected_event_ids"], "temporary_file_removed": not Path(temporary.name).exists()})
            '''),
        cell("markdown", "atlas-next-evidence", '''
            The useful result is an auditable inventory of event directions,
            evidence and next observations, including failures. A discriminating
            lens interpretation needs adequate data, validated angular/parallax
            information and lens-light/alternative-object checks. Published
            population-prior summaries remain attributed conditional statements.
            No mass, current lens location, new black-hole interpretation or
            successful known-system recovery is manufactured by this walkthrough.
            ''')
    ]
    return {"cells": cells, "metadata": {
        "kernelspec": {"display_name": "Python 3 (BHSM Blackhole Tracker)", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
        "bhsm_interpretation": {"framework": "BHSM", "product_version": version,
            "one_Einstein_GHY_exterior_response_counted_once": True,
            "new_physical_fit": False, "accepted_engine_black_hole": False},
        "generator": {"path": "scripts/make_candidate_atlas_notebook.py",
            "sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
        "formal_repository": "https://github.com/ncarberry64/Berger-Hopf-Standard-Model"
    }, "nbformat": 4, "nbformat_minor": 5}


def main() -> None:
    raw = (json.dumps(build_notebook(), indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    DESTINATION.write_bytes(raw)
    print(DESTINATION.name + " SHA-256 " + hashlib.sha256(raw).hexdigest())


if __name__ == "__main__":
    main()
