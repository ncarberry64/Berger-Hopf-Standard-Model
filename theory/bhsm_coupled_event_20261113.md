# Coupled-event mass-gap investigation: corrected normal equation

**13 November 2026. Claim class: conditional initial-data construction and
restricted action identities. Physical completion and a physical mass gap
remain open.** This checkpoint changes no official prediction, acceptance
gate, frozen forecast, or scientific source module.

The material-advection momentum term changes the interpretation of the earlier
normal-force test. A mixed electric/magnetic initial construction closes the
retained twelve lapse projections and has zero **Maxwell contribution** to the
full normal Euler equation. Replacing the assumed parent source by a fresh
charged preparation and scalar response changes those targets. These pieces
have not been solved together as a physical BHSM history.

## Correction to the partial normal-force interpretation

The earlier restricted calculation used the partial derivative `L_x`. The full
normal Euler row is `L_x - d_t L_U`. Even when `L_U=0` at an instant, its time
derivative need not vanish. The moving-cap geometry supplies the central
electric combination `v - (beta + y U) p_chi`. At static geometry and compact
interior support, field evolution cancels the moving-chart terms, leaving

```text
F_x = (1/32) integral ell_x|chi [R v^2 - R p_chi^2 - k^2 p^2/R] dchi.
```

Here the radial factor `R` inside the integral is the source radial metric
function. The global radius is one at this event. The old partial-derivative
separating certificate remains evidence about its own system; it is not an
obstruction to the full normal Euler equation. The historical files are
preserved rather than rewritten.

The source action owners are pinned on the independent muon continuation at
[`78bb39fe86d7c0652ae049379677c291fd04dd05`](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/commit/78bb39fe86d7c0652ae049379677c291fd04dd05):
[moving-cap geometry](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/blob/78bb39fe86d7c0652ae049379677c291fd04dd05/src/bhsm/interface/muon_holomorphic_normal_geometry.py),
[Maxwell action](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/blob/78bb39fe86d7c0652ae049379677c291fd04dd05/src/bhsm/interface/muon_parent_maxwell_full_weak.py), and
[mean causal action](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/blob/78bb39fe86d7c0652ae049379677c291fd04dd05/src/bhsm/interface/muon_parent_mean_causal_action.py).
This export does not merge that branch or identify it with the separate PR #465.

## Reproduced finite initial data

The event has `x=-0.001995427003365648`, global `R=C=N=1`, and
`beta=U=qdot=0`. A constant-angular central HY mode has curl `k=2` and regular
exponent `alpha=1`. Thirteen of fifty compact carrier supports are active.
Disjoint electric and magnetic supports make their own central momentum flux
zero pointwise at this initial event. No future reflecting boundary condition
is imposed, and the magnetic profiles are not stationary Maxwell solutions.

The saved target contains twelve known lapse projections and a zero Maxwell
normal contribution in the prior conditional-parent problem. It does not
include the fresh charged/scalar loads below.

| Quantity | Portable reproduction |
| --- | ---: |
| Electric energy T | 15.768184076346918 |
| Magnetic energy V | 13.497754707124447 |
| Total cap-normalized energy | 29.265938783471363 |
| Maximum retained 12+normal residual | 6.13e-13 |
| Partial material L_x | 42.80663529599068 |
| Direct d_t L_U | 42.80663529597454 |
| Normal contact consistency error | 1.56e-11 |
| Maxwell radius Euler contribution | 42.8885149988062 |

Independent Fourier/Bessel and adaptive quadrature previously gave a retained
residual of `2.2871e-13`. The exported implementation uses direct Gauss-Legendre
quadrature. These are numerical agreement tests, not outward error bounds.

The action's fiber fifth power gives radius weights `R_global^7 T` and
`R_global^5 V`. With `q0=log R_global` and `x=s/R_global`, retaining the
induced velocity contact gives `F_q0=7T-5V-x F_x` at zero geometry rates and
accelerations. The known bulk/eta/FR/sigma contribution is
`5.969760198435043`; its sum with the Maxwell contribution is
`48.858275197240985`. Charged, scalar and exterior/native terms are additional.
The old assumed `h(x)` supplies no justified radius derivative.

## Fresh charged preparation and scalar response

