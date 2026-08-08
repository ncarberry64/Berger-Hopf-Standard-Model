# BHSM Manual Action-Owned G2/C3-Odd Coefficient Sprint

**Date:** 2026-08-03  
**Repository baseline:** BHSM v11.3, PR #217, merge `3e324a05e50b8128d28b84968b4ef3d2b064dd73`  
**Input milestone:** `BHSM_COMMON_ATTACHMENT_GRAM_HESSIAN_POSITIVE_AND_SIMPLE`  
**Target:** `ACTION_OWNED_G2_ORIENTED_C3_ODD_RESPONSE_COEFFICIENT`

---

## 1. Correction to the fixed-octave projection

The previous projection applied one fixed \(k=0\) rank-one attachment response to all
three exact family projectors. Together with the reciprocal \(\pm\pi/3\) phase
twist, that operation necessarily produced

\[
\ell_0=\ell_2.
\]

The exact BHSM family ledger does not assign one common octave to all three
families. In the charged-lepton sector, the three family projectors own the
distinct boundary modes

\[
P_0:\ (k,j)=(0,0),
\qquad
P_1:\ (k,j)=(5,2),
\qquad
P_2:\ (k,j)=(9,3).
\]

The correct action projection therefore evaluates one selected attachment
branch on each projector's own \(S^3\) spectral eigenvalue.

---

## 2. Action-normalized KKT attachment pencil

Use the v11.3 whitened coordinates

\[
(q_C,q_W,x_D),
\qquad
x_D=q_D/\lambda_D.
\]

The exact attachment constraint is

\[
-q_C+q_W+x_D=0.
\]

A tangent basis is

\[
N=
\begin{pmatrix}
1&1\\
1&0\\
0&1
\end{pmatrix},
\]

and the reduced kinetic Gram matrix is

\[
K_\parallel=N^TN
=
\begin{pmatrix}
2&1\\
1&2
\end{pmatrix}.
\]

Let

\[
h=h_C>0
\]

be the action-normalized finite-radius core stiffness. At the critical wall
point,

\[
h_W=0.
\]

For one \(S^3\) octave with eigenvalue

\[
K=k(k+2),
\]

the relational-depth stiffness is

\[
h_D(K)=1+K.
\]

The tangent Hessian is then

\[
H_\parallel(K)
=
\begin{pmatrix}
h&h\\
h&h+1+K
\end{pmatrix}.
\]

---

## 3. Exact lower attachment branch

The generalized characteristic equation is

\[
\det\!\left(H_\parallel(K)-\mu K_\parallel\right)=0,
\]

or

\[
\boxed{
3\mu^2-2(h+K+1)\mu+h(K+1)=0.
}
\]

The two roots are

\[
\mu_\pm(K;h)
=
\frac{
h+K+1
\pm
\sqrt{(K+1)^2-h(K+1)+h^2}
}{3}.
\]

Select the lower positive branch:

\[
\boxed{
\mu_-(K;h)
=
\frac{
h+K+1
-
\sqrt{(K+1)^2-h(K+1)+h^2}
}{3}.
}
\]

For \(h>0\) and \(K\ge0\), both generalized roots are real and positive because

\[
\mu_+\mu_-=\frac{h(K+1)}{3}>0,
\]

\[
\mu_++\mu_-=\frac{2(h+K+1)}{3}>0,
\]

and the discriminant is strictly positive.

---

## 4. Strict octave monotonicity

Set

\[
t=K+1>0.
\]

Then

\[
\frac{\partial\mu_-}{\partial K}
=
\frac13
\left[
1-
\frac{2t-h}
{2\sqrt{t^2-ht+h^2}}
\right].
\]

The identity

\[
4(t^2-ht+h^2)-(2t-h)^2=3h^2
\]

is strictly positive for \(h>0\). Therefore

\[
\left|2t-h\right|
<
2\sqrt{t^2-ht+h^2},
\]

and hence

\[
\boxed{
\frac{\partial\mu_-}{\partial K}>0.
}
\]

The lower attachment response is therefore strictly ordered by the exact
boundary octave.

---

## 5. Exact charged-lepton family octaves

The round \(S^3\) boundary operator is

\[
-\Delta_{S^3}Y_{k\ell m}=k(k+2)Y_{k\ell m}.
\]

For the action-owned charged-lepton family modes:

\[
K_0=0(0+2)=0,
\]

\[
K_1=5(5+2)=35,
\]

\[
K_2=9(9+2)=99.
\]

Thus

\[
K_0<K_1<K_2.
\]

By strict monotonicity,

\[
\boxed{
\mu_0<\mu_1<\mu_2,
}
\]

where

\[
\mu_f=\mu_-(K_f;h_C).
\]

This gives three positive, nondegenerate action-normalized family response
stiffnesses on one selected stable attachment branch.

---

## 6. Exact C3 family response

Let \(P_0,P_1,P_2\) be the exact Spin(8)/\(C_3\) family projectors. The correct
family operator is

\[
\boxed{
H_\ell^{(-)}(h_C)
=
\mu_0P_0+\mu_1P_1+\mu_2P_2.
}
\]

This is already diagonal in the exact family-projector decomposition and
commutes with the triality cycle \(C\).

Write it in the Hermitian \(C_3\) commutant basis:

\[
H_\ell^{(-)}
=
aI+x(C+C^2)+iy(C-C^2).
\]

The exact coefficients are

\[
\boxed{
a=\frac{\mu_0+\mu_1+\mu_2}{3},
}
\]

\[
\boxed{
x=\frac{2\mu_0-\mu_1-\mu_2}{6},
}
\]

\[
\boxed{
y=\frac{\mu_2-\mu_1}{2\sqrt3}.
}
\]

