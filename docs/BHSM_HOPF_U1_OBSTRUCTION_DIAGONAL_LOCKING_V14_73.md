# BHSM v14.73 — Hopf U(1)-Reduction Obstruction and Diagonal Curvature-Locking Gate

## Executive result

v14.72 found an exact `3+6` Berger splitting in the nine-dimensional
\(\ell=2\) shape sector once a fixed \(U(1)\) axis is chosen.

v14.73 tests whether that fixed axis can be made global over the retained
quaternionic Hopf base.

It cannot.

For

\[
SU(2)\simeq Sp(1)\longrightarrow S^7\longrightarrow S^4,
\qquad c_2=+1,
\]

a smooth global reduction to \(U(1)\) is topologically obstructed.

Therefore the v14.72 fixed-axis Berger projector is a valid **local,
collarwise, or total-space spectral mechanism**, but it cannot simply be
declared a globally descending rank-three associated bundle over the full
\(S^4\) base.

This removes one completion route but exposes a better one: the topology
naturally points back toward a **fully non-Abelian triplet locking**, not a
global Abelian axis.

---

## 1. Exact U(1)-reduction obstruction

Suppose the principal \(SU(2)\) Hopf bundle \(P\) reduced to a maximal torus
\(U(1)\).

The associated fundamental complex rank-two bundle would split as

\[
E=L\oplus L^{-1}.
\]

But

\[
H^2(S^4;\mathbb Z)=0,
\]

so

\[
c_1(L)=0.
\]

Hence

\[
c_2(E)
=
c_1(L)c_1(L^{-1})
=
-c_1(L)^2
=
0.
\]

The retained Hopf bundle has

\[
c_2(E)=+1.
\]

Contradiction.

Therefore

\[
\boxed{
P\text{ admits no smooth global }SU(2)\to U(1)\text{ reduction over }S^4.
}
\]

Equivalently, the associated twistor sphere bundle \(P/U(1)\to S^4\) has no
global section.

---

## 2. The unoriented Berger axis is obstructed too

The rank-three projector from v14.72 depends on an **axis**, so

\[
\hat n\sim-\hat n.
\]

Its stabilizer is therefore the normalizer \(N(U(1))\), rather than just
\(U(1)\).

But

\[
N(U(1))/U(1)\cong\mathbb Z_2,
\]

and

\[
H^1(S^4;\mathbb Z_2)=0.
\]

Thus any \(N(U(1))\) reduction over \(S^4\) would have a trivial associated
\(\mathbb Z_2\) bundle and would further reduce to \(U(1)\).

That reduction has just been proved impossible.

Hence

\[
\boxed{
\text{even the globally smooth unoriented fixed-axis reduction is obstructed.}
}
\]

---

## 3. Why this does not contradict the old twistor-Berger geometry

The old construction has a globally defined circle direction on the **total
space**

\[
S^1\to S^7\to CP^3,
\]

and therefore can write a global total-space metric

\[
g_7
=
L_4^2g_{H_4}
+
L_2^2g_{V_2}
+
L_1^2\eta^2.
\]

But that circle direction is not a basic \(Sp(1)\)-equivariant axis field over
the quaternionic base \(S^4\).

That distinction matters physically.

A general \(Sp(1)\) transition rotates the right-weight axis. Therefore a
fixed \(m_R=0\) subspace is not preserved by all full-base transition
functions.

So the v14.72 projector

\[
P_{m=0}
\]

does not automatically define the required physical rank-three bundle on
\(M_5\).

The topology explains why the authoritative v7.1 construction correctly kept
the full \(Sp(1)\) associated-bundle transport and did not assert a preferred
global \(U(1)\) axis.

---

## 4. Bare intrinsic Berger Einstein-Hilbert term

There is a second independent result.

For

\[
g_B
=
L_2^2(\sigma_1^2+\sigma_2^2)
+
L_1^2\sigma_3^2
\]

