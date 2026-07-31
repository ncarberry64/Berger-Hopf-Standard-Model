# BHSM master-action relative-channel normalization v8.7

## Result

The master-action audit separates two questions that had been conflated:

1. **How are orthogonal geometric channels canonically normalized?**
2. **Does the physical action attach those channels to one localized charged-current operator?**

The first question has a unique conditional answer. The second remains open in the current master action.

## 1. Exact C3 normalization

For the normalized characters

\[
|\chi_k\rangle=\frac1{\sqrt3}\sum_{n=0}^2\omega^{-kn}|n\rangle,
\]

one has

\[
\langle\chi_k|\chi_l\rangle=\delta_{kl}.
\]

The point-centered transfer decomposes exactly as

\[
\boxed{
T_{\rm point}=\frac{T_{\chi_0}+T_{\chi_1}+T_{\chi_2}}{\sqrt3}.
}
\]

The factor \(1/\sqrt3\) is therefore a Fourier basis-conversion coefficient. It is not the relative dynamical coupling between the singlet and complex channels.

## 2. Common-parent quadratic normalization

The v7.1 normalized retained-mode pushforward has the form

\[
c_{\alpha\beta}=c_{\rm parent}
\int_F u_\alpha^*u_\beta\,d\nu_F.
\]

For orthonormal triality characters,

\[
c_{\alpha\beta}=c_{\rm parent}\delta_{\alpha\beta}.
\]

A common canonical field rescaling removes \(c_{\rm parent}\), leaving

\[
\left|\frac{c_{\chi_1}}{c_{\chi_0}}\right|=1.
\]

There is no rank or \(\sqrt3\) enhancement between two normalized C3 character states.

## 3. G2 complex phase

For a unit vector \(x\perp u\), with \(J_u^2=-1\) on the six-plane,

\[
\Pi_{10}x=\frac{x-iJ_ux}{2}.
\]

Its normalized form is

\[
\boxed{
z_+=\frac{x-iJ_ux}{\sqrt2}.
}
\]

Thus the two real components have equal modulus and relative phase \(-i\). The conjugate polarization gives \(+i\).

Combining common-parent orthonormal normalization with the selected \(\Pi_{10}\) branch yields

\[
\boxed{
\frac{c_{\chi_1}}{c_{\chi_0}}=-i,
\qquad
\left|\frac{c_{\chi_1}}{c_{\chi_0}}\right|=1.
}
\]

The corresponding profile is

\[
\boxed{T_{\rm can}=T_{\chi_0}-iT_{\chi_1}}
\]

up to one irrelevant common scalar and the conjugate branch.

## 4. Why this is not yet a physical master-action output

The current stratified action contains a parent carrier quadratic term and a normalized spectral pushforward rule, but it keeps the localized Standard Model fermions, Yukawa matrices, and charged current on the intrinsic M4 stratum. It does not contain a common term identifying \(\chi_0\) and \(\chi_1\) as two components of one localized charged-current operator.

C3 symmetry alone cannot fix this attachment. The most general Hermitian C3-commuting operator is

\[
J=aI+x(C+C^2)+iy(C-C^2),
\]

with three independent real coefficients. The current minimal action selects no nontrivial junction/current generator.

Therefore the exact status is

\[
\boxed{
\texttt{BHSM\_CANONICAL\_ORTHONORMAL\_G2\_C3\_RELATIVE\_NORMALIZATION\_DERIVED\_CONDITIONALLY}
}
\]

but

\[
\boxed{
\texttt{BHSM\_MASTER\_ACTION\_PHYSICAL\_G2\_C3\_CHANNEL\_COUPLING\_REMAINS\_UNSELECTED}.
}
\]

## 5. Frozen-screen kill test

The canonical profile \(T_{\chi_0}-iT_{\chi_1}\), with the existing oriented polar map, is precisely the v8.6 character-normalized candidate. It generates nonzero CP but does not pass the frozen CKM hierarchy screen.

That failure must not be repaired by tuning the relative channel norm. The relative norm is already canonically fixed under the common-parent premise. The remaining error belongs to the missing profile-to-current attachment, oriented incidence law, or physical current kernel.

## Final missing theorem

\[
\boxed{
\texttt{ACTION\_OWNED\_COMMON\_PARENT\_CURRENT\_TERM\_ATTACHING\_ORTHONORMAL\_C3\_MODES\_TO\_THE\_G2\_POLARIZED\_LOCALIZED\_CHARGED\_CURRENT}
}
\]

