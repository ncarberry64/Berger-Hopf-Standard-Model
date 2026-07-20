# Rare-B A_FB Zero Forward-Prediction Kill Screen v5.0

Sprint: `bhsm-rare-b-afb-zero-forward-prediction-v5-0`

Primary verdict: `RARE_B_AFB_ZERO_PREDICTION_BLOCKED`

Secondary verdict: `RARE_B_MICROPLATEAU_NODE_PREDICTION_BLOCKED`

## Scope

This sprint tests whether existing BHSM artifacts can produce a specific, falsifiable, pre-registered rare-B prediction for the `A_FB(q^2)` zero-crossing point in:

```text
B0 -> K*0 mu+ mu-
```

It does not fit existing flavor-anomaly data, does not tune to published `B0 -> K*0 mu+ mu-` measurements, and does not reopen the blocked v4.5-v4.9 gauge-coupling normalization chain.

## Observable Interface

`A_FB(q^2)`:
forward-backward asymmetry in the lepton angular distribution.

`q^2`:
squared dimuon invariant mass, conventionally reported in `GeV^2`.

`q0^2`:
the value of `q^2` where `A_FB` changes sign, so `A_FB(q0^2)=0`.

`P'_5`:
optimized angular observable in `B -> K* l l` angular analyses.

`dB/dq^2`:
differential branching fraction.

Important:
This sprint does not compute a Standard Model global fit. It only defines the BHSM forward-prediction kill screen and records whether a BHSM pre-registered prediction is available from existing artifacts.

The `A_FB` zero-crossing is a comparatively clean benchmark with reduced hadronic sensitivity relative to many other rare-B observables, but it is not treated as uncertainty-free.

## Kill-Screen Result

BHSM currently lacks an artifact-backed rare-B observable map from its geometric mode/transport structure to the `A_FB(q^2)` zero-crossing. No forward `q0^2` prediction is claimed.

The existing repository contains artifact-backed CKM structure and bounded charged-current targets, but that does not by itself define:

- a `b -> s mu+ mu-` rare-B transition operator;
- a Wilson-coefficient or effective-Hamiltonian interface;
- a hadronic form-factor interface;
- a BHSM geometric null-balance condition corresponding to `A_FB(q^2)=0`;
- a bridge from any exact dimensionless null coordinate to physical `q^2` units.

Therefore the primary target remains blocked, not conditional-derived and not derived.

## Secondary Micro-Plateau Screen

Micro-plateau structure remains qualitative/exploratory and is not a BHSM prediction.

The repository does not currently provide exact node coordinates for residual features in `P'_5(q^2)`, `dB/dq^2`, or `A_FB(q^2)` from Farey nodes, lattice nodes, mode thresholds, or relative-boundary transition points. A qualitative statement that rare-B residuals may contain bumpy or tooth-like structure is not a prediction without exact node positions and a no-fit mapping to the observable convention.

## Audit Propositions

| Proposition | Classification |
| --- | --- |
| BHSM contains an artifact-backed map for `b -> s mu+ mu-` rare-B transitions. | `blocked` |
| BHSM defines a geometric null-balance condition corresponding to `A_FB(q^2)=0`. | `blocked` |
| BHSM can produce a numerical `q0^2` prediction in `GeV^2` without fitting target data. | `blocked` |
| BHSM can produce an exact dimensionless null coordinate but lacks physical `q^2` conversion. | `false` |
| The `q0^2` prediction depends on blocked physical gauge-coupling normalization. | `unknown` |
| BHSM predicts exact micro-plateau node coordinates in `P'_5` or `dB/dq^2`. | `blocked` |
| The micro-plateau node coordinates are derived from Farey/lattice/geometric nodes rather than fitted residuals. | `blocked` |
| The sprint changes frozen predictions. | `false` |

## Hindsight

### Validated

- `A_FB` zero-crossing is identified as a high-value rare-B forward-prediction target.
- Observable interface localized: `B0 -> K*0 mu+ mu-`, `A_FB(q^2)`, and `q0^2` where `A_FB(q0^2)=0`.
- `P'_5`, `dB/dq^2`, and `A_FB` residual micro-plateaus are valid secondary exploratory targets only if exact nodes are derivable.
- No-fit and pre-registration discipline is established.
- Existing v4.5-v4.9 coupling blockers are preserved.

### Invalidated / downgraded

- Qualitative claims about bumpy residuals are not predictions without exact node coordinates.
- A geometric metaphor of plasma over lattice is not enough to compute `A_FB(q^2)`.
- A correct CKM matrix alone does not automatically provide a rare-B observable map.
- Blocked gauge-coupling normalization cannot be smuggled into rare-B predictions.
- No `q0^2` placeholder, empirical offset, or retrospective explanation is acceptable as a forward prediction.

### Still open

- `b -> s` rare-B observable map.
- `A_FB` null-balance equation.
- `q^2` physical-unit bridge.
- Wilson-coefficient or effective-Hamiltonian interface if required.
- Hadronic/form-factor interface if required.
- Exact Farey/lattice/node map for micro-plateaus.
- Experimental binning and falsification protocol.
- `OPEN_MISSING_GAUGE_COUPLING_ACTION_ATTACHMENT`.
- `OPEN_MISSING_ALPHA_I_ACTION_DERIVATION`.
- `OPEN_MISSING_ALPHA2_ACTION_DERIVATION`.
- `OPEN_MISSING_G2_BH_ACTION_SOURCE`.
- `OPEN_MISSING_CKM_COEFFICIENT_VALUE_SOURCE`.
- `CKM_EXPONENT_NOT_DERIVED`.
- `FULL_BHSM_NOT_COMPLETE`.

## No-Go Guardrails

This sprint does not claim:

- a BHSM `A_FB` zero prediction;
- a `q0^2` value in `GeV^2`;
- exact micro-plateau node coordinates;
- use of existing LHCb, CMS, ATLAS, Belle, or Belle II data to fit a prediction;
- solved gauge-coupling normalization;
- derived `alpha_i=lambda_i` or `alpha_2=lambda_2`;
- action-derived `g2_BH`;
- derived CKM coefficient value or exponent;
- full BHSM completion;
- institutional endorsement;
- falsification or replacement of continuous QFT.

## Forward Work Required

To leave the blocked state, a future sprint must supply an artifact-backed no-fit chain that maps BHSM mode/transport geometry to the rare-B observable convention, derives a null-balance condition, supplies either a physical `q0^2` value or an exact dimensionless coordinate plus physical bridge, and records a falsification criterion before comparison with future data.
