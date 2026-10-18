# Windows checkout and museum source-query repairs

The Institutional onboarding run 39137328724 checked the PR #465 merge
`1a2d83085b049168e3f530aa33a7071c813e6d08` (research head
`7fc4d8109ab25d4683e325f1bf896869d9ef960c`, base
`00614fa0d479a2de78460ca061cc5304cdb610cf`). Two engineering failures occurred:

- Windows job 117704404175 failed during checkout with `Filename too long`.
  A Windows-only step now enables Git long-path handling before checkout on
  the disposable runner. Physical paths, assertions and tolerances are unchanged.
- Museum job 117704403978 failed when the source-tracking test captured the
  entire `git ls-files -z` output and exceeded Node's default subprocess buffer.
  It now requests the distinct cited paths with literal pathspecs and an option
  separator. Every existing citation, path-safety and file-access assertion is
  preserved; an empty citation set fails before Git is invoked.

The museum test and its imported modules are present on the compatible base
tree, but the test is absent at the research head. These repairs are therefore
based on the complete existing main tree; the research branch is not reset,
rebased or supplemented with an incomplete museum feature. The source blobs
reviewed before modification are:

| File | Git blob |
| --- | --- |
| `.github/workflows/institutional.yml` | `77aa78cc5c710bd97171e24bb43dc5a6bf00ca38` |
| `museum/scripts/test-physics-questions.mjs` | `be94a4d25dc1fcbe3d09b37cfea81bdce6e126cd` |

The continuation's loose `CI_FINDINGS.md` and `CODEX_TASK.txt` were available
locally. Its described patch files and harness were absent, so equivalent
changes were reconstructed against the exact blobs above and independently
checked. This is not a claim to have executed the unavailable supplied harness.

`python -m pytest -q tests/test_ci_source_tracking.py` executes the museum's
actual assertion body against a scratch Git index with 14,006 tracked paths
and over 1 MiB of unrestricted output. It reproduces the original ENOBUFS
failure, accepts exact tracked citations and literal brackets, and rejects
untracked paths, wildcard substitutions, missing files, parent traversal and
empty citations. Duplicate citations also pass. The fixture never modifies
the research checkout or its Git index.

Local validation used Node 24.19.0, Git for Windows 2.54.0 and Python 3.14.
The full museum science suite passed all 42 tests, TypeScript checking and
the complete Pages build passed, and 20 focused/affected pytest tests passed.
The forbidden-claim, status, frozen-integrity, precision and public-readiness
audits passed; the recorded precision delta remains `1.066e-14 <= 1e-13`.
The new source-query controls are included in the portable-core CI test command.

An initial concurrent build/pytest invocation passed all 20 assertions but
exited with failure when the repository test guard detected four generated
asset writes from the build. After the build finished, only its five known
generated assets were restored to their clean initial checkout bytes; the
focused pytest command then passed with exit zero and no guard warning. The
research checkout was untouched throughout. Hosted CI results must be checked
on the published repair PR and the later PR #465 merge tree.

The bounded query depends on the citation list's size rather than the complete
research archive. Arbitrarily large future citation sets may require batching
or streaming. Git long-path support does not certify every downstream Windows
tool. Local controls do not substitute for a fresh hosted Windows checkout or
the actual PR merge-tree CI. No scientific prediction, calibration, archive,
physical admission threshold or unresolved physical nonpass is changed.
