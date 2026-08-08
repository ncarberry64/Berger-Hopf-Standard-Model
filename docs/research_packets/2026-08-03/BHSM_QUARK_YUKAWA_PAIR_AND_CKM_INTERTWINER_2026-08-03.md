# BHSM Manual Quark Yukawa Pair and Common Left-Handed Intertwiner Sprint

**Date:** 2026-08-03  
**Repository baseline:** BHSM v11.3, PR #217  
**Input milestone:** locally complete conditional charged-lepton action sector  
**Target:** `ACTION_OWNED_UP_DOWN_YUKAWA_OPERATOR_PAIR_WITH_COMMON_LEFT_HANDED_CHARGED_CURRENT_INTERTWINER`

---

## 1. Frozen quark family modules

The exact three-slot ledgers are

\[
\mathcal F_u:
\quad
(0,0),\ (6,0),\ (10,1),
\]

\[
\mathcal F_d:
\quad
(0,0),\ (6,3),\ (8,2).
\]

Let

\[
q=k-2j,
\qquad
K=k(k+2).
\]

Then

\[
(K,q)_u
=
(0,0),\ (48,6),\ (120,8),
\]

\[
(K,q)_d
=
(0,0),\ (48,0),\ (80,4).
\]

No measured quark mass or mixing datum enters these assignments.

---

## 2. Sector spectral operators

For the frozen Berger parameter \(a\), define

\[
\lambda_{k,j}(a)
=
K+(a^2-1)q^2.
\]

The exact sector operators are

\[
\mathcal L_u
=
\sum_{f=0}^{2}\lambda_f^{(u)}P_f^{(u)},
\]

\[
\mathcal L_d
=
\sum_{f=0}^{2}\lambda_f^{(d)}P_f^{(d)}.
\]

The corresponding overlap operators are

\[
\mathcal T_u
=
\exp\left(-\frac{\mathcal L_u}{4\pi}\right),
\]

\[
\mathcal T_d
=
\exp\left(-\frac{\mathcal L_d}{4\pi}\right).
\]

They are positive, Hermitian, and diagonal in their exact family-projector
bases.

---

## 3. Middle-up virtual-door dressing

The repository's weak-double-projection result fixes

\[
Z_{\rm virt}^{u,2}=\frac12
\]

for the middle up-sector mode \((6,0)\).

Define

\[
D_{\rm virt}^{u}
=
P_0^{(u)}
+\frac12P_1^{(u)}
+P_2^{(u)}.
\]

Since \(D_{\rm virt}^{u}\) and \(\mathcal T_u\) are functions of the same
orthogonal projector set, they commute.

The dressed up response is

\[
\boxed{
\widehat{\mathcal T}_u
=
D_{\rm virt}^{u}\mathcal T_u.
}
\]

No corresponding family-dependent down-sector dressing is inserted in this
sprint.

---

## 4. Minimal action-owned Yukawa pair

Let \(c_u>0\) and \(c_d>0\) be the sector-wide scalar source/lift
normalizations to be obtained by the same trace-normalized action procedure
used in the charged-lepton sector.

The minimal Yukawa operators are

\[
\boxed{
\mathbb Y_u^{\rm BH}
=
c_u\,J_u^\dagger
\widehat{\mathcal T}_u
R_u,
}
\]

\[
\boxed{
\mathbb Y_d^{\rm BH}
=
c_d\,J_d^\dagger
\mathcal T_d
R_d.
}
\]

Here:

- \(\mathcal F_Q\) is the common left-handed quark-doublet family space;
- \(J_u:\mathcal F_Q\to\mathcal F_u\) and
  \(J_d:\mathcal F_Q\to\mathcal F_d\) are left-handed incidence
  identifications;
- \(R_u,R_d\) are right-handed unitary identifications.

Right-handed rotations do not enter the CKM matrix.

The intrinsic Yukawa action is

\[
\boxed{
S_{4,q}^{\rm BH}
=
-\int_{M_4}d\mu_4
\left[
\bar Q_L\mathbb Y_d^{\rm BH}Hd_R
+
\bar Q_L\mathbb Y_u^{\rm BH}\widetilde H u_R
+\mathrm{h.c.}
\right].
}
\]

