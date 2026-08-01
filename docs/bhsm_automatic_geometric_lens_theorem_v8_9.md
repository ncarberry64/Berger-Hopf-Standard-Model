# BHSM automatic eight-dimensional geometric lens theorem v8.9

## Theorem

Let \(\Phi_*\) be an action-selected stationary configuration of the BHSM
stratified eight-dimensional geometry.  Let

\[
\mathfrak C_f:\mathbb C^3_{\rm family}\longrightarrow\mathcal Q_8,
\qquad f\in\{u,d\},
\]

be smooth full-rank composite-state immersions into the gauge- and
diffeomorphism-quotiented geometric configuration space.  Write

\[
A_f=D\mathfrak C_f|_{\Phi_*}.
\]

Let \(\mathbb K_8\) be the positive kinetic pairing and
\(\mathbb H_8=\operatorname{Hess}_{\Phi_*}S_{\rm BHSM}^{\rm strat}\) the
self-adjoint physical Hessian.  Define the pullback forms

\[
G_f=A_f^\dagger\mathbb K_8A_f>0,
\qquad
Q_f=A_f^\dagger\mathbb H_8A_f=Q_f^\dagger.
\]

Assume that the spectrum of

\[
L_f=G_f^{-1/2}Q_fG_f^{-1/2}
\]

is simple, and that the raw common-parent \(C_3/G_2\) current kernel
\(K_{ud}\) has full rank.

Then the eight-dimensional action canonically determines the two sector
lenses and the physical charged-current orientation by

\[
G_f^{-1/2},
\qquad
L_f=W_f\,\operatorname{diag}(\mu_{f,0},\mu_{f,1},\mu_{f,2})W_f^\dagger,
\]

\[
X_f=G_f^{-1/2}W_f,
\]

\[
\widetilde K_{ud}=G_u^{-1/2}K_{ud}G_d^{-1/2},
\qquad
\mathcal U_{CG}=\operatorname{Pol}(\widetilde K_{ud}),
\]

and

\[
\boxed{
V_{\rm geom}=W_u^\dagger\mathcal U_{CG}W_d.
}
\]

The construction satisfies

\[
X_f^\dagger G_fX_f=I_3,
\qquad
X_f^\dagger Q_fX_f
=\operatorname{diag}(\mu_{f,0},\mu_{f,1},\mu_{f,2}),
\]

and \(V_{\rm geom}\) is unitary.

The two lenses are unique modulo independent phases of nondegenerate
eigenvectors.  Those phases do not alter \(|V_{ij}|\), the three mixing
angles, or the Jarlskog invariant.  The selected \(G_2\) complex branch fixes
the remaining CP-orientation sign.

No continuous lens angle, normalization, or phase is introduced.

## Proof

### 1. Grinding is forced by the kinetic form

Because \(G_f\) is positive definite, the spectral theorem gives one and only
one positive inverse square root \(G_f^{-1/2}\).  Any reduced field with kinetic
term

\[
\bar\psi_fG_f i\slashed D\psi_f
\]

is canonically normalized by this operator.  An alternative positive
normalization does not exist.  This is the geometric **grinding** step: all
norm and shear inherited from the eight-dimensional composite immersion are
removed by the action's own kinetic metric.

### 2. Polishing is forced by the response Hessian

The whitened response

\[
L_f=G_f^{-1/2}Q_fG_f^{-1/2}
\]

is Hermitian.  Its simple spectrum has unique ordered rank-one spectral
projectors.  Choosing normalized eigenvectors gives a unitary matrix \(W_f\),
unique only up to column phases.  Therefore

\[
X_f=G_f^{-1/2}W_f
\]

is the unique generalized-eigenmode frame modulo those phases.  Direct
substitution gives

\[
X_f^\dagger G_fX_f=I,
\qquad
X_f^\dagger Q_fX_f=\operatorname{diag}(\mu_f).
\]

