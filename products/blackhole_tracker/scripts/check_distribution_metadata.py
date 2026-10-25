"""Check built distribution licensing, citations and wheel integrity without fits."""
from __future__ import annotations

import argparse
import base64
import csv
from email.parser import BytesParser
import hashlib
import io
import json
from pathlib import Path
import tarfile
import tomllib
import zipfile

PRODUCT = Path(__file__).resolve().parents[1]
FORMAL_REPOSITORY = "https://github.com/ncarberry64/Berger-Hopf-Standard-Model"


def _sha(payload):
    return hashlib.sha256(payload).hexdigest()


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _metadata(payload, project):
    metadata = BytesParser().parsebytes(payload)
    _require(metadata["Name"] == project["name"], "distribution name mismatch")
    _require(metadata["Version"] == project["version"], "distribution version mismatch")
    if project.get("authors"):
        _require(metadata["Author"] == ", ".join(item["name"] for item in project["authors"]),
                 "distribution author mismatch")
    _require(metadata["License-Expression"] == project["license"], "license expression mismatch")
    _require(set(metadata.get_all("License-File", [])) == set(project["license-files"]),
             "both legal notices must be declared in metadata")
    _require(tuple(map(int, metadata["Metadata-Version"].split("."))) >= (2, 4),
             "PEP 639 requires core metadata 2.4 or later")
    urls = dict(value.split(", ", 1) for value in metadata.get_all("Project-URL", []))
    for key in ("Repository", "Citation"):
        _require(urls.get(key) == project["urls"][key], key + " URL mismatch")
        _require(urls[key].startswith(FORMAL_REPOSITORY), key + " must cite formal BHSM Git")
    return {"version": metadata["Version"], "metadata_version": metadata["Metadata-Version"],
            "author": metadata["Author"],
            "license_expression": metadata["License-Expression"],
            "license_files": metadata.get_all("License-File"),
            "repository": urls["Repository"], "citation": urls["Citation"]}


def inspect_distribution(wheel, sdist, product=PRODUCT):
    """Fail closed on missing/altered notices, citation drift or RECORD damage."""
    wheel, sdist, product = Path(wheel), Path(sdist), Path(product)
    project = tomllib.loads((product / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    notices = {name: (product / name).read_bytes() for name in project["license-files"]}
    _require(set(notices) == {"LICENSE.md", "ACADEMIC_USE.md"}, "unexpected notice inventory")
    citation = (product / "CITATION.cff").read_bytes()
    _require(citation == (product / "bhtracker/CITATION.cff").read_bytes(),
             "source citation copies differ")
    with zipfile.ZipFile(wheel) as archive:
        entries = [info for info in archive.infolist() if not info.is_dir()]
        names = [info.filename for info in entries]
        _require(len(names) == len(set(names)), "duplicate wheel member")
        files = {name: archive.read(name) for name in names}
    metadata_names = [name for name in files if name.endswith(".dist-info/METADATA")]
    _require(len(metadata_names) == 1, "expected one wheel metadata record")
    dist_info = metadata_names[0].rsplit("/", 1)[0]
    wheel_metadata = _metadata(files[metadata_names[0]], project)
    for name, original in notices.items():
        _require(files.get(dist_info + "/licenses/" + name) == original,
                 "wheel notice bytes differ: " + name)
    _require(files.get("bhtracker/CITATION.cff") == citation, "wheel citation bytes differ")
    record_name = dist_info + "/RECORD"
    records = list(csv.reader(io.StringIO(files[record_name].decode("utf-8"))))
    _require(len(records) == len({row[0] for row in records}), "duplicate RECORD entry")
    _require({row[0] for row in records} == set(files), "RECORD must cover every wheel file")
    for name, digest, size in records:
        if name == record_name:
            _require(not digest and not size, "RECORD self-entry must be unhashed")
            continue
        _require(digest.startswith("sha256="), "expected SHA256 RECORD entry: " + name)
        actual = base64.urlsafe_b64encode(hashlib.sha256(files[name]).digest()).rstrip(b"=").decode()
        _require(digest == "sha256=" + actual and size == str(len(files[name])),
                 "wheel RECORD hash/size mismatch: " + name)
    with tarfile.open(sdist, "r:gz") as archive:
        entries = [info for info in archive.getmembers() if info.isfile()]
        names = [info.name for info in entries]
        _require(len(names) == len(set(names)), "duplicate sdist member")
        source_files = {info.name: archive.extractfile(info).read() for info in entries}
    roots = {name.split("/", 1)[0] for name in source_files}
    _require(len(roots) == 1, "expected one sdist root")
    root = roots.pop() + "/"
    for name, original in notices.items():
        _require(source_files.get(root + name) == original, "sdist notice bytes differ: " + name)
    for name in ("CITATION.cff", "bhtracker/CITATION.cff"):
        _require(source_files.get(root + name) == citation, "sdist citation bytes differ: " + name)
    _require(root + "PACKAGING_AND_CITATION.md" in source_files, "sdist packaging guide missing")
    _require(root + "scripts/check_distribution_metadata.py" in source_files,
             "sdist distribution checker missing")
    sdist_metadata = _metadata(source_files[root + "PKG-INFO"], project)
    return {"schema": "bhtracker.distribution_metadata.v1", "passed": True,
            "product_version": project["version"], "formal_repository": FORMAL_REPOSITORY,
            "wheel": {"path": str(wheel), "sha256": _sha(wheel.read_bytes()),
                      "bytes": wheel.stat().st_size, "members": len(files),
                      "metadata": wheel_metadata, "all_RECORD_hashes_and_sizes_valid": True},
            "sdist": {"path": str(sdist), "sha256": _sha(sdist.read_bytes()),
                      "bytes": sdist.stat().st_size, "members": len(source_files),
                      "metadata": sdist_metadata},
            "legal_notices": {name: {"bytes": len(value), "sha256": _sha(value),
                                    "wheel_and_sdist_bytes_exact": True}
                              for name, value in notices.items()},
            "citation_sha256": _sha(citation), "citation_copies_exact": True,
            "scope": "Distribution metadata and contents only; no scientific calculation or validation."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheel", type=Path, required=True)
    parser.add_argument("--sdist", type=Path, required=True)
    parser.add_argument("--product", type=Path, default=PRODUCT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = inspect_distribution(args.wheel, args.sdist, args.product)
    payload = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")


if __name__ == "__main__":
    main()

