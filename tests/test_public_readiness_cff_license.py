"""CFF 1.2 metadata compatibility must preserve the exact legal/author checks."""
import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "cff_readiness_audit", ROOT / "tools/audit_public_readiness.py")
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


@pytest.fixture
def citation_root(tmp_path, monkeypatch):
    for name in ("CITATION.cff", ".zenodo.json"):
        (tmp_path / name).write_bytes((ROOT / name).read_bytes())
    (tmp_path / "README.md").write_text("[LICENSE.md](LICENSE.md)", encoding="utf8")
    handoff = tmp_path / "docs/bhsm_public_scientific_handoff_v6_21_0.md"
    handoff.parent.mkdir()
    handoff.write_text("[LICENSE.md](../LICENSE.md)", encoding="utf8")
    monkeypatch.setattr(AUDIT, "ROOT", tmp_path)
    return tmp_path


def change_cff(root, old, new):
    path = root / "CITATION.cff"
    text = path.read_text(encoding="utf8")
    assert old in text
    path.write_text(text.replace(old, new), encoding="utf8")


def test_structured_author_and_immutable_custom_notice_are_accepted(citation_root):
    result = AUDIT.check_citation()
    assert result["passed"], result
    assert result["license"] == "LicenseRef-AllRightsReserved"
    assert result["license_url"] == AUDIT.ARCHIVAL_LICENSE_URL
    assert AUDIT.check_license_visibility()["passed"]


@pytest.mark.parametrize("notice", [
    "https://opensource.org/license/mit/",
    AUDIT.REPOSITORY + "/blob/main/LICENSE.md",
])
def test_changed_or_mutable_notice_is_refused(citation_root, notice):
    change_cff(citation_root, AUDIT.ARCHIVAL_LICENSE_URL, notice)
    assert not AUDIT.check_citation()["passed"]
    assert not AUDIT.check_license_visibility()["passed"]


@pytest.mark.parametrize("license_id", ["MIT", "LicenseRef-AllRightsReserved"])
def test_scalar_license_cannot_override_cff_custom_notice(citation_root, license_id):
    path = citation_root / "CITATION.cff"
    with path.open("a", encoding="utf8") as stream:
        stream.write(f'\nlicense: "{license_id}"\n')
    assert not AUDIT.check_citation()["passed"]
    assert not AUDIT.check_license_visibility()["passed"]


@pytest.mark.parametrize("old,new", [
    ('given-names: "Norman P."', 'given-names: "Other"'),
    ('family-names: "Carberry"', 'family-names: "Other"'),
    ("0009-0000-6650-3485", "0000-0000-0000-0000"),
])
def test_changed_structured_author_identity_is_refused(citation_root, old, new):
    change_cff(citation_root, old, new)
    assert "CITATION.cff:author" in AUDIT.check_citation()["failures"]


def test_extra_author_is_not_hidden_by_a_literal_name(citation_root):
    change_cff(citation_root, 'version: "v1.1.0"',
               '  - family-names: "Other"\nversion: "v1.1.0"')
    assert "CITATION.cff:author" in AUDIT.check_citation()["failures"]


def test_duplicate_author_identity_field_is_refused(citation_root):
    change_cff(citation_root, '    given-names: "Norman P."',
               '    given-names: "Norman P."\n    given-names: "Norman P."')
    assert "CITATION.cff:author" in AUDIT.check_citation()["failures"]


def test_archival_doi_is_still_checked(citation_root):
    change_cff(citation_root, "10.5281/zenodo.20663419", "10.5281/zenodo.99999999")
    assert "doi_consistency" in AUDIT.check_citation()["failures"]


def test_zenodo_permission_is_still_checked(citation_root):
    path = citation_root / ".zenodo.json"
    text = path.read_text(encoding="utf8")
    assert "LicenseRef-AllRightsReserved" in text
    path.write_text(text.replace("LicenseRef-AllRightsReserved", "MIT"), encoding="utf8")
    assert ".zenodo.json:license" in AUDIT.check_citation()["failures"]


def test_current_license_links_are_still_required(citation_root):
    (citation_root / "README.md").write_text("No link", encoding="utf8")
    assert "README license link" in AUDIT.check_license_visibility()["failures"]


def test_formal_repository_citation_is_still_required(citation_root):
    change_cff(citation_root,
               f'repository-code: "{AUDIT.REPOSITORY}"',
               'repository-code: "https://github.com/example/workspace"')
    assert "CITATION.cff:repository-code" in AUDIT.check_citation()["failures"]
