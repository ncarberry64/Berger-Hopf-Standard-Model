# Manuscript Generation

Primary final-paper files for release `v1.2.0`:

- `manuscript/BHSM_final_paper.md`
- `manuscript/BHSM_final_paper.tex`
- `manuscript/BHSM_final_paper.pdf`

The Markdown manuscript is the human-editable source. The LaTeX file is a
typeset version of the same conservative release package. If a LaTeX toolchain
is available, rebuild the PDF from the `manuscript/` directory:

```powershell
pdflatex -interaction=nonstopmode -halt-on-error BHSM_final_paper.tex
pdflatex -interaction=nonstopmode -halt-on-error BHSM_final_paper.tex
```

The paper uses repository ledgers and frozen outputs. It must not be edited to
claim experimental confirmation, QCD confinement, quantum gravity, or a final
replacement of the Standard Model.
