# BHSM v14.74 — \(\ell=2\) Landau Locking and Goldstone Triplet Gate

## Executive result

v14.73 closed the smooth full-base \(U(1)\)-axis route: the retained
\(c_2=1\) quaternionic Hopf bundle cannot globally reduce to \(U(1)\).

That does **not** kill the three-channel program.

There is a topology-compatible route already inside the \(\ell=2\) shape
sector itself.

Represent the real nine-dimensional \(\ell=2\) coefficient space as

\[
Q\in \mathbb R^3\otimes\mathbb R^3
\simeq \operatorname{Mat}_{3\times3}(\mathbb R),
\]

with round symmetry

\[
Q\longmapsto R_L Q R_R^T,
\qquad
(R_L,R_R)\in SO(3)_L\times SO(3)_R.
\]

On the reflection-symmetric equal-cap branch, cap exchange sends the normal
shape displacement to its negative, so

\[
Q\mapsto -Q.
\]

The resulting even Landau action has a remarkable exact phase: if the
quadratic \(\ell=2\) mode becomes unstable while the two quartic invariants
stabilize it, the new vacuum spontaneously locks the two \(SO(3)\)'s to the
diagonal subgroup and generates **exactly three Goldstone orientation
directions**.

Those three directions are the antisymmetric `3` in

\[
3\otimes3=1\oplus3\oplus5.
\]

They are therefore not an inserted projector.  They arise as the tangent
space of the broken-symmetry vacuum manifold.

---

## 1. Complete even quartic invariant action

Define

\[
I_2=\operatorname{Tr}(Q^TQ),
\]

\[
I_4=\operatorname{Tr}\!\left[(Q^TQ)^2\right].
\]

The determinant is also invariant under \(SO(3)_L\times SO(3)_R\),

\[
\det(R_LQR_R^T)=\det Q,
\]

but

\[
\det(-Q)=-\det Q.
\]

Hence it is forbidden on the retained reflection-symmetric branch.

To quartic order the most general even invariant potential is therefore

\[
\boxed{
V(Q)
=
\frac r2 I_2
+
\frac u4 I_2^2
+
\frac v4 I_4.
}
\]

The implementation verifies invariance under deterministic independent left and
right rotations to machine precision.

This is a structural effective expansion.  The coefficients \(r,u,v\) have
**not** been assigned numerical BHSM values.

---

## 2. Nonzero isotropic locking branch

Consider

\[
Q=sI_3.
\]

More generally the symmetry orbit is

\[
Q=sR,\qquad R\in SO(3).
\]

For \(Q=sI\),

\[
I_2=3s^2,
\qquad
I_4=3s^4.
\]

Stationarity gives

\[
s\left[r+(3u+v)s^2\right]=0.
\]

The nonzero branch is

\[
\boxed{
s^2=-\frac r{3u+v}.
}
\]

It exists when

\[
\boxed{
r<0,\qquad 3u+v>0.
}
\]

The stabilizer of \(Q=sI\) satisfies

\[
R_LIR_R^T=I
\quad\Longleftrightarrow\quad
R_L=R_R.
\]

Therefore

\[
SO(3)_L\times SO(3)_R
\longrightarrow
SO(3)_{\rm diag}.
\]

The vacuum manifold is

\[
\boxed{
\frac{SO(3)_L\times SO(3)_R}{SO(3)_{\rm diag}}
\simeq SO(3),
}
\]

with dimension

\[
6-3=\boxed3.
\]

This requires no global \(U(1)\) axis and therefore does not encounter the
v14.73 obstruction.

---

## 3. Exact \(1+3+5\) Hessian

At \(Q=sI\), perturbations split into

\[
\delta Q
=
\delta Q_{\bf1}
+
\delta Q_{\bf3}
+
\delta Q_{\bf5},
\]

where

\[
\delta Q_{\bf1}
=
\frac{\operatorname{Tr}\delta Q}{3}I,
\]

\[
\delta Q_{\bf3}
=
\frac12(\delta Q-\delta Q^T),
\]

and

\[
\delta Q_{\bf5}
=
\frac12(\delta Q+\delta Q^T)
-
\frac{\operatorname{Tr}\delta Q}{3}I.
\]

Before imposing stationarity, the even-branch Hessian eigenvalues are

\[
h_1
=
r+(9u+3v)s^2,
\]

\[
h_3
=
r+(3u+v)s^2,
\]

\[
h_5
=
r+(3u+3v)s^2.
\]

Using

\[
r+(3u+v)s^2=0
\]

gives

\[
\boxed{h_1=-2r,}
\]

\[
\boxed{h_3=0,}
\]

\[
\boxed{h_5=2vs^2.}
\]

Thus

\[
\boxed{
r<0,\qquad v>0,\qquad3u+v>0
}
\]

produces:

- one positive singlet;
- exactly three zero modes;
- five positive quintet modes.

The zero modes are not an accident.  They are Goldstone directions required by
the spontaneous breaking

\[
SO(3)_L\times SO(3)_R\rightarrow SO(3)_{\rm diag}.
\]

The finite-difference Hessian calculation reproduces the analytic sector
eigenvalues.

---

## 4. Quartic boundedness

For the singular values of \(Q\),

\[
\frac{I_4}{I_2^2}\in\left[\frac13,1\right].
\]

Therefore the quartic form

\[
uI_2^2+vI_4
\]

is positive for all nonzero \(Q\) precisely when

\[
v\ge0:
\qquad
u+\frac v3>0,
\]

or

