# Berger-Hopf Standard Model: A No-Retuning Geometric Reinterpretation Framework with Frozen Predictions and a Completed Theorem Package

Norman P. Carberry  
Independent Researcher  
Okauchee Lake, Wisconsin, USA  
Email: [carberry8878130@hotmail.com](mailto:carberry8878130@hotmail.com)  
ORCID: <https://orcid.org/0009-0000-6650-3485>

## Abstract

The Berger-Hopf Standard Model (BHSM) is a no-retuning geometric
reinterpretation framework for Standard Model flavor, couplings, generations,
and electroweak-scale structure. This final release preserves the frozen BHSM
v1.0 prediction package and records the completed internal theorem package
reported by the repository ledger. The frozen model has two branches:
`BHSM_BARE_V1` and `BHSM_DRESSED_V1_CANDIDATE`. The dressed candidate applies
`Z_virt^{u,2}=1/2` only to `c/t` and leaves all other frozen outputs unchanged.
The completed theorem chain includes complete operator identification, action
uniqueness, projector commutator control, projector graph-domain stability,
H_T lower-bound transfer, index theorem closure, mirror exclusion, the full
H_T theorem, and the full BHSM theorem package. This paper does not claim
experimental confirmation, QCD confinement, PMNS/neutrino completion, new
particle discovery, or publication acceptance.

## Introduction

BHSM asks whether a fixed Berger-Hopf internal geometry can organize Standard
Model-like flavor and coupling structure without post-hoc retuning. The
repository therefore separates three layers: frozen model outputs, theorem
obligations internal to the BHSM framework, and empirical/precision comparison
work. The final package here closes the internal theorem chain according to the
repository ledger while preserving all frozen outputs exactly.

## BHSM Frozen Model Overview

The frozen configuration is fixed before scoring:

| Quantity | Frozen value |
| --- | --- |
| Canonical geometry | `a = 1.157054135733433` |
| Universal overlap width | `S = 0.07957747154594767` |
| Bare branch | `BHSM_BARE_V1` |
| Dressed candidate branch | `BHSM_DRESSED_V1_CANDIDATE` |
| Virtual dressing rule | `Z_virt^{u,2}=1/2` for `c/t` only |

The fixed charged-sector mode ledger is:

| Sector | Heavy | Middle | Light |
| --- | --- | --- | --- |
| Charged leptons | `(0,0)` | `(5,2)` | `(9,3)` |
| Up quarks | `(0,0)` | `(6,0)` | `(10,1)` |
| Down quarks | `(0,0)` | `(6,3)` | `(8,2)` |

## Berger-Hopf Geometry

The canonical Berger anisotropy is alpha-anchored:

```text
a = alpha^{-1}/(12*pi^2) = 1.157054135733433
```

The universal overlap width is:

```text
S = 1/(4*pi) = 0.07957747154594767
```

Mode suppressions use the supplied Berger-Hopf ledger and overlap rules. The
final theorem package does not modify these constants, modes, tolerances, or
outputs.

## Frozen Constants and Prediction Ledger

| Quantity | `BHSM_BARE_V1` | `BHSM_DRESSED_V1_CANDIDATE` | Changed |
| --- | --- | --- | --- |
| `c/t` | `0.008310500554068288` | `0.004155250277034144` | `True` |
| `u/t` | `1.2690463017606151e-05` | `1.2690463017606151e-05` | `False` |
| `s/b` | `0.021933971495439474` | `0.021933971495439474` | `False` |
| `d/b` | `0.0011165200546001757` | `0.0011165200546001757` | `False` |
| `sin_theta_13` | `0.0035623676140463315` | `0.0035623676140463315` | `False` |

The frozen v1.0 score summary is:

- Bare: `{'PASS': 22}`
- Dressed candidate: `{'PASS': 21, 'SCHEME_SENSITIVE': 1}`

## Bare and Dressed Branch Definitions

`BHSM_BARE_V1` is the pure alpha-anchored Berger-Hopf overlap model.

`BHSM_DRESSED_V1_CANDIDATE` applies the virtual-environment dressing factor
`Z_virt^{u,2}=1/2` only to the middle up-sector ratio `c/t`. The candidate
branch does not alter `u/t`, CKM `sin_theta_13`, down-sector ratios, lepton
ratios, gauge outputs, Higgs/electroweak outputs, H_T outputs, or scalar
outputs.

