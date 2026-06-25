# Current BHSM Status

Current status: structural architecture integrated conditional; numerical closure open.

BHSM follows the rule: derive -> freeze -> compare -> claim.

## What Is Integrated Conditionally

- finite algebra / gauge skeleton
- hypercharge and anomaly ledger
- charged-sector structural branches
- A-local charged branch matrix export
- A-background identity branch with verified dependency order
- `Z_virt^{u,2}=1/2` only for up-sector middle mode `(q,j)=(6,0)`
- neutral Hessian sector
- neutral bridge / PMNS structural source
- CKM structural source
- boundary relative-holonomy CP source
- no-retuning prediction protocol

## What Is Candidate Or Diagnostic

- B-diagnostic `rho_ch` scans using `q^2 + rho_ch*j^2`
- charged shape-freeze diagnostics
- neutral Hessian / bridge numerical scaffolds
- CKM and PMNS structural sources
- boundary relative-holonomy CP source
- comparison-ready prediction package

These components organize the architecture. They do not close numerical prediction.

## What Has Been Downgraded Or Rejected As Primary

The minimal positive diagonal `K_collar` anisotropic branch was audited after
A-local and A-background identity branch export. It compressed all three
charged-sector hierarchies, producing `STACK_COLLAR_REJECTED_AS_PRIMARY`. This
does not invalidate BHSM; it downgrades this minimal `K_collar` route as the
primary charged-precision mechanism and redirects charged precision work toward
finite-width/jet-heat response, localized thresholds, common-scale transport,
or independently action-derived non-diagonal collar structure.

## What Remains Open

- boundary-derived `chi`
- non-diagonal value-curvature `K_collar` only if action-derived
- oriented finite-width / jet-heat response audit
- absolute same-sector mass ratios
- cross-sector transported mass ratios
- residual RG coefficients
- full scheme/common-scale alignment
- exact action derivation of `g_bridge=16/189`
- neutral eta/beta/kappa final derivation
- neutral threshold rules
- PMNS numerical closure
- CKM numerical closure
- CP numerical closure
- Higgs/electroweak absolute scale
- final comparison-ready prediction package

## What Is Forbidden To Claim

- BHSM is proven
- BHSM replaces the Standard Model
- BHSM predicts all particle masses
- BHSM has solved CKM/PMNS
- BHSM has predicted the Higgs mass
- BHSM is experimentally confirmed

## Latest PR / Checkpoint Summary

PR #40, `PO-BH: Codex reentry branch audit and K-collar scaffold`, restored
Codex workflow state, classified the charged generator as `B-diagnostic`, and
recorded that A-background was not implemented in that checkpoint.

PR #41, `PO-BH: A-background collar dependency-order scaffold`, exported
A-local and A-background identity branch matrices, verified the A-background
dependency order, preserved the B-diagnostic branch, and ran the K-collar
response audit. The identity K-collar route was `STACK_COLLAR_REJECTED_AS_PRIMARY`.

Frozen predictions changed: no.

Official predictions changed: no.
