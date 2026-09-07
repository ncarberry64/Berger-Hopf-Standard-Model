# AE3.1 current-C2 coexact SU(2)L charged-current theorem

## Same-domain charged source

The retained left-handed doublets carry the exact raising and lowering
generators

\[
 T_+=\begin{pmatrix}0&1\\0&0\end{pmatrix},\qquad
 T_-=T_+^\dagger,
\]

in the ordered bases \((u_L,d_L)\) and \((\nu_L,e_L)\). Right-handed
singlets are annihilated. The two Hermitian coordinates

\[
 T_1=\frac{T_++T_-}{2},\qquad
 T_2=\frac{T_+-T_-}{2i}
\]

inherit the existing lowest-Weyl coexact current-C2 source and contact jets.
Their complex recombination gives the adjoint pair \(W^\pm\) and
\(J_\pm\). No new weak coupling, source normalization, or family matrix is
introduced.

The one-family trace is

\[
 \operatorname{Tr}(T_-T_+)=3_{\rm color}+1_{\rm lepton}=4,
\]

and the retained three-family trace is 12.

## Exact family consequence

The weak raising current acts as the identity on \(\mathbb C^3_{\rm family}\).
The current-C2 up and down response shapes transported from the frozen BHSM
modules are both diagonal in the same family projector basis. Hence

\[
 K_{ud}^{\rm current}=I_3,
 \qquad [H_u,H_d]=0.
\]

The canonical response-basis readout is therefore

\[
 V_{\rm response}=I_3,\qquad J_{\rm response}=0.
\]

This is an exact no-mixing theorem for the present family-central charged
current, not a claim that the physical CKM matrix is the identity. The
absolute up/down Yukawa prefactors are still missing, and the action has not
selected a family-noncentral dressing of the left-handed up/down embeddings.

The historical middle-up factor \(Z_{\rm virt}^{u,2}=1/2\) is not inserted.
It remains a frozen conditional dressing output rather than a term in the
current AE3.1 action.

The smallest missing object for nontrivial mixing is now explicit: a
family-noncentral action dressing of the common left-handed up/down embeddings,
or an equivalent mixed second variation. An arbitrary CKM unitary is not an
allowed substitute.

- `CURRENT_C2_COEXACT_SU2L_CHARGED_SOURCE_PAIR_DERIVED = TRUE`
- `CURRENT_C2_SU2L_RAISING_CURRENT_FAMILY_KERNEL_IS_I3 = TRUE`
- `CURRENT_C2_CANONICAL_QUARK_RESPONSE_BASIS_CKM_IS_I3 = TRUE`
- `PRESENT_ACTION_NONTRIVIAL_CKM_DERIVED = FALSE`
- `PHYSICAL_CKM_MATRIX_DERIVED = FALSE`
- `MIDDLE_UP_VIRTUAL_DRESSING_PROMOTED = FALSE`
