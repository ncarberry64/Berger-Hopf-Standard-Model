# BHSM 1.0 definition of done

## Internal finish line

BHSM 1.0 is internally release complete when every quantity in its official
prediction and benchmark set is derived from one frozen parent action and
one frozen input ledger; all variational, operator, normalization, scale,
and observable maps required for those quantities are closed; the finite
declared Standard Model benchmark suite is reproducible; novel predictions
and falsification criteria are frozen; and no open release blocker can
change a headline equation, coefficient, particle assignment, benchmark,
prediction, or completion claim.

Peer review, institutional endorsement, citation count, and future
experimental confirmation are external validation stages. They are not
internal completion gates.

## Tier A — BHSM Core Complete

Tier A requires:

- one parent action for every claimed sector;
- complete configurations and variational domains;
- correct gauge and fermion structure;
- anomaly consistency and generation structure;
- charged and neutral current structure;
- mathematically valid operators and reductions;
- closure of every dimensionless headline relation;
- every dimensionless coefficient used by an official prediction is either
  derived or explicitly typed as an unfitted independent theory input;
- no independent input is advertised as a BHSM prediction.

The only permitted Tier-A verdict is `BHSM_CORE_COMPLETE`.

Current status: **blocked**. The parent-action, sector-domain, charged
hierarchy, charged-lepton, CKM, neutrino, gauge, boundary
measure, and retained scalar/topographic dependencies are not all closed.
The scalar quartic is an explicit independent input to a parameterized
theory; selecting it is required only for a parameter-free extension.

## Tier B — BHSM Physical Complete

Tier B requires Tier A plus:

- canonical four-dimensional normalization;
- physical scale bridge;
- physical observable map;
- scheme classification for masses, couplings, and mixing quantities;
- no hidden retuning;
- representative established-physics benchmarks.

Allowed verdicts are
`BHSM_PHYSICAL_COMPLETE_ACTION_DERIVED_SCALE` or
`BHSM_PHYSICAL_COMPLETE_ONE_UNIVERSAL_SCALE_CALIBRATION`.

One universal dimensionful calibration is permitted only if:

1. all dimensionless structure is independently derived;
2. exactly one universal scale remains;
3. it is common to all sectors;
4. it is explicitly labeled as calibration;
5. the calibrated quantity is not called a prediction;
6. no dimensionless coefficient is fitted;
7. no sector-specific retuning occurs.

Current status: **not eligible because Tier A is blocked**.

## Tier C — Internally Complete / External Review Ready

Tier C requires Tier B plus:

- a frozen finite benchmark suite;
- frozen novel predictions;
- explicit falsification criteria;
- clean-environment reproduction;
- deterministic artifacts;
- complete derivation manuscript;
- synchronized status and claim ledgers;
- a public release package;
- no remaining release blocker.

The sole Tier-C verdict is `BHSM_1_0_RELEASE_COMPLETE`.

Current status: **not eligible because Tier B is blocked**.

## Six cumulative gates

| Gate | Required result | Current status |
| --- | --- | --- |
| G1 Parent action | every retained sector attached to one frozen action with coefficient provenance | blocked |
| G2 Mathematical legitimacy | valid domains, variations, boundaries, gauges, adjoints, kernels, inverses, and needed nonlinear reductions | partial |
| G3 Standard Model structure | every retained structural claim derived or removed | blocked |
| G4 Parameter and scale closure | every dimensionless prediction derived; scale action-derived or one transparent universal calibration | blocked |
| G5 Finite validation and prediction set | typed benchmark suite, novel predictions, and falsification criteria frozen | downstream blocked |
| G6 Reproducibility and release | clean regeneration of headline artifacts and manuscript | partial/downstream |

The machine-readable gate and dependency records are:

- `artifacts/BHSM_1_0_completion_gate.json`;
- `artifacts/BHSM_release_blocker_DAG.json`;
- `artifacts/BHSM_scope_relevance_registry.json`.

## Release-relevance firewall

An open item is release blocking only if resolving it can materially change:

1. a parent-action term or coefficient;
2. an admissible field or variational domain;
3. a representation, charge, generation, or particle assignment;
4. a canonical dimensionless parameter;
5. the physical scale or observable map;
6. an official benchmark;
7. an official novel prediction;
8. a falsification criterion;
9. reproducibility of a headline result;
10. the truth of a BHSM 1.0 claim.

Every release blocker must name the affected headline deliverable and its
dependency path. Everything else belongs in
`BHSM_POST_1_0_RESEARCH_BACKLOG.md`.

## Fixed-h exact branch

The exact neighboring D0 branch cancellation is

\[
\lambda_5^{\rm branch}=-18.1974927890349085,
\]

whereas the quartic minimum requires

\[
\lambda_5>-13.95809839182684.
\]

Therefore the cancellation point lies in the quartic-maximum region. The
exact-branch obstruction is a completed scientific result, not a release
requirement. The reduced effective family is the BHSM 1.0 local scalar
object. Higher-order work at the unselected cancellation point is post-1.0.

## Current critical path

The next highest-upstream release blocker is
`RB-01_UNIFIED_PARENT_ACTION_PROVENANCE`. The v6.30.8 dependency audit
reclassifies `RB-02_SCALAR_QUARTIC_INVARIANT_SELECTION` as a
`PARAMETER_FREE_EXTENSION_BLOCKER`: `lambda5` is an explicit independent
theory input, is not predicted, and is absent from every frozen-output
computation path.

## Current exact verdict

`BHSM_SCALAR_QUARTIC_PARAMETERIZED_NOT_PREDICTED`

## v7.0 RB-01 reconciliation

The complete action attempt localizes RB-01 to the missing
`COVARIANT_BULK_BOUNDARY_REDUCTION_FUNCTOR`. Levelwise actions and finite
typed inputs are insufficient for Tier A without the functor that maps
fields, measures, domains, coefficients, and Hessians across dimensions.

Tier A remains blocked; Tiers B/C remain ineligible. The current exact
verdict superseding the v6.30.8 campaign verdict is:

`BHSM_UNIFIED_PARENT_ACTION_BLOCKED_BY_MISSING_COVARIANT_BULK_BOUNDARY_REDUCTION_FUNCTOR_SOURCE`
