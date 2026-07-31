# BHSM common-parent charged-current attachment v8.8

## Result

The missing attachment can be added without a new particle, a new charged-current coupling, or a tunable singlet/complex coefficient.

The minimal construction is not a second interaction beside the Standard Model charged current. It **replaces the family identity inside the existing weak raising and lowering generators** by the canonical unitary map obtained from the common-parent geometric kernel.

The result is

\[
\boxed{
\mathcal L_{\rm cc}^{C_3/G_2}
=-\frac{g_2}{\sqrt2}\left[
W_\mu^+\,\bar u_L\gamma^\mu\mathcal U_{CG}d_L
+W_\mu^-\,\bar d_L\gamma^\mu\mathcal U_{CG}^\dagger u_L
\right].
}
\]

No independent \(g_{\rm ch}\) is introduced. The coefficient is the already-owned \(SU(2)\) coupling \(g_2\).

## 1. Common-parent kernel

Define the bifundamental geometric kernel

\[
\mathcal K_{CG}
=
P_u\,\mathcal R_{8\to4}\!\left[
\Pi_{10}
\left(P_{\chi_0}\oplus P_{\chi_1}\right)
\mathfrak J_{\rm parent}[G,\omega,\sigma]
\right]P_d.
\]

Here:

- \(P_{\chi_0}\) and \(P_{\chi_1}\) are the normalized \(C_3\) character projectors;
- \(\Pi_{10}=(Q-iJ_u)/2\) is the selected \(G_2\) complex polarization for the raising channel;
- \(\mathfrak J_{\rm parent}\) is the current kernel made from the existing parent geometry, connection, and scalar-wall data;
- \(P_u\) and \(P_d\) are the already-declared sector projectors.

In the normalized two-channel basis,

\[
\boxed{
\mathcal K_{CG}\propto T_{\chi_0}-iT_{\chi_1}.
}
\]

The lowering channel carries the Hermitian adjoint and therefore the conjugate \(G_2/C_3\) branch automatically.

## 2. Canonical family isometry

A weak generator must act unitarily between the three down-family and three up-family spaces. For full-rank \(\mathcal K_{CG}\), the unique canonical isometry is its polar factor:

\[
\boxed{
\mathcal U_{CG}
=
\mathcal K_{CG}
\left(\mathcal K_{CG}^\dagger\mathcal K_{CG}\right)^{-1/2}.
}
\]

This inverse square root is not a fitted response function. It is the canonical orthonormalization required to turn the full-rank bifundamental kernel into a unitary weak-family map.

The v8.7 numerical profile was used only to stress-test the domain. Its singular values are

\[
(1.73277875,\;0.22342732,\;0.00630746),
\]

so the proxy kernel is full rank. Those numerical values retain screen ingredients and are not promoted as an action-derived vertex.

## 3. Exact weak-algebra closure

On the ordered weak-doublet space \(\mathcal H_u\oplus\mathcal H_d\), define

\[
\mathbb T_+^{CG}
=
\begin{pmatrix}
0&\mathcal U_{CG}\\
0&0
\end{pmatrix},
\qquad
\mathbb T_-^{CG}
=
\begin{pmatrix}
0&0\\
\mathcal U_{CG}^\dagger&0
\end{pmatrix},
\]

and

\[
\mathbb T_3
=\frac12
\begin{pmatrix}
I_3&0\\
0&-I_3
\end{pmatrix}.
\]

Because \(\mathcal U_{CG}\) is unitary,

\[
[\mathbb T_3,\mathbb T_+^{CG}]=\mathbb T_+^{CG},
\qquad
[\mathbb T_3,\mathbb T_-^{CG}]=-\mathbb T_-^{CG},
\]

and

\[
\boxed{
[\mathbb T_+^{CG},\mathbb T_-^{CG}]=2\mathbb T_3.
}
\]

The quadratic Casimir remains \(3I_6/4\). Thus the geometric attachment is an exact representation of the existing weak algebra rather than an extra interaction pasted onto it.

A decisive consequence is that \(\mathbb T_3\) remains family-central. The term generates no tree-level flavor-changing neutral current.

## 4. No-double-counting form

If the existing localized action is written with the identity charged current, the exact replacement can be implemented as

\[
\Delta\mathcal L_{\rm attach}
=-\frac{g_2}{\sqrt2}\left[
W_\mu^+\bar u_L\gamma^\mu(\mathcal U_{CG}-I_3)d_L
+\mathrm{h.c.}
\right].
\]

