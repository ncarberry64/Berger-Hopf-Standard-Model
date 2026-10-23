# Hopf-charge bound for a stationary-nodal great circle

## Result and scope

Let P be a real two-plane in R4, W=P-perp, and let A be a nonzero symmetric trace-free matrix satisfying A|P=0. On the round unit S3 set F_A(X)=X^TAX. This is precisely a real n=2 scalar with value and differential zero along the great circle S3 intersect P. Let J be any orthogonal complex structure on R4, representing a Hopf action. For an orthonormal basis e1,e2 of W define

\[
\kappa=|e_1^TJe_2|\in[0,1],\qquad
A_0=\frac{A+J^TAJ}{2},\quad
A_2=\frac{A-J^TAJ}{2}.
\]

The subscripts denote Hopf-neutral and absolute-charge-two sectors. Then

\[
\boxed{\quad
\frac{\|A_2\|_F^2}{\|A\|_F^2}
=\frac{1+\kappa^2}{2}\ge\frac12.
\quad}
\]

The quantity kappa is the absolute cosine of the Kahler angle of the transverse two-plane. It is independent of the choice or orientation of its orthonormal basis. All nonzero stationary-nodal scalars sharing the same great circle have the same charged fraction for fixed J, regardless of the transverse shear orientation or amplitude. If P is J-invariant, kappa=1 and the state is entirely charged.

For the actual Berger family with inverse fibre scale a>0 and physical radius R,

\[
h_{a,R}=R^2(h_H+a^{-2}\eta^2),
\]

the normalized scalar Rayleigh quotient is

\[
\boxed{\quad
\mathscr R_a(F_A)=\frac{8+4(a^2-1)f_2}{R^2},\qquad
\frac{\partial\mathscr R_a}{\partial(a^2)}
=\frac{4f_2}{R^2}\in\left[\frac2{R^2},\frac4{R^2}\right],
\quad}
\]

where f2=(1+kappa²)/2. This is a geometric susceptibility, not a light-transfer prediction on a squashed spacetime. In the round limit all n=2 sectors remain degenerate at 8/R². No preferred J, a, physical initial amplitude, or microscopic-to-cosmological action map is selected here.

## 1. Why the nodal condition is A|P=0

For an arbitrary STF A,

\[
F_A=X^TAX,\qquad
\nabla_{S^3}F_A=2(AX-F_AX).
\]

At a point, simultaneous vanishing of value and differential is equivalent to AX=0. Along an open nonzero segment of a great circle `X(chi)=cos(chi) X_o+sin(chi) n_o`, those X span P=span(X_o,n_o). Hence stationary-nodal behavior along that ray is equivalent to A|P=0. It is enough to check two independent points. Conversely A|P=0 gives both vanishing conditions at every point of that circle.

Symmetry implies A has no mixed P-W blocks. Trace freedom means its remaining 2×2 block C on W is trace free. Thus, in a basis adapted to W then P,

\[
A=\begin{pmatrix}C&0\\0&0\end{pmatrix},\qquad
C=\begin{pmatrix}u&v\\v&-u\end{pmatrix}.
\]

Every nonzero such C has eigenvalues +lambda,−lambda, with lambda²=u²+v². Therefore the great-circle condition is stronger than a stationary node at one point: it forces rank two, rather than allowing a rank-three transverse tidal matrix.

## 2. Exact trace identity

Write the restriction of the skew matrix J to W as

\[
J_{WW}=\begin{pmatrix}0&j\\-j&0\end{pmatrix},\qquad |j|=\kappa.
\]

Only this block can contribute to the following contraction because A vanishes on P. Multiplication of the displayed 2×2 matrices gives

\[
\begin{aligned}
\operatorname{tr}(AJ^TAJ)
&=\operatorname{tr}(C J_{WW}^T C J_{WW})\\
&=-j^2\operatorname{tr}(C^2)\\
&=-\kappa^2\|A\|_F^2.
\end{aligned}
\]

Equivalently choose C's eigenbasis: the two cross terms are `lambda*(-lambda)*j²`, while diagonal skew entries vanish. This proves the identity for every orthogonal complex J, including both orientation classes; no special quaternion parameterization is assumed.

The map T(A)=J^TAJ is an orthogonal involution on symmetric matrices. Therefore

\[
\begin{aligned}
\|A_2\|_F^2
&=\tfrac14\big(\|A\|_F^2+\|T(A)\|_F^2
-2\langle A,T(A)\rangle_F\big)\\
&=\tfrac12(1+\kappa^2)\|A\|_F^2.
\end{aligned}
\]

