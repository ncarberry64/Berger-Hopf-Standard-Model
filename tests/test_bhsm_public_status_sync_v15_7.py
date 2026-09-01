from __future__ import annotations

import json
from pathlib import Path

from bhsm.interface.current_program_status import CURRENT_VERSION, status_payload
from bhsm.interface.public_status_sync_v15_7 import (
    audit_payload,
    broken_current_links,
    current_surface_sections,
    semantic_status_audit,
)
from bhsm.interface.science_hardening import payload_for_command


ROOT = Path(__file__).resolve().parents[1]
FLAGS = (
    "UNCHANGED_AE2_LOCALIZATION_CARRIER_FOUND",
    "PHYSICAL_ENCAPSULATION_IDENTIFIED",
    "FULL_BHSM_COMPLETE",
)


def test_historical_python_status_baseline_remains_v15_10() -> None:
    assert CURRENT_VERSION == "v15.10"
    assert status_payload()["FULL_BHSM_COMPLETE"] is False


def test_canonical_public_sections_are_fail_closed() -> None:
    for name, text in current_surface_sections().items():
        for flag in FLAGS:
            assert f"{flag} = FALSE" in text, name


def test_current_section_links_resolve() -> None:
    assert broken_current_links() == []


def test_json_status_is_semantically_current() -> None:
    audit = semantic_status_audit()
    assert audit["version"] == "2.0"
    assert audit["surface_results"]["docs/current_bhsm_status.json"] is True
    assert audit["all_current"] is True


def test_historical_cli_remains_fail_closed_but_is_not_public_authority() -> None:
    current = payload_for_command("physics-status")["physics_current_status"]
    assert current["current_version"] == CURRENT_VERSION
    assert current["FULL_BHSM_COMPLETE"] is False


def test_public_audit_passes_and_never_touches_usb() -> None:
    payload = audit_payload()
    assert payload["USB_TOUCHED"] is False
    assert payload["pass"] is True


def test_root_readme_current_block_is_concise() -> None:
    section = current_surface_sections()["README.md"]
    assert "Gate 7 is **OPEN**" in section
    assert len(section.splitlines()) < 55


def test_historical_machine_status_is_archived_verbatim() -> None:
    archived = json.loads(
        (ROOT / "docs/archive/status/current_bhsm_status_pre_2026_09_01.json")
        .read_text(encoding="utf-8")
    )
    assert archived["current_version"] == "v15.10"
    assert archived["FULL_BHSM_COMPLETE"] is False


def test_archival_release_badge_is_not_called_current_science() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "Latest archival release" in readme
    assert "Current research status" in readme