in the stored Maurer-Cartan convention, the intrinsic scalar curvature is

\[
\boxed{
R_B
=
\frac{2}{L_2^2}
-
\frac{L_1^2}{2L_2^4}.
}
\]

At fixed fiber volume,

\[
\rho^3=L_2^2L_1,
\qquad
\beta=L_1/L_2,
\]

this becomes

\[
\boxed{
\rho^2R_B
=
2\beta^{2/3}
-\frac12\beta^{8/3}.
}
\]

Its derivative is

\[
\boxed{
\frac{\partial R_B}{\partial\beta}
=
\frac{4(1-\beta^2)}
{3\rho^2\beta^{1/3}}.
}
\]

For positive \(\beta\),

\[
\partial_\beta R_B=0
\iff
\boxed{\beta=1}.
\]

And

\[
\left.
\partial_\beta^2R_B
\right|_{\beta=1}
=
-\frac{8}{3\rho^2}.
\]

So the bare isolated intrinsic EH fiber term cannot select the needed
\(\beta_\star\neq1\). Multiplying that term by an overall action sign changes
maximum versus minimum, but not the stationary location.

This is **not** a reduction of the complete M8 action to one term. It is an
exact kill screen for the simplest possible intrinsic-fiber source.

---

## 5. A useful anisotropy invariant

For the same fixed-volume Berger family,

\[
Q
=
2\left(
|\mathrm{Ric}|^2-\frac{R^2}{3}
\right)
\]

reduces exactly to

\[
\boxed{
\rho^4Q
=
\frac43
\beta^{4/3}
(\beta^2-1)^2.
}
\]

Thus

\[
Q\ge0
\]

and it vanishes only at the round point.

A positive coefficient in a minimizing action therefore reinforces the round
branch. A negative coefficient could destabilize it, but would require
additional stabilizing terms.

The authoritative coefficient/sign of such a full parent contribution is not
derived here.

---

## 6. The topology-compatible replacement: non-Abelian diagonal locking

A global axis is not required if BHSM keeps the full rank-three structure.

Let \(J_i\) be spin-one generators on two rank-three factors. Define

\[
\boxed{
K_\Delta
=
\sum_{i=1}^3 J_i\otimes J_i.
}
\]

This commutes with the diagonal \(SU(2)\), and its spectrum is

\[
\boxed{
-2,\quad -1,\quad +1
}
\]

with multiplicities

\[
\boxed{
1,\quad3,\quad5.
}
\]

The exact projectors are

\[
P_1=\frac{K_\Delta^2-I}{3},
\]

\[
\boxed{
P_3
=
-\frac12
(K_\Delta^2+K_\Delta-2I),
}
\]

\[
P_5
=
\frac{K_\Delta^2+3K_\Delta+2I}{6}.
\]

The numerical implementation gives ranks `1,3,5`, with projector errors at
machine precision.

This exactly reproduces the v14.70 representation split **without choosing a
global \(U(1)\) line**.

The missing physical object is a global action-owned soldering/intertwiner
that tells us which two triplet bundles are being locked. A natural candidate
class is the full non-Abelian quaternionic-Hopf connection curvature or a
mixed parent/shape Hessian built from it.

That source is not yet derived.

---

## 7. General diagonal-equivariant Hessian

Once a physical triplet soldering is available, every diagonal-equivariant
self-adjoint operator on the \(1\oplus3\oplus5\) sector can be written

\[
\boxed{
H_{\ell=2}
=
c_0I+c_1K_\Delta+c_2K_\Delta^2.
}
\]

Its three eigenvalues are

\[
h_1=c_0-2c_1+4c_2,
\]

\[
h_3=c_0-c_1+c_2,
\]

\[
h_5=c_0+c_1+c_2.
\]

The triplet is strictly softest precisely when

\[
h_3<h_1,\qquad h_3<h_5,
\]

which gives

