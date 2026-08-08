# BHSM v14.71 — Round-Branch Full Second-Shape Hessian Centrality No-Go

## Result

v14.70 found an exact rank-three subspace inside the first positive scalar
shape sector,

\[
\mathcal H_{\ell=2}\cong(1,1),\qquad \dim \mathcal H_2=9,
\]

after **choosing** a diagonal `SU(2)`:

\[
3\otimes3=1\oplus3\oplus5.
\]

v14.71 asks the sharper question: can the complete current BHSM second-shape
Hessian on the retained round/reflection-symmetric/isotropic branch make that
choice by itself once the omitted bulk, GHY, compatibility/KKT, and spectral
terms are included?

The answer is **no**.

The exact commutant of the full

\[
SU(2)_L\times SU(2)_R
\]

action on the nine-dimensional `(1,1)` representation is one-dimensional.
Therefore every self-adjoint full-round-equivariant Hessian is

\[
\boxed{H_{\ell=2}=c_2 I_9.}
\]

The unknown physical coefficient `c_2` can affect stability and the common
ell=2 eigenvalue, but it cannot split the nine-dimensional space into
`1+3+5` and cannot select the triplet.

Primary verdict:

`BHSM_V14_71_ON_THE_RETAINED_ROUND_REFLECTION_SYMMETRIC_ISOTROPIC_BRANCH_THE_COMPLETE_ACTION_OWNED_SECOND_SHAPE_HESSIAN_MUST_COMMUTE_WITH_THE_FULL_SU2L_TIMES_SU2R_ACTION_ON_THE_ELL2_NINE_DIMENSIONAL_IRREP_SO_BY_SCHURS_LEMMA_IT_IS_SCALAR_ON_THAT_SPACE_AND_CANNOT_SELECT_THE_DIAGONAL_SU2_TRIPLET;_THE_EXACT_FULL_PRODUCT_COMMUTANT_HAS_DIMENSION_ONE_WHILE_THE_DIAGONAL_SU2_COMMUTANT_HAS_DIMENSION_THREE_SPANNED_BY_THE_1_3_5_PROJECTORS_THEREFORE_PHYSICAL_THREE_CHANNEL_SELECTION_REQUIRES_AN_ACTION_SELECTED_SYMMETRY_BREAKING_HOPF_BERGER_CONNECTION_OR_NONROUND_POLARIZATION_BACKGROUND_BEFORE_THE_CALDERON_HEAT_AND_NEUTRINO_GATES`

Full BHSM completion remains false. Mark III is not reached.

---

## 1. Exact commutant calculation

Use the real spin-one/vector generators `J_i` on `R^3`.  On

\[
R^3\otimes R^3\cong R^9
\]

the product-group generators are

\[
L_i=J_i\otimes I_3,\qquad
R_i=I_3\otimes J_i.
\]

For an arbitrary real `9 x 9` operator `X`, impose

\[
[X,L_i]=0,\qquad [X,R_i]=0,\qquad i=1,2,3.
\]

The resulting exact linear system has 81 unknown operator entries and
numerical rank 80, hence

\[
\boxed{\dim \operatorname{Comm}(SU(2)_L\times SU(2)_R)=1.}
\]

The commutant is therefore `span{I_9}`.

This is the finite-dimensional computational form of Schur's lemma for the
irreducible `(1,1)` representation.

---

## 2. Why the omitted round action sectors cannot change this conclusion

The no-go does **not** require the missing physical coefficient of every
second-variation term.

On the retained round/isotropic branch:

1. the universal second-shape/Jacobi term is `SO(4)` invariant;
2. the round M5 bulk and GHY terms are invariant under the seam isometry group;
3. the M8 horizontal pushforward and natural trace maps are equivariant;
4. the compatibility/KKT system is built from those natural maps;
5. Schur-complement elimination of equivariant blocks remains equivariant;
6. heat, resolvent, zeta, and determinant functional calculus of an equivariant
   operator remains equivariant.

Therefore the complete second-shape operator may change from the bare
geometric value

\[
5/a^2
\]

to some physically derived coefficient/operator value `c_2`, but on
`\mathcal H_2` it still has the form

\[
c_2 I_9
\]

unless the stationary background itself carries an action-owned
symmetry-breaking object.

This is a **symmetry theorem**, not a numerical evaluation of the full BHSM
Hessian.

---

## 3. KKT/Schur centrality

A representative invariant block Hessian has the form

\[
H=
\begin{pmatrix}
aI_9 & bI_9\\
bI_9 & cI_9
\end{pmatrix}.
\]

Eliminating the second block gives

