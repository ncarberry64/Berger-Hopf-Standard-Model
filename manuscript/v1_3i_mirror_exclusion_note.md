# BHSM v1.3I Mirror Exclusion Derivation Note

Branch: `bhsm-v1.3-ht-spectrum`

Status: development audit

Theorem complete: `False`

## Purpose

BHSM v1.3I audits whether the opposite-chirality mirror candidates identified
in v1.3H are excluded by three existing BHSM structures:

1. the weak chiral projector;
2. the Higgs-selected `U(1)` boundary phase;
3. the v1.2 sector boundary functional.

No frozen BHSM v1.0/v1.1 predictions, canonical constants, tolerances, mode
ledger, public release tags, v1.2 action-origin outputs, or v1.3 state
ontology outputs are changed.

## Conservative Exclusion Rule

A mirror candidate is marked `EXCLUDED` only if at least one channel supplies a
model-internal exclusion rule without empirical masses, CKM/PMNS values, or
residual minimization.

If all channels are ambiguous, the candidate remains `OPEN_MIRROR_RISK`.

## Channel Results

| Mirror | Sector | (k,j,q) | chi | Chiral projector | Higgs-U1 phase | Boundary functional | Final |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `mirror_lepton` | `lepton` | `(0,0,0)` | `+1` | `EXCLUDED_BY_CHIRAL_PROJECTOR` | `OPEN` | `OPEN` | `EXCLUDED` |
| `mirror_up` | `up` | `(0,0,0)` | `+1` | `EXCLUDED_BY_CHIRAL_PROJECTOR` | `OPEN` | `OPEN` | `EXCLUDED` |
| `mirror_down` | `down` | `(0,0,0)` | `+1` | `EXCLUDED_BY_CHIRAL_PROJECTOR` | `OPEN` | `OPEN` | `EXCLUDED` |

The chiral projector channel excludes the generated mirror candidates because
their chirality is opposite to the protected kernel chirality `chi=-1`. This
uses the BHSM weak-doublet chiral projector from the internal action scaffold.

The Higgs-selected `U(1)` and sector boundary-functional channels are reported
but not used to force exclusion. They remain open until a full
chirality-resolved spectral boundary calculation is derived.

## Index Status

The scaffold index remains:

```text
n_L - n_R = 3
```

Theorem completion remains:

```text
theorem_complete = False
```

because the topological index theorem, formal/coordinate zero-mode alignment,
and infinite-basis complement bound remain open.

## Claim Boundary

BHSM v1.3I audits whether mirror zero modes are excluded by the chiral
projector, Higgs-selected `U(1)` boundary phase, and v1.2 sector boundary
functional. It does not prove the full `H_T` theorem unless mirror exclusion,
the index theorem, and the infinite-basis complement bound are all closed.

## Recommended Next Step

v1.3J should attack the remaining `OPEN_ALIGNMENT_GAP` between formal
sector-labeled zero modes and the finite Level 2 coordinate-protected block,
or derive the topological index theorem `Index(D_twist)=3`.
