"""Release metadata contracts and rejection of altered built distribution files."""
from __future__ import annotations

import ast
import base64
import csv
import hashlib
import importlib.util
import io
from pathlib import Path
import re
import tarfile
import tomllib
import zipfile

import pytest

PRODUCT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "distribution_metadata", PRODUCT / "scripts/check_distribution_metadata.py")
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)


def test_source_license_and_citation_contract():
    project = tomllib.loads((PRODUCT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    assert project["license"] == "LicenseRef-AllRightsReserved"
    assert project["license-files"] == ["LICENSE.md", "ACADEMIC_USE.md"]
    assert project["authors"] == [{"name": "Norman P. Carberry"}]
    original_notices = {
        "LICENSE.md": "94a171b0a8056f93771d01e06776b775bf856372ee4bd9c212262a09adea3e1e",
        "ACADEMIC_USE.md": "7eb5bd4c891164427f80c633ab307707ea7cb874a8bf7a248a4ed748c49ee10b",
    }
    for name, expected in original_notices.items():
        # Git checkouts can choose LF or CRLF; the legal text must not change.
        raw = (PRODUCT / name).read_bytes().replace(b"\r\n", b"\n")
        assert hashlib.sha256(raw).hexdigest() == expected
    citation = (PRODUCT / "CITATION.cff").read_bytes()
    assert citation == (PRODUCT / "bhtracker/CITATION.cff").read_bytes()
    text = citation.decode("utf-8")
    assert re.findall(r'^version: "([^"]+)"$', text, re.MULTILINE) == [project["version"]]
    assert 'repository-code: "' + CHECKER.FORMAL_REPOSITORY + '"' in text
    assert 'license-url: "' + CHECKER.FORMAL_REPOSITORY + '/blob/bfced7926f2ad91da609c84c943369562a687862/LICENSE.md"' in text
    assert not re.search(r"^license:", text, re.MULTILINE)  # CFF 1.2 cannot use custom SPDX LicenseRef values.
    assert "10.5281/zenodo.20663419" not in text  # Historical repository DOI is not a new software DOI.
    module = ast.parse((PRODUCT / "bhtracker/provenance.py").read_text(encoding="utf-8"))
    versions = [ast.literal_eval(node.value) for node in module.body
                if isinstance(node, ast.Assign)
                and any(isinstance(target, ast.Name) and target.id == "VERSION"
                        for target in node.targets)]
    assert versions == [project["version"]]


@pytest.fixture
def distributions(tmp_path):
    product = tmp_path / "source"
    (product / "bhtracker").mkdir(parents=True)
    (product / "pyproject.toml").write_text(
        '[project]\nname="sample"\nversion="1.0rc1"\n'
        'license="LicenseRef-AllRightsReserved"\n'
        'license-files=["LICENSE.md","ACADEMIC_USE.md"]\n'
        '[project.urls]\nRepository="' + CHECKER.FORMAL_REPOSITORY + '"\n'
        'Citation="' + CHECKER.FORMAL_REPOSITORY + '/blob/main/CITATION.cff"\n',
        encoding="utf-8")
    notices = {"LICENSE.md": b"Copyright notice.\r\n",
               "ACADEMIC_USE.md": b"Limited academic evaluation permission.\r\n"}
    citation = b"cff-version: 1.2.0\nmessage: Cite reviewed source.\n"
    for name, value in {**notices, "CITATION.cff": citation}.items():
        (product / name).write_bytes(value)
    (product / "bhtracker/CITATION.cff").write_bytes(citation)
    metadata = (
        "Metadata-Version: 2.4\nName: sample\nVersion: 1.0rc1\n"
        "License-Expression: LicenseRef-AllRightsReserved\n"
        "License-File: LICENSE.md\nLicense-File: ACADEMIC_USE.md\n"
        "Project-URL: Repository, " + CHECKER.FORMAL_REPOSITORY + "\n"
        "Project-URL: Citation, " + CHECKER.FORMAL_REPOSITORY + "/blob/main/CITATION.cff\n\n"
    ).encode()
    info = "sample-1.0rc1.dist-info"
    wheel_files = {info + "/METADATA": metadata, "bhtracker/CITATION.cff": citation,
                   "bhtracker/__init__.py": b'"""Sample fixture."""\n',
                   **{info + "/licenses/" + n: b for n, b in notices.items()}}
    source_files = {"sample-1.0rc1/" + n: b for n, b in {
        **notices, "CITATION.cff": citation, "bhtracker/CITATION.cff": citation,
        "PACKAGING_AND_CITATION.md": b"Fixture packaging guide.\n",
        "scripts/check_distribution_metadata.py": b"# Fixture checker.\n",
        "PKG-INFO": metadata}.items()}
    wheel = tmp_path / "sample.whl"
    sdist = tmp_path / "sample.tar.gz"

    def write_wheel(files, stale_record=False):
        rows = []
        for name, value in files.items():
            digest = base64.urlsafe_b64encode(hashlib.sha256(value).digest()).rstrip(b"=").decode()
            rows.append([name, "sha256=" + digest, str(len(value))])
        record = info + "/RECORD"
        rows.append([record, "", ""])
        stream = io.StringIO()
        csv.writer(stream).writerows(rows)
        payload = dict(files)
        payload[record] = stream.getvalue().encode()
        if stale_record:
            payload["bhtracker/__init__.py"] = b"tampered after RECORD creation"
        with zipfile.ZipFile(wheel, "w") as archive:
            for name, value in payload.items():
                archive.writestr(name, value)

    def write_sdist(files):
        with tarfile.open(sdist, "w:gz") as archive:
            for name, value in files.items():
                member = tarfile.TarInfo(name)
                member.size = len(value)
                archive.addfile(member, io.BytesIO(value))

    write_wheel(wheel_files)
    write_sdist(source_files)
    return product, wheel, sdist, wheel_files, source_files, write_wheel, write_sdist


def test_complete_distribution_preserves_crlf_notices(distributions):
    product, wheel, sdist, *_ = distributions
    result = CHECKER.inspect_distribution(wheel, sdist, product)
    assert result["passed"]
    assert all(row["wheel_and_sdist_bytes_exact"] for row in result["legal_notices"].values())


@pytest.mark.parametrize("change, expected", [
    ("missing_permission", "wheel notice bytes differ: ACADEMIC_USE.md"),
    ("altered_permission", "wheel notice bytes differ: ACADEMIC_USE.md"),
    ("altered_citation", "wheel citation bytes differ"),
    ("stale_record", "wheel RECORD hash/size mismatch"),
])
def test_wheel_rejects_legal_citation_and_record_damage(distributions, change, expected):
    product, wheel, sdist, files, _, write_wheel, _ = distributions
    files = dict(files)
    key = "sample-1.0rc1.dist-info/licenses/ACADEMIC_USE.md"
    if change == "missing_permission":
        del files[key]
    elif change == "altered_permission":
        files[key] = b"Replacement terms must not pass."
    elif change == "altered_citation":
        files["bhtracker/CITATION.cff"] = b"Unrelated citation."
    write_wheel(files, stale_record=change == "stale_record")
    with pytest.raises(ValueError, match=re.escape(expected)):
        CHECKER.inspect_distribution(wheel, sdist, product)


def test_sdist_rejects_altered_permission_even_when_wheel_is_intact(distributions):
    product, wheel, sdist, _, files, _, write_sdist = distributions
    files = dict(files)
    files["sample-1.0rc1/ACADEMIC_USE.md"] = b"Altered source archive permission."
    write_sdist(files)
    with pytest.raises(ValueError, match="sdist notice bytes differ: ACADEMIC_USE.md"):
        CHECKER.inspect_distribution(wheel, sdist, product)

