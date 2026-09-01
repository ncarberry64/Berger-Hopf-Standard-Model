from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "tools/audit_public_surfaces.py"
SPEC = importlib.util.spec_from_file_location("audit_public_surfaces", AUDIT_PATH)
assert SPEC is not None and SPEC.loader is not None
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


def test_public_surface_audit_passes() -> None:
    result = AUDIT.audit()
    assert result["passed"] is True, result
    assert all(result["checks"].values())


def test_canonical_flags_are_fail_closed_everywhere() -> None:
    result = AUDIT.audit()
    assert all(result["flag_checks"].values())
    assert result["checks"]["no_full_completion_promotion"] is True


def test_cms_validation_is_qualified_and_provenanced() -> None:
    result = AUDIT.audit()
    assert all(result["cms_checks"].values())
    assert all(result["provenance_checks"].values())
    assert result["checks"]["no_cms_physics_promotion"] is True


def test_status_history_is_preserved_outside_current_authority() -> None:
    result = AUDIT.audit()
    assert result["checks"]["historical_surfaces_archived"] is True
