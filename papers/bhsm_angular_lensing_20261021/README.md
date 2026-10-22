# Angular Selection Rules and Time-Delay Relations for Berger–Hopf Lensing in a Closed Cosmology

**New theoretical and computational research paper — 21 October 2026.**

Author review draft for *Galaxies*, “Strong Gravitational Lens Modeling.”
Author: Norman P. Carberry, Independent Researcher, Oconomowoc, Wisconsin, USA.

This package calculates conditional angular light transfer from the full
scalar `n=2` family of a declared closed BHSM/R1 effective realization.
It contains a new manuscript, new angular kernels, a linked shear/time-delay
prediction, a constructive effective-potential correspondence, a restricted
source-redshift contrast, and executable checks. No observational target data
are used.

## Completed scientific result

The normalized spatial family has nine real harmonics: one angular monopole,
three dipoles and five quadrupoles. Each has six physical initial coordinates.
The monopole/dipole sector has no first-order smooth tracefree shear; the
quadrupoles do. A specified quadrupole has a central ray where the scalar
perturbation and its first gradient vanish, but its tidal Hessian does not.

For that nodal preparation, a fixed physical singular isothermal lens, and a
fixed physical source displacement, the computed relative-delay derivative is

```text
delta(Delta t) / Delta t0
    = sqrt(2) [(g_os - g_ol) dot y] cos(2 phi).
```

All three propagation maps use the same initial state. The lens-to-source
coefficient cancels from this particular SIS derivative after both the source
angle and local lens impact are varied correctly.

For the illustrative normalized initial vector
`y=(0,0,0.001,0,0,0)`, a 200 km/s SIS, physical source offset 0.8 kpc, and
H0=67.4 km/s/Mpc, the executed first-order predictions are:

| Lens redshift | Source redshift | Baseline delay, days | Change at phi=0, seconds |
|---:|---:|---:|---:|
| 0.3 | 1.0 | 7.753621449 | -0.353216090 |
| 0.3 | 0.6 | 9.268876035 | -0.123113165 |
| 0.5 | 1.5 | 11.583862635 | -1.163397674 |
| 0.8 | 2.0 | 17.264698902 | -2.871296635 |

A 90-degree source rotation reverses each sign. At 45 degrees the first-order
shift is zero. The 0.001 is a coefficient of an L2-normalized spatial harmonic,
not a uniform 0.1% density perturbation, fitted amplitude or uniquely selected
microscopic state.

The exact effective-potential construction preserves the image equations and
relative times for one source plane. It represents the same retained light
transfer in ordinary lens variables. The two-source contrast excludes only
absorption into one fixed physical quadratic contribution at the main lens;
it does not break general mass-sheet or line-of-sight freedom.

## Read the paper

- `manuscript/main.tex`: root manuscript.
- `manuscript/main.pdf`: built author review draft, when the PDF build is run.
- `docs/RESEARCH_FINDINGS.md`: accessible explanation, claim boundaries and next physical question.
- `theory/ANGULAR_TRANSFER_DERIVATION.md`: detailed mathematical derivation.
- `review/`: separate analytic and computational review notes and receipts.

The draft's funding and competing-interest statements require the author's
confirmation before journal submission. No journal submission has been made.

## Reproduce

The execution environment used Python 3.12.14 and the pinned packages in
`requirements.txt`. Install those packages in an environment of your choice,
then run from this directory:

```bash
python scripts/reproduce.py
```

The replay verifies the immutable inherited inputs, recomputes all numerical
stages, executes the independent checks, and regenerates tables and figures.
Its run receipt records the commands, return codes and key results.
It reads no network data and needs no archive credentials.

Build the manuscript with a standard TeX installation:

```bash
python scripts/build_manuscript.py
```

This requires `latexmk`, `pdflatex`, BibTeX and the packages named in
`manuscript/main.tex`. PDF visual review is a separate human/assistant step;
a successful TeX compilation does not establish physical correctness.

Individual stages, in dependency order:

```bash
python theory/verify_exact_identities.py
python scripts/check_angular_geometry.py
python code/angular_optical_response.py
python code/audit_nodal_angular_geodesic.py
python code/strong_lensing_prediction.py
python code/shared_state_relations.py
python review/check_geometry_identities.py
python review/audit_sis_prediction.py
python scripts/make_figures_and_tables.py
```

Only NumPy, SciPy and Matplotlib are needed for those stages. SymPy, Astropy
and telescope-specific software are not dependencies.

## Scientific scope

- Linear smooth scalar perturbations; paraxial propagation; one weak-field
  thin-lens encounter; nonconjugate propagation vertices.
- Six independent physical anchors per normalized spatial harmonic at z=2.1.
- Generic results are tracefree maps. The complete first-order delay example
  uses the specially declared nodal quadrupole.
- Fixed physical lens and source displacement; fixed measured reference
  redshifts; continued noncaustic SIS image branches.
- Finite linear-map completions are derivative checks, not a nonlinear BHSM
  solution or a prediction of a second-order timing shift at the angular null.
- No unique physical state selection, observed signal, observational
  significance, microscopic preparation, or global stability theorem.
- Numerical residuals assess the implemented equations. They are not error
  bars on unknown physics or observational uncertainty.

## What is inherited and why

`code/vendor_original/` contains exact relevant action, background and anchor
provider files from `ncarberry64/Manuscript-Generation` commit
`06cf7c1b85d6605bfee0cc0d07fb2af86a66cae9`. Their Git blob identities, SHA-256
hashes and source URLs are in `code/vendor_original/SOURCE_MANIFEST.json`.
The historical prediction manifest is retained byte-for-byte; **only
`background_R1` is consumed**. Its historical observational fields do not
enter this work. Some import dependencies have broader old capabilities;
only the documented state conversion/provider functions are invoked here.

The angular calculation, lens response, consistency contrast and manuscript
are separate from the previous observational sprints. The source includes
the inherited conditional effective system because it supplies the temporal
responses; it does not inherit claims of physical or observational validation.

## Numerical evidence

The main execution gives maximum absolute differences of 1.45e-14 between
Green quadrature and a forced Jacobi ODE, 1.47e-13 under temporal refinement,
and 2.08e-15 between the original angular-ray derivative and its kernel.
Direct image-solving derivatives agree with the analytic delay law to
7.12e-12 in the dimensionless derivative; an independent SI baseline agrees
to 6.24e-16 relative. See `artifacts/` and `review/` for definitions and
complete receipts. Source hashes and a release file manifest make the
delivered calculation auditable.
