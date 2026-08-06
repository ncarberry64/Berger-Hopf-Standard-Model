# BHSM Manual Stable-Attachment-to-Triality Projection Sprint

**Date:** 2026-08-03  
**Repository baseline:** BHSM v11.3, PR #217, merge `3e324a05e50b8128d28b84968b4ef3d2b064dd73`  
**Input result:** `BHSM_COMMON_ATTACHMENT_GRAM_HESSIAN_POSITIVE_AND_SIMPLE`  
**Target:** Select one physical attachment mode and project it onto the exact three Spin(8)/C3 family projectors.

## 1. Stable attachment mode selected

The two physical common-domain attachment roots are

\[
\mu_\pm=
\frac{
68h_C+65
\pm\sqrt{4624h_C^2+5768h_C+1985}
}{128}.
\]

Select

\[
\boxed{\mu_-}
\]

because it is the smaller positive generalized eigenvalue and therefore the
ground restoring branch of the stable attachment system.

For the stored action-normalized core representative

\[
h_C=0.181391690148362,
\]

\[
\boxed{\mu_-=0.1633821478999081549.}
\]

No measured particle mass enters this selection.

## 2. Exact attachment eigenvector

Use tangent coordinates \(z=(z_1,z_2)\) with

\[
N=
\begin{pmatrix}
1&1\\
0&1\\
1&0
\end{pmatrix},
\qquad
v_-=Nz.
\]

Choose \(z_1=1\) and define

\[
r=\frac{z_2}{z_1}
=
-\frac{h_C+\frac34-\mu_-}
{h_C+\frac78-\frac12\mu_-}.
\]

Then, in the order \((q_C,q_D,q_W)\),

\[
v_-=(1+r,r,1).
\]

The exact constraint is automatic:

\[
-(1+r)+r+1=0.
\]

Define

\[
t=1+r=\frac{q_C}{q_W}.
\]

For the representative branch,

\[
r=-0.7879440409547453337,
\]

\[
t=0.2120559590452546663.
\]

A \(G_\parallel\)-normalized representative is approximately

\[
v_-=(0.12559584,-0.46668102,0.59227686),
\]

up to an irrelevant overall sign.

## 3. Exact C3 family projectors

Let

\[
C=
\begin{pmatrix}
0&0&1\\
1&0&0\\
0&1&0
\end{pmatrix},
\qquad
\omega=e^{2\pi i/3}.
\]

The exact projectors are

\[
\boxed{
P_k=\frac13\left(I+\omega^{-k}C+\omega^{-2k}C^2\right),
\qquad k=0,1,2.
}
\]

They satisfy

\[
P_iP_j=\delta_{ij}P_i,
\qquad
P_0+P_1+P_2=I,
\qquad
CP_k=\omega^kP_k.
\]

## 4. Reciprocal triality phase twist

Apply the declared core/wall phase twist

\[
D_\theta=
\operatorname{diag}
\left(e^{-i\pi/3},1,e^{+i\pi/3}\right).
\]

The selected attachment carrier is

\[
\psi_-=D_\theta v_-.
\]

The normalized projector weights are

\[
\rho_k=
\frac{\psi_-^\dagger P_k\psi_-}
{\psi_-^\dagger\psi_-}.
\]

For any real attachment tangent vector satisfying

\[
-q_C+q_D+q_W=0,
\]

write \(q_W=1\), \(q_C=t\), and \(q_D=t-1\). Direct exact projection gives

\[
\boxed{
\rho_0=\rho_2=
\frac{3t^2-3t+1}{6(t^2-t+1)}
}
\]

and

\[
\boxed{
\rho_1=
\frac{2}{3(t^2-t+1)}.
}
\]

These obey

\[
2\rho_0+\rho_1=1.
\]

The equality

\[
\boxed{\rho_0=\rho_2}
\]

is exact and independent of which physical attachment eigenmode is selected.
It follows from the reciprocal \(\pm\pi/3\) phase law together with the exact
attachment constraint.

## 5. Canonical C3 projection of the response

Let the selected rank-one response be

\[
R_-=
\mu_-
\frac{|\psi_-\rangle\langle\psi_-|}
{\langle\psi_-,\psi_-\rangle}.
\]

The canonical conditional expectation onto the C3 commutant is

\[
\mathcal E_{C_3}(R_-)
=
\frac13\sum_{n=0}^{2}C^nR_-C^{-n}.
\]

Equivalently,

\[
\boxed{
H_{\rm fam}^{(-)}
=
\sum_{k=0}^{2}P_kR_-P_k
=
\sum_{k=0}^{2}\ell_kP_k,
}
\]

where

\[
\boxed{\ell_k=\mu_-\rho_k.}
\]

This is the unique orthogonal projection of the selected response onto the
algebra of C3-compatible Hermitian family operators.

## 6. Numerical three-projector response

For

\[
h_C=0.181391690148362,
\]

the exact-mode projection gives

\[
\rho_0=\rho_2
=
0.09979754753057689239,
\]

\[
\rho_1
=
0.8004049049388462152.
\]

Therefore

\[
\boxed{
\ell_0=\ell_2
=
0.01630513767068882769,
}
\]

\[
\boxed{
\ell_1
=
0.1307718725585304995.
}
\]

The square-root restoring hierarchy is