Likewise `||A0||²=(1−kappa²)||A||²/2`; the two sectors are orthogonal. Because J is orthogonal, kappa≤1. Equality kappa=1 holds exactly when W is J-invariant, which is equivalent to P being J-invariant. At equality A0=0.

The weaker statement that a nonzero purely neutral STF scalar has no stationary node follows, but the great-circle theorem is sharper: at least half of the normalized spatial power is charged, for **every** possible J.

## 3. Scalar normalization and the actual Berger operator

For normalized Haar measure dmu=dOmega3/(2 pi²),

\[
\int_{S^3}F_AF_B\,d\mu=\frac{\operatorname{tr}(AB)}{12}
\]

for symmetric trace-free A and B. This follows from the exact fourth moment

\[
\int X_iX_jX_kX_l\,d\mu
=\frac{\delta_{ij}\delta_{kl}+\delta_{ik}\delta_{jl}
+\delta_{il}\delta_{jk}}{24}.
\]

Consequently the matrix fraction f2 equals the scalar L2 power fraction. The Berger volume differs from the round volume by a constant a^(-1); normalized Haar measure is unchanged, and a common unnormalized constant also cancels from a Rayleigh quotient.

Let K(X)=JX be the unit-round Hopf generator. For this metric convention,

\[
\Delta_{a,R}=R^{-2}[\Delta_1+(a^2-1)K^2].
\]

The symmetric involution split obeys `[A0,J]=0`, `{A2,J}=0`, whence

\[
KF_{A_0}=0,\qquad K^2F_{A_2}=-4F_{A_2}.
\]

All round n=2 harmonics satisfy `−Delta1 F=8 F`. Thus the neutral sector has eigenvalue 8/R² and real dimension three; the charged sector has eigenvalue (4+4a²)/R² and real dimension six. Orthogonality gives the stated Rayleigh quotient and derivative. The relation is exact at every a>0 for the fixed spatial test function F_A and fixed R; no small-squashing expansion is needed. If a<1, the inequality for the quotient itself reverses relative to the ordering at a>1, but the susceptibility range is unchanged.

This agrees with the BHSM historical scalar spectrum

`lambda_(k,j)(a)=k(k+2)+(a²−1)(k−2j)²`

recovered from `Downloads/BHSM_ATTACHMENT_TO_BERGER_OVERLAP_HIERARCHY_2026-08-03.md`, section 4. Its charged-lepton restoring-map application is not used in this argument.

## 4. Connection to the declared round optical experiment

Along the nodal round great circle, the constant ambient vectors spanning W are a parallel screen basis: they remain tangent, perpendicular to the ray, and have zero ambient derivative. The spherical Hessian is

\[
\operatorname{Hess}_{S^3}F_A(U,V)
=2U^TAV-2F_A\langle U,V\rangle.
\]

The parallel screen block is therefore exactly 2C. It is nonzero and trace free, although scalar value and first derivative vanish all along the ray. In a screen basis rotated by E in O(2), it is `2 E^T C E`; at physical radius R it is divided by R². A scalar optical potential of the form `W_opt(eta,X)=T(eta)F_A(X)` has the same screen pattern multiplied by T(eta). This is the spatial reason the declared nodal preparation can alter the retained Jacobi/shear maps while eliminating value/gradient endpoint terms.

More than one independent C can be used. Every nonzero instantaneous linear combination still shares A|P=0 and satisfies the identical charged fraction for fixed P and J. This permits the parent paper's conditional multi-profile optical family without adding a single-profile alignment assumption.

The geometric theorem does not justify evolving the round R1 six-state system on a nonround metric. In particular A0 and A2 generally acquire different spectral behavior on a Berger sphere; a nodal cancellation between them need not persist under a new evolution. A nonround constrained action and optical projection must be rederived before treating the susceptibility as a strong-lensing observable. The present optical application remains on the declared round R1 branch.

## 5. Auxiliary-action nodal rigidity on a fixed Berger sphere

The following is an additional exact result for a declared free scalar action. It is **not** the constrained R1 metric/matter action or a reduction of the full BHSM parent action. Let

\[
\mathcal N_P=\{A=A^T,\ \operatorname{tr}A=0,\ A|P=0\}.
\]

This two-dimensional linear space is the stationary-nodal great-circle space. With fixed a,R,J use the scalar action