## Complete Theorem Package Summary

| Node | Final status |
| --- | --- |
| Complete operator identification | `PROVEN` |
| Action uniqueness | `PROVEN` |
| Projector commutator control | `PROVEN` |
| Projector graph-domain stability | `PROVEN` |
| H_T lower-bound transfer | `HT_LOWER_BOUND_TRANSFER_PROVEN` |
| Index theorem | `INDEX_THEOREM_PROVEN` |
| Mirror exclusion | `MIRROR_EXCLUSION_PROVEN` |
| Full H_T theorem | `FULL_HT_THEOREM_PROVEN` |
| Full BHSM theorem package | `FULL_BHSM_THEOREM_PACKAGE_COMPLETE` |

## Complete Operator Theorem

The complete operator identification closure records the Berger-Hopf operator
used by the final theorem package as identified in the repository ledger. The
release package does not use the coordinate-first kernel for the final H_T
decision.

## Action Uniqueness Theorem

The action-origin program derives the charged-sector boundary operators from an
explicit symbolic sector boundary functional, reduces that functional from a
symbolic parent internal-action scaffold, and records uniqueness under the
current BHSM axioms.

## Projector Commutator Theorem

Projector commutator control is recorded as proven for the final theorem chain.
The release guard tests prevent a final theorem-complete claim when any
required commutator node is open or conditional.

## Projector Graph-Domain Theorem

Projector graph-domain stability is recorded as proven for the complete graph
domain used in the H_T lower-bound transfer. The final release does not change
frozen model outputs.

## H_T Lower-Bound Theorem

The H_T lower-bound transfer is recorded as `HT_LOWER_BOUND_TRANSFER_PROVEN`.
The H_T theorem status is `FULL_HT_THEOREM_PROVEN`.

## Index Theorem

The final index result is:

```text
dim ker D_twist = 3
```

with exactly one protected state in each sector:

- lepton
- up
- down

## Mirror Exclusion Theorem

The final mirror-exclusion result is `MIRROR_EXCLUSION_PROVEN`. No
coordinate-first kernel, chirality-flipped partner, Higgs-U1 mirror channel,
boundary mirror channel, or topographic/mixed-sector mirror channel remains
protected in the final theorem ledger.

## Full H_T Theorem

The full H_T theorem is recorded as `FULL_HT_THEOREM_PROVEN`, with the final
formal sector-labeled kernel and no coordinate-first protected block.

## Full BHSM Theorem Decision

The final BHSM theorem decision is:

```text
FULL_BHSM_THEOREM_PACKAGE_COMPLETE
```

Final paper preparation is allowed by the repository theorem ledger.

## Limitations

- The theorem package is an internal BHSM theorem completion, not empirical
  confirmation of BHSM by experiment.
- Precision QCD/RG threshold matching remains future empirical/precision work.
- PMNS/neutrino rows remain effective-extension screens unless separately
  promoted by explicit model content.
- The release does not claim QCD confinement.
- The release does not claim new particle discovery.
- The release does not guarantee publication acceptance.
- No Zenodo DOI is invented in this repository.

## Falsifiability and Future Precision Work

The frozen package remains falsifiable through the predeclared no-retuning
prediction ledger and tolerance bands. Future work should focus on
scheme-consistent precision QCD/RG threshold matching, external empirical
comparisons, and independent review of the theorem chain.

## Reproducibility Instructions

Run:

```powershell
python -m pytest -q
```

The release package includes frozen sanity checks confirming that:

- `BHSM_BARE_V1` is unchanged.
- `BHSM_DRESSED_V1_CANDIDATE` is unchanged.
- `a` is unchanged.
- `S` is unchanged.
- the dressed branch changes only `c/t`.
- `u/t` is unchanged.
- CKM `sin_theta_13` is unchanged.

## AI-Assisted Drafting/Coding Acknowledgment

The author used AI-assisted drafting and coding support to organize repository
artifacts, tests, manuscript text, and release metadata. Scientific
responsibility, claim discipline, and release approval remain with the author.

## License and Status Statement

All rights reserved. This release is public-facing research software and
manuscript material, but it is not distributed under an open-source license.

## References

See `manuscript/references.md` and `CITATION.cff`.
