# Hopf-neutral n=2 stationary-nodal obstruction

This is a new supporting geometric derivation from the actual Berger/Hopf scalar structure recovered in the historical record. It does not select a physical Hopf structure, an optical coupling, an initial state, or a squashed-spacetime cosmology. An exact symbolic calculation and seeded numerical checks are supplied in `check_hopf_nodal.py`; execution writes `hopf_nodal_receipt.json`.

## Statement

Let J be an orthogonal complex structure on R4, so J^T=−J and J²=−I. On the unit S3 write a real n=2 scalar as

\[
F_A(X)=X^TAX,\qquad A=A^T,\quad\operatorname{tr}A=0,\quad X^TX=1.
\]

The Hopf circle through X is `X(theta)=exp(theta J)X`. Suppose F_A is invariant under every such circle. Then either A=0 or F_A has **no point at which both its value and differential vanish**. This conclusion holds for any positive Berger metric built from this Hopf structure, because vanishing of a differential is metric independent.

For an optical experiment requiring `F_A(X_o)=0` and `dF_A|_(X_o)=0`, a nonzero spatial n=2 state therefore needs a nonzero Hopf-charged component. The previous nodal scalar preparation cannot be realized using a purely Hopf-basic n=2 profile. This is a restriction on the declared geometric state, not a microscopic preparation rule.

## Proof from the action of the Hopf group

Hopf invariance gives

\[
e^{-\theta J}Ae^{\theta J}=A,
\qquad [A,J]=0.
\]

Choose a J-adapted orthonormal basis with

\[
J=\begin{pmatrix}0&-I_2\\I_2&0\end{pmatrix}.
\]

A real symmetric matrix commuting with J is the real representation of a Hermitian 2×2 matrix. Trace freedom gives the complete three-parameter form

\[
A=\begin{pmatrix}
u&v&0&w\\
v&-u&-w&0\\
0&-w&u&v\\
w&0&v&-u
\end{pmatrix}.
\]

Direct multiplication yields

\[
A^2=\rho^2I_4,\qquad
\rho^2=u^2+v^2+w^2=\tfrac14\operatorname{tr}A^2.
\]

Its eigenvalues are +rho,+rho,−rho,−rho. Thus a nonzero such A is invertible. On S3 the round tangential gradient is

\[
\nabla F_A=2(AX-F_A X).
\]

Consequently `F_A(X_o)=0` and `dF_A|_(X_o)=0` are equivalent to `AX_o=0`. Nonzero A is invertible and X_o is a unit vector, so this is impossible. The formula also gives the stronger pointwise identity

\[
\boxed{F_A^2+\frac14|\nabla F_A|^2=\rho^2.}
\]

For a Hopf-invariant function the derivative in the fibre direction vanishes. Horizontal lengths agree in the unit-base Berger family below, so the same gradient identity holds in that convention. At physical radius R, replace the gradient term by `R² |grad_phys F_A|²/4`.

## Genuine Berger spectral content

The recovered source `Downloads/BHSM_ATTACHMENT_TO_BERGER_OVERLAP_HIERARCHY_2026-08-03.md`, §4, supplies

\[
\lambda_{k,j}(a)=k(k+2)+(a^2-1)(k-2j)^2.
\]

Here a is an **inverse fibre scale**. To make its geometric content explicit, let K(X)=JX be the unit round Hopf Killing vector, eta its round dual, and use

\[
h_a=h_H+a^{-2}\eta^2,\qquad a>0.
\]

The volume density is the round one times the constant a^(-1). The inverse metric changes by `(a²−1)K⊗K`; K is divergence free. Thus

\[
\Delta_a=\Delta_1+(a^2-1)K^2.
\]

For a Hopf charge-q function, `K²F=−q²F`, giving the recovered spectral formula. At physical radius R all eigenvalues acquire `R^(-2)`.

For the entire k=2 real nine-dimensional scalar sector, define

\[
A_0=\tfrac12(A+J^TAJ),\qquad
A_2=\tfrac12(A-J^TAJ).
\]

Then A0 commutes with J, A2 anticommutes with J, and the two subspaces are orthogonal in the Frobenius pairing. The neutral subspace has real dimension three; the charged subspace has real dimension six. Acting along the Hopf circle gives

\[
KF_{A_0}=0,\qquad K^2F_{A_2}=-4F_{A_2}.
\]

Since all round n=2 harmonics obey `−Δ1 F=8 F`,

\[
\boxed{
\lambda_0=8\ (\text{dimension }3),\qquad
\lambda_{|q|=2}=4+4a^2\ (\text{dimension }6).
}
\]

The splitting is present for a≠1 and vanishes in the round limit a=1. It is a property of an actual Berger metric and Hopf action, whereas labeling a round-S3 quadrupole “Berger” alone provides no such splitting.

## Nodal states and remaining freedom

The obstruction does not eliminate the nodal experiment from the full n=2 family. For the displayed J, take

\[
A=\operatorname{diag}(1,0,-1,0),\qquad X_o=(0,0,0,1)^T.
\]

This A anticommutes with J, lies entirely in the charged sector, and satisfies AX_o=0. Its Hessian on the tangent space has eigenvalues +2,0,−2; it is a nonzero stationary nodal tidal preparation. The pure charged witness therefore verifies that the no-go is specific to the neutral sector. A generic nodal matrix can also mix sectors with cancellation at the observer.

No preferred J or relation between the cosmological R1 branch and a nonround Berger background has been established here. Applying the split eigenvalues to six-state R1 evolution without rederiving its constraints would change its physical model. The scalar spectrum is geometric; the full constrained metric/matter evolution and optical projection require a common action and domain. The result can safely enter the new paper as a supporting exact restriction on possible Hopf-basic versus Hopf-charged spatial states, while the primary optical calculation retains its declared round R1 domain.

## Provenance and originality scope

Inherited: the BHSM scalar eigenvalue formula, Hopf charges, quadratic realization of n=2 harmonics. Independently derived here: the explicit neutral matrix form, pointwise amplitude-gradient identity, stationary-nodal obstruction, charged witness, and full 3+6 k=2 split in the stated convention. These are consequences of standard Hopf/Berger geometry; no first-ever claim is made. Their contribution to the present project is to constrain the preparation of the recovered lensing experiment using actual Hopf structure. The symbolic and numerical checks are internal AI-assisted verification, not independent peer review.