This is gauge invariant and renormalizable.

---

## 5. Dimensionless hierarchy seeds

Using

\[
a=\frac{137.035999084}{12\pi^2},
\qquad
S=\frac1{4\pi},
\]

the up-sector Berger costs are

\[
\lambda_u
=
0,\ 60.1958738286423,\ 141.68155347314186.
\]

The bare overlap eigenvalues are

\[
1,\ 0.008310500554068288,\ 1.2690463017606151\times10^{-5}.
\]

After the exact middle-up dressing,

\[
\boxed{
\widehat t_u
=
1,\ 0.004155250277034144,\ 
1.2690463017606151\times10^{-5}.
}
\]

The down-sector costs are

\[
\lambda_d
=
0,\ 48,\ 85.42038836828547,
\]

with overlap eigenvalues

\[
\boxed{
t_d
=
1,\ 0.021933971495439474,\ 0.0011165200546001757.
}
\]

These are geometric dimensionless hierarchy seeds. The sector-wide absolute
normalizations \(c_u,c_d\) remain separate action objects.

---

## 6. Left-handed mass-response operators

The left-handed Hermitian response operators are

\[
H_u
=
\mathbb Y_u^{\rm BH}
(\mathbb Y_u^{\rm BH})^\dagger,
\]

\[
H_d
=
\mathbb Y_d^{\rm BH}
(\mathbb Y_d^{\rm BH})^\dagger.
\]

Right-handed unitary maps cancel:

\[
H_u
=
c_u^2J_u^\dagger
\widehat{\mathcal T}_u^2J_u,
\]

\[
H_d
=
c_d^2J_d^\dagger
\mathcal T_d^2J_d.
\]

Let \(U_u,U_d\) diagonalize \(H_u,H_d\). Then

\[
\boxed{
V_{\rm CKM}=U_u^\dagger U_d.
}
\]

---

## 7. Canonical-identification no-mixing theorem

The currently attached family modules use the same ordered three-slot
architecture. The minimal canonical identification is

\[
J_u=J_d=J_{\rm can},
\]

mapping base to base, first excitation to first excitation, and second
excitation to second excitation.

Under this identification,

\[
H_u
=
J_{\rm can}^\dagger
\operatorname{diag}
(c_u^2\widehat t_{u,0}^2,
c_u^2\widehat t_{u,1}^2,
c_u^2\widehat t_{u,2}^2)
J_{\rm can},
\]

\[
H_d
=
J_{\rm can}^\dagger
\operatorname{diag}
(c_d^2t_{d,0}^2,
c_d^2t_{d,1}^2,
c_d^2t_{d,2}^2)
J_{\rm can}.
\]

Therefore

\[
\boxed{
[H_u,H_d]=0.
}
\]

Since each spectrum is simple, both operators have the same left-handed
eigenvectors. Up to phases and a common ordering convention,

\[
\boxed{
V_{\rm CKM}=I_3.
}
\]

The Jarlskog invariant vanishes:

\[
\boxed{J_{\rm CKM}=0.}
\]

Thus distinct diagonal quark hierarchies do not by themselves generate
mixing.

---

## 8. Required noncommuting action object

A nontrivial CKM matrix requires

\[
[H_u,H_d]\neq0.
\]

This can arise only if the action supplies a relative left-handed incidence
map between the up and down family modules.

Let

\[
K_{ud}:\mathcal F_d\to\mathcal F_u
\]

be the action-derived charged-current cross-Gram/current kernel. Its polar
decomposition is

\[
K_{ud}=W_{ud}|K_{ud}|.
\]

When \(K_{ud}\) is full rank, \(W_{ud}\) is unitary.

The common left-handed identifications must then satisfy

\[
\boxed{
J_uJ_d^\dagger=W_{ud}
}
\]

up to family rephasings fixed by the charged-current convention.

Equivalently, on the common quark-doublet space,

