# BHSM v1.2C Parent-Action Minimality and Uniqueness Audit

This note audits whether the v1.2B symbolic parent internal-action scaffold is
minimal and unique under the current BHSM axioms. It does not change the
frozen v1.0 or v1.1 prediction packages.

## Minimality Result

The tested parent-action ingredients are:

- `I_HOPF`;
- `I_U1`;
- `I_BASE`;
- `I_WEAK`;
- `I_COF`;
- `I_BDY`.

The local minimality audit removes each term and verifies that the relevant
coefficient opens rather than remaining silently derived.

| Removed term | Expected effect |
| --- | --- |
| `I_HOPF` | fiber coefficient opens |
| `I_U1` | fiber coefficient opens |
| `I_BASE` | base coefficient opens |
| `I_WEAK` | base coefficient opens |
| `I_COF` | base coefficient opens |
| `I_BDY` | target opens |

Result: `MINIMAL_UNDER_TESTED_PARENT_TERMS`.

## Uniqueness Result

The audit tests nearby variants:

- flip Hopf orientation;
- flip weak chirality sign;
- remove coframe triplet participation;
- change coframe factor to singlet;
- change boundary winding multiplier;
- swap weak-component sign;
- allow trace U(1) as dynamical;
- disable Higgs-selected U(1).

Under the current BHSM axioms, none of these controlled variants recovers the
charged-sector mode ledger. The resulting status is:

```text
UNIQUE_UNDER_BHSM_AXIOMS
```

This means no tested nearby variant competes with the BHSM parent-action
scaffold. It does not prove global uniqueness of the complete internal action.

## Frozen Package Protection

The v1.2C audit does not modify:

- `BHSM_BARE_V1`;
- `BHSM_DRESSED_V1_CANDIDATE`;
- canonical `a`;
- universal `S`;
- frozen mode ledger;
- frozen tolerances or prediction outputs.

## Claim Boundary

BHSM v1.2C audits whether the parent-action scaffold is minimal and unique
under the current BHSM axioms. It does not claim full uniqueness of the
complete internal action unless competing variants are excluded by explicit
tests.
