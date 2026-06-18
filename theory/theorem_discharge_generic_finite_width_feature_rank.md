# PO-BH-33 — Generic Finite-Width Feature-Rank Scaffold

## 1. Mission

This theorem-discharge layer continues the Berger–Hopf Standard Model derivation program toward a complete derivation of Standard Model structure from Berger–Hopf boundary geometry.

The immediate goal is to move from the generic \(y_0\) Wigner feature scaffold to a finite-width feature-rank scaffold without fitting fermion masses, CKM, or PMNS data.

## 2. Previous theorem layers achieved

Earlier theorem-discharge layers established:

\[
q=k-2j,\qquad k=q+2j,
\]

\[
\ell=\frac{k}{2},\qquad n=\frac{q}{2},\qquad j=\ell-n,
\]

the full admissible Wigner/Hopf multiplet

\[
\left\{D^{k/2}_{m,q/2}(y)\right\}_{m=-\ell}^{+\ell},
\]

and the generic-y0 evaluation

\[
D^{k/2}_{m,q/2}(y_0)
=
e^{-im\alpha_0}
d^{k/2}_{m,q/2}(\beta_0)
e^{-i(q/2)\gamma_0}.
\]

PO-BH-32 isolated \(\beta_0\) as the open reduced-Wigner magnitude selector.

## 3. Why finite-width feature rank is the next blocker

The strict point-sampling limit can collapse Yukawa structure. A finite-width scalar/topographic profile contributes derivatives and moment tensors around \(y_0\). The key question is whether the three generation-mode feature multiplets in each sector can support rank three under universal finite-width contractions.

This layer does not compute numerical Yukawa values. It defines the symbolic rank problem.

## 4. Feature multiplet

For each mode \((k,q)\), define the local feature multiplet

\[
F_{k,q}(y_0)
=
\left\{
D^{k/2}_{m,q/2}(y_0),
\partial_a D^{k/2}_{m,q/2}(y_0),
\partial_a\partial_b D^{k/2}_{m,q/2}(y_0)
\right\}_{m=-\ell}^{+\ell}.
\]

The derivative coordinates are the symbolic local coordinates inherited from the generic \(y_0\) scaffold.

## 5. Finite-width moment scaffold

A universal finite-width scalar/topographic profile gives symbolic moments such as:

\[
M_0,\qquad M_a,\qquad M_{ab},\qquad \cdots
\]

or, for a symmetric profile, the reduced scaffold

\[
M_0,\qquad M_{ab},\qquad \cdots.
\]

This branch does not choose numerical moment values.

## 6. Rank support condition

Rank-three support requires that the three generation-mode feature multiplets in a sector remain independent after universal finite-width moment contractions.

A symbolic way to audit this is to define a feature Gram or minor determinant:

\[
G_{ij}=\langle F_i,F_j\rangle_M
\]

and ask whether at least one \(3\times3\) determinant is not identically zero as a symbolic function of the open universal quantities.

## 7. Generic-rank interpretation

If a determinant is not identically zero, rank three is generically supported away from special degenerate loci.

Special lower-rank loci may include:
- axis-collapse cases such as \(\beta_0=0\);
- vanishing finite-width moments;
- coincident or linearly dependent feature vectors;
- additional symmetry constraints.

This theorem layer must distinguish generic support from numerical prediction.

## 8. What may be promoted

This branch may promote a symbolic scaffold:

\[
\text{GENERIC\_FINITE\_WIDTH\_FEATURE\_RANK\_SCAFFOLD\_DERIVED\_CONDITIONAL}.
\]

It may not promote actual rank-three Yukawa matrices unless a nonzero symbolic determinant or equivalent theorem is actually discharged.

## 9. Guardrails

This branch does not:
- fit masses;
- import CKM or PMNS;
- choose \(\beta_0\) to match data;
- derive numerical Yukawa values;
- claim full SM derivation;
- claim replacement readiness;
- change frozen predictions;
- force \(m=q/2\).

## 10. Downstream bridge

If later branches prove a nonzero generic determinant, BHSM can proceed to finite-width Yukawa matrix construction. If not, the open problem remains the rank independence of the feature multiplets.

## Conclusion

This branch defines the generic finite-width feature-rank scaffold. It turns the open symbolic \(y_0\) and \(m\)-multiplet data into a precise rank-support problem under universal finite-width moment contractions. It does not derive a nonzero determinant, numerical Yukawa values, CKM, PMNS, or replacement readiness unless separately proven by repo-supported theorem machinery.

Follow-up: `theory/theorem_discharge_explicit_symbolic_gram_minor.md` constructs explicit generation feature matrices and symbolic 3x3 minor candidates. The nonzero symbolic minor and Wigner/Hopf local jet-independence theorem remain open.
