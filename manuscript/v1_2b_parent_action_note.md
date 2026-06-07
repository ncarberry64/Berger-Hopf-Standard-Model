# BHSM v1.2B Parent Internal-Action Boundary Derivation Note

This note extends the BHSM v1.2 omega action-origin program. It adds a symbolic
parent Berger-Hopf internal-action scaffold and reduces it to the sector
boundary functional used to obtain the charged-sector boundary operators.

No frozen v1.0 or v1.1 prediction output is changed.

## Parent Action Scaffold

The symbolic parent action is:

```text
S_int = int_I bar(Psi)(i slash D_Berger + A_Hopf + A_base + A_Higgs-U(1) + P_L + P_cof)Psi + S_boundary
```

Its reduction tracks:

- `I_HOPF`: Hopf-fiber connection;
- `I_U1`: Higgs-selected U(1) boundary connection;
- `I_BASE`: base S^2 angular connection;
- `I_WEAK`: weak/chirality projector term;
- `I_COF`: coframe triplet projector term;
- `I_BDY`: sector boundary winding/index term.

## Reduction Rules

| Output | Parent terms | Result |
| --- | --- | --- |
| `fiber_q` | `I_HOPF`, `I_U1` | Hopf fiber and Higgs-U(1) terms reduce to the q-coefficient inputs. |
| `base_j` | `I_BASE`, `I_WEAK`, `I_COF` | Base, weak/chirality, and coframe terms reduce to the j-coefficient inputs. |
| `target` | `I_BDY` | Boundary winding/index reduces to the sector target. |

The resulting boundary functional reproduces:

```text
Omega_ell = -q + 2j = 3
Omega_u   =  q - 2j = 6
Omega_d   =  q + 4j = 12
```

## Necessity Checks

The tests verify:

- removing `I_HOPF` or `I_U1` prevents fiber coefficient derivation;
- removing `I_BASE`, `I_WEAK`, or `I_COF` prevents base coefficient derivation;
- removing `I_BDY` prevents target derivation;
- no empirical mass, CKM, PMNS, or residual module is imported;
- frozen BHSM v1.0/v1.1 outputs remain unchanged.

## Claim Boundary

BHSM v1.2B reduces the sector boundary functional from a symbolic parent
internal-action scaffold. A full unique derivation from the complete
Berger-Hopf twisted Dirac/bundle action remains open unless proven.

## v1.2C Minimality and Uniqueness Addendum

The v1.2C audit removes each required parent-action ingredient and confirms
that the corresponding coefficient opens:

- `I_HOPF` or `I_U1` removal opens the fiber coefficient;
- `I_BASE`, `I_WEAK`, or `I_COF` removal opens the base coefficient;
- `I_BDY` removal opens the target.

The controlled nearby variants tested in v1.2C do not recover the charged-sector
mode ledger under the current BHSM axioms. The audit status is
`UNIQUE_UNDER_BHSM_AXIOMS`, with `theorem_complete=False`.