\[
\boxed{
\sqrt{\ell_0}:\sqrt{\ell_2}:\sqrt{\ell_1}
=
1:1:2.832011002.
}
\]

The projection is positive but not threefold nondegenerate.

## 7. Exact C3 commutant coefficients

Every Hermitian C3-compatible family response has the form

\[
H_{\rm gen}
=
aI+x(C+C^2)+iy(C-C^2).
\]

For the projected lower attachment branch,

\[
a=\frac{\mu_-}{3},
\]

\[
x=\frac{\ell_0-a}{2},
\]

and the exact degeneracy condition is

\[
\boxed{y=\sqrt3\,x.}
\]

Numerically,

\[
a=0.05446071596663605164,
\]

\[
x=-0.01907778914797361198,
\]

\[
y=-0.03304370010037645312.
\]

The family roots are

\[
a+2x=\ell_0,
\]

\[
a-x-\sqrt3y=\ell_1,
\]

\[
a-x+\sqrt3y=\ell_2=\ell_0.
\]

Thus the reciprocal attachment projection lands exactly on one of the
C3-discriminant planes.

## 8. Why the existing G2 structure does not yet split the pair

The repository's selected G2 reduction is triality compatible: all three
Spin(8) carriers restrict to the same \(1+7\) G2 module, and the same unit
section is transported through the exact triality isomorphisms.

The G2 complex structure supplies conjugate rank-three polarizations, but the
current action does not supply a family-dependent scalar coefficient that
moves the attachment response away from

\[
y=\sqrt3x.
\]

Therefore G2 compatibility alone preserves the exact twofold result obtained
above.

## 9. Smallest C3-preserving imbalance operator

The smallest Hermitian operator that preserves C3 while moving the spectrum
off the degeneracy plane is

\[
\boxed{
\Delta H_{\rm imb}
=
\delta_{\rm G2/C3}\,i(C-C^2).
}
\]

It requires no new family projector and no breaking of C3. It changes

\[
y\longrightarrow y+\delta_{\rm G2/C3}.
\]

The three roots become

\[
\boxed{
\ell_0'=\ell_0,
}
\]

\[
\boxed{
\ell_1'=\ell_1-\sqrt3\,\delta_{\rm G2/C3},
}
\]

\[
\boxed{
\ell_2'=\ell_0+\sqrt3\,\delta_{\rm G2/C3}.
}
\]

All three remain positive when

\[
-\frac{\ell_0}{\sqrt3}
<
\delta_{\rm G2/C3}
<
\frac{\ell_1}{\sqrt3}.
\]

They are pairwise nondegenerate provided

\[
\delta_{\rm G2/C3}
\notin
\left\{
0,\,
\frac{\ell_1-\ell_0}{\sqrt3},\,
\frac{\ell_1-\ell_0}{2\sqrt3}
\right\}.
\]

Numerically the positivity interval is

\[
\boxed{
-0.0094137750
<
\delta_{\rm G2/C3}
<
0.0755011761.
}
\]

The coefficient must be extracted from the action. It is not fitted here.

## 10. Exact action-extraction formula

For any action-derived family response \(H_{\rm family}\), define

\[
x=
\frac16
\operatorname{Tr}
\left[(C+C^2)H_{\rm family}\right],
\]

\[
y=
\frac16
\operatorname{Tr}
\left[i(C-C^2)H_{\rm family}\right].
\]

The required G2/C3 imbalance invariant is

\[
\boxed{
\delta_{\rm G2/C3}
=
y-\sqrt3x.
}
\]

The current reciprocal attachment projection gives

\[
\boxed{\delta_{\rm G2/C3}=0.}
\]

A nonzero action-derived value is exactly what is required to obtain three
nondegenerate generation stiffnesses.

## 11. Sprint verdict

### Derived

- The lower stable attachment mode is selected without measured input.
- Its exact constrained eigenvector is constructed.
- Its response is projected onto the exact \(P_0,P_1,P_2\) projectors.
- All three projected stiffnesses are positive.
- The current projection yields an exact twofold degeneracy.
- The degeneracy is independent of choosing the lower or upper tangent mode.
- The smallest C3-preserving imbalance operator and its exact positivity
  interval are derived.

### Invalidated

- The reciprocal \(\pm\pi/3\) twist by itself does **not** produce three
  nondegenerate family roots on the exact attachment tangent domain.
- Selecting the other stable attachment mode does not remove this structural
  equality.

### Open

- The action-owned value of \(\delta_{\rm G2/C3}\).
- The exact parent term or constraint reduction producing that coefficient.
- The absolute physical mass scale.

## 12. Primary verdict

\[
\boxed{
\texttt{
BHSM\_LOWER\_STABLE\_ATTACHMENT\_MODE\_PROJECTED\_ONTO\_EXACT\_C3\_FAMILY\_PROJECTORS
}
}
\]

with the sharpened result

\[
\boxed{
\texttt{
BHSM\_RECIPROCAL\_TRIALITY\_PROJECTION\_POSITIVE\_BUT\_TWOFOLD\_DEGENERATE
}
}
\]

and exact next object

\[
\boxed{
\texttt{
ACTION\_OWNED\_G2\_ORIENTED\_C3\_ODD\_RESPONSE\_COEFFICIENT
}
}
\]

defined by

\[
\boxed{
\delta_{\rm G2/C3}=y-\sqrt3x.
}
\]
