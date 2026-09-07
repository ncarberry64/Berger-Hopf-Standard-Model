# Current flagship manuscript

`BHSM_flagship.tex` is the working manuscript for the current completion
campaign. It is separate from the frozen historical manuscripts and is not
ready for journal submission. It currently reports the AE3 carrier, the
complete midpoint chain-rule prescription, stored-solve error methodology,
and the completed 371-node scalar certificate. All physical-completion
claims remain gated by the definition of done.

Run `python manuscript/flagship/build_evidence.py` from the repository root,
then compile `BHSM_flagship.tex` twice with pdfLaTeX from this directory.
`generated/` contains deterministic figure and numeric inputs. The generator
verifies the source certificate, NPZ hash, immutable Git revision, and equality
with the plotted Museum dataset before creating these inputs.

For byte-identical PDF reproduction, set `SOURCE_DATE_EPOCH=1788739200`
and `FORCE_SOURCE_DATE=1`, use job name `BHSM_flagship_working_manuscript`,
and the repository's `output/pdf` output directory. The checked-in draft PDF
matches the visually inspected six-page output. The retained TeX environment
is pdfTeX 1.40.28 / MiKTeX 25.12; another distribution may typeset identically
without producing the same PDF bytes.

The final submission version requires the completed scientific certificates,
an observable classification matrix, full derivation and comparison sections
supported by those results, synchronized status and claim ledgers, and final
journal formatting and author declarations. No missing physical output should
be filled with a simulation, historical fit, or unproved assertion.
