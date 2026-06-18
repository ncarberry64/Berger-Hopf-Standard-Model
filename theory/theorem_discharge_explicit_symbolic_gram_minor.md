# PO-BH-34 - Explicit Symbolic Gram/Minor Theorem Attempt

## 1. Mission

This branch attempts the next theorem-discharge wall after PO-BH-33: construct explicit symbolic generation feature matrices and candidate \(3\times3\) minors for the finite-width Wigner/Hopf feature problem.

It does not change frozen predictions and does not import mass, CKM, or PMNS data.

## 2. Previous theorem layers achieved

The prior layers established the conditional harmonic labels

\[
k=q+2j,\qquad \ell=k/2,\qquad n=q/2,
\]

the admissible \(m\)-multiplet, the generic \(y_0=(\alpha_0,\beta_0,\gamma_0)\) Wigner evaluation, and the PO-BH-33 finite-width Gram/minor rank condition.

## 3. Why explicit symbolic minors are the current wall

PO-BH-33 defined the rank condition but did not construct concrete minor candidates. This branch makes the obstruction sharper: every sector now has explicit symbolic feature matrices and candidate minors, but the repository still lacks a proof that any candidate determinant is not identically zero.

## 4. Canonical generation labels

| sector | generation labels \((q,j,k,\ell,n)\) |
| --- | --- |
| reference_charged | \((0,0,0,0,0)\), \((1,2,5,5/2,1/2)\), \((3,3,9,9/2,3/2)\) |
| reference_neutral | \((0,0,0,0,0)\), \((3,0,3,3/2,3/2)\), \((1,1,3,3/2,1/2)\) |
| cyclic_upper | \((0,0,0,0,0)\), \((6,0,6,3,3)\), \((8,1,10,5,4)\) |
| cyclic_lower | \((0,0,0,0,0)\), \((0,3,6,3,0)\), \((4,2,8,4,2)\) |

## 5. Feature matrix construction

Rows are local feature atoms:

`value_lowest`, `value_center`, `value_highest`, `d_alpha_lowest`, `d_beta_center`, `d_gamma_highest`, and `d2_local_center`.

Each matrix entry is tied to a Wigner/Hopf jet expression

\[
D^\ell_{m,n}(y_0)=
e^{-im\alpha_0}d^\ell_{m,n}(\beta_0)e^{-in\gamma_0}
\]

or a named local derivative of that expression. The entries are not arbitrary independent formal variables.

## 6. Symbolic Gram/minor definition

For each sector, the branch enumerates candidate \(3\times3\) determinants using three feature rows and the three generation columns. These are candidate minors of the feature matrix, or equivalently candidate minors of a finite-width contracted Gram construction.

## 7. Wigner/Hopf jet-independence audit

Global Peter-Weyl independence of distinct matrix coefficients is recorded as a structural support. The missing step is local finite-jet injectivity at the specific \(y_0\) and through the retained finite-width moment contractions.

Therefore:

`WIGNER_HOPF_JET_INDEPENDENCE_REMAINS_OPEN`.

## 8. Finite-width moment nondegeneracy condition

The finite-width route requires at least one nondegenerate universal second-moment block and contractions that do not project all three generation feature columns onto a lower-dimensional subspace.

This branch defines the condition but does not derive it from BHSM geometry.

## 9. Generic rank-three support theorem attempt

Conditional theorem form:

If the local Wigner/Hopf jet map \(J_r(y_0)\) is injective on the three generation labels in a sector and the finite-width moment contractions include at least one nondegenerate universal block, then the sector supports rank three generically away from proper degenerate loci.

The antecedents remain open, so rank-three support is not promoted.

## 10. Degenerate loci audit

Degenerate loci include axis collapse such as \(\beta_0=0\), vanishing finite-width moments, noninjective local jets, coincident reduced-Wigner beta factors, or moment contractions that collapse the columns.

## 11. Non-tautology audit

The construction avoids treating arbitrary independent symbols as a determinant proof. Entries are tied to mode labels and Wigner/Hopf expressions; the branch does not choose \(\beta_0\), moments, or feature rows to fit observed data.

## 12. What this achieves

This branch completes an explicit symbolic feature-matrix and minor-candidate layer:

`GENERATION_FEATURE_MATRICES_CONSTRUCTED`

`SYMBOLIC_3X3_MINOR_CANDIDATES_ENUMERATED`

## 13. What remains before numerical Yukawa values

The next proof obligation is to prove a nonzero determinant or an equivalent Wigner/Hopf local jet independence theorem, then derive finite-width moment nondegeneracy from the BHSM scalar/topographic profile.

## 14. CKM/PMNS status

CKM and PMNS values remain open. No mixing data are imported.

## 15. Replacement readiness status

BHSM replacement readiness is not claimed. Frozen and official predictions are unchanged.

