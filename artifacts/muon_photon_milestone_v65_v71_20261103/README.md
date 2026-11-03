# Muon photon-source and boundary reductions, v65-v71

This is a reproducible **conditional mathematical milestone**, not a physical
muon prediction. The physical current, event/reconnection solution, full
native/relative remainder, Pauli anomaly and total uncertainty remain open.
The original physical guard is 2e-10; numerical method checks use 2e-11.
The admitted temporal20 t=2^-9 point is an initializer for these coefficient
calculations, not an admitted complete physical Cauchy state.

| Stage | Established component | Still required |
| --- | --- | --- |
| v65 | Eight-source photon/current coefficients | Complete projected current |
| v66 | Radial Gauss return and source-flux identities | Inherited flux and full bulk/boundary load |
| v67 | Propagated photon dual and diagonal normal-pair charge insertion | Dressed independent traces |
| v68 | Exact adopted pair normalization and weighted flux estimates | Physical columns and complete source norm |
| v69 | Weighted pole/current bound and weak native-source formulation | Native kernel/trace regularity and physical entering/time jets |
| v70 | Local radial weak-source cancellation and ordered transport response | Angular and actual pole/event contacts |
| v71 | Photon scalar seam cancellation; evaluated angular connection insertion | Complete same-domain native/relative boundary contraction |

Each stage contains its full derivation in `REPORT.md`, its unchanged final
coefficient producer and tests, frozen numerical inputs, source provenance
and excerpts, and one final `expected_result.json`. The two serialization
helpers were extracted unchanged from the original preparation scripts.
No extraction of old worktrees or reconstruction of historical campaigns
is needed. Original local checkpoints remain immutable.

`release_manifest.json` records every copied input/source hash, the original
path and the exact helper transformation. Some source ownership predates
the published parent commit and is represented by frozen data, excerpts and
hashes; this package does not claim those ancestor artifacts were all already
public. The adopted preparation remains 500 MeV beams, 100 fm widths,
centers at +/-1000 fm, unpolarized exact pair, and no extra radiation relative
to the inherited reference. No new occupations or boundary-selection rule
are introduced.

## Reproduce

Dependencies: Python 3.14, NumPy 2.4.6 and pytest 9.0.3 were used for the
verified reproduction. Use trusted package installations. The runner requires
`-I -S` and explicit package directories, disables startup path processing,
pytest plugins and conftest, checks import origins, and runs one stage at a
time. It makes no network calls or installations.

From this directory:

```text
python -I -S reproduce.py --site-packages <trusted-site-packages> --out <fresh-output-directory>
```

Repeat `--site-packages` if NumPy and pytest occupy separate trusted roots.
The runner verifies the release hashes, reproduces each final result,
checks it byte-for-byte against the saved JSON, and runs all 45 tests.
Generated matrix arrays and local logs go to the fresh output directory;
they are deliberately not duplicated in Git. Only frozen input arrays are
shipped. Run the command again with another fresh output directory if an
independent byte comparison is wanted.

Machine-specific runtime receipts, interruption logs, original private path
metadata, duplicate runs and superseded generated arrays are excluded from
this public copy. The reports retain the scientific correction history and
limits; exclusion of old outputs does not erase them from local archives.
No measured anomaly was fitted, no physical tolerance was changed, and no
method defect is reported as physical uncertainty.