\[
\boxed{
V_{\rm CKM}
\simeq
\operatorname{Pol}(K_{ud}),
}
\]

after ordering the up and down mass eigenstates and removing unphysical
diagonal phases.

This is the smallest action-owned object capable of producing mixing without
inserting an arbitrary unitary matrix.

---

## 9. Exact candidate definition of the cross kernel

The required kernel must come from one mixed second variation or current
pairing, for example

\[
\boxed{
(K_{ud})_{ij}
=
\left\langle
u_i^{(u)},
\,
\mathcal J_+^{\rm action}
u_j^{(d)}
\right\rangle_{\rm common}
}
\]

where \(\mathcal J_+^{\rm action}\) is the normalized \(SU(2)_L\) raising
current on the common attachment/boundary domain.

Equivalent Hessian language is

\[
\boxed{
(K_{ud})_{ij}
\propto
\frac{\delta^2S_{\rm strat}}
{\delta\bar u_{L,i}\,\delta d_{L,j}}
\bigg|_{\rm charged\ current,\ background}.
}
\]

The kernel must satisfy:

1. common-domain normalization;
2. \(SU(2)_L\) current ownership;
3. gauge covariance;
4. full rank;
5. basis covariance;
6. no fitted entries;
7. no measured CKM input;
8. compatibility with the exact family projectors;
9. preservation of neutral-current family centrality.

---

## 10. What can and cannot be promoted

### Derived conditionally

- exact up and down spectral operators;
- positive dimensionless quark hierarchy seeds;
- exact middle-up \(1/2\) dressing;
- local gauge-invariant Yukawa operator forms;
- left-handed response operators;
- proof that canonical same-slot attachment yields \(V_{\rm CKM}=I\);
- polar-decomposition route from one action-owned cross kernel to CKM.

### Not yet derived

- sector-wide absolute quark scales \(c_u,c_d\);
- a nonzero cross-sector kernel \(K_{ud}\);
- nontrivial CKM angles;
- a CKM phase or Jarlskog invariant;
- RG-transported quark masses.

No arbitrary matrix is inserted to bypass these gates.

---

## 11. Hindsight 20/20 classification

### VALIDATED

- The frozen up/down ledgers generate distinct positive hierarchy seeds.
- The middle-up virtual-door factor is compatible with the spectral operator.
- Both Yukawa terms can be placed in the intrinsic \(M_4\) action.
- Right-handed identifications do not affect CKM.
- A single common left-handed cross kernel is sufficient in principle.
- Polar decomposition gives the canonical unitary part of that kernel.

### INVALIDATED

- Assuming distinct up/down eigenvalues automatically produce CKM mixing.
- Using the same ordered family projectors and claiming a nontrivial CKM
  matrix.
- Inserting a historical CKM screen directly as the action intertwiner.
- Choosing an arbitrary relative unitary \(J_uJ_d^\dagger\).

### OPEN

- Action derivation of \(K_{ud}\).
- Absolute up/down source normalizations.
- CP orientation of the cross kernel.
- Common-scheme transport and external comparison.

---

## 12. Verdicts

\[
\boxed{
\texttt{
BHSM\_ACTION\_OWNED\_UP\_DOWN\_YUKAWA\_SPECTRAL\_PAIR\_CONSTRUCTED\_CONDITIONALLY
}
}
\]

\[
\boxed{
\texttt{
BHSM\_CANONICAL\_COMMON\_FAMILY\_IDENTIFICATION\_FORCES\_TRIVIAL\_CKM
}
}
\]

\[
\boxed{
\texttt{
BHSM\_NONTRIVIAL\_CKM\_BLOCKED\_BY\_MISSING\_ACTION\_OWNED\_UP\_DOWN\_CROSS\_GRAM\_CURRENT\_KERNEL
}
}
\]

Exact next object:

\[
\boxed{
\texttt{
ACTION\_NORMALIZED\_SU2L\_RAISING\_CURRENT\_CROSS\_GRAM\_KERNEL\_ON\_FROZEN\_UP\_DOWN\_FAMILY\_MODULES
}
\]