---

## 7. Action-owned G2/C3-odd coefficient

Define the degeneracy-plane displacement by

\[
\delta_{\rm G2/C3}=y-\sqrt3x.
\]

Substituting the exact projector coefficients gives

\[
\boxed{
\delta_{\rm G2/C3}(h_C)
=
\frac{\mu_2-\mu_0}{\sqrt3}.
}
\]

Equivalently,

\[
\boxed{
\delta_{\rm G2/C3}(h_C)
=
\frac{
\mu_-(99;h_C)-\mu_-(0;h_C)
}{\sqrt3}.
}
\]

Because the lower branch is strictly increasing in \(K\),

\[
\boxed{
\delta_{\rm G2/C3}(h_C)>0
\qquad
\text{for every }h_C>0.
}
\]

The coefficient is therefore fixed by:

1. the action-derived finite-radius core stiffness \(h_C\);
2. the v11.3 common attachment KKT pencil;
3. the exact charged-lepton \(S^3\) octave assignments;
4. the exact \(C_3\) family projectors.

No independent odd coefficient, mediator, or measured mass is required.

---

## 8. Representative action-normalized value

Use the stored finite-radius core representative

\[
h_C=0.181391690148362.
\]

Then

\[
\boxed{
\mu_0=0.0862060050795243,
}
\]

\[
\boxed{
\mu_1=0.0905813107333889,
}
\]

\[
\boxed{
\mu_2=0.0906546790821877.
}
\]

The exact commutant coefficients evaluate to

\[
\boxed{
a=0.0891473316317003,
}
\]

\[
\boxed{
x=-0.00147066327608801,
}
\]

\[
\boxed{
y=0.0000211796179644791,
}
\]

and therefore

\[
\boxed{
\delta_{\rm G2/C3}
=
0.00256844313297461.
}
\]

The action-normalized square-root stiffness hierarchy is

\[
\boxed{
\sqrt{\mu_0}:\sqrt{\mu_1}:\sqrt{\mu_2}
=
1:1.025058860:1.025476161.
}
\]

This is a nondegenerate geometric seed, not yet the full charged-lepton mass
hierarchy.

---

## 9. Relationship to the existing BHSM degree ledger

For the two excited charged-lepton modes,

\[
\Omega_\ell=-q+2j=3.
\]

Thus the common sector degree correctly identifies them as members of one
charged-lepton response class, but it does not distinguish their family
positions.

Their exact geometric positions differ:

\[
(q,j)=(1,2)
\quad\Rightarrow\quad
q^2+j^2=5,
\]

\[
(q,j)=(3,3)
\quad\Rightarrow\quad
q^2+j^2=18,
\]

and their \(S^3\) octaves differ:

\[
K_1=35,
\qquad
K_2=99.
\]

The \(C_3\)-odd coefficient is therefore sourced by the octave-position
difference inside the common \(\Omega_\ell=3\) sector.

---

## 10. What this closes

The previous fixed-\(k\) result

\[
\delta_{\rm G2/C3}=0
\]

was a consequence of applying one response to all projectors.

The corrected action-owned construction gives

\[
\boxed{
\delta_{\rm G2/C3}>0
}
\]

and hence three positive, nondegenerate family response eigenvalues.

The generation-splitting coefficient is now derived without fitting.

---

## 11. Remaining hierarchy amplification

The lower attachment branch satisfies

\[
\lim_{K\to\infty}\mu_-(K;h_C)=\frac{h_C}{2}.
\]

Therefore the raw stiffness splitting is naturally bounded and modest. It
provides a stable three-family seed but does not by itself generate the full
electron–muon–tau hierarchy.

The next action object is the nonlinear map that converts the stable
attachment response and geometric octave position into the full Berger–Hopf
overlap response:

\[
\boxed{
\mathcal Z_f
=
\mathcal Z
\left(
\mu_f,\,
K_f,\,
q_f^2+j_f^2,\,
\Omega_f
\right).
}
\]

It must be derived from the action and evaluated without measured mass input.

---

## 12. Hindsight 20/20 status

### VALIDATED

- One lower stable attachment branch can serve all three family projectors.
- Each family projector carries its own action-owned \(S^3\) octave.
- The lower response is strictly increasing with octave.
- The resulting family stiffnesses are positive and nondegenerate.
- The \(C_3\)-odd coefficient is fixed analytically.
- No free \(y_\sigma\), new mediator, or measured mass is needed.

### REFINED

- A single fixed-\(k\) projector average is not the correct family response.
- The reciprocal phase structure organizes the projectors, while the
  action-owned octave spectrum supplies the nondegeneracy.
- The common \(\Omega_\ell=3\) degree defines the sector; octave position
  distinguishes the generations.

### OPEN

- The action-derived nonlinear attachment-to-Berger overlap response.
- The absolute physical scale.
- Final identification of the sorted stiffness roots with
  \(e,\mu,\tau\) after overlap amplification.

---

## 13. Primary verdict

\[
\boxed{
\texttt{
BHSM\_ACTION\_OWNED\_G2\_C3\_ODD\_RESPONSE\_COEFFICIENT\_DERIVED\_FROM\_FAMILY\_OCTAVE\_SPLITTING
}
}
\]

\[
\boxed{
\texttt{
BHSM\_THREE\_FAMILY\_LOWER\_ATTACHMENT\_RESPONSE\_POSITIVE\_AND\_NONDEGENERATE
}
}
\]

Exact next object:

\[
\boxed{
\texttt{
ACTION\_OWNED\_ATTACHMENT\_TO\_BERGER\_OVERLAP\_RESPONSE\_MAP
}
}
\]