The separately reviewed finite preparation was rebuilt at the same geometry,
using **trial** `H=(0,1)`, the mechanical connection and material `At=0`.
Its sign ranks are 2 positive and 4 negative. High-precision and block-form
checks find a small nonzero electromagnetic current
`-1.1506712693e-19`, with strict retained-input magnitude interval
`[6.8573e-20,3.18231e-19]`. This interval covers specified constant conventions,
not unknown physical input uncertainty. It is not a physical charge prediction.
The finite sign-chart crossing near `x=2.50679515946e-13` prevents carrying
that sign chart uniformly across the crossing; it says nothing about physical
gaplessness.

The prepared source gives `j_x=0.04788975226925122`,
`j_logR|x=6.000048346774097`, and
`j_q0|proper-s=6.000143907278959`. Its full normal equation also contains
`-6.000048346780961 Udot` and the coupled contacts.

At this neutral Higgs axis every scalar velocity has zero electromagnetic
moment-map component. It cannot cancel the retained finite remainder exactly.
The least-squares phase cancels the reachable current projection with
`omega=-78.95872154448457`, phase energy `39.47936077221332`, and residual norm
`4.98255275316845e-20`. The normalized scalar action includes spatial and
potential terms; with the unresolved nonnegative source operand
`P=lambda_H (1-nu_squared_action)^2`, its additional contractions are:

| Scalar quantity | Value |
| --- | --- |
| Energy E_H | 39.49820701277065 + 0.006332422691494 P |
| Lapse action derivative | -E_H |
| Normal force at fixed raw geometry-variation jets | 0.8695063690097925 - 0.000151631451832 P |
| Fixed-x log-radius derivative | 118.4192360760826 - 0.01899726807448135 P |
| Normal-speed inertia increment | E_H |

The full normal Euler includes `-E_H Udot` and coupled contacts. The scalar
amplitude force `78.921029063312 - 0.0253296907659751 lambda_H(1-nu^2)` is a
polar-coordinate variation at fixed phase rate, not fixed Cartesian Hdot.
Fixed-charge elimination uses the negative-energy Routhian. Neither constant
phase momentum nor an evolved scalar solution is assumed established.

These loads invalidate reuse of the bare thirteen-row balance as a combined
solution. Setting an unspecified exterior reaction to their negative would
not derive a physical response. The EM cokernel obstructs this restricted
compensator, not every possible charged completion.

The portable program below reproduces the mixed-field rows only. The charged,
scalar and known-radius numbers are separately reviewed retained results,
documented in the [review extract](../artifacts/bhsm_coupled_event_20261113/retained_review.json).
Their complete preparation machinery and private history are not included in
this export; they are not advertised as independently reproducible from the
portable mixed-field input file alone.

## Regime hypotheses and remaining gates

Excitation is the lowest envelope; an ordinary envelope is not full
encapsulation. Mass can arise through environmental interactions in any of
these regimes. A changing environmental response for the same prepared
internal history is a hypothesis to test. It does not require identical future
evolution. The water/interface/air analogy gives conceptual guidance, not a
universal ordering of coupling strengths or arbitrary numerical coefficients.
This initial interface diagnostic is not three completed regime solutions.

The [assumption ledger](../artifacts/bhsm_coupled_event_20261113/assumptions.json)
records dependencies and falsification tests. Remaining physical gates are
the incoming preparation and independent analytic dual; full sourced Gauss,
metric, scalar and normal equations on one admitted event/bulk domain;
native/heat/state/exterior response and derivatives; physical evolution;
an independently specified matched parent and integrable relative energy
charge; clock/scale calibration; and the complementary physical spectrum.
Parent-subtracted energy is not assumed positive. This provides no physical
mass-gap result or Clay Yang-Mills proof.

## Reproduce the exported calculation

From the repository root with Python and NumPy:

```bash
python audits/bhsm_coupled_event_20261113.py --output result.json
python -m pytest -q tests/test_bhsm_coupled_event_20261113.py
```

The [inputs](../artifacts/bhsm_coupled_event_20261113/inputs.json) contain all
coefficients used by this evaluator and source-relative provenance hashes.
No source producers, empirical masses, or private machine paths are imported.
Tests cover the missing-momentum false failure, amplitude perturbation,
discarded magnetic fields, unresolved radius force, domain rejection and
byte-identical repeated output. [Validation](../artifacts/bhsm_coupled_event_20261113/validation.json)
records the seven passing focused tests. Byte identity is checked on the same
runtime; floating-point bytes need not be identical across NumPy/BLAS builds.
Repository-wide validation and any limited materialization coverage are
reported separately in the PR; focused tests do not certify the whole action.
