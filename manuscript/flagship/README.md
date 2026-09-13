# Current flagship manuscript

`BHSM_flagship.tex` is the working manuscript for the current completion
campaign. It is separate from the frozen historical manuscripts and is not
ready for journal submission. It currently reports the AE3 carrier, the
complete midpoint chain-rule prescription, stored-solve error methodology,
and the completed 371-node scalar certificate. The September 7 revision adds
the photon diagnostic scope correction, the retained EC stationary-domain
obstruction, and the conditional lepton sum rule with its missing physical
dressing. Photon values are generated from the validated audit report after
its source hashes are checked. All physical-completion
claims remain gated by the definition of done. The September 13 revision
adds the paired local midpoint/endpoint refinement, its limited scope, and
the exact two-radius self-map and derivative conditions. Its local numbers
come from the reviewed artifact at revision `68a18555`. The separate
`generated/stored_margin_source.json` supplies all stored-polynomial inputs,
exact rational margins and original raw source hashes; the generator replays
its self-map inequalities exactly. The complete physical certification margin
remains unknown.

A subsequent saved-data supplement, `column_box_obstruction.md`, proves that
the current independent-coordinate right-column enclosure permits normalized
gain at least 54.843547458166. It therefore cannot by itself certify
contraction. This is a limitation of the Cartesian relaxation, not physical
noncontraction. The supplied JSON contains every exact arithmetic operand;
`python manuscript/flagship/replay_column_box_obstruction.py` verifies the
proof with the standard library. This supplement accompanies the ten-page
PDF; it is not a new physical derivative calculation or a completion claim.

Run `python manuscript/flagship/build_evidence.py` from the repository root,
and `python manuscript/flagship/build_local_evidence.py`, then compile
`BHSM_flagship.tex` twice with pdfLaTeX from this directory.
`generated/` contains deterministic figure and numeric inputs. The generator
verifies the source certificate, NPZ hash, immutable Git revision, and equality
with the plotted Museum dataset before creating these inputs.

For byte-identical PDF reproduction, set `SOURCE_DATE_EPOCH=1788739200`
and `FORCE_SOURCE_DATE=1`, use job name `BHSM_flagship_working_manuscript`,
and the repository's `output/pdf` output directory. The earlier draft PDF is
preserved; the September 13 evidence update uses job name
`BHSM_flagship_numerical_update_20260913`. The retained TeX environment
is pdfTeX 1.40.28 / MiKTeX 25.12; another distribution may typeset identically
without producing the same PDF bytes.

The September 13 PDF has ten pages. The affected pages were rendered and
visually checked; the numerical inputs and final PDF each reproduced byte
for byte. The final LaTeX log has no overfull boxes or undefined references.
Existing scalar and photon inputs were reused without rerunning their science.

The final submission version requires the completed scientific certificates,
an observable classification matrix, full derivation and comparison sections
supported by those results, synchronized status and claim ledgers, and final
journal formatting and author declarations. No missing physical output should
be filled with a simulation, historical fit, or unproved assertion.