\[
\boxed{
c_1>0,
\qquad
c_1<3c_2.
}
\]

An exact witness is

\[
(c_0,c_1,c_2)=(0,1,1),
\]

for which

\[
(h_1,h_3,h_5)=(2,0,2).
\]

A single term \(c_1K_\Delta\) alone does **not** make the triplet the softest
sector for either sign of \(c_1\).

Again, these are selection conditions, not physical BHSM coefficient values.

---

## 8. Hindsight 20/20 ledger

### VALIDATED

- The full-base \(U(1)\) reduction is topologically obstructed by \(c_2=1\).
- The unoriented fixed-axis/normalizer reduction is also obstructed.
- Total-space twistor \(S^1\) geometry does not imply a basic full-base axis.
- The v14.72 fixed-\(m\) rank-three projector is local/total-space rather than a
  globally descended \(M_5\) physical subbundle.
- Bare intrinsic Berger EH has only \(\beta=1\) as a positive fixed-volume
  stationary point.
- \(Q=2(|Ric|^2-R^2/3)\) is an exact nonnegative Berger anisotropy invariant.
- Non-Abelian diagonal locking gives exact `1+3+5` spectral projectors.
- The general diagonal-equivariant Hessian has three independent sector
  coefficients.
- The rank-three-softest coefficient region is explicit.

### INVALIDATED

- A globally smooth \(Sp(1)\to U(1)\) polarization section is the completion
  route on the full \(S^4\) base.
- The v14.72 Berger \(m=0\) carrier can simply be transported globally.
- Bare intrinsic EH selects \(\beta_\star\neq1\).
- One linear \(K_\Delta\) term automatically makes the triplet the softest
  physical sector.

### RECLASSIFIED

The symmetry-selection problem now has two branches:

1. **Abelian fixed-axis Berger route:** useful locally, globally obstructed.
2. **Full non-Abelian diagonal-locking route:** topology-compatible, but the
   action-owned soldering and coefficients are open.

This makes the v14.70 diagonal triplet more important again: topology favors a
full-triplet locking mechanism over a globally selected line.

### OPEN

The exact next object is

`ACTION_OWNED_NONABELIAN_HOPF_CURVATURE_OR_CONNECTION_SOLDERING_MAP_BETWEEN_THE_RELEVANT_TWO_RANK_THREE_BUNDLES_ON_THE_FULL_PREIMAGE_STATIONARY_BACKGROUND_WITH_A_GAUGE_COVARIANT_MIXED_SECOND_VARIATION_H_ELL2_EQUALS_C0_I_PLUS_C1_KDELTA_PLUS_C2_KDELTA_SQUARED_DERIVED_FROM_THE_GLOBAL_ACTION_AND_WITH_THE_RANK_THREE_SECTOR_SPECTRALLY_ISOLATED_WITHOUT_A_GLOBAL_U1_REDUCTION_THEN_TRANSPORTED_INTO_THREE_TRANSVERSE_CALDERON_SHAPE_CURRENT_DERIVATIVES_RELATIVE_HEAT_SUPERTRACE_AND_THE_FROZEN_NEUTRINO_KILL_SCREEN`

---

## Completion state

`GLOBAL_FIXED_AXIS_BERGER_ROUTE = TOPOLOGICALLY_BLOCKED`

`LOCAL_BERGER_RANK3_MECHANISM = VALIDATED_CONDITIONAL`

`BARE_INTRINSIC_EH_NONROUND_BETA_SELECTION = INVALIDATED`

`NONABELIAN_DIAGONAL_LOCKING = REPRESENTATION_THEOREM_VALIDATED / ACTION SOURCE OPEN`

`PHYSICAL_EXECUTION = BLOCKED`

`FULL_BHSM_COMPLETE = FALSE`

`MARK_III = NOT_REACHED`

No physical mass, CKM, PMNS, splitting, coupling, width, or probability is
emitted.