\[
H_{\rm eff}
=
aI_9-bI_9(cI_9)^{-1}bI_9
=
\left(a-\frac{b^2}{c}\right)I_9.
\]

The implementation verifies zero centrality and product-group commutator
residuals at machine precision.

Thus compatibility/KKT elimination cannot secretly create the triplet split.

---

## 4. Nonlocal heat/zeta centrality

If the round seed operator satisfies

\[
[P,U_g]=0,
\]

then for any spectral function `f`,

\[
[f(P),U_g]=0.
\]

In particular,

\[
e^{-tP},\qquad (P+\mu^2)^{-1},\qquad \log(P+\mu^2)
\]

remain central on an irreducible round harmonic sector.

So the nonlocal relative determinant can shift the common ell=2 response but
cannot select the diagonal triplet while the seed/background retains full
round symmetry.

---

## 5. What changes after a diagonal SU(2) is physically selected

For the diagonal generators

\[
D_i=L_i+R_i,
\]

the commutant dimension becomes

\[
\boxed{3.}
\]

It is spanned by the exact projectors

\[
P_1,\quad P_3,\quad P_5
\]

onto

\[
3\otimes3=1\oplus3\oplus5.
\]

A diagonal-equivariant Hessian can therefore have the general form

\[
\boxed{
H_{\rm diag}
=
c_1P_1+c_3P_3+c_5P_5.
}
\]

When `c_1`, `c_3`, and `c_5` differ, the operator commutes with the chosen
diagonal `SU(2)` but no longer with the full product symmetry.

That is the exact mathematical condition BHSM needs.

The triplet does not need to be invented.  It already exists.  The unresolved
physics is the action-owned mechanism that **chooses the diagonal subgroup and
produces the split coefficients**.

---

## 6. What could provide that selector

Eligible classes include:

- a Berger/Hopf anisotropy selected by the global stationary action;
- a physical connection or Wilson/holonomy background;
- a nonround cap/seam tensor background;
- a localized anisotropic stationary matter/current configuration.

No such object is adopted in v14.71.

A coordinate choice, arbitrary polarization, or measured flavor data may not
be used to select it.

---

## 7. Hindsight 20/20 ledger

### VALIDATED

- `H_2` is an irreducible `(1,1)` representation of the round product group.
- The full product-group commutant has dimension one.
- A full-round-equivariant ell=2 Hessian is scalar.
- The diagonal-SU2 commutant has dimension three.
- The exact rank `1,3,5` projectors span that diagonal commutant.
- Equivariant KKT/Schur reduction preserves centrality.
- Spectral functional calculus preserves centrality.
- Unknown round coefficients can change stability but cannot select a triplet.

### INVALIDATED

- Adding the omitted **round-symmetric** bulk/GHY/KKT/nonlocal terms as such can
  select the triplet.
- The existence of the diagonal `1+3+5` decomposition means BHSM has already
  selected the diagonal subgroup.
- A round spectral determinant can act as a hidden triplet selector.

### RECLASSIFIED

The v14.70 “complete second-shape Hessian” blocker is now split:

1. **round stability/eigenvalue:** still needs the complete physical Hessian;
2. **three-channel selection:** already proved impossible on the full
   round-symmetric branch.

The highest-upstream flavor/shape object is therefore an action-selected
symmetry-breaking stationary background or connection.

### OPEN

- physical symmetry-breaking selector;
- proof that it is not gauge/coordinate;
- full second-shape Hessian on that background;
- isolated rank-three physical eigenspace;
- three physical shape derivatives;
- complete Calderón/gauge/ghost projectors;
- relative heat supertrace;
- frozen no-retuning neutrino execution.

---

## 8. Completion state

`FULL_BHSM_COMPLETE = FALSE`

`MARK_III = NOT_REACHED`

`PHYSICAL_EXECUTION = BLOCKED`

No physical mass, CKM/PMNS entry, mass splitting, coupling, width, or
probability is emitted.

The exact next object is:

`ACTION_SELECTED_SYMMETRY_BREAKING_STATIONARY_PARENT_CHILD_BACKGROUND_OR_CONNECTION_POLARIZATION_THAT_REDUCES_THE_ROUND_SU2L_TIMES_SU2R_SYMMETRY_TO_A_SPECIFIC_DIAGONAL_SU2_OR_SMALLER_GROUP_WITH_DERIVED_ELL2_SECOND_SHAPE_SPLITTING_AND_A_UNIQUE_PHYSICAL_TRIPLET_FOLLOWED_BY_THREE_SHAPE_CALDERON_DERIVATIVES_RELATIVE_HEAT_SUPERTRACE_AND_FROZEN_NEUTRINO_KILL_SCREEN`