\[
S=\frac12\int dt\left[
\langle\dot A,\dot A\rangle-c_s^2\langle A,\mathcal L_a A\rangle
\right],\qquad c_s>0,
\]

where the pairing is the scalar Haar pairing (equivalently the Frobenius pairing divided by 12), and

\[
\mathcal L_a=\lambda_0P_0+\lambda_2P_2,\quad
\lambda_0=8/R^2,\quad\lambda_2=(4+4a^2)/R^2.
\]

Time is in physical units if c_s carries length/time; set c_s=1 in length-time units. The Euler equation is `Addot+c_s² L_a A=0`.

**Rigidity theorem.** If a≠1, a nonzero solution remains in N_P throughout a time interval with nonempty interior if and only if P is J-invariant and its initial position/velocity lie in N_P. For a=1, every N_P is invariant. The identically zero solution is always an exception to the nonzero condition.

**Necessity.** If A(t) belongs to N_P for the entire interval, so does its second derivative, since N_P is a fixed linear space. The equation gives L_a A in N_P. Because lambda0≠lambda2,

\[
P_0A=\frac{\lambda_2A-\mathcal L_aA}{\lambda_2-\lambda_0}\in\mathcal N_P.
\]

But a nonzero neutral STF matrix is invertible (its square is rho² I), whereas every member of N_P annihilates the two-plane P. Hence P0 A=0 throughout the interval. At any time when A≠0 it is purely charged, so the bound forces kappa=1. This is equivalent to J-invariance of P.

**Sufficiency.** If P is J-invariant, the bound gives P0 A=0 for every A in N_P. Thus L_a acts on N_P as lambda2 times the identity. The solution for initial A,V in N_P is

\[
A(t)=\cos[\omega_2(t-t_i)]A_i
+\frac{\sin[\omega_2(t-t_i)]}{\omega_2}V_i,
\qquad \omega_2=c_s\sqrt{\lambda_2},
\]

which stays in N_P. If a=1, L_a=(8/R²)I on all nine n=2 coordinates, so the same argument applies to every P with omega=sqrt(8)c_s/R. Standard uniqueness of this finite linear equation handles a nonzero solution that passes through A=0 at an isolated time.

The necessity argument also survives scalar damping and a scalar mass term,

`Addot+gamma(t) Adot+[c_s² L_a+m²(t) I]A=0`,

because A,Adot,Addot all lie in N_P if the solution does. These terms do not mix the two spatial sectors. This extension is an algebraic statement about a specified auxiliary equation, not an assertion that the cosmological physical response has this form. General sources, sector-dependent dynamics or metric constraints require their own analysis.

**Concrete rest preparation.** Take R=c_s=1, a=1.2, A_i=diag(1,−1,0,0), V_i=0, and P=span(e3,e4). For kappa=0 the exact solution is

\[
A(t)=\cos(\sqrt8\,t)A_0+
\cos(\sqrt{9.76}\,t)A_2,
\]

and its relative leakage into the forbidden nodal-plane columns is

\[
\frac{\|A(t)\Pi_P\|_F}{\|A_i\|_F}
=\frac12\left|\cos(\sqrt8\,t)-\cos(\sqrt{9.76}\,t)\right|.
\]

It begins as 0.44 t²+O(t⁴), while for kappa=1 the preparation is purely charged and this leakage is identically zero. The companion `check_hopf_nodal_rigidity.py` records exact/operator checks and a small numerical table for these two cases. They illustrate geometric scalar propagation only, with no assigned observational amplitude.

## 6. Skeptical assessment

The bound is stronger and more specific than a familiar cos(2 phi) pattern or a chosen Hopf-neutral restriction: every nonzero stationary-nodal great-circle quadrupole carries at least 50% charged power, independent of which J is chosen. It ties a physically motivated preparation used by the recovered optical experiment to actual Hopf representation content and gives a parameter-free range for scalar spectral sensitivity.

Mathematically the proof is short representation geometry and a Kahler-angle identity. It should not be advertised as a major new general theorem without a broader literature search. Its defensible novelty is its application to this preparation and its explicit role in the BHSM chain. The bound by itself does not close the microscopic-action-to-optics arrow or prove an observable Berger effect. A strong paper must make the conditional optical result useful on its own and state exactly which geometric inputs are inherited and which are derived here.

The companion script gives exact symbolic checks for the trace identity, decomposition, and spectral formula, plus random orthogonal-complex-structure checks in both orientation classes. These are internal AI-assisted proof checks, not external peer review.
