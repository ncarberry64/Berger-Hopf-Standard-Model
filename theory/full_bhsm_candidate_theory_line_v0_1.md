# Full BHSM Candidate Theory Line v0.1

Status: `FULL_BHSM_CANDIDATE_ARCHITECTURE`

This note consolidates a candidate-only theory line for the Berger-Hopf
Standard Model (BHSM). It is an audit scaffold, not an update to the frozen
prediction package.

## Master Action Layer

Candidate master line:

```text
S_BHSM = S_SM,local + S_T + S_boundary + S_response
```

Claim-status ledger:

| Layer | Status | Role |
| --- | --- | --- |
| `FULL_BHSM_CANDIDATE_ARCHITECTURE` | candidate only | organizing architecture |
| `LOCAL_SM_GAUGE_LAYER_PRESERVED` | input/local infrared layer | preserves the Standard Model representation ledger |
| `BOUNDARY_FLAVOR_CHANNEL_LAYER` | partial | organizes sector boundary degrees and mode ledgers |
| `TOPOGRAPHIC_STABILITY_LAYER` | structural candidate | supplies stability and complement-gap scaffolds |
| `RESPONSE_SELECTOR_LAYER` | candidate/partial | supplies optional non-official response factors |

BHSM does not yet derive the full local Standard Model gauge group from first
principles. The safe claim is that BHSM preserves the local Standard Model
gauge representation layer and geometrizes the boundary/flavor/channel layer
that organizes mode ledgers, candidate effective Yukawas, response factors,
mixings, and neutrino structure.

## Representation Operators

The candidate representation operators are:

```text
O_q = 3B - L
O_j = -4T3 + 2(3B)(1/2 - T3)
Omega_f(q,j) = O_q q + O_j j
q = k - 2j
k = q + 2j
N(q,j) = q^2 + j^2
```

Sector evaluations:

| Sector | B | L | T3 | O_q | O_j | Omega |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| charged lepton | 0 | 1 | -1/2 | -1 | +2 | `Omega_l=-q+2j` |
| neutrino | 0 | 1 | +1/2 | -1 | -2 | `Omega_nu=-q-2j=-k` |
| up | 1/3 | 0 | +1/2 | +1 | -2 | `Omega_u=q-2j` |
| down | 1/3 | 0 | -1/2 | +1 | +4 | `Omega_d=q+4j` |

## Sector Target Degree Law

Candidate law:

```text
Omega_star = 3 * 2 ** (3B + (3B)(1/2 - T3))
```

Interpretation:

| Sector | Target magnitude | Candidate interpretation |
| --- | ---: | --- |
| charged lepton | 3 | primitive charged/lepton coherent boundary cover |
| neutrino | 3 | equal-degree conjugate cover; sign supplied by `Omega_nu=-k` |
| up | 6 | colored quark lift |
| down | 12 | colored lower-doublet lift |

Status: `SECTOR_TARGET_DEGREE_LIFT_LAW_STRUCTURAL_CANDIDATE`.

This formula is candidate-only and must not update official predictions.

## Mode-Ledger Rule

The conditional ledger rule scans nonnegative integer `(q,j)` pairs satisfying
the sector operator and target magnitude, applies the sector admissibility
constraints needed by the representation channel, converts to `k=q+2j`, and
then records the heavy reference `(0,0)` plus two nonzero representatives.

Status: `FERMION_MODE_LEDGER_FROM_REP_RULES_CONDITIONAL`.

Expected ledgers:

| Sector | q,j ledger | k,j ledger |
| --- | --- | --- |
| charged lepton | `(0,0), (1,2), (3,3)` | `(0,0), (5,2), (9,3)` |
| neutrino | `(0,0), (3,0), (1,1)` | `(0,0), (3,0), (3,1)` |
| up | `(0,0), (6,0), (8,1)` | `(0,0), (6,0), (10,1)` |
| down | `(0,0), (0,3), (4,2)` | `(0,0), (6,3), (8,2)` |

The charged-lepton and neutrino orderings remain part of the candidate
boundary-channel prescription rather than a completed theorem.

## Response Selector

Response factors remain candidate-only and non-official:

```text
operator activity = (N^2 - 1)/N^2
lepton N=3 gives 8/9
eta_l candidate = 8 alpha/(9 pi)
pure-fiber middle-up candidate = 1/2
light-up amplitude candidate = 1/sqrt(3)
light-up probability hazard = 1/3
CKM 2-3 interface candidate = (1/2)^(1/16)
```

Status labels:

```text
RESPONSE_SELECTOR_STRUCTURAL_CANDIDATE
LEPTON_8_9_CHANNEL_RULE_PARTIAL
PURE_FIBER_MIDDLE_UP_HALF_CANDIDATE_ONLY
LIGHT_UP_THREE_PAIR_AMPLITUDE_PROJECTION_CANDIDATE_ONLY
CKM_1_16_INTERFACE_BLOCK_CANDIDATE_ONLY
```

These factors are not interchangeable. The half-rule is not applied to down
modes. The CKM interface dilution is not applied as a mass correction.

## Gauge Coupling Layer

Candidate boundary normalization:

```text
alpha_G = C_G / (6*pi^2)
C_U1 = 1
C_SU2 = dim(SU2)-1 = 2
C_SU3 = dim(SU3)-1 = 7
alpha_1:alpha_2:alpha_3 = 1:2:7
```

Status: `GAUGE_COUPLING_ACTIVE_GENERATOR_COUNT_STRUCTURAL_CANDIDATE`.

This is a candidate boundary normalization layer, not a derivation of the full
local gauge group.

## Claim Hygiene

No official prediction is changed. No frozen prediction file is modified. No
claim is made that the full Standard Model has been derived from first
principles.
