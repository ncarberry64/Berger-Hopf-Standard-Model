from __future__ import annotations

from pathlib import Path

from bhsm.interface.aether_cycle_sigma_coefficient_reconstruction_v15_10 import EXACT_NEXT_OBJECT, PRIMARY_VERDICT
from bhsm.interface.current_program_status import CURRENT_VERSION, status_payload
from bhsm.interface.public_status_sync_v15_7 import (
    audit_payload,
    broken_current_links,
    current_surface_sections,
    semantic_status_audit,
    stale_current_status_hits,
)
from bhsm.interface.science_hardening import payload_for_command


ROOT = Path(__file__).resolve().parents[1]


def test_current_version_is_v15_10() -> None:
    assert CURRENT_VERSION == "v15.10"


def test_all_human_current_sections_name_v15_10_and_exact_object() -> None:
    for name, section in current_surface_sections().items():
        assert "v15.10" in section, name
        assert EXACT_NEXT_OBJECT in section, name


def test_no_stale_version_is_called_current() -> None:
    assert stale_current_status_hits() == []


def test_current_section_links_resolve() -> None:
    assert broken_current_links() == []


def test_json_status_is_semantically_current() -> None:
    audit = semantic_status_audit()
    assert audit["surface_results"]["docs/current_bhsm_status.json"] is True


def test_cli_physics_status_is_semantically_current() -> None:
    current = payload_for_command("physics-status")["physics_current_status"]
    assert current["current_version"] == CURRENT_VERSION
    assert current["primary_verdict"] == PRIMARY_VERDICT
    assert current["exact_next_object"] == EXACT_NEXT_OBJECT
    assert current["FULL_BHSM_COMPLETE"] is False


def test_python_status_exposes_cycle_failures() -> None:
    payload = status_payload()
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert payload["nonlinear_cycle_status"]["NONLINEAR_FORMATION_MAP"] == (
        "UNDEFINED_MISSING_ACTION_OWNED_LOCAL_CONFIGURATION_OR_DOMAIN"
    )
    assert payload["backward_closure_status"]["PHYSICAL_UNSTABLE_CONFIGURATION"] == (
        "OPEN_NO_LOCALIZED_CONSTRAINT_SOLVED_NEGATIVE_MODE"
    )
    assert payload["REPOSITORY_EXISTING_ANSWER_EXHAUSTED"] is True


def test_public_audit_passes_and_never_touches_usb() -> None:
    payload = audit_payload()
    assert payload["pass"] is True
    assert payload["USB_TOUCHED"] is False


def test_root_readme_new_visitor_block_is_concise() -> None:
    section = current_surface_sections()["README.md"]
    assert "Empirical status" in section
    assert "FULL_BHSM_COMPLETE = FALSE" in section
    assert len(section.splitlines()) < 70


def test_archival_release_badge_is_not_called_current_science() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "Latest archival release" in readme
    assert "Current research status" in readme
