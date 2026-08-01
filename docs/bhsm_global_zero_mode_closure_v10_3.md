# BHSM v10.3 Global Zero-Mode Closure Audit

On a compact domain, a self-adjoint equation

\[
\mathcal Oq=J
\]

with kernel `u0` requires the Fredholm condition

\[
\langle u_0,J\rangle=0
\]

unless the kernel is lifted or a global amplitude is independently fixed.
This is a compatibility condition; it is not automatically a restoring law.

## Previously solved fold response

V6.29 already contains a compact response under different names. Its quotient
kernel is

\[
z_A=\sec^2(\pi t/4),\qquad z_\psi=1,
\]

with positive normalized lift

\[
M_z=3(8-\pi)>0,
\]

and source response `c_z=-j_z/M_z`. This is imported as an exact fold-sector
Schur/Fredholm result. It does not act on the Hopf breathing mode and fixes no
dimensional scale.

## Hamiltonian and homogeneous mode

The integrated Hamiltonian relation

\[
\int_{\Sigma_7}\mathcal H\,d\mu_7=0
\]

follows from the local lapse equation. It is not an additional equation that
fixes the homogeneous radion. With

\[
\beta=\beta_0+\widetilde\beta,
\qquad \int\widetilde\beta\,d\mu=0,
\]

the current action leaves `beta0` unfixed and has no positive homogeneous
radion equilibrium. Eta degree fixes a topological sector but no length.

No `V_star`, curvature target, or energy target is adopted.

Verdict:
`BHSM_NO_GLOBAL_RESTORING_CONSTRAINT_EXISTS_WITHOUT_AN_EXTERNAL_SCALE_INPUT`.
