# Boundary Integer Charge/Hypercharge Bridge

Status: `candidate_diagnostic`

This bridge reproduces the Standard Model electric charge and hypercharge table from integer candidate primitives under a diagnostic mapping. It does not yet derive those primitives from Berger-Hopf boundary geometry and does not constitute a full Standard Model derivation.

## Claim Labels

- `BOUNDARY_INTEGER_CHARGE_HYPERCHARGE_BRIDGE_CANDIDATE`
- `SM_CHARGE_TABLE_REPRODUCED_DIAGNOSTIC`
- `HYPERCHARGE_REWRITE_FROM_INTEGER_PRIMITIVES`
- `WEAK_INTERFACE_ACTIVITY_DERIVATION_REMAINS_OPEN`
- `CHIRAL_STRUCTURE_DERIVATION_REMAINS_OPEN`
- `FULL_SM_DERIVATION_NOT_CLAIMED`

## Integer Candidate Primitives

```text
C = 3B
ell = L
sigma = 2T3_orientation
w = weak-interface activity
```

Interpretation of the new bridge primitive:

```text
w in {0,1}
w=1 -> weak doublet / interface-active state
w=0 -> weak singlet / interface-inactive state
```

This is not fully derived chirality. The remaining proof obligation is to derive why weak-interface activity corresponds to SM chiral structure.

## Bridge Equations

```text
T3 = w*sigma/2
Y = C/3 - ell + (1-w)*sigma
Q = T3 + Y/2
Q = sigma/2 + C/6 - ell/2
```

## Diagnostic Charge Table

| field | C | ell | sigma | w | T3 | Y | Q |
| --- | --- | --- | --- | --- | --- | --- | --- |
| nu_L | 0 | 1 | 1 | 1 | 1/2 | -1 | 0 |
| e_L | 0 | 1 | -1 | 1 | -1/2 | -1 | -1 |
| u_L | 1 | 0 | 1 | 1 | 1/2 | 1/3 | 2/3 |
| d_L | 1 | 0 | -1 | 1 | -1/2 | 1/3 | -1/3 |
| nu_R optional | 0 | 1 | 1 | 0 | 0 | 0 | 0 |
| e_R | 0 | 1 | -1 | 0 | 0 | -2 | -1 |
| u_R | 1 | 0 | 1 | 0 | 0 | 4/3 | 2/3 |
| d_R | 1 | 0 | -1 | 0 | 0 | -2/3 | -1/3 |

## Open Proof Obligations

- Derive C as a color-active boundary sector from Berger-Hopf channel geometry.
- Derive ell as a lepton-sector boundary indicator from boundary closure.
- Derive sigma as upper/lower weak-interface orientation.
- Derive w as weak-interface activity and explain why it corresponds to SM chiral doublet/singlet structure.
- Derive anomaly cancellation from global boundary closure using the integer primitive charge table.

## Guardrails

- Candidate bridge only.
- No official predictions are changed.
- No frozen predictions are changed.
- No full Standard Model derivation is claimed.
- No BHSM replacement claim is made.
- No full gauge-group derivation is claimed.
