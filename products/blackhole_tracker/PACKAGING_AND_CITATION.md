# Distribution licensing and citations

The formal source and reviewer record are the
[BHSM Git repository](https://github.com/ncarberry64/Berger-Hopf-Standard-Model),
under `products/blackhole_tracker/`. Cite the product's [CITATION.cff](CITATION.cff)
and record the exact reviewed commit and artifact SHA256 hashes used in a run.
The installed wheel also contains the same citation at `bhtracker/CITATION.cff`.

The root BHSM citation retains its historical `v1.1.0` record and
`10.5281/zenodo.20663419` DOI. That DOI is not assigned here to the separately
versioned Tracker software. A prerelease version in this product citation does
not establish journal acceptance, a new black hole or independent recovery of
a known black hole.

`LICENSE.md` and `ACADEMIC_USE.md` are copies of the existing formal BHSM notices.
Read both: the latter grants the stated limited noncommercial scientific
research, verification, peer-review and teaching permissions. This packaging
change does not alter those terms or grant an open-source license. The custom
SPDX identifier `LicenseRef-AllRightsReserved` identifies these nonstandard
terms in Python package metadata. CFF 1.2 uses `license-url` for a nonstandard
license, so the software citation links to the immutable formal notice. Both
complete notices accompany the distribution.

The two license files are explicitly declared in `pyproject.toml`. A PEP 639
capable build backend, `setuptools>=77.0.3`, is required. A normal isolated build
resolves that build requirement; an offline build must provide it in advance.
Wheel installations do not require setuptools at runtime. The existing
Python requirement remains `>=3.11`.

The source archive retains the researcher guides, launcher and helper sources,
research protocols and metadata, and test support files. Original observations
remain in their separately documented source packs. Experimental research
scripts still require their declared inputs, prospective freezes and execution
admissions; installing or inspecting the distribution does not run them.

The standard SDIST is compact: it includes the portable cadence kit and public
evidence manifests/helpers, but omits the three large numbered evidence parts.
The full optional public evidence is retained in the
[formal BHSM source tree](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/tree/main/products/blackhole_tracker/research/validation_20261024/evidence_public_v2)
at `products/blackhole_tracker/research/validation_20261024/evidence_public_v2/`.
Use the reviewed commit identified by the release record. Obtain its three
`BHSM_Calibration_PUBLIC_Content_v1.tar.xz.part001` through `.part003` files
separately; installation never downloads them. The complete local researcher
package retains these parts too. Original observations and native-brightness
prepared parents remain excluded from this public evidence.

From an unpacked product source directory, verify and assemble those external
parts using the included standard-library helper. Replace `FORMAL_CHECKOUT` with
the reviewed BHSM checkout and choose new output/receipt paths:

```text
python -I -B research/validation_20261024/evidence_public_v2/join_public_evidence_v1.py --manifest research/validation_20261024/evidence_public_v2/PUBLIC_PARTS_MANIFEST_v1.json --manifest-sha256 2fad7609abd8b3fff638b4db9799be84be779f14902075faafab25508c0bfae9 --parts-root FORMAL_CHECKOUT/products/blackhole_tracker/research/validation_20261024/evidence_public_v2 --output NEW_PUBLIC.tar.xz --receipt NEW_JOIN_RECEIPT.json
```

The assembled archive must contain exactly 119,420,524 bytes with SHA256
`91f501317821e937d22d52fbea20130995911ed2f1562409b073fc900fa7710e`.
Omit `--output` to verify without writing it. The included
`README_PUBLIC_RESEARCHER_v3.txt` gives normalized-payload verification and exact
restoration commands and their runtime limits. Content integrity does not
establish scientific calibration or clear the publication hold. Neither the
assembled archive, local delivery ZIP nor the private LOCAL transport belongs
in the routine SDIST or Museum download tree.

Build the source archive and then its wheel, without running scientific fits:

```text
python -m build --outdir /absolute/path/to/distributions
python scripts/check_distribution_metadata.py --wheel /absolute/path/to/distributions/bhsm_blackhole_tracker-VERSION-py3-none-any.whl --sdist /absolute/path/to/distributions/bhsm_blackhole_tracker-VERSION.tar.gz --output /absolute/path/to/metadata-check.json
```

Run these commands from the product directory and replace `VERSION` with the
version in `pyproject.toml`. The check compares each embedded legal document
byte-for-byte with its source copy, checks installed citation content and
metadata, and verifies all wheel RECORD hashes and sizes. It also checks the
source archive rather than assuming it contains the same files as the wheel.
Cross-platform checkouts may use different line endings; each archive must
preserve the exact notice bytes supplied to its own build.

The metadata follows the [PyPA license-file guidance](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#license-and-license-files)
and the [CFF 1.2 schema](https://github.com/citation-file-format/citation-file-format/blob/1.2.0/schema.json).
