# BHSM external pseudo-blind calibration report — 2026-09-02

## Authority and provenance

This file records an external, comparison-only diagnostic snapshot supplied on
2026-09-02.  Its source text has SHA-256
`E784E09C42282E6CFF59CF935CB718FF793D354606A928C5128DE5BF75D713DF`.
It was received while the repository was at commit
`a3244dc26f2415e06ac8ba79a36c4da1375a79f8` on the existing
`codex/g7-green-correlated-all` worktree.

The numerical references below are user-supplied diagnostic markers.  They
are not promoted here as independently sourced experimental determinations,
and they are not inputs to any action, branch, trajectory, spectrum, mode,
normalization, scale, dressing, transport, or prediction calculation.

## Prediction firewall

The required order is:

```text
DERIVATION FIRST -> FREEZE -> EXTERNAL COMPARISON
```

Until the action-owned physical background is frozen, this report must not be
imported by scientific source code, materializers, solvers, selectors, or
certificate scripts.  In particular, the values in this report must not:

- fit or modify the Gate-7 center, branch, action, trajectory, spectrum, or
  mode ledger;
- select coefficients, carriers, modes, signs, exponents, normalizations,
  physical scales, renormalization prescriptions, or mathematically allowed
  branches;
- introduce observable-specific correction factors or additional empirical
  inputs; or
- rewrite historical frozen prediction artifacts or their hashes.

At intake, Gate 7 remains `ACTIVE_NOT_CLOSED`.  The current critical path is
the same-center outward `Y,Z1,Z2` construction in one causal 74-dimensional
norm.  The in-progress correlated central Green-scalar certificate is part of
that pre-existing mathematical path and has no dependency on this report.

## External diagnostic snapshot

| Sector / observable | Frozen or historical BHSM value | External marker | Intake observation |
|---|---:|---:|---|
| CKM `gamma` | approximately `64.6 deg` | mid-60-degree region | encouraging |
| `|Vtd/Vts|` | approximately `0.2084` | approximately `0.207` | ratio substantially closer than individual magnitudes |
| `alpha_s` | `0.118208` | approximately `0.1180` | encouraging |
| `sin^2(theta_W)` | `0.230769` | approximately `0.23122` in MS scheme | encouraging; scheme transport remains relevant |
| electroweak `v` | `246.170 GeV` | approximately `246.22 GeV` | encouraging |
| `m_mu/m_tau` | `0.0600745` | approximately `0.0594635` | encouraging |
| neutrino `sin^2(theta12)` | `0.311441` | approximately `0.3088` | encouraging |
| neutrino `sin^2(theta13)` | `0.0218921` | approximately `0.02215` | encouraging |
| neutrino `Delta m^2_21 / Delta m^2_31` | `0.0291894` | approximately `0.0298` | high-value dimensionless marker |
| `m_e/m_tau` | historical value implicit in the reported residual | external marker implicit | approximately `+3.4%` residual |
| individual `|Vtd|`, `|Vts|` | historical values implicit in the reported residual | external markers implicit | each previously approximately `+4%` while their ratio is better |
| Higgs zeroth-order mass screen | `123.085 GeV` | approximately `125.20 GeV` | approximately `-1.7%`; not a dressed pole |
| CKM `beta` / `sin(2 beta)` | historical frozen result | external marker implicit | modest but significant low-side residual |
| neutrino `sin^2(theta23)` | `0.543784` | normal-ordering best-fit marker near `0.470` | octant-sensitive; presently broad allowed region |

The intake pattern suggests, but does not establish, that dimensionless ratios
and geometric hierarchies are more stable than several absolute or
precision-normalized quantities.  That statement is a hypothesis to test
after freeze, not a premise available to the derivation.

## Post-Gate-7 audit ledger

All rows remain `DEFERRED_UNTIL_PHYSICAL_BACKGROUND_FREEZE`.

1. Recompute the CKM sector from the action-owned background.  Test whether a
   common few-percent `Vtd`/`Vts` normalization shift changes while the
   successful ratio remains stable.
2. Recompute the charged-lepton hierarchy.  Determine whether `mu/tau` and
   `electron/tau` move coherently or independently.
3. Propagate the independently action-derived electroweak normalization and
   re-evaluate `sin^2(theta_W)`, `alpha_s`, and `v` without empirical
   selection.
4. Replace the zeroth-order Higgs screen only when the action-derived dressed
   physical pole exists.  Do not tune that pole to `125.20 GeV`.
5. Recompute neutrino propagation.  Preserve `sin^2(theta23)=0.543784` as a
   sentinel unless an independently derived action correction changes it, and
   explicitly record the selected octant.
6. Recompute `Delta m^2_21 / Delta m^2_31` before attaching an absolute
   neutrino scale.

For every row, the future audit record must identify the independently derived
change, freeze its provenance and hashes, and only then calculate the external
residual movement.

## Diagnostic classification to be tested

After freeze, classify each observable as one of:

1. stable invariant geometric ratio;
2. common-normalization or physical-scale attachment;
3. RG or scheme transport;
4. action-derived self-energy or dressing;
5. experimentally ambiguous; or
6. genuine structural failure.

No classification is considered established merely because it would explain
the current residual pattern.

## Success and adverse criteria

A meaningful positive outcome requires independently demanded completion
corrections to improve multiple residuals while preserving successful ratios,
without observable-specific tuning or an increase in independent empirical
inputs.  One correction improving several correlated residuals is especially
informative.

The calibration must be flagged adverse if measured values are needed to
select branches, separate empirical corrections are needed for individual
observables, successful frozen ratios are destroyed, free parameters
proliferate, several independent sectors move naturally farther from the
external markers, or prediction outputs become dependent on this dataset.

## Current assessment

The snapshot supports continued mathematical development but does not
experimentally validate BHSM.  The residuals remain untouched sentinels.
No post-Gate-7 comparison has been executed by this report.
