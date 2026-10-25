"""Acquire exactly two pinned OGLE cadence parents, without fitting observations.

Default: describe and verify bundled non-observational metadata, no network.
--verify-existing: read-only hashes of an existing data root, no network.
--download: explicit bounded HTTPS retrieval into a NEW external data root.
Public accessibility does not grant redistribution rights. No native files ship
in this kit. A valid hash establishes byte identity, not scientific calibration.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import time
import urllib.request

METADATA = {
    "pilot_selection.json": "dafb05962f93ecf73e0ab17ebb55c3de0de533db2837ba330e05279c5d6ceac0",
    "download_manifest.json": "d2d0256b0dd95380bce6c42ce52d447ebdc63dd251fb29da2d95267291005922",
}
SOURCES = (
    {"event_id": "OGLE3-ULENS-0033", "stratum": "long_duration",
     "relative_path": "raw/ogle3/photometry/photBLG100.3.I.144687.dat",
     "url": "https://ftp.astrouw.edu.pl/ogle/ogle3/blg_tau/PHOT/CLASSA-OPTIMIZED/photBLG100.3.I.144687.dat",
     "bytes": 29574, "sha256": "31324077d637261ddea50336e4fe239cdda928c2b34e0fce94fe49350d8e05c2"},
    {"event_id": "OGLE3-ULENS-0127", "stratum": "ordinary_duration_control",
     "relative_path": "raw/ogle3/photometry/photBLG101.4.I.196393.dat",
     "url": "https://ftp.astrouw.edu.pl/ogle/ogle3/blg_tau/PHOT/CLASSA-OPTIMIZED/photBLG101.4.I.196393.dat",
     "bytes": 29915, "sha256": "f2af29c637cdda5fac7ee7ac313c0a67c17124996301de886de974be3de87e7d"},
)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def metadata_root(explicit=None):
    if explicit is not None:
        return explicit
    adjacent = Path(__file__).resolve().parent / "cadence_metadata_v1"
    if adjacent.is_dir():
        return adjacent
    return Path(__file__).resolve().parents[1] / "research/validation_20261024/cadence_metadata_v1"


def admitted_metadata(root):
    result = {}
    for name, expected in METADATA.items():
        path = root / name
        if path.stat().st_size > 1024 * 1024:
            raise ValueError("Metadata exceeds bounded size")
        raw = path.read_bytes()
        if digest(raw) != expected:
            raise ValueError("Frozen metadata hash mismatch: " + name)
        result[name] = raw
    selection = json.loads(result["pilot_selection.json"])
    manifest = json.loads(result["download_manifest.json"])
    for spec in SOURCES:
        rows = [r for r in selection["selected"] if r["event_id"] == spec["event_id"]]
        records = [r for r in manifest["files"] if r["relative_path"] == spec["relative_path"]]
        if len(rows) != 1 or len(records) != 1:
            raise ValueError("Unique frozen cadence mapping required")
        if rows[0]["relative_path"] != spec["relative_path"] or rows[0]["stratum"] != spec["stratum"]:
            raise ValueError("Frozen selection mapping mismatch")
        if any(records[0][key] != spec[key] for key in ("url", "bytes", "sha256")):
            raise ValueError("Frozen download mapping mismatch")
    return result


def check_existing(root):
    admitted_metadata(root)
    results = []
    for spec in SOURCES:
        path = root / spec["relative_path"]
        with path.open("rb") as stream:
            raw = stream.read(spec["bytes"] + 1)
        if len(raw) != spec["bytes"] or digest(raw) != spec["sha256"]:
            raise ValueError("Native original byte identity mismatch: " + spec["event_id"])
        results.append({**spec, "state": "VERIFIED_EXISTING", "local_path": str(path.resolve())})
    return results


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        raise ValueError("Redirect refused; original pinned provider URL required")


def retrieve(root, spec, timeout, deadline, events):
    partial = root / "download_attempts" / (Path(spec["relative_path"]).name + ".partial")
    partial.parent.mkdir(exist_ok=True)
    request = urllib.request.Request(spec["url"], headers={"User-Agent": "BHSM-research-cadence-fetch/1; two pinned public originals"})
    opener = urllib.request.build_opener(NoRedirect())
    start = time.monotonic()
    data = bytearray()
    with partial.open("xb") as saved:
        with opener.open(request, timeout=timeout) as response:
            if response.status != 200 or response.geturl() != spec["url"]:
                raise ValueError("Exact provider URL and HTTP200 required")
            while True:
                if time.monotonic() - start > deadline:
                    raise TimeoutError("Total per-file deadline exceeded")
                block = response.read(min(8192, spec["bytes"] + 1 - len(data)))
                if block:
                    saved.write(block)
                    data.extend(block)
                if time.monotonic() - start > deadline:
                    raise TimeoutError("Total per-file deadline exceeded after read; received bytes retained")
                if not block:
                    break
                if len(data) > spec["bytes"]:
                    raise ValueError("Provider response exceeds frozen byte budget")
        saved.flush()
        os.fsync(saved.fileno())
    if len(data) != spec["bytes"] or digest(data) != spec["sha256"]:
        raise ValueError("Downloaded file differs from original; no substitution admitted")
    target = root / spec["relative_path"]
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    events.append({**spec, "state": "DOWNLOADED_HASH_VERIFIED", "local_path": str(target.resolve()),
                   "partial_retained": str(partial.resolve()), "elapsed_seconds": time.monotonic()-start})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--download", action="store_true", help="Explicitly permit the two bounded HTTPS requests")
    modes.add_argument("--verify-existing", action="store_true", help="Hash existing originals, with no network")
    parser.add_argument("--data-root", type=Path, help="NEW directory for download, existing directory for verification")
    parser.add_argument("--metadata-root", type=Path)
    parser.add_argument("--timeout-seconds", type=float, default=10.0)
    parser.add_argument("--deadline-seconds", type=float, default=60.0)
    parser.add_argument("--receipt", type=Path, help="Optional NEW receipt path; downloads also write into their NEW data root")
    args = parser.parse_args()
    if not (0 < args.timeout_seconds <= 30 and args.timeout_seconds <= args.deadline_seconds <= 120):
        parser.error("Timeout must be positive <=30s; per-file deadline between timeout and120s")
    if (args.download or args.verify_existing) and args.data_root is None:
        parser.error("--data-root required for the selected mode")
    if args.receipt is not None and args.receipt.exists():
        raise FileExistsError("Receipt must be new")
    root = metadata_root(args.metadata_root)
    metadata = admitted_metadata(root)
    receipt = {"schema": "bhsm.calibration.two_cadence_acquisition.v1", "python": platform.python_version(),
               "mode": "download" if args.download else "verify-existing" if args.verify_existing else "describe-no-network",
               "metadata_sha256": METADATA, "sources": list(SOURCES), "events": [], "network_requested": bool(args.download),
               "scientific_calls": 0, "fits": 0, "native_redistribution_permission_assumed": False,
               "qualification": "Byte acquisition only; no calibration validation, new analysis admission or BH identification."}
    code = 0
    created = False
    try:
        if args.download:
            args.data_root.mkdir(parents=True, exist_ok=False)
            created = True
            for name, raw in metadata.items():
                with (args.data_root / name).open("xb") as stream:
                    stream.write(raw)
            for spec in SOURCES:
                retrieve(args.data_root, spec, args.timeout_seconds, args.deadline_seconds, receipt["events"])
            receipt["status"] = "TWO_ORIGINALS_DOWNLOADED_AND_VERIFIED"
        elif args.verify_existing:
            receipt["events"] = check_existing(args.data_root)
            receipt["status"] = "TWO_EXISTING_ORIGINALS_VERIFIED"
        else:
            receipt["status"] = "METADATA_VERIFIED_NO_NETWORK"
    except Exception as error:
        receipt["status"] = "ACQUISITION_UNRESOLVED"
        receipt["error_type"] = type(error).__name__
        receipt["error"] = str(error)
        code = 1
    raw = (json.dumps(receipt, sort_keys=True, indent=2, allow_nan=False)+"\n").encode("utf8")
    if created:
        with (args.data_root / "CADENCE_ACQUISITION_RECEIPT_v1.json").open("xb") as stream:
            stream.write(raw)
    if args.receipt is not None:
        with args.receipt.open("xb") as stream:
            stream.write(raw)
    print(raw.decode("utf8"), end="")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
