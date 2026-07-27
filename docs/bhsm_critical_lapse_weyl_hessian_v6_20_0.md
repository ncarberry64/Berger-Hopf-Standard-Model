# BHSM v6.20.0 critical lapse--Weyl Hessian

Primary theorem:
`BHSM_CRITICAL_LAPSE_WEYL_DOMAIN_IS_UNDERDETERMINED`.

## Frozen action and background

The calculation uses the already frozen normalized representative
\(q_5=\kappa _1=Z_5=1\), \(C_\partial/\kappa _1=1/2\):

\[
S_{\rm bulk}
=\frac12\int_{M_5}\sqrt{-g}\,(\kappa _1R_5-\kappa _0)
-\frac{Z_5}{2}\int_{M_5}\sqrt{-g}\,(\nabla\sigma)^2-\int\sqrt{-g}\,U_5 ,
\]

with one GHY term on each reflected cap, the common intrinsic
\(C_\partial R_4\) term on B1, and the exact metric matcher. No action term
or coefficient is added.

The stored critical solution
\[
X_c=2,\qquad N_0=\frac{\pi}{4},\qquad
a_0(t)=\sqrt2\sin\frac{\pi t}{4},\qquad \sigma _0=0
\]
obeys, exactly,
\[
H_0^2-\frac{2}{a_0^2}=-1,\qquad
\frac{a_{0,tt}}{N_0^2a_0}=-1,\qquad H_0(1)=1 .
\]
The scalar background equation and critical odd scalar boundary value also
vanish. GHY cancels the normal derivatives of the metric variation on each
cap before the derivative expansion.

## Principal two-derivative block

Use
\[
N=N_0(1+A),\qquad
h_{\mu\nu}=a_0^2[(1+2\psi)\bar h_{\mu\nu}
2D_\mu D_\nu E],\qquad
\delta\sigma=q(x)u_1(t).
\]
First form \(S=B-a_0^2\partial_tE\), reproduce the momentum relation, then
choose \(E=0\). Fixed support gives \(\zeta=0\), while v6.18 gives
\[
\Pi_\perp B=-\tau\frac{\pi\chi _1}{16}t\,\Pi_\perp q,\qquad C_\Sigma=0.
\]

The determinant and inverse-metric factors for the displayed linear metric
ansatz are
\[
\frac{\sqrt{-h}}{a_0^4\sqrt{-\bar h}}
=1+4\psi+4\psi^2,\qquad
a_0^2h^{\mu\nu}
=(1-2\psi+4\psi^2)\bar h^{\mu\nu}.
\]
The action-derived radial measure is therefore
\[
d\mu_{\rm rad}=N_0a_0^4dt
=\pi\sin^4\!\left(\frac{\pi t}{4}\right)dt.
\]

After four-dimensional integration by parts, the two reflected P1 caps give
\[
\mathcal L_{\rm bulk}^{(2,\partial_4^2)}
=6\kappa _1N_0a_0^2
\left(D_\mu A D^\mu\psi+D_\mu\psi D^\mu\psi\right).
\]
Thus the bulk principal Hessian in the weighted radial pairing is
\[
\mathcal L_{A\psi}^{\rm bulk,crit}
=
\begin{pmatrix}
0 & 6\kappa _1/a_0^2\\
6\kappa _1/a_0^2 & 12\kappa _1/a_0^2
\end{pmatrix}.
\]
It is a real order-zero multiplication saddle operator. Its formal adjoint
equals itself under \(N_0a_0^4dt\), and its bulk Green form vanishes.
The common B1 term contributes the symmetric endpoint Hessian
\[
\frac12(12C_\partial)(D\psi_J)^2.
\]
The matcher contributes no independent propagating block after
\(h=\iota^*g\) and elimination of \(\Lambda^{\mu\nu}\).

The ADM extrinsic-curvature sector also fixes the threading portions of the
mixed source:
\[
J_A^{(B)}
=\frac{6\kappa _1B_q(a_{0,t}/a_0)}
{N_0^2a_0^2},\qquad
J_\psi^{(B)}
=-\frac{6\kappa _1B_q}{N_0^2a_0^2}\partial_t ,
\]
where \(B_q=-\tau(\pi\chi _1/16)t\). These reproduce the inherited momentum
response. They are not the full \(J_{\rm rad}^{\rm crit}\).

## Earliest obstruction

The physical fold tangent stored by v6.11 contains both
\(\delta X=\tau\chi _1q\) and the radial profiles \(a_1,N_1\). The
repository does not store the covariant metric-valued representative
\[
\mathcal T^{(X)}_{\mu\nu}(x,x')
=\left.
\frac{\delta\bar h_{\mu\nu}[X](x)}{\delta X(x')}
\right|_{X=2},
\qquad
\delta R_4[\mathcal T^{(X)}]=\tau\chi _1q ,
\]
modulo four-dimensional diffeomorphisms and with the regulated M4 domain
fixed. It stores only the scalar \(X(q)\) after substituting the maximally
symmetric branch into the on-shell action.

\(\mathcal T^{(X)}\) is a symmetric-two-tensor-valued scalar Green operator.
Before the normalized \(q_5=1\) convention, its coefficient has dimension
\(L^2\). It is needed simultaneously in the P1 \(R_4\) term, intrinsic B1
\(R_4\) term, and exact matcher. It fixes:

- the remaining \(q\)-\(A\) and \(q\)-\(\psi\) source;
- the two independent scalar B1 junction projections;
- the actual and adjoint domains;
- kernel and source compatibility;
- the separation from the Einstein-frame Weyl term.

Without it, a chosen local metric family would be an extra domain/gauge
input. Consequently the condition count, kernel dimensions, Fredholm
status, full \(J_{\rm rad}\), and constrained inverse are undefined. No
generic pseudoinverse or numerical boundary-value solve is admissible.

The minimum next derivation is to choose the repository's covariant,
regulated M4 metric family \(\bar h[X]\), compute its gauge-quotiented
Fréchet derivative, and insert that derivative into the existing
P1+GHY+B1+matcher action. This requires no new action.

## Kinetic verdict

The known terms remain
\[
K_{\rm scalar}=2\int a_0^2u_1^2\,d\rho\ge2>0,\qquad
K_{\rm Weyl}
=\frac{3\chi _1^2(4-\pi)^2}{16\pi}
=1.220620174933802\ldots .
\]
But \(K_{\rm shift+endpoint}^{\rm red}\), \(k_q^E\), their uncertainty,
sheet behavior, and kinetic sign are not defined before the missing
metric-tangent/domain completion. The fold is not classified as positive,
ghost, or null, and no physical mass is inferred.
