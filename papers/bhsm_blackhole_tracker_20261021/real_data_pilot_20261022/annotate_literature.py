"""Add versioned literature metadata without changing frozen fits or ranking."""
import argparse
from copy import deepcopy
import csv
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf8")


def write_csv(path, rows):
    keys = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", encoding="utf8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=keys); writer.writeheader()
        for row in rows:
            writer.writerow({key: json.dumps(value, separators=(",", ":"), allow_nan=False) if isinstance(value, (dict, list)) else value for key, value in row.items()})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prior-cohort", type=Path, required=True)
    parser.add_argument("--target-audit", type=Path, required=True)
    args = parser.parse_args()
    cohort = json.loads(args.prior_cohort.read_text(encoding="utf8"))
    audit = json.loads(args.target_audit.read_text(encoding="utf8"))
    records = json.loads((BASE / "derived_v1/all_100_results.json").read_text(encoding="utf8"))
    ranking = json.loads((BASE / "derived_v1/followup_ranking.json").read_text(encoding="utf8"))
    lookups = {row["event_id"]: row for row in cohort["rows"]}
    target = {row["event_id"]: row for row in audit["targets"]}
    if set(lookups) != {row["event_id"] for row in records}:
        raise ValueError("literature annotation membership does not match frozen100-event table")
    output = BASE / "literature_annotations_v1"; output.mkdir(parents=True, exist_ok=True)
    write_json(output / "prior_cohort_crossmatch.json", cohort)
    write_json(output / "target_prior_literature.json", audit)
    derived = []
    for original in records:
        row = deepcopy(original); match = lookups[row["event_id"]]
        refs = [{"citation": "Wyrzykowski et al. (2015), ApJS216,12", "doi": "10.1088/0067-0049/216/1/12",
                 "url": "https://arxiv.org/abs/1405.3134", "role": "Published standard-event catalog and native observations"}]
        row["prior_59_parallax_cohort_status"] = match["status"]
        row["prior_59_parallax_cohort_matches"] = match["matches"]
        row["catalog_database_id"] = match["ogle_db_id_checked"]
        row["additional_confirmed_aliases"] = target.get(row["event_id"], {}).get("aliases_confirmed", [])
        row["literature_search_date"] = cohort["search_date"]
        row["novelty_status"] = "UNRESOLVED_NO_NEW_LENS_INTERPRETATION_CLAIM"
        row["literature_scope"] = "Primary59-event parallax-cohort exact-ID/alias/coordinate crossmatch; two eligible targets also receive bounded additional primary literature searches. This is not complete novelty clearance."
        if match["matches"]:
            refs.append({"citation": "Wyrzykowski et al. (2016), MNRAS458,3012", "doi": "10.1093/mnras/stw426",
                         "url": "https://arxiv.org/abs/1509.04899", "role": "Prior parallax-event/lens interpretation; not new likelihood measurements"})
        if row["event_id"] == "OGLE3-ULENS-0264":
            refs.append({"citation": "Mroz and Wyrzykowski (2021), ActaAstron71,89", "doi": "10.32023/0001-5237/71.2.1",
                "url": "https://arxiv.org/abs/2107.13701", "role": "Prior-dependent historical remnant reanalysis, not a direct mass measurement imported here"})
        if row["event_id"] in target:
            row["target_prior_result"] = target[row["event_id"]]["prior_result"]
            row["target_followup_caution"] = target[row["event_id"]]["followup_recommendation"]
        if row["event_id"] == "OGLE3-ULENS-3092":
            refs.extend([{"citation": "Yock (2008), High magnification events by MOA in2007", "url": "https://arxiv.org/abs/0805.1775",
                          "role": "Primary cross-identification MOA2007BLG027=OGLE2007BLG057; no BH mass established"},
                         {"citation": "Official OGLE EWS2007BLG057", "url": "https://ogle.astrouw.edu.pl/ogle3/ews/2007/blg-057.html",
                          "role": "Event alias/coordinate check; EWS and optimized-reduction star IDs retained distinctly"}])
            row["source_association_caution"] = target[row["event_id"]]["catalog_id_caution"]
        row["primary_study_references"] = refs
        # Every numerical/diagnostic field remains exactly the frozen value.
        for key, value in original.items():
            if key != "novelty_status" and row[key] != value:
                raise AssertionError("literature annotation altered a frozen result")
        derived.append(row)
    by_id = {row["event_id"]: row for row in derived}
    annotated_ranking = []
    for original in ranking:
        row = deepcopy(original)
        row.update({key: value for key, value in by_id[row["event_id"]].items() if key not in original or key == "novelty_status"})
        annotated_ranking.append(row)
    write_json(output / "all_100_results.json", derived); write_csv(output / "all_100_results.csv", derived)
    write_json(output / "followup_ranking.json", annotated_ranking); write_csv(output / "followup_ranking.csv", annotated_ranking)
    receipt = {"schema": "bhsm_pilot_literature_annotation/1", "fit_or_ranking_logic_changed": False,
        "frozen_table_sha256": sha(BASE / "derived_v1/all_100_results.json"),
        "frozen_ranking_sha256": sha(BASE / "derived_v1/followup_ranking.json"),
        "prior_cohort_evidence_sha256": sha(args.prior_cohort), "target_evidence_sha256": sha(args.target_audit),
        "event_count": len(derived), "prior_parallax_cohort_match_count": sum(bool(row["matches"]) for row in lookups.values()),
        "no_new_black_hole_interpretation_claimed": True,
        "files": [{"path": path.name, "sha256": sha(path), "bytes": path.stat().st_size} for path in sorted(output.iterdir()) if path.is_file()]}
    write_json(BASE / "LITERATURE_ANNOTATION_RECEIPT.json", receipt)
    print(json.dumps({"status": "ANNOTATED_WITHOUT_REFITTING_OR_RERANKING", "rows": len(derived),
                      "prior_parallax_matches": receipt["prior_parallax_cohort_match_count"], "output": str(output)}))


if __name__ == "__main__":
    main()
