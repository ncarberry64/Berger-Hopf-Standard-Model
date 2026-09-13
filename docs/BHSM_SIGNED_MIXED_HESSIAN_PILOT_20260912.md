# Signed mixed physical Hessian pilot, 12 September 2026

Directly contracting the fixed preconditioner into the complete mixed action
residuals tightens the physical Hessian enclosure on the selected endpoint-13
tube. The physical domain, action, weights, eigenpair family, response family
and original scalar contractions are unchanged.

| Maximum interval radius | Previous evaluation | Signed mixed evaluation |
| --- | ---: | ---: |
| Mixed eigenline solve | 27.12349 | 0.07788556 |
| Mixed physical response solve | 18,351,714.656 | 51,660.656 |
| Complete original Hessian normalization | 12,209.9151 | 10.18836 |
| Common-border Hessian normalization | 167.65755 | 0.2161600 |

The common-border result improves about 775-fold relative to the previous
common-border diagnostic. Both new Hessian evaluations contain the verified
point Hessian, whose maximum absolute value is about 8.18e-5. These are
enclosure radii, not new physical observations or relative prediction errors.

The width-attribution diagnostic that motivated this change evaluated formal
expressions after selected midpoint substitutions. Making all mixed jets
exact reduced the old normalized expression radius to about 4.26e-5, while
making first variations or scalar terms exact hardly helped. These
counterfactuals may violate the coupled identities and are explicitly not
physical enclosures. They identify arithmetic sensitivity only.

The change evaluates R(rhs-K z0) using signed action contractions with rows
of R before producing separate interval RHS coordinates. It retains the
mixed eigenvalue terms, both first-response coupling terms, the complete
weighted source variation, and the differentiated normalization and
orthogonality equations. The derivation is in
`theory/n12_gate7_signed_mixed_variation_residuals.md`.

Two independent tests compare both residuals with separately assembled dense
bordered systems for a synthetic two-mode action. They cover nonzero centers,
unequal weights, two transverse columns, and an uncertain action coefficient.
The physical producer separately verifies its point eigenpair and preserves
all seven solves and all original scalar variations.

`scripts/reproduce_n12_gate7_signed_mixed_hessian_pilot.py` independently
invokes the physical producer and saved-data normalizer, compares both record
files and both data files byte for byte, and writes a narrowly scoped receipt
only if all four comparisons succeed. Failed outputs remain preserved.

Both calculations have now reproduced byte for byte. The paired direct data
hash is `F69A65426721DB77DC00687EB9B144C032D5C7B7A0E390D11F6857C1A97A88C7`;
the paired normalized data hash is
`A410BBF7C8348A30360AA20EEF67F3754A590A84257020BE8DAB12A817F15462`.
The compact evidence artifact records both record hashes, the receipt,
individual solve radii and the earlier width-attribution diagnostic. The
first-run records retain their historical unreproduced flag; the separate
successful reproduction receipt establishes the completed second invocation.

The scope is one scaled longitudinal direction against weighted physical
input column 0 on one paired endpoint tube. Full transverse/longitudinal
direction coverage, all 99 derivative columns, actual midpoint and full-path
coverage, higher remainders, physical quotient identification and contraction
remain separate requirements. Neither Gate 7 nor BHSM is complete, and these
diagnostics do not add a Museum observable or justify manuscript completion.