This is the **polishing** step: the action Hessian fixes the principal optical
axes and their ordering.

### 3. The common current is automatically normalized

After canonical normalization, the raw parent kernel is

\[
\widetilde K_{ud}=G_u^{-1/2}K_{ud}G_d^{-1/2}.
\]

Full rank gives a unique polar decomposition

\[
\widetilde K_{ud}=\mathcal U_{CG}H,
\qquad
H=(\widetilde K_{ud}^\dagger\widetilde K_{ud})^{1/2}>0.
\]

Thus

\[
\mathcal U_{CG}
=\widetilde K_{ud}
(\widetilde K_{ud}^\dagger\widetilde K_{ud})^{-1/2}
\]

is the unique canonical unitary part.  Its use in the weak raising/lowering
generator preserves the exact \(SU(2)\) algebra.

### 4. The physical matrix is the comparison of the two finished lenses

Transforming the canonical fields into their ordered response eigenbases gives

\[
V_{\rm geom}=W_u^\dagger\mathcal U_{CG}W_d.
\]

It is a product of unitary maps, hence unitary.  The previously independent
symbols \(U_u\) and \(U_d\) are therefore not inputs; they are the eigenframes
\(W_u\) and \(W_d\) computed from the two pullback action Hessians.

### 5. Eigenvector phases are not physical missing parameters

Let \(P_{f,i}\) denote the rank-one spectral projectors of \(L_f\).  Then

\[
|V_{ij}|^2
=\operatorname{Tr}
\left(
P_{u,i}\mathcal U_{CG}P_{d,j}\mathcal U_{CG}^\dagger
\right),
\]

which contains no eigenvector phase convention.

Likewise, with

\[
\Delta_f=\prod_{i<j}(\mu_{f,i}-\mu_{f,j}),
\]

\[
\operatorname{Tr}
\left(
[L_u,\mathcal U_{CG}L_d\mathcal U_{CG}^\dagger]^3
\right)
=6iJ\Delta_u\Delta_d.
\]

Thus \(J\) is also determined without choosing phases.  Complex conjugating
the global \(G_2\) branch reverses the CP orientation; selecting
\(\Pi_{10}\) rather than \(\Pi_{01}\) fixes that sign.

This proves the theorem.

## Meaning of the lens metaphor

The geometry does two different jobs:

1. **Grinding:** \(G_f^{-1/2}\) removes the unequal norms and nonorthogonality
   produced when the 8D composite state reaches the localized sector.
2. **Polishing:** the ordered eigenprojectors of \(L_f\) select the final
   principal axes of the up and down sectors.

The charged-current matrix is what one sees by looking through both finished
lenses with the common \(C_3/G_2\) current between them.

## Exact BHSM status

This theorem eliminates arbitrary mass-basis isometries **once** the composite
immersions and their action pullbacks have been evaluated.  It does not invent
those pullbacks or replace their calculation with a screen.

The remaining task is now a concrete geometric computation:

\[
\boxed{
A_f=D\mathfrak C_f,
\quad
G_f=A_f^\dagger\mathbb K_8A_f,
\quad
Q_f=A_f^\dagger\mathbb H_8A_f,
\quad
K_{ud}=A_u^\dagger\mathfrak J_{CG}A_d
}
\]

on the actual action-selected 8D vacuum.

Therefore the new verdict is

\[
\boxed{
\texttt{BHSM\_EIGHT\_DIMENSIONAL\_ACTION\_GRAM\_HESSIAN\_LENS\_THEOREM\_PROVED\_CONDITIONALLY}
}
\]

and

\[
\boxed{
\texttt{BHSM\_UP\_DOWN\_MASS\_BASIS\_LENSES\_ARE\_CANONICAL\_OUTPUTS\_OF\_THE\_COMPOSITE\_EIGHT\_DIMENSIONAL\_ACTION\_REDUCTION\_CONDITIONALLY}.
}
\]

