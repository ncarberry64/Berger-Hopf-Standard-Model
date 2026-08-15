"""Offline BHSM v6.21 public-review readiness audit and manifest writer."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
VERSION = "v6.21.0"
SOURCE_MAIN_SHA = "5fbad0de4e414084743c081693aebe510bb0b84f"
PREDECESSOR_MERGE_SHA = SOURCE_MAIN_SHA
BRANCH = "bhsm-public-review-readiness-v6-21-0"
SCIENTIFIC_COMMIT = SOURCE_MAIN_SHA
VERDICT_READY = "BHSM_REPOSITORY_PUBLIC_REVIEW_READY"
MANIFEST = ROOT / "artifacts" / "BHSM_public_review_readiness_manifest_v6_21_0.json"

REPOSITORY = "https://github.com/ncarberry64/Berger-Hopf-Standard-Model"
VISIBILITY = "PUBLIC"
DEFAULT_BRANCH = "main"
LATEST_RELEASE_TAG = "v1.1.0"
LATEST_RELEASE_DATE = "2026-06-26"
DOI = "10.5281/zenodo.20663419"
ZENODO_ARCHIVE_VERSION = "v1.2.0"
ZENODO_ARCHIVE_DATE = "2026-06-12"
LICENSE_ID = "LicenseRef-AllRightsReserved"
CITATION_TITLE = (
    "Berger-Hopf Standard Model: "
    "Artifact-Backed Geometric Physics Research Framework"
)

REQUIRED_PUBLIC_FILES = [
    "README.md",
    "STATUS.md",
    "CLAIMS.md",
    "QUICKSTART.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "LICENSE.md",
    "CITATION.cff",
    ".zenodo.json",
    "ARTIFACT_INDEX.md",
    "docs/bhsm_public_scientific_handoff_v6_21_0.md",
]

CURRENT_MARKDOWN_FILES = [
    "README.md",
    "STATUS.md",
    "CLAIMS.md",
    "QUICKSTART.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "docs/bhsm_in_plain_language.md",
    "docs/bhsm_public_scientific_handoff_v6_21_0.md",
]

ALIGNMENT_FILES = [
    "README.md",
    "STATUS.md",
    "CLAIMS.md",
    "docs/current_bhsm_status.md",
]

ALIGNMENT_PHRASES = [
    "v18.83",
    "376",
    "complete-child",
    "eta",
    "persistence",
    "full_bhsm_complete = false",
    "frozen predictions",
]

FROZEN_HASHES = {
    "docs/frozen_predictions.md": (
        "9EA147C56537520C86D3C4F9B864C6BA98BAC9E64931EDAE96449F3B335A36C4"
    ),
    "docs/frozen_predictions.json": (
        "F38210E0689871A25A9D5B0A1A4239883B7240CD7D0E25CDCF4C8CAB72A2CBE7"
    ),
}

QUICKSTART_COMMANDS = [
    "python -m bhsm.interface --help",
    "python -m bhsm.interface registry",
    "python -m bhsm.interface physics-status --format markdown",
    "python tools/audit_forbidden_claims.py",
    "python tools/audit_bhsm_status.py",
    "python tools/audit_frozen_prediction_integrity.py",
    "python tools/verify_precision.py",
]

UNSUPPORTED_CLAIMS = [
    "complete physical BHSM action",
    "complete Standard Model derivation",
    "empirical validation",
    "physical fold mass or kinetic classification",
    "action-derived gauge couplings",
    "action-derived CKM exponent",
    "physical neutrino mass or Delta m^2",
    "collider-production readiness",
    "CERN or institutional endorsement",
]

MARKDOWN_LINK = re.compile(
    r"(?<![A-Za-z0-9_!])\[[^\]]+\]\(([^)]+)\)"
)
EXTERNAL_SCHEMES = ("http://", "https://", "mailto:")
DOI_PATTERN = re.compile(r"10\.5281/zenodo\.\d+")
LOCAL_PATH_PATTERNS = [
    re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+", re.IGNORECASE),
    re.compile(r"/home/[A-Za-z0-9._-]+/"),
]
STALE_CURRENT_PATTERNS = {
    "complete_claim": re.compile(r"\bBHSM is complete\b", re.IGNORECASE),
    "validated_claim": re.compile(
        r"\bBHSM has been experimentally validated\b", re.IGNORECASE
    ),
    "endorsement_claim": re.compile(r"\bCERN endorsement\b", re.IGNORECASE),
    "pending_doi": re.compile(r"\bDOI pending\b", re.IGNORECASE),
    "stale_complete_headline": re.compile(
        r"Complete Internal Boundary No-Fit Package", re.IGNORECASE
    ),
}
SECRET_PATTERNS = {
    "github_token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    "openai_key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "private_key": re.compile(
        r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
    ),
    "assigned_password": re.compile(
        r"(?i)\bpassword\s*[:=]\s*[\"']?(?!example|placeholder|redacted)"
        r"[A-Za-z0-9!@#$%^&*._-]{12,}"
    ),
}
TEXT_SUFFIXES = {
    ".c",
    ".cc",
    ".cff",
    ".cmake",
    ".cpp",
    ".css",
    ".csv",
    ".h",
    ".hpp",
    ".html",
    ".ini",
    ".json",
    ".md",
    ".py",
    ".sh",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
LARGE_FILE_THRESHOLD = 10 * 1024 * 1024
ALLOWED_LARGE_ARTIFACT_LIMIT = 12 * 1024 * 1024
ALLOWED_LARGE_ARTIFACTS = {
    "artifacts/BHSM_aether_n3_fresh_sbp_fifth_v0_priority_v17_36.json",
    "artifacts/BHSM_aether_n3_fresh_sbp_log_scale_priority_family_v17_27.json",
    "artifacts/BHSM_aether_n3_fresh_sbp_third_v0_priority_v17_31.json",
    "artifacts/BHSM_aether_n3_fresh_sbp_three_owner_priority_v17_47.json",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def frozen_sha256(path: Path) -> str:
    """Hash frozen records in their declared canonical CRLF form."""

    payload = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
    return hashlib.sha256(payload).hexdigest().upper()


def read_text(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def current_slice(relative: str) -> str:
    text = read_text(relative)
    if relative == "STATUS.md":
        return text.split("<!--", 1)[0]
    if relative == "CLAIMS.md":
        return text.split("## Allowed", 1)[0]
    return text


def tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return [line for line in result.stdout.splitlines() if line]


def parse_cff_top_level() -> dict[str, str]:
    values: dict[str, str] = {}
    for line in read_text("CITATION.cff").splitlines():
        if line.startswith((" ", "\t", "-")):
            continue
        match = re.match(r"^([a-z][a-z0-9-]*):\s*(.*)$", line)
        if not match:
            continue
        value = match.group(2).strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        values[match.group(1)] = value
    return values


def check_required_files() -> dict:
    missing = [
        relative for relative in REQUIRED_PUBLIC_FILES if not (ROOT / relative).is_file()
    ]
    empty = [
        relative
        for relative in REQUIRED_PUBLIC_FILES
        if (ROOT / relative).is_file() and (ROOT / relative).stat().st_size == 0
    ]
    return {"passed": not missing and not empty, "missing": missing, "empty": empty}


def check_markdown_links() -> tuple[dict, list[str]]:
    broken: list[dict[str, object]] = []
    external: set[str] = set()
    checked = 0
    for relative in CURRENT_MARKDOWN_FILES:
        path = ROOT / relative
        if not path.is_file():
            continue
        for line_number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            for match in MARKDOWN_LINK.finditer(line):
                target = match.group(1).strip().strip("<>")
                if target.startswith(EXTERNAL_SCHEMES):
                    external.add(target)
                    continue
                if target.startswith("#"):
                    continue
                target = target.split("#", 1)[0]
                target = target.split(" ", 1)[0]
                if not target:
                    continue
                checked += 1
                resolved = (path.parent / unquote(target)).resolve()
                if not resolved.exists():
                    broken.append(
                        {
                            "path": relative,
                            "line": line_number,
                            "target": target,
                        }
                    )
    return (
        {"passed": not broken, "checked": checked, "broken": broken},
        sorted(external),
    )


def check_current_claims_and_paths() -> dict:
    findings: list[dict[str, object]] = []
    inspected = [
        "README.md",
        "STATUS.md",
        "CLAIMS.md",
        "QUICKSTART.md",
        "CITATION.cff",
        ".zenodo.json",
        "docs/bhsm_in_plain_language.md",
        "docs/bhsm_public_scientific_handoff_v6_21_0.md",
    ]
    for relative in inspected:
        text = current_slice(relative)
        for line_number, line in enumerate(text.splitlines(), start=1):
            for category, pattern in STALE_CURRENT_PATTERNS.items():
                if pattern.search(line):
                    findings.append(
                        {"path": relative, "line": line_number, "category": category}
                    )
            for pattern in LOCAL_PATH_PATTERNS:
                if pattern.search(line):
                    findings.append(
                        {
                            "path": relative,
                            "line": line_number,
                            "category": "absolute_developer_path",
                        }
                    )
    return {"passed": not findings, "findings": findings}


def check_citation() -> dict:
    cff = parse_cff_top_level()
    zenodo = json.loads(read_text(".zenodo.json"))
    cff_dois = set(DOI_PATTERN.findall(read_text("CITATION.cff")))
    zenodo_dois = set(DOI_PATTERN.findall(read_text(".zenodo.json")))
    failures: list[str] = []
    expected_cff = {
        "cff-version": "1.2.0",
        "title": CITATION_TITLE,
        "version": LATEST_RELEASE_TAG,
        "date-released": LATEST_RELEASE_DATE,
        "repository-code": REPOSITORY,
        "license": LICENSE_ID,
    }
    for key, expected in expected_cff.items():
        if cff.get(key) != expected:
            failures.append(f"CITATION.cff:{key}")
    if zenodo.get("title") != CITATION_TITLE:
        failures.append(".zenodo.json:title")
    if zenodo.get("version") != LATEST_RELEASE_TAG:
        failures.append(".zenodo.json:version")
    if zenodo.get("license") != LICENSE_ID:
        failures.append(".zenodo.json:license")
    if not zenodo.get("creators") or (
        zenodo["creators"][0].get("orcid") != "0009-0000-6650-3485"
    ):
        failures.append(".zenodo.json:creator_orcid")
    if cff_dois != {DOI} or zenodo_dois != {DOI}:
        failures.append("doi_consistency")
    if "Norman P. Carberry" not in read_text("CITATION.cff"):
        failures.append("CITATION.cff:author")
    return {
        "passed": not failures,
        "failures": failures,
        "cff_version": cff.get("cff-version"),
        "title": cff.get("title"),
        "release_tag": cff.get("version"),
        "release_date": cff.get("date-released"),
        "doi": DOI,
        "license": cff.get("license"),
        "zenodo_archive_version": ZENODO_ARCHIVE_VERSION,
        "zenodo_archive_date": ZENODO_ARCHIVE_DATE,
    }


def check_license_visibility() -> dict:
    readme = read_text("README.md")
    handoff = read_text("docs/bhsm_public_scientific_handoff_v6_21_0.md")
    cff = parse_cff_top_level()
    failures = []
    if "[LICENSE.md](LICENSE.md)" not in readme:
        failures.append("README license link")
    if "[LICENSE.md](../LICENSE.md)" not in handoff:
        failures.append("handoff license link")
    if cff.get("license") != LICENSE_ID:
        failures.append("CFF license")
    return {"passed": not failures, "failures": failures}


def check_reproduction_commands() -> dict:
    quickstart = read_text("QUICKSTART.md")
    missing_docs = [command for command in QUICKSTART_COMMANDS if command not in quickstart]
    required_scripts = [
        "tools/audit_public_readiness.py",
        "tools/audit_forbidden_claims.py",
        "tools/audit_bhsm_status.py",
        "tools/audit_frozen_prediction_integrity.py",
        "tools/verify_precision.py",
    ]
    missing_scripts = [
        relative for relative in required_scripts if not (ROOT / relative).is_file()
    ]
    help_run = subprocess.run(
        [sys.executable, "-m", "bhsm.interface", "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
    )
    help_text = help_run.stdout
    missing_cli = [
        command for command in ("registry", "physics-status") if command not in help_text
    ]
    makefile = read_text("Makefile")
    make_target = "reviewer-smoke:" in makefile
    passed = (
        help_run.returncode == 0
        and not missing_docs
        and not missing_scripts
        and not missing_cli
        and make_target
    )
    return {
        "passed": passed,
        "missing_documented_commands": missing_docs,
        "missing_scripts": missing_scripts,
        "missing_cli_commands": missing_cli,
        "reviewer_smoke_target": make_target,
    }


def looks_textual(path: Path) -> bool:
    return path.suffix.lower() in TEXT_SUFFIXES or path.name in {
        "Makefile",
        "LICENSE",
    }


def check_hygiene() -> dict:
    tracked = tracked_files()
    env_files: list[str] = []
    credential_files: list[str] = []
    secret_findings: list[dict[str, object]] = []
    merge_markers: list[dict[str, object]] = []
    malformed_lfs: list[str] = []
    junk: list[str] = []
    large_files: list[dict[str, object]] = []
    allowed_large_files: list[dict[str, object]] = []

    for relative in tracked:
        path = ROOT / relative
        parts = set(Path(relative).parts)
        if path.name == ".env" or path.name.startswith(".env."):
            env_files.append(relative)
        if path.suffix.lower() in {".pem", ".p12", ".pfx", ".key"}:
            credential_files.append(relative)
        if {"__pycache__", ".pytest_cache", ".mypy_cache"} & parts:
            junk.append(relative)
        if relative.startswith(("build/", "dist/")) or path.suffix == ".pyc":
            junk.append(relative)
        if not path.is_file():
            continue
        size = path.stat().st_size
        if size > LARGE_FILE_THRESHOLD:
            row = {"path": relative, "bytes": size}
            if (
                relative in ALLOWED_LARGE_ARTIFACTS
                and size <= ALLOWED_LARGE_ARTIFACT_LIMIT
            ):
                allowed_large_files.append(row)
            else:
                large_files.append(row)
        if not looks_textual(path) or size > 2 * 1024 * 1024:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if text.startswith("version https://git-lfs.github.com/spec/v1"):
            if not (
                re.search(r"^oid sha256:[0-9a-f]{64}$", text, re.MULTILINE)
                and re.search(r"^size \d+$", text, re.MULTILINE)
            ):
                malformed_lfs.append(relative)
        for line_number, line in enumerate(text.splitlines(), start=1):
            if re.match(r"^(<<<<<<< |>>>>>>> |\|\|\|\|\|\|\| )", line):
                merge_markers.append({"path": relative, "line": line_number})
            if relative in {
                "tools/audit_public_readiness.py",
                "tests/test_bhsm_public_readiness_v6_21_0.py",
            }:
                continue
            for category, pattern in SECRET_PATTERNS.items():
                if pattern.search(line):
                    secret_findings.append(
                        {"path": relative, "line": line_number, "category": category}
                    )

    passed = not (
        env_files
        or credential_files
        or secret_findings
        or merge_markers
        or malformed_lfs
        or junk
        or large_files
    )
    return {
        "passed": passed,
        "tracked_env_files": env_files,
        "credential_files": credential_files,
        "secret_findings": secret_findings,
        "merge_markers": merge_markers,
        "malformed_lfs_pointers": malformed_lfs,
        "tracked_cache_or_build_junk": junk,
        "large_file_threshold_bytes": LARGE_FILE_THRESHOLD,
        "allowed_large_artifact_limit_bytes": ALLOWED_LARGE_ARTIFACT_LIMIT,
        "allowed_large_artifacts": allowed_large_files,
        "unexpected_large_files": large_files,
    }


def check_science_alignment() -> dict:
    missing: dict[str, list[str]] = {}
    for relative in ALIGNMENT_FILES:
        text = " ".join(current_slice(relative).split()).casefold()
        absent = [phrase for phrase in ALIGNMENT_PHRASES if phrase not in text]
        if absent:
            missing[relative] = absent
    return {"passed": not missing, "missing_phrases": missing}


def check_frozen_predictions() -> dict:
    files = []
    passed = True
    for relative, expected in FROZEN_HASHES.items():
        actual = frozen_sha256(ROOT / relative)
        unchanged = actual == expected
        passed = passed and unchanged
        files.append(
            {
                "path": relative,
                "expected_sha256": expected,
                "actual_sha256": actual,
                "unchanged": unchanged,
            }
        )
    return {
        "passed": passed,
        "frozen_predictions_changed": not passed,
        "files": files,
    }


def blocking_verdict(checks: dict[str, dict]) -> str:
    mapping = [
        ("required_files", "REQUIRED_PUBLIC_FILE_MISSING"),
        ("markdown_links", "INTERNAL_LINK_FAILURE"),
        ("current_claims", "STALE_PUBLIC_CLAIM"),
        ("citation", "CITATION_RELEASE_MISMATCH"),
        ("license_visibility", "LICENSE_VISIBILITY_FAILURE"),
        ("reproduction", "BROKEN_QUICKSTART"),
        ("hygiene", "REPOSITORY_HYGIENE_FAILURE"),
        ("science_alignment", "CURRENT_SCIENCE_MISALIGNMENT"),
        ("frozen_predictions", "FROZEN_PREDICTION_CHANGE"),
    ]
    for key, reason in mapping:
        if not checks[key]["passed"]:
            return f"BHSM_PUBLIC_REVIEW_BLOCKED_BY_{reason}"
    return VERDICT_READY


def audit() -> dict:
    links, external_urls = check_markdown_links()
    checks = {
        "required_files": check_required_files(),
        "markdown_links": links,
        "current_claims": check_current_claims_and_paths(),
        "citation": check_citation(),
        "license_visibility": check_license_visibility(),
        "reproduction": check_reproduction_commands(),
        "hygiene": check_hygiene(),
        "science_alignment": check_science_alignment(),
        "frozen_predictions": check_frozen_predictions(),
    }
    passed = all(row["passed"] for row in checks.values())
    verdict = VERDICT_READY if passed else blocking_verdict(checks)
    return {
        "audit": "bhsm_public_readiness",
        "version": VERSION,
        "passed": passed,
        "verdict": verdict,
        "checks": checks,
        "external_urls": external_urls,
    }


def manifest_payload(result: dict) -> dict:
    frozen = {
        row["path"]: row["actual_sha256"]
        for row in result["checks"]["frozen_predictions"]["files"]
    }
    blockers = [
        name for name, row in result["checks"].items() if not row["passed"]
    ]
    return {
        "artifact": "BHSM_public_review_readiness_manifest_v6_21_0",
        "version": VERSION,
        "source_main_sha": SOURCE_MAIN_SHA,
        "predecessor_merge_sha": PREDECESSOR_MERGE_SHA,
        "branch": BRANCH,
        "scientific_commit": SCIENTIFIC_COMMIT,
        "repository": {
            "url": REPOSITORY,
            "visibility": VISIBILITY,
            "default_branch": DEFAULT_BRANCH,
        },
        "public_file_inventory": {
            relative: (ROOT / relative).is_file()
            for relative in REQUIRED_PUBLIC_FILES
        },
        "tested_quickstart_commands": QUICKSTART_COMMANDS,
        "audit_results": {
            name: row["passed"] for name, row in result["checks"].items()
        },
        "external_urls_recorded": result["external_urls"],
        "current_scientific_summary": {
            "research_frontier": "v18.83",
            "n3_exact_residual_norm": 0.80554785212226,
            "event_to_complete_child_map": "derived_and_executed",
            "complete_child_chart_rank": 14,
            "complete_child_persistence": "validated_for_1e-4",
            "simultaneous_n3_saddle": "open_residual_nonzero",
            "physical_mass_claim": False,
        },
        "active_construction_target": (
            "Continue physically admissible exact 376-row descent from the "
            "latest accepted frontier to F376 zero"
        ),
        "unsupported_claims": UNSUPPORTED_CLAIMS,
        "citation": {
            "title": CITATION_TITLE,
            "latest_github_release_tag": LATEST_RELEASE_TAG,
            "latest_github_release_date": LATEST_RELEASE_DATE,
            "doi": DOI,
            "doi_resolution_checked": True,
            "zenodo_archive_version": ZENODO_ARCHIVE_VERSION,
            "zenodo_archive_date": ZENODO_ARCHIVE_DATE,
            "license": LICENSE_ID,
        },
        "frozen_prediction_hashes": frozen,
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "scientific_formulas_changed": False,
        "scientific_source_modules_changed": False,
        "public_readiness_verdict": result["verdict"],
        "blockers": blockers,
    }


def deterministic_json(payload: dict) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def materialize_manifest(result: dict) -> Path:
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_bytes(deterministic_json(manifest_payload(result)).encode("utf-8"))
    return MANIFEST


def human_output(result: dict) -> str:
    lines = [
        f"BHSM public-readiness audit {result['version']}",
        f"verdict: {result['verdict']}",
    ]
    for name, row in result["checks"].items():
        lines.append(f"{'PASS' if row['passed'] else 'FAIL'} {name}")
    lines.append(f"external URLs recorded: {len(result['external_urls'])}")
    if not result["passed"]:
        lines.append("Detected values are never printed; findings contain only paths, lines, and categories.")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", choices=("human", "json"), default="human")
    parser.add_argument(
        "--materialize",
        action="store_true",
        help="write the deterministic public-readiness manifest",
    )
    args = parser.parse_args()
    result = audit()
    if args.materialize:
        materialize_manifest(result)
    if args.format == "json":
        print(deterministic_json(result), end="")
    else:
        print(human_output(result))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
