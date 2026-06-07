# BHSM v1.3 H_T Spectrum Plan

Branch: `bhsm-v1.3-ht-spectrum`

Objective: attack the largest remaining Standard-Model-equivalence blocker:
the full twisted Dirac / `H_T` spectrum.

This plan does not change frozen v1.0/v1.1 predictions, constants, tolerances,
mode ledgers, or branch outputs.

## Current H_T Status

The current repository contains a finite-basis and lower-bound program for the
topographic stability operator `H_T`. The no-extra-light-state theorem remains
open.

Current status to preserve:

- Level 2 finite-basis `H_T` proxy exists.
- Spectral lower-bound scaffold exists.
- Basis-convergence audit exists.
- Formal sufficient theorem scaffold exists.
- `theorem_complete` remains `False`.

## Existing Proxy / Scaffold Modules

Relevant modules already present:

- `src/twisted_dirac.py`
- `src/ht_operator.py`
- `src/spectral_gap.py`
- `src/spectral_bounds.py`
- `src/positivity.py`
- `src/theorem_scaffold.py`
- `src/scalar_decoupling.py`

Relevant notebooks and reports:

- `notebooks/06_twisted_dirac_ht_spectrum.ipynb`
- `notebooks/09_twisted_dirac_level2_operator.ipynb`
- `notebooks/10_spectral_lower_bound_program.ipynb`
- `notebooks/11_basis_convergence_ht_bound.ipynb`
- `theory/ht_no_extra_light_theorem_scaffold.md`
- `theory/proof_gap_report.md`

## Required Mathematical Target

The main spectral target is:

```text
H_T|_{H_perp} >= (4 pi^2 v)^2
```

Equivalently, in the dimensionless Hopf-gap normalization already used in the
repository:

```text
H_T|_{H_perp} >= mu_H = 64 pi^5
```

## Required Zero-Mode Target

The protected-family target is:

```text
dim ker D_twist = 3
```

The complement `H_perp` must exclude exactly these protected chiral zero modes
and must not contain additional light mirror or scalar/topographic states.

## Near-Term Goals

1. Derive a Berger twisted Dirac eigenvalue formula or rigorous lower bound.
2. Separate protected zero modes from the complement without relying only on
   finite-basis projection.
3. Prove or bound the first complement eigenvalue of the twisted Dirac square.
4. Integrate the positive-semidefinite curvature/profile condition:

```text
V_profile|_{H_perp} >= 0
```

5. Compare the analytic or semi-analytic lower bound to the current Level 2
   finite-basis result.
6. Keep all failures explicit and preserve `theorem_complete=False` until the
   full assumptions are proven.

## Non-Goals

- No retuning of `a`, `S`, mode ledgers, tolerances, `Z_virt`, or frozen
  predictions.
- No changes to `BHSM_BARE_V1` or `BHSM_DRESSED_V1_CANDIDATE`.
- No claim that the `H_T` theorem is complete unless the full analytic or
  sufficient spectral proof is implemented.
- No replacement of the v1.1 public release package.

## First Technical Task

Start with a representation-aware symbolic/analytic inventory of the Level 2
twisted Dirac matrix terms:

- diagonal Berger/spin-connection contribution;
- Hopf twist contribution;
- boundary/chirality contribution;
- sector-coupling terms;
- protected zero-mode projection;
- PSD profile contribution.

Then classify which terms admit direct analytic lower bounds and which still
depend on finite-basis estimates.
