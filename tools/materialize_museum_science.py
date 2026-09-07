"""Publish existing BHSM evidence to the Museum; never run or retune physics.

Reviewed numeric additions must point to a hash-bound, explicitly promoted
source record. This validates publication metadata, not the physical proof.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = "theory/bhsm_prediction_ledger.json"
BUNDLE = "artifacts/BHSM_aether_hybrid_standard_model_bundle_v15_53.json"
MAP = "artifacts/current_semantics/BHSM_CURRENT_SYSTEM_INTEGRATION_MAP.json"
INTAKE = "data/museum/approved_science_outputs.json"
TARGET = "data/museum/bhsm_science_collection.json"
COPIES = ("museum/app/science-collection.json", "museum/public/data/science-collection.json")
PARTICLES = [
    {"id": key, "name": name, "sector": sector, "moment_basis": basis}
    for key, name, sector, basis in [
        ("electron", "Electron", "Charged leptons", "charged-lepton"),
        ("muon", "Muon", "Charged leptons", "charged-lepton"),
        ("tau", "Tau", "Charged leptons", "charged-lepton"),
        ("nu_e", "Electron neutrino", "Neutrinos", "neutral-mode"),
        ("nu_mu", "Muon neutrino", "Neutrinos", "neutral-mode"),
        ("nu_tau", "Tau neutrino", "Neutrinos", "neutral-mode"),
        ("up", "Up quark", "Quarks", "confined-mode"),
        ("charm", "Charm quark", "Quarks", "confined-mode"),
        ("top", "Top quark", "Quarks", "confined-mode"),
        ("down", "Down quark", "Quarks", "confined-mode"),
        ("strange", "Strange quark", "Quarks", "confined-mode"),
        ("bottom", "Bottom quark", "Quarks", "confined-mode"),
        ("photon", "Photon", "Gauge / scalar bosons", "boson-specific"),
        ("gluon", "Gluon", "Gauge / scalar bosons", "boson-specific"),
        ("W", "W boson", "Gauge / scalar bosons", "boson-specific"),
        ("Z", "Z boson", "Gauge / scalar bosons", "boson-specific"),
        ("higgs", "Higgs boson", "Gauge / scalar bosons", "spin-zero"),
        ("proton", "Proton", "Composite benchmarks", "composite"),
        ("neutron", "Neutron", "Composite benchmarks", "composite"),
    ]
]

def source_bytes(path):
    data = path.read_bytes()
    return data.replace(b"\r\n", b"\n") if path.suffix in {".json", ".md", ".py"} else data

def pointer(document, path):
    if not path.startswith("/"):
        raise ValueError("A source JSON pointer is required")
    for part in path[1:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        document = document[int(part)] if isinstance(document, list) else document[part]
    return document

def reviewed_outputs(root, intake):
    outputs = []
    ids = set()
    for entry in intake["outputs"]:
        key = entry["id"]
        if key in ids:
            raise ValueError("Duplicate output id")
        ids.add(key)
        if entry["exhibit"] not in {"decays", "magnetic", "predictions", "forces"}:
            raise ValueError("Unknown science exhibit")
        if not entry.get("review_record") or not entry.get("reviewed_by"):
            raise ValueError("An explicit academic review record is required")
        path = (root / entry["source_path"]).resolve()
        if not path.is_relative_to((root / "artifacts").resolve()) or not path.is_file():
            raise ValueError("Derived outputs must come from a retained artifact")
        data = source_bytes(path)
        if hashlib.sha256(data).hexdigest() != entry["source_sha256"]:
            raise ValueError("Source hash mismatch")
        row = pointer(json.loads(data), entry["source_pointer"])
        if entry["exhibit"] in {"decays", "magnetic"}:
            if entry.get("particle") not in {p["id"] for p in PARTICLES}:
                raise ValueError("Unknown particle identity")
            if not entry.get("observable") or any(row.get(k) != entry.get(k) for k in ("particle", "observable")):
                raise ValueError("Source-owned particle and observable must match the exhibit")
        if row.get("classification") not in {"DERIVED_POINT_PREDICTION", "DERIVED_INTERVAL_PREDICTION"}:
            raise ValueError("A screen or comparison cannot become a derived prediction")
        if row.get("physical_promotion_ready") is not True or row.get("experimental_target_used") is not False:
            raise ValueError("Physical promotion and no-fit evidence are required")
        for field in ("action_version", "domain", "units", "source_revision", "uncertainty_note"):
            if not row.get(field):
                raise ValueError("Missing source-owned provenance: " + field)
        value = row["value"]
        numbers = value if isinstance(value, list) else [value]
        if not all(type(v) in (int, float) and math.isfinite(v) for v in numbers):
            raise ValueError("Finite numeric output is required")
        if row["classification"] == "DERIVED_INTERVAL_PREDICTION":
            if len(numbers) != 2 or numbers[0] > numbers[1]:
                raise ValueError("An ordered interval is required")
        elif isinstance(value, list):
            raise ValueError("Point prediction must be scalar")
        gates = row.get("gates", {})
        required = {"gate7_closed", "action_selected_external_state", "physical_units_fixed"}
        if entry["exhibit"] == "magnetic":
            required |= {"ward_identity_closed", "renormalization_fixed", "moment_definition_fixed"}
        if entry["exhibit"] == "decays":
            required |= {"amplitude_action_derived", "channel_inventory_complete"}
        if not all(gates.get(gate) is True for gate in required):
            raise ValueError("An observable-specific physical gate remains open")
        outputs.append({**entry, "result": row})
    return outputs

def build(root=ROOT):
    root = Path(root)
    sources = {}
    def read(relative):
        data = source_bytes(root / relative)
        sources[relative] = hashlib.sha256(data).hexdigest()
        return json.loads(data)
    ledger, bundle, current, intake = [read(p) for p in (LEDGER, BUNDLE, MAP, INTAKE)]
    if bundle.get("validation_passed") is not True or current.get("validation_passed") is not True:
        raise ValueError("Retained structural evidence is invalid")
    return {
        "schema": "BHSM_MUSEUM_SCIENCE_COLLECTION_V1",
        "source_hashes": sources,
        "FULL_BHSM_COMPLETE": current["FULL_BHSM_COMPLETE"],
        "particles": PARTICLES,
        "prediction_ledger": ledger,
        "sm_bundle": {key: bundle[key] for key in ("classification", "chiral_bundle", "claim_boundary", "validation")},
        "approved_outputs": reviewed_outputs(root, intake),
        "policy": "Prototypes stay in the main collection. Sandbox comparisons supplement them. Only reviewed source-owned outputs replace pending values; simulation is never promoted by relabeling.",
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = (json.dumps(build(), indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
    for relative in (TARGET, *COPIES):
        path = ROOT / relative
        if args.check:
            if not path.is_file() or source_bytes(path) != payload:
                raise SystemExit("Stale Museum science snapshot: " + relative)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
    print("Museum science collection: " + ("verified" if args.check else "materialized"))

if __name__ == "__main__":
    main()
