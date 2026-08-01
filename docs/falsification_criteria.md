# Falsification Criteria

These criteria are copied and summarized from the frozen v1.0 falsification
ledger.

| ID | Criterion | Status |
| --- | --- | --- |
| `F1` | Alpha-anchored geometry cannot be derived from the internal action. | `OPEN_PROOF_OBLIGATION` |
| `F2` | `Omega_f` cannot be derived from the twisted Dirac/bundle action. | `OPEN_PROOF_OBLIGATION` |
| `F3` | Scheme-consistent quark ratios disagree beyond fixed tolerance bands. | `FALSIFIABLE_NUMERICAL_BRANCH` |
| `F4` | CKM outputs fail outside fixed tolerances. | `FALSIFIABLE_NUMERICAL_BRANCH` |
| `F5` | PMNS effective-extension outputs are decisively contradicted. | `EFFECTIVE_EXTENSION_BRANCH` |
| `F6` | Full twisted Dirac/H_T spectrum produces extra light states below `4*pi^2 v`. | `OPEN_SPECTRAL_THEOREM` |
| `F7` | Unscreened light scalar/topographic modes remain. | `OPEN_ACTION_LEVEL_PROOF` |
| `F8` | Higher-loop/threshold RG matching breaks coupling agreement. | `OPEN_RG_MATCHING` |
| `F9` | Any post-freeze adjustment of `a`, `S`, modes, or `Z_virt` based on residuals. | `FREEZE_CONSTRAINT` |

This release is falsifiable because it freezes constants, modes, tolerances,
and outputs before comparison.

## BHSM v1 Comparison Gates

The internal profile-scale identities and no-empirical-derivation gate are internal gates. Charged-sector, CKM/PMNS/CP, and DESI checks are comparison-only gates and are `NOT_EVALUATED_DATA_ABSENT` until target data are supplied.

## BHSM v1.0.0 Falsification And Comparison Layer

The v1.0.0 release keeps falsification outside the derivation pipeline. The
machine-readable gate artifact is:

```text
artifacts/BHSM_falsification_gates_v1.json
```

Internal gates verify package integrity and no empirical derivation inputs.
External gates require target data, scheme metadata, and comparison metadata.
If target data are absent, those gates are reported as
`NOT_EVALUATED_DATA_ABSENT`, not as internal failures.

The release remains falsifiable because the internal constants and outputs are
frozen before external comparison.

## BHSM v1.1.0 HEP Handoff Falsification Boundary

The v1.1.0 HEP handoff package does not change frozen BHSM outputs. It adds a
runtime-validation path for the minimal bounded collider-interface subset.
Failed FeynRules, UFO, MadGraph, LHE/HepMC, Athena, or CMSSW gates should be
reported as software/interface validation failures unless they trace back to a
frozen BHSM source artifact.

## BHSM v10.0 envelopment falsification boundary

The v10.0 structural extension makes no empirical particle prediction. Its
internal claims fail if the C3 projector algebra, eta variational identities,
`pi1(Map_*^N(S7,S7))=Z2` topology, seven-dimensional scaling laws, independent
profile quadratures, or global dilation degeneracy cannot be reproduced.
A future physical-particle claim additionally fails unless a gauge-fixed
relative-periodic orbit passes constraint, convergence, conservation, and
Floquet tests before comparison. Frozen observables remain outside and
unchanged by this campaign.

## BHSM v10.1 relational doctrine falsification boundary

Doctrine integration fails if the canonical author JSON or its SHA changes
without authorization, an author status is silently promoted to `DERIVED`,
or a hard invariant is bypassed. The geometry claim fails if `S3 x M4` is
treated as M8 without the lifted-seam/collar map. A future buoyancy claim fails
unless its sign, stability, weak-field limit, equivalence principle, and
backreaction follow from one covariant variation. Complementarity fails
unless the full action, charges, spectra, representations, and vertices obey
the involution. Entropy, neutrino equivalence, and measurement claims remain
ineligible without their named maps and probability theorem.

## BHSM v10.2 Topological-Buoyancy obstruction falsification boundary

The obstruction fails if the current checked-in action and its declared
domain can be shown, without a new term or fitted parameter, to vary one
physical normal/radion degree, admit a positive static background, pull all
localized stress into that equation, and derive a covariant global restoring
constraint. Any future positive buoyancy claim must also derive its
gauge-invariant compactness observable, energy-depth sign, weak-field limit,
equivalence behavior, stability, and dimensional scale from that same action.
The present campaign emits none of those physical outputs.

## BHSM v10.3 three-mode/depth boundary

The present verdict fails if the checked-in action already supplies a distinct,
action-owned, gauge-invariant spacetime-removal/depth degree `q_D`, independent
of core/Hopf `q_C`, enclosure-wall/fold `q_W`, and coordinate seam motion.
After that prerequisite is met, one common action/domain must derive the full
three-mode kinetic matrix, Hessian, source, boundary maps, Hermitian
interference law, physical spectrum, and selected output without fitted
coefficients. The v6.27 seam--fold projection remains an observable readout;
it is not a fourth physical degree. Generation phases must be derived from the
sector cycle and cannot be inferred from the three-mode count.
