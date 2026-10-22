# Hopf-charge bounds and state-dependent light transfer

Author review draft for MDPI Galaxies, Strong Gravitational Lens Modeling.
Norman P. Carberry. No journal submission is authorized or performed here.

The central new result is a sharp Hopf-charge bound for the stationary-nodal
degree-two preparations used by the recovered angular-lensing experiment:
at least half the normalized squared amplitude is Hopf charged, and a
Hopf-fibre ray requires a pure charged preparation. The fixed-radius Berger
Dirichlet susceptibility follows exactly. An auxiliary free-scalar spectral
action gives a nodal-persistence rigidity theorem; it is distinct from the
round cosmological R1 application.

The calculation also opens independent angular histories of the recovered
conditional six-state R1 action and evaluates their ordered-transfer
rotation. Established lensing identities show why a raw antisymmetric
strong-lens Jacobian does not identify an observable signal without source
and lens calibration. Read RESULT_STATEMENT.md before interpreting numbers.

Files:

- manuscript/main.pdf and main.tex: new focused draft and complete derivation.
- provenance/RECOVERY_MAP.md: compact recovery, sources, route decision.
- provenance/: detailed bounded recovery and primary literature audits.
- code/rotation_response.py and results/rotation_response.json: full 6x6 response.
- review/: independent AI-assisted checks, proof scripts and skeptical review.
- LAY_REPORT.md: what has and has not been established.
- ../bhsm_angular_lensing_20261021/: byte-preserved recovered starting package.

The starting package was recovered from Downloads, not PR #23. Its original
PDF, failure/status flags, vendor source and saved results are preserved.
Replay logs made during recovery live separately in the recovery output.

## Reproduce offline

Use Python with the versions in requirements.txt (the recorded execution
versions). From this directory:

    python scripts/reproduce.py

The command verifies original provider hashes, runs the geometric proof checks,
recomputes the R1 kernel and independent matrix-ODE controls, and regenerates
figures/tables. No observation, network data, credentials or fitted amplitude
is read. Both sibling paper directories are included in the release ZIP.

Build from manuscript/ with:

    latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex

Existing repository gates are recorded separately in VALIDATION.md.
The manuscript uses a generic article layout for author review; it is not a
journal submission. Funding, conflicts and final scientific claims require
author review before any later submission. No target submission date is set.
