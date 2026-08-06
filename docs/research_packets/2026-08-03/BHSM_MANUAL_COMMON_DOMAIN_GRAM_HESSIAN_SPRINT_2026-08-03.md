# BHSM Manual Common-Domain Gram–Hessian Sprint

**Date:** 2026-08-03  
**Repository baseline:** BHSM v11.3, PR #217, merge `3e324a05e50b8128d28b84968b4ef3d2b064dd73`  
**Target:** `ACTION_NORMALIZED_CORE_WALL_RESPONSE_GRAM_HESSIAN_ON_COMMON_ATTACHMENT_DOMAIN`

## 1. Selected common-domain coordinates

Use the v11.3 reciprocal attachment domain with:

\[
I_C=Q_H(G_8),\qquad I_W=g_5,\qquad I_W=\upsilon I_C.
\]

The action-normalized coordinates are:

- \(q_C\): canonical logarithmic horizontal core-incidence response;
- \(q_W\): canonical compatible wall-incidence response;
- \(q_D\): canonical relational-depth response.

The core coordinate is obtained from the finite-radius degree-one collective envelope branch. If \(R\) is its radius and \(Q_H(G_8)\) is homogeneous of degree two in \(R\), then

\[
\delta\ln I_C=2\frac{\delta R}{R_0}.
\]

Canonical normalization removes the coordinate Jacobian, so the core stiffness is the invariant frequency ratio

\[
h_C=\omega_C^2
=
\frac{V_C''(R_0)}{M_{RR}(R_0)}
=
\frac{30\kappa_1A_2R_0^3}
{\kappa_1D_2R_0^5+D_8/R_0}.
\]

Every factor in the numerator and denominator is positive on the finite-radius \(p=2+p=8\) branch. Therefore

\[
\boxed{h_C>0.}
\]

The strict fixed-\(h\) wall branch has a positive same-domain kinetic coefficient

\[
k_W=6.673443432880105
\]

and vanishing quadratic and cubic potential coefficients. Its first local interaction is quartic. After canonical normalization,

\[
\boxed{h_W=0}
\]

at the critical attachment point.

The ground relational-depth entry is taken in the declared action normalization:

\[
h_D=1.
\]

No independent inherited core–wall, core–depth, or wall–depth potential block is inserted. The v7.1 parent KKT Hessian is stratum-block-diagonal before compatibility reduction; the mixed entries below come from reciprocal attachment.

## 2. Canonical reciprocal normalization

Use the primitive normalized representative

\[
\rho_0=1,\qquad
\lambda_D=1,\qquad
s=\frac{\rho_0}{4\lambda_D^2}=\frac14.
\]

The action-normalized Gram matrix in the order \((q_C,q_D,q_W)\) is

\[
G=
\begin{pmatrix}
1&3/4&-1/2\\
3/4&7/4&-3/4\\
-1/2&-3/4&1
\end{pmatrix}.
\]

Its leading principal minors are

\[
1,\qquad \frac{19}{16},\qquad \frac34.
\]

Hence

\[
\boxed{G>0.}
\]

## 3. Common-domain Hessian

Let \(h=h_C\). The canonical reciprocal Hessian is

\[
\boxed{
H(h)=
\begin{pmatrix}
h+1/4&1/4&1/8\\
1/4&1&1/4\\
1/8&1/4&1/4
\end{pmatrix}.
}
\]

Its leading principal minors are

\[
\Delta_1=h+\frac14,
\]

\[
\Delta_2=h+\frac{3}{16},
\]

\[
\Delta_3=\det H=\frac{6h+1}{32}.
\]

Therefore

\[
\boxed{
H>0\quad\Longleftrightarrow\quad h>-\frac16.
}
\]

Since the action-derived collective core branch gives \(h_C>0\),

\[
\boxed{H>0}
\]

without tuning the numerical core profile.

This is the central profile-independent stability theorem of the sprint.

## 4. Full generalized response spectrum

The action-normalized response roots solve

\[
\det(H-\lambda G)=0.
\]

The exact cubic is

\[
\boxed{
192\lambda^3
-(304h+364)\lambda^2
+(464h+133)\lambda
-(48h+8)=0.
}
\]

For every \(h>-1/6\), \(G>0\) and \(H>0\), so all three generalized eigenvalues are real and positive.

The cubic discriminant is

\[
16Q(h),
\]

where

\[
Q(h)=
906416128h^4
-908940800h^3
+87747088h^2
+80303592h
+16773569.
\]

An exact Sturm calculation gives two sign variations at both
\(h=-\infty\) and \(h=+\infty\), so \(Q\) has no real roots. Since
\(Q(0)=16773569>0\),

\[
Q(h)>0\quad\text{for all real }h.
\]

Thus the full response spectrum is always simple:

\[
\boxed{\lambda_1<\lambda_2<\lambda_3.}
\]

## 5. Exact KKT attachment constraint

The v11.3 multiplier equation linearizes to

\[
-q_C+q_D+q_W=0
\]

in the normalized representative. The constraint row and tangent basis are

\[
B=(-1,1,1),
\]

\[
N=
\begin{pmatrix}
1&1\\
0&1\\
1&0
\end{pmatrix},
\qquad BN=0.
\]

The physical tangent matrices are

\[
G_\parallel=N^TGN
=
\begin{pmatrix}
1&1/2\\
1/2&17/4
\end{pmatrix},
\]

