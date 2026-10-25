"""Print, acquire or verify one frozen public Gaia18ajz context response.

No arguments makes no network request. This helper never parses observations,
selects rows, associates an object with the event, or runs a physical model.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_PATH = ROOT / "research/primary_target_20261023/PRIMARY_NATIVE_INTAKE_PROTOCOL_v1.json"
PROTOCOL_SHA256 = "38d7085b2eeffae5c0e32537c1ca31f7a8cd57f94b153b13d468bc9553a39399"
NATIVE_SHA256 = "f3fdaebb9a4881213d1db2deb529c2779c9cb5883a089e18c7c8356623c82a84"
NATIVE_BYTES = 312255
LIMIT_BYTES = 12000000
TIMEOUT_SECONDS = 45
FORMAL_REPOSITORY = "https://github.com/ncarberry64/Berger-Hopf-Standard-Model"
RAW_FILENAME = "native_response.bin"
RECEIPT_FILENAME = "context_verification_receipt.json"


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def file_digest(path: Path) -> tuple[int, str]:
    """Hash retained bytes with bounded memory, including rejected prefixes."""
    count = 0
    value = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(65536):
            count += len(chunk)
            value.update(chunk)
    return count, value.hexdigest()


def write_json(path: Path, value: dict) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")


def protocol() -> tuple[bytes, dict, str]:
    raw = PROTOCOL_PATH.read_bytes()
    if digest(raw) != PROTOCOL_SHA256:
        raise ValueError("Frozen intake protocol bytes differ; no request is permitted.")
    value = json.loads(raw)
    expected = {
        "POS": "CIRCLE 277.56025 -8.22021 0.0002777777777777778",
        "COLLECTION": "ztf_dr21", "FORMAT": "ipac_table",
    }
    if value["ztf_request"]["parameters"] != expected or value["limits"] != {
        "timeout_seconds": TIMEOUT_SECONDS, "response_bytes": LIMIT_BYTES, "retry_count": 0,
    }:
        raise ValueError("Frozen request or limits differ; no request is permitted.")
    url = value["ztf_request"]["endpoint"] + "?" + urllib.parse.urlencode(expected)
    return raw, value, url


class NoRedirect(urllib.request.HTTPRedirectHandler):
    """Keep one fixed endpoint request; redirects are retained HTTP failures."""

    def redirect_request(self, request, fp, code, message, headers, new_url):
        return None


def retain_response(response, destination, receipt, started: float) -> bool:
    """Preserve received bytes up to the fixed cap; never accept a capped read."""
    complete = False
    count = 0
    while count < LIMIT_BYTES:
        if time.monotonic() - started >= TIMEOUT_SECONDS:
            receipt["read_limit_status"] = "ELAPSED_DEADLINE_REACHED_RESPONSE_INCOMPLETE"
            return False
        chunk = response.read(min(65536, LIMIT_BYTES - count))
        if chunk:
            destination.write(chunk)
            count += len(chunk)
        if time.monotonic() - started >= TIMEOUT_SECONDS:
            receipt["read_limit_status"] = "ELAPSED_DEADLINE_REACHED_RESPONSE_INCOMPLETE"
            return False
        if not chunk:
            complete = True
            break
    receipt["read_limit_status"] = (
        "EOF_OBSERVED" if complete else "BYTE_CAP_REACHED_RESPONSE_NOT_ACCEPTED"
    )
    return complete


def acquire(url: str, destination, receipt: dict, started: float) -> bool:
    """One public request, zero retries, no credentials or response parsing."""
    if time.monotonic() - started >= TIMEOUT_SECONDS:
        receipt["read_limit_status"] = "ELAPSED_DEADLINE_REACHED_BEFORE_REQUEST"
        return False
    request = urllib.request.Request(url, headers={
        "User-Agent": "BHSM-Blackhole-Tracker-frozen-context-helper/1.0",
    })
    opener = urllib.request.build_opener(NoRedirect())
    receipt["network_requests_attempted"] = 1
    try:
        response = opener.open(request, timeout=TIMEOUT_SECONDS)
    except urllib.error.HTTPError as error:
        # HTTPError is also a readable response; preserve its native error body.
        receipt["http_status"] = error.code
        receipt["response_headers"] = list(error.headers.items()) if error.headers else []
        receipt["final_url"] = error.geturl()
        with error:
            retain_response(error, destination, receipt, started)
        receipt["failure"] = "HTTP_ERROR"
        return False
    with response:
        receipt["http_status"] = response.status
        receipt["response_headers"] = list(response.headers.items())
        receipt["final_url"] = response.geturl()
        complete = retain_response(response, destination, receipt, started)
    return complete and receipt["http_status"] == 200 and receipt["final_url"] == url


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--download", action="store_true", help="Explicitly make the one frozen public request")
    action.add_argument("--verify-existing", type=Path, metavar="FILE", help="Verify local native bytes; make no HTTP request")
    parser.add_argument("--output", type=Path, metavar="NEW_DIRECTORY", help="Required for an action; parent must exist")
    args = parser.parse_args()
    try:
        protocol_raw, protocol_value, url = protocol()
    except (OSError, ValueError, KeyError) as error:
        parser.error(str(error))
    if not args.download and args.verify_existing is None:
        if args.output is not None:
            parser.error("--output needs --download or --verify-existing; no files were created")
        print(json.dumps({
            "protocol": protocol_value, "protocol_sha256": PROTOCOL_SHA256,
            "expected_native_sha256": NATIVE_SHA256, "expected_native_bytes": NATIVE_BYTES,
            "network_requests_performed": 0,
            "usage": "Choose --verify-existing FILE --output NEW_DIRECTORY or explicitly --download --output NEW_DIRECTORY.",
        }, indent=2))
        return 0
    if args.output is None:
        parser.error("--output NEW_DIRECTORY is required so every attempted action retains a receipt")
    output = args.output.resolve()
    try:
        output.mkdir()  # Exclusive ownership: never enter or write into an existing run.
    except OSError as error:
        parser.error("Cannot create fresh output directory; existing files were not changed: " + str(error))
    receipt = {
        "schema": "bhsm.primary_target_context_helper_receipt.v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "action": "DOWNLOAD" if args.download else "VERIFY_EXISTING",
        "protocol_sha256": PROTOCOL_SHA256,
        "helper_sha256": digest(Path(__file__).read_bytes()),
        "formal_repository": FORMAL_REPOSITORY,
        "requested_url": url, "request_parameters": protocol_value["ztf_request"]["parameters"],
        "limits": protocol_value["limits"], "retry_attempts": 0,
        "timeout_semantics": "45-second urllib socket timeout with elapsed-deadline checks before and after bounded reads; not an OS hard wall-clock guarantee. Local verification uses the same byte/deadline cap.",
        "network_requests_attempted": 0,
        "source_path": str(args.verify_existing.resolve()) if args.verify_existing is not None else None,
        "native_file": RAW_FILENAME, "expected_native_sha256": NATIVE_SHA256,
        "expected_native_bytes": NATIVE_BYTES, "accepted_frozen_byte_identity": False,
        "source_association": "CONTEXTUAL_CONE_ONLY_NOT_ADOPTED_LENS_OR_SOURCE_ID",
        "observation_parser_calls": 0, "selection_calls": 0, "model_calls": 0,
        "publication_ready": False, "known_BH_recovery_accepted": False,
        "status": "STARTED_UNACCEPTED",
    }
    started = time.monotonic()
    response_complete = False
    try:
        with (output / "frozen_intake_protocol.json").open("xb") as stream:
            stream.write(protocol_raw)
        with (output / RAW_FILENAME).open("xb") as destination:
            if args.download:
                response_complete = acquire(url, destination, receipt, started)
            else:
                # Read-only source; over-limit inputs retain an explicitly incomplete prefix.
                receipt["local_source_bytes_reported"] = args.verify_existing.stat().st_size
                with args.verify_existing.open("rb") as source:
                    response_complete = retain_response(source, destination, receipt, started)
    except Exception as error:
        receipt["failure"] = type(error).__name__ + ": " + str(error)
    native_path = output / RAW_FILENAME
    if native_path.exists():
        native_size, native_hash = file_digest(native_path)
        receipt["native_sha256"] = native_hash
        receipt["native_bytes"] = native_size
        receipt["retained_native_bytes_complete"] = response_complete
        receipt["retained_content_scope"] = "COMPLETE_INPUT" if response_complete else "RECEIVED_PREFIX_ONLY_NOT_FULL_INPUT"
        accepted = (response_complete and native_size == NATIVE_BYTES and native_hash == NATIVE_SHA256
                    and "failure" not in receipt)
        receipt["accepted_frozen_byte_identity"] = accepted
        receipt["status"] = "ACCEPTED_FROZEN_BYTE_IDENTITY_ONLY" if accepted else "REJECTED_RETAINED_NATIVE_BYTES"
    else:
        receipt["status"] = "FAILED_NO_NATIVE_BYTES_RECEIVED"
    receipt["elapsed_seconds"] = time.monotonic() - started
    receipt["qualification"] = (
        "Hash equality reproduces frozen context bytes, not source/lens association, calibrated likelihood, "
        "BH identity or a new discovery. A changed public response is never silently adopted. "
        "An incomplete or over-limit input retains only its received prefix, explicitly marked incomplete and always rejected."
    )
    write_json(output / RECEIPT_FILENAME, receipt)
    print(json.dumps({"status": receipt["status"], "receipt": str(output / RECEIPT_FILENAME),
                      "native_sha256": receipt.get("native_sha256")}, ensure_ascii=True))
    return 0 if receipt["accepted_frozen_byte_identity"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
