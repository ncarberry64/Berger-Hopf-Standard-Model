# Galaxies submission files

The target is the live **Strong Gravitational Lens Modeling** call in *Galaxies*: <https://www.mdpi.com/journal/galaxies/special_issues/50J931CL3Q>. The formal reviewer source is the [BHSM repository](https://github.com/ncarberry64/Berger-Hopf-Standard-Model); Manuscript-Generation is a development workspace.

After compiling and visually reviewing the manuscript, run from this paper directory:

```text
python submission/prepare_submission.py /path/to/submission-files
```

This verifies the exact abstract, the BHSM code citation and the reviewed PDF hash. It prepares the PDF, a focused source ZIP with every manuscript/figure source, the metadata and an explicitly unapproved cover-letter draft. Its receipt checks archive members and hashes. To recompile the focused archive, extract it and run `latexmk -cd -pdf -interaction=nonstopmode -halt-on-error manuscript/main.tex`. The separate complete reviewer archive also includes the runnable product, supporting papers, provenance, tests and receipts.

The current under-200-word abstract, author details, funding/conflict declarations and substantive AI disclosure are prepared. The author has confirmed unpublished journal status, no concurrent consideration and no previous MDPI submission. Final approval of the actual files and applicable publication terms remain with the author during manual submission. No upload, agreement, charge commitment or submission is performed by this script.

The official instructions allow free-format submission, require a cover letter and complete LaTeX ZIP, and cap total files at120MB: <https://www.mdpi.com/journal/galaxies/instructions>. The live call lists1500CHF APC; no waiver, discount, payment or acceptance is assumed. The submission portal is <https://susy.mdpi.com/user/manuscripts/upload>.