\[
H_\parallel=N^THN
=
\begin{pmatrix}
h+3/4&h+7/8\\
h+7/8&h+7/4
\end{pmatrix}.
\]

Their determinants are

\[
\det G_\parallel=4,
\]

\[
\det H_\parallel=\frac{48h+35}{64}.
\]

Therefore the exact constrained tangent Hessian is positive for

\[
h>-\frac{35}{48}.
\]

The core theorem \(h_C>0\) again lies safely inside this domain.

## 6. Exact physical tangent roots

The two KKT-tangent restoring roots solve

\[
\det(H_\parallel-\mu G_\parallel)=0,
\]

or

\[
\boxed{
256\mu^2-(272h+260)\mu+(48h+35)=0.
}
\]

Hence

\[
\boxed{
\mu_\pm=
\frac{
68h+65
\pm
\sqrt{4624h^2+5768h+1985}
}{128}.
}
\]

The internal discriminant polynomial is strictly positive for all real \(h\)
because its discriminant is \(-3444736<0\) and its leading coefficient is
positive. Thus the two KKT-tangent modes are always nondegenerate.

For \(h>0\),

\[
\boxed{0<\mu_-<\mu_+.}
\]

## 7. Representative action-normalized core value

The stored degree-one collective representative gives

\[
h_C=\omega_C^2=0.181391690148362.
\]

At this value, the full generalized response roots are

\[
\lambda_1=0.092869094124559,
\]

\[
\lambda_2=0.651077903297987,
\]

\[
\lambda_3=1.439089845312360.
\]

The corresponding restoring-stiffness square-root ratio is

\[
\boxed{
1:2.647773757:3.936482723.
}
\]

These are the three positive response roots of the unconstrained
three-coordinate pencil.

The exact KKT-tangent roots are

\[
\mu_-=0.163382147899908,
\]

\[
\mu_+=1.044971522882727,
\]

with square-root ratio

\[
\boxed{1:2.529006392.}
\]

The normalized tangent eigenvectors in the order \((q_C,q_D,q_W)\) are
approximately

\[
v_-=(0.125596,-0.466681,0.592277),
\]

\[
v_+=(-1.023096,-0.179468,-0.843628),
\]

and satisfy \(Bv_\pm=0\).

## 8. Physical interpretation of mode counts

The response pencil has three positive simple coordinate-response roots.
The exact multiplier constraint leaves two independent local attachment
motions.

This does not remove the three-generation architecture. The three families
live in the independent exact \(C_3\) projector space, not in the attachment
constraint normal.

A particle-sector spectrum must therefore:

1. select one stable attachment branch \(\mu_r\);
2. pull the action response onto the three exact triality projectors
   \(P_0,P_1,P_2\);
3. diagonalize the resulting Hermitian \(C_3\) response.

For

\[
H_{\rm gen}=aI+x(C+C^2)+iy(C-C^2),
\]

the family stiffnesses are

\[
\ell_0=a+2x,
\]

\[
\ell_1=a-x-\sqrt3\,y,
\]

\[
\ell_2=a-x+\sqrt3\,y.
\]

The charged-lepton restoring spectrum would then be formed from the selected
attachment branch and these three action-derived family projections. No
measured lepton mass is used in this construction.

## 9. Hindsight 20/20 classification

### VALIDATED

- The core degree-one collective branch has strictly positive
  action-normalized stiffness.
- The critical wall branch has positive kinetic norm and zero quadratic
  potential curvature.
- The canonical reciprocal Gram matrix is strictly positive.
- The common-domain Hessian is strictly positive for \(h_C>-1/6\).
- The full generalized response spectrum has three positive nondegenerate
  roots for the action-derived \(h_C>0\).
- The exact KKT tangent domain has two positive nondegenerate restoring modes.
- No fitted coefficient, new field, mediator, or mass datum is required.

### REFINED

- Three response coordinates do not equal three independent KKT tangent
  motions.
- The lepton triplet must be produced by the exact \(C_3\) family projector
  space after selecting a stable attachment branch.
- The representative numerical roots are action-normalized dimensionless
  stiffnesses, not absolute particle masses.

### OPEN

- The exact action projection of the selected attachment branch onto
  \(P_0,P_1,P_2\).
- The G2/C3 imbalance coefficients \(a,x,y\).
- The absolute unit bridge.
- Assignment of the selected stable attachment branch to the charged-lepton
  carrier.

## 10. Sprint verdict

\[
\boxed{
\texttt{BHSM\_COMMON\_ATTACHMENT\_GRAM\_HESSIAN\_POSITIVE\_AND\_SIMPLE}
}
\]

\[
\boxed{
\texttt{BHSM\_MARK\_II\_UNCONDITIONAL\_ON\_THE\_ACTION\_SELECTED\_FINITE\_RADIUS\_CORE\_BRANCH}
}
\]

The next exact object is

\[
\boxed{
\texttt{ACTION\_PROJECTED\_C3\_TRIALITY\_RESPONSE\_ON\_SELECTED\_STABLE\_ATTACHMENT\_BRANCH}
}
\]

with the target

\[
m_e:m_\mu:m_\tau
=
\sqrt{\ell_{(1)}}:
\sqrt{\ell_{(2)}}:
\sqrt{\ell_{(3)}}.
\]