\[
v<0:
\qquad
u+v>0.
\]

The diagonal-locking stability conditions have \(v>0\) and

\[
3u+v>0,
\]

which are exactly sufficient for quartic boundedness.

So this is a genuine locally stable Landau phase modulo Goldstone directions,
not merely a saddle constructed by hand.

---

## 5. The three modes are intrinsically non-Abelian

Let \(L_i\) be the standard generators of \(\mathfrak{so}(3)\).

The broken relative rotations act as

\[
Q
\mapsto
e^{\epsilon L_i}Q
\]

relative to the opposite factor. At \(Q=sI\),

\[
\boxed{
\delta_iQ=sL_i.
}
\]

These are antisymmetric matrices and span the rank-three Hessian kernel.

Their Gram matrix is

\[
\langle\delta_iQ,\delta_jQ\rangle
=
2s^2\delta_{ij}.
\]

And

\[
\boxed{
[L_i,L_j]
=
\epsilon_{ijk}L_k.
}
\]

So the three structural channels are not three unrelated scalar modes.  They
are the tangent generators of one \(SO(3)\) relative-orientation manifold.

This directly supplies the **noncommuting three-channel algebra** that earlier
Calderón/wake sprints required at the kinematic level.

It does not yet provide physical propagation phases or detector flavor maps.

---

## 6. Rotor form

On the vacuum manifold write

\[
Q(\tau)=sR(\tau),
\qquad R(\tau)\in SO(3).
\]

For a kinetic term

\[
\frac Z2
\operatorname{Tr}(\dot Q^T\dot Q),
\]

the low-energy orientation dynamics become an \(SO(3)\) rotor,

\[
\frac{I_{\rm eff}}2|\omega|^2,
\]

with

\[
\boxed{
I_{\rm eff}=2Zs^2.
}
\]

At the exact symmetric classical level the three Goldstone gaps are all zero.
Physical splittings must therefore come from a later action-derived source:
nonlocal holonomy, boundary response, explicit symmetry breaking, or another
globally owned term.

No such splitting is inserted in v14.74.

---

## 7. Relation to Hopf curvature

The canonical quaternionic-Hopf connection remains important, but its role is
now cleaner.

It is a global non-Abelian connection and can contribute covariantly to:

- the projected quadratic coefficient \(r\);
- quartic coefficients \(u,v\);
- transport of the nonround background;
- explicit Goldstone lifting or holonomy terms.

What it cannot do by itself on the homogeneous round background is choose one
orientation \(R\) of \(Q=sR\): doing that before the instability would simply
reintroduce the symmetry-selection problem.

Thus the immediate calculation is not “pick a Hopf axis.” It is

\[
\boxed{
\text{project the actual global action onto }r,u,v.
}
\]

---

## 8. What this changes

### VALIDATED

- A full-base \(U(1)\) reduction is unnecessary for exactly three shape
  directions.
- The \(\ell=2\) order parameter admits a reflection-even quartic Landau action.
- A nonzero isotropic branch spontaneously breaks
  \(SO(3)_L\times SO(3)_R\) to the diagonal.
- The vacuum manifold has dimension three.
- The Hessian contains exactly three Goldstone modes.
- The Goldstone modes are precisely the antisymmetric triplet.
- Their generators obey the non-Abelian \(\mathfrak{so}(3)\) algebra.
- The stable coefficient cone is explicit.
- The mechanism is topology-compatible with v14.73.

### INVALIDATED

- Three channels require a globally chosen Berger axis.
- The diagonal triplet must be manually inserted into the action.
- Three independent scalar minima are required to obtain three channels.
- Structural Goldstones can already be called physical neutrino flavors.

### RECLASSIFIED

The three-channel problem is now separated into:

1. **existence of exactly three noncommuting structural directions:** derived
   conditionally from the bifurcated \(\ell=2\) phase;
2. **does the BHSM action actually enter that phase?** open at \(r,u,v\);
3. **what lifts/splits the three Goldstones physically?** open;
4. **how do those directions enter the operator-valued Calderón/wake system?**
   open.

---

## 9. Exact next calculation

The next upstream calculation is now unusually specific:

\[
r
=
\left.
D^2\Gamma_{\rm BHSM}
\right|_{\ell=2},
\]

and the two independent fourth derivatives

\[
u,\qquad v
\]

of the complete global action, including bulk, GHY, compatibility/KKT and
nonlocal spectral contributions.

The decisive no-fit test is

\[
\boxed{
r<0,\qquad
v>0,\qquad
3u+v>0.
}
\]

If those inequalities hold on one action-selected branch, the nonround
\(Q=sR\) phase and its three Goldstone directions follow without introducing
a new selector parameter.

The resulting nonround cap/seam background must then be solved and the three
Goldstone directions inserted into the physical Calderón operator.

---

## Completion state

`ELL2_DIAGONAL_LOCKING_MECHANISM = STRUCTURALLY_DERIVED`

`THREE_GOLDSTONE_CHANNELS = STRUCTURALLY_DERIVED`

`GLOBAL_U1_AXIS_REQUIRED = FALSE`

`ACTION_PROJECTED_R_U_V = OPEN`

`PHYSICAL_NONROUND_BACKGROUND = OPEN`

`PHYSICAL_GOLDSTONE_SPLITTINGS = OPEN`

`PHYSICAL_EXECUTION = BLOCKED`

`FULL_BHSM_COMPLETE = FALSE`

`MARK_III = NOT_REACHED`

No physical mass, CKM, PMNS, splitting, coupling, width, or probability is
emitted.