Adding this correction to the existing identity current gives exactly the new current with \(\mathcal U_{CG}\). It does not double count \(g_2\), the weak boson, or a second charged-current operator.

## 5. Basis and transport covariance

Under independent family-basis changes,

\[
\mathcal K_{CG}\mapsto V_u\mathcal K_{CG}V_d^\dagger.
\]

Polar decomposition is equivariant:

\[
\mathcal U_{CG}\mapsto V_u\mathcal U_{CG}V_d^\dagger.
\]

Therefore the fermion bilinear is basis invariant.

For a spacetime-dependent parent profile, the correct compatibility condition is

\[
D_\mu^{\rm fam}\mathcal U_{CG}
=
\partial_\mu\mathcal U_{CG}
+\mathcal A_\mu^u\mathcal U_{CG}
-\mathcal U_{CG}\mathcal A_\mu^d.
\]

On the retained stationary branch this is zero. In the dynamic case, \(\mathcal A_\mu^{u,d}\) are the existing parent-induced associated-bundle connections; no arbitrary family connection or coefficient is added.

## 6. Conditional variational ownership

If an action-derived parent kernel is supplied, the candidate term's variation produces both the localized weak current and a reaction on the parent geometric fields:

\[
\frac{\delta S}{\delta W_\mu^+}
=-\frac{g_2}{\sqrt2}\sqrt{-h}\,
\bar u_L\gamma^\mu\mathcal U_{CG}d_L.
\]

Writing \(\mathcal K=\mathcal U H\), with \(H=(\mathcal K^\dagger\mathcal K)^{1/2}\), its exact differential is determined by

\[
H\,\delta H+\delta H\,H
=
\delta\mathcal K^\dagger\mathcal K
+\mathcal K^\dagger\delta\mathcal K,
\]

and

\[
\delta\mathcal U
=(\delta\mathcal K-\mathcal U\delta H)H^{-1}.
\]

Consequently variation of \(G\), \(\omega\), or \(\sigma\) propagates through \(\delta\mathcal K\) into the localized current. The term is not merely a post-processing definition of a matrix.

## 7. Uniqueness under the BHSM constraints

Under the requirements of locality, Lorentz invariance, Hermiticity, family-basis covariance, exact \(SU(2)\) closure, no new field, and no new continuous coefficient:

1. the raising-channel family kernel must be unitary;
2. the full-rank parent kernel supplies a unique canonical unitary through polar decomposition;
3. the coefficient must be the existing \(g_2/\sqrt2\);
4. the relative \(C_3/G_2\) phase is the already-derived \(-i\);
5. the lowering channel is fixed by Hermitian conjugation.

Thus no arbitrary \(g_{\rm ch}\), relative channel magnitude, continuous phase, or interpolation function is permitted.

## 8. Exact claim boundary

This sprint constructs the missing interface form conditionally. It does not add it to the authoritative stratified action and does not prove that the previously frozen numerical heat-kernel profile is the local parent current kernel.

The physical mass-basis charged-current matrix is

\[
V_{\rm phys}=U_u^\dagger\mathcal U_{CG}U_d.
\]

The localized Yukawa/mass-basis isometries \(U_u\) and \(U_d\) remain independent in the present stratified EFT. Therefore \(\mathcal U_{CG}\) is not yet promoted as the physical CKM matrix, and frozen predictions remain unchanged.

## Verdict

\[
\boxed{
\texttt{BHSM\_MINIMAL\_ZERO\_PARAMETER\_COMMON\_PARENT\_C3\_G2\_CHARGED\_CURRENT\_TERM\_CONSTRUCTED\_CONDITIONALLY}
}
\]

and

\[
\boxed{
\texttt{BHSM\_C3\_G2\_CHARGED\_CURRENT\_INTERFACE\_CONSTRUCTION\_CONDITIONAL\_ON\_ACTION\_DERIVED\_PARENT\_KERNEL}.
}
\]

The remaining exact object is

\[
\boxed{
\texttt{ACTION\_DERIVATION\_OF\_THE\_LOCAL\_PARENT\_CURRENT\_KERNEL\_AND\_MASS\_BASIS\_ATTACHMENT\_WITHOUT\_SCREEN\_INPUTS}.
}
\]
