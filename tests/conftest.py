"""Repository-wide pytest isolation for tracked scientific sources.

Generators are intentionally callable against a repository root for explicit
materialization workflows. Tests must never use that capability to mutate the
checkout that is being reviewed.
"""

from __future__ import annotations

import os
from pathlib import Path
import stat
import subprocess
import warnings

import pytest


ROOT = Path(__file__).resolve().parents[1]
_ORIGINAL_WRITE_TEXT = Path.write_text
_ORIGINAL_WRITE_BYTES = Path.write_bytes
_ORIGINAL_READ_BYTES = Path.read_bytes
_ARTIFACT_ROOT = (ROOT / "artifacts").resolve()
_CRLF_ARTIFACT_EXCEPTIONS = frozenset(
    {"CKM_no_fit_operator_output_v1.json"}
)
_CRLF_FROZEN_PATHS = frozenset(
    {
        (ROOT / "docs" / "frozen_predictions.md").resolve(),
        (ROOT / "docs" / "frozen_predictions.json").resolve(),
    }
)


def _canonical_test_bytes(path: Path) -> bytes:
    """Read materialized JSON with its repository-canonical line endings.

    Git's Windows checkout conversion can leave historical artifact files
    as CRLF in an existing clone even after an ``eol=lf`` attribute is
    introduced.  Materializers and index blobs are canonical LF, so byte
    comparisons normalize only that checkout representation.  Explicit
    hash-frozen CRLF artifacts remain untouched.
    """

    payload = _ORIGINAL_READ_BYTES(path)
    resolved = path.resolve()
    if resolved in _CRLF_FROZEN_PATHS:
        return payload.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
    try:
        relative = resolved.relative_to(_ARTIFACT_ROOT)
    except ValueError:
        return payload
    if (
        resolved.suffix.lower() == ".json"
        and resolved.name not in _CRLF_ARTIFACT_EXCEPTIONS
        and relative.parts
    ):
        return payload.replace(b"\r\n", b"\n")
    return payload


def _tracked_paths() -> tuple[Path, ...]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return tuple(
        (ROOT / os.fsdecode(item)).resolve()
        for item in result.stdout.split(b"\0")
        if item
    )


TRACKED_PATHS = frozenset(_tracked_paths())
_SESSION_SNAPSHOT = {
    path: (path.read_bytes(), stat.S_IMODE(path.stat().st_mode))
    for path in TRACKED_PATHS
    if path.exists() and path.is_file()
}


def _inside_checkout(path: Path) -> bool:
    try:
        path.relative_to(ROOT.resolve())
    except ValueError:
        return False
    return True


@pytest.fixture(autouse=True)
def protect_tracked_checkout(monkeypatch: pytest.MonkeyPatch):
    """Canonicalize artifact reads and restore tracked writes after each test."""

    originals: dict[Path, tuple[bytes, int] | None] = {}

    def remember(path: Path) -> Path:
        resolved = path.resolve()
        if resolved in TRACKED_PATHS and resolved not in originals:
            originals[resolved] = (
                (resolved.read_bytes(), stat.S_IMODE(resolved.stat().st_mode))
                if resolved.exists()
                else None
            )
        return resolved

    def guarded_write_text(
        path: Path,
        data: str,
        encoding: str | None = None,
        errors: str | None = None,
        newline: str | None = None,
    ) -> int:
        remember(path)
        return _ORIGINAL_WRITE_TEXT(
            path,
            data,
            encoding=encoding,
            errors=errors,
            newline=newline,
        )

    def guarded_write_bytes(path: Path, data: bytes) -> int:
        remember(path)
        return _ORIGINAL_WRITE_BYTES(path, data)

    monkeypatch.setattr(Path, "write_text", guarded_write_text)
    monkeypatch.setattr(Path, "write_bytes", guarded_write_bytes)
    monkeypatch.setattr(Path, "read_bytes", _canonical_test_bytes)
    yield

    for path, snapshot in originals.items():
        if snapshot is None:
            if path.exists():
                path.unlink()
            continue
        original, mode = snapshot
        path.parent.mkdir(parents=True, exist_ok=True)
        _ORIGINAL_WRITE_BYTES(path, original)
        path.chmod(mode)


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Restore and report any tracked mutation that escaped the write guard."""
    del exitstatus
    mutated: list[str] = []

    for path, (original, mode) in _SESSION_SNAPSHOT.items():
        current = path.read_bytes() if path.exists() else None
        if current == original:
            continue
        mutated.append(path.relative_to(ROOT).as_posix())
        path.parent.mkdir(parents=True, exist_ok=True)
        _ORIGINAL_WRITE_BYTES(path, original)
        path.chmod(mode)

    missing_from_snapshot = [
        path
        for path in TRACKED_PATHS
        if _inside_checkout(path) and path not in _SESSION_SNAPSHOT and path.exists()
    ]
    for path in missing_from_snapshot:
        mutated.append(path.relative_to(ROOT).as_posix())
        path.unlink()

    if mutated:
        warnings.warn(
            pytest.PytestWarning(
                "pytest restored tracked files mutated by a test: "
                + ", ".join(sorted(mutated))
            ),
            stacklevel=1,
        )
        session.exitstatus = pytest.ExitCode.TESTS_FAILED
