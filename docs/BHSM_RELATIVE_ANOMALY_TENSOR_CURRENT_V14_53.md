# BHSM v14.53 — Relative Anomaly and Tensor-Current Obstruction

## Primary verdict

`BHSM_V14_53_THE_POSITIVE_GAUGE_SIGN_MINIMAL_DIRAC_RELATIVE_WEYL_ANOMALY_IS_NEGATIVE_FOR_A_NONROUND_BERGER_CHILD_RELATIVE_TO_A_ROUND_PARENT_AND_CAN_SUPPLY_THE_SCALE_STABILIZING_SIGN_COMPONENT`

## Evaluability verdict

`BHSM_THE_FULL_PREIMAGE_SCALE_POINT_IS_NOT_NUMERICALLY_EVALUABLE_FROM_THE_CURRENT_ARCHIVE_BECAUSE_THE_MATCHED_CHILD_PARENT_BACKGROUND_FULL_RELATIVE_POWER_COEFFICIENT_AND_COMPLETE_RELATIVE_HEAT_KERNEL_HAVE_NOT_BEEN_CONSTRUCTED`

## Flavor verdict

`BHSM_ALL_CURRENT_ACTION_OWNED_C3_FAMILY_RESPONSES_LIE_IN_THE_ABELIAN_GROUP_ALGEBRA_C_OF_C3_AND_CANNOT_GENERATE_A_NONTRIVIAL_CKM_MATRIX_WITHOUT_A_NONCENTRAL_PETER_WEYL_TENSOR_CURRENT`

## Exact next object

`MATCHED_CHILD_PARENT_FULL_PREIMAGE_BACKGROUND_AND_RELATIVE_HEAT_KERNEL_EVALUATING_A6_B_Z_TOGETHER_WITH_AN_ACTION_OWNED_NONCENTRAL_PETER_WEYL_TENSOR_CURRENT_MIXED_VARIATION_FIXING_AT_LEAST_THREE_INDEPENDENT_CROSS_BLOCK_CHANNEL_COEFFICIENTS`

---

## 1. Purpose

v14.52 established the correct coupled scale form

\[
\Gamma_{\rm rel}(x,a)
=
\sum_p A_p(a)e^{px}+B(a)+Z(a)x,
\qquad
x=\log(L/\ell_{\rm ref}),
\]

and proved that the family-blind algebraic \(\Lambda_{85}\) constraint cannot by
itself generate nontrivial CKM bridges.

v14.53 asks the two next concrete questions.

1. Can any component of \(Z(a)=\zeta_{\rm rel}(0;a)\) be evaluated exactly and
   numerically from the present geometry?
2. Do the additional action-owned family structures recovered in the full
   recall—octave-dependent responses, the \(G_2/C_3\)-odd term, sector weights,
   and overlap semigroups—escape the v14.52 commutativity obstruction?

The answers are:

- one universal minimal-Dirac Weyl component of \(Z(a)\) is evaluable and has
  the scale-stabilizing sign;
- the total anomaly and total relative power coefficient remain unevaluable
  without the matched full-preimage problem;
- every currently action-owned family operator remains inside the abelian
  algebra \(\mathbb C[C_3]\), so the CKM obstruction survives intact.

---

## 2. Minimal Dirac relative Weyl anomaly

For one four-component Euclidean Dirac spinor, choosing the overall sign that
gives a positive Yang–Mills kinetic form gives the local Weyl contribution

\[
a_4(D^2)\supset
-\frac{1}{320\pi^2}
\int d^4x\sqrt g\,
C_{\mu\nu\rho\sigma}C^{\mu\nu\rho\sigma},
\]

modulo the Euler density, total derivatives, kernel dimensions, and additional
endomorphism terms.

Use the diagnostic product

\[
M_4=S^1_T\times S^3_a(R),
\]

with Berger metric

\[
h_a=R^2(\sigma_1^2+\sigma_2^2+a^2\sigma_3^2).
\]

The Weyl invariant is

\[
C^2
=
\frac{64}{3R^4}(a^2-1)^2.
\]

Writing

\[
\tau=\frac{T}{R},
\]

and using

\[
\operatorname{Vol}(S^3_a)=2\pi^2aR^3,
\]

gives

\[
\boxed{
\int_{S^1\times S^3_a}\sqrt g\,C^2
=
\frac{128\pi^2}{3}\tau\,a(a^2-1)^2.
}
\]

For a round parent, \(a_{\rm parent}=1\), this term vanishes. Therefore the
child-minus-round-parent contribution per Dirac spinor is

\[
\boxed{
Z_W(a)
=
-\frac{2}{15}\tau\,a(a^2-1)^2.
}
\]

For \(N_D\) equal minimal Dirac copies,

\[
Z_W(a)
=
-\frac{2N_D}{15}\tau\,a(a^2-1)^2.
\]

It is strictly negative for every nonround positive \(a\neq1\).

### Berger derivatives

Define

\[
F(a)=a(a^2-1)^2.
\]

Then

\[
F'(a)=(a^2-1)(5a^2-1),
\]

\[
F''(a)=4a(5a^2-3).
\]

Hence

\[
Z_W'(a)=-\frac{2N_D\tau}{15}(a^2-1)(5a^2-1),
\]

\[
Z_W''(a)=-\frac{8N_D\tau}{15}a(5a^2-3).
\]

These are exact local contributions to the v14.52 Berger stationarity system.
They are not the full derivative of the full relative determinant.

---

## 3. Numerical diagnostic at the frozen Berger witness

Use only the historical frozen diagnostic

\[
a_{\rm fr}
=
\frac{137.035999084}{12\pi^2}
=
1.157054135733433.
\]

For one Dirac spinor and \(\tau=1\),

\[
F(a_{\rm fr})
=
0.1327927983742844,
\]

\[
\int C^2
=
55.91946185675985,
\]

\[
\boxed{
Z_W(a_{\rm fr})
=
-0.017705706449904587,
}
\]

\[
\boxed{
Z_W'(a_{\rm fr})
=
-0.2571916176486935,
}
\]

\[
\boxed{
Z_W''(a_{\rm fr})
=
-2.27947154125001.
}
\]

As a normalized algebraic check only, set the full power amplitude to
\(A_6=1\) and replace the total anomaly by this single component. The v14.52
one-power equation gives

\[
\left(\frac{L}{\ell_{\rm ref}}\right)^6
=
-\frac{Z_W}{6A_6},
\]

so

\[
\frac{L}{\ell_{\rm ref}}
=
0.37872763993306113,
\]

and

\[
\Gamma_{xx}=-6Z_W
=
0.10623423869942752>0.
\]

This proves the sign mechanism in a deterministic witness. It is not a BHSM
scale prediction because \(A_6=1\) is only a normalization witness and
\(Z_W\) is only one component of the total anomaly.

---

## 4. Why the full numerical scale point still cannot be emitted

The full quantities are

\[
A_p(a)
=
A_p^{\rm child}(a)-A_p^{\rm parent}(a),
\]

\[
B(a)
=
\Gamma_{\rm finite}^{\rm child}(a)
-
\Gamma_{\rm finite}^{\rm parent}(a),
\]

\[
Z(a)
=
\zeta_{\rm child}(0;a)-\zeta_{\rm parent}(0;a).
\]

A numerical evaluation requires one matched pair with identical comparison data:

- the full child Einstein–eta–collar–Higgs–Dirac–Yang–Mills solution;
- the corresponding parent reference solution;
- the common self-adjoint seam domain;
- all bosonic, fermionic, gauge-fixed, and ghost Hessians;
- collective-zero-mode subtraction;
- GHY, corner, interface, and counterterm completion;
- the trace-class relative heat kernel and kernel-dimension ledger.

The existing numerical witnesses

\[
\Delta\widehat{\mathcal E}_{\rm red}=9.8689261083,
\qquad
\lambda^*=0.3644325544,
\qquad
\Delta\widehat E_{\rm BY}\approx10.5970
\]

cannot be inverted into \(A_p,B,Z\). They were computed with incomplete source
content and witness coefficients, and the omitted terms alter both the
stationary background and the fluctuation operators.

Thus v14.53 supplies a real numerical component of the anomaly, not a false
full-preimage value.

---

## 5. Complete current action-owned family algebra

Let \(C\) be the cyclic shift on the exact family space, \(C^3=I\). The current
action-owned family structures are combinations of:

- exact \(C_3\) projectors;
- octave-dependent diagonal attachment response;
- the odd response \(iy(C-C^2)\);
- Berger spectral functions;
- the overlap semigroup;
- sector degree or incidence rescalings;
- the family-identity weak current.

Every such Hermitian response can be written

\[
\boxed{
H_f
=
a_fI+x_f(C+C^2)+iy_f(C-C^2).
}
\]

More generally,

\[
H_f=\sum_{n=0}^2c_{f,n}C^n.
\]

All such operators lie in

\[
\mathbb C[C_3].
\]

Because \(C_3\) is abelian, its complex group algebra is abelian. Therefore

\[
\boxed{
[H_u,H_d]=0
}
\]

for arbitrary sector-dependent coefficients.

This remains true when

\[
y_u\neq y_d,
\qquad
x_u\neq x_d,
\qquad
a_u\neq a_d.
\]

The two matrices share the same discrete Fourier eigenbasis. Consequently,

\[
V_{\rm CKM}=W_u^\dagger W_d
\]

is the identity up to row/column phases and permutations.

### Consequence for the recovered odd coefficient

The nonzero \(G_2/C_3\)-odd coefficient is a genuine family-splitting result. It
can distinguish the three character eigenvalues and orient an already sourced
complex response. But while it remains inside \(\mathbb C[C_3]\), it cannot
produce a nonzero Jarlskog invariant between the up and down sectors.

Thus:

\[
\boxed{
\text{family nondegeneracy}
\not\Rightarrow
\text{family mixing}.
}
\]

---

## 6. Required noncentral tensor current

The existing normalized Peter–Weyl library supplies a noncentral operator basis.
The minimal \((L,r)\) channel table is

\[
\begin{array}{c|ccc}
 & D_0&D_1&D_2\\\hline
U_0&(0,0)&(3,0)&(4,-2)\\
U_1&(3,3)&(3,3)&(1,1)\\
U_2&(5,4)&(4,4)&(2,2)
\end{array}
\]

and all nine channels have nonzero normalized representation-theory witnesses.

Representation theory does not fix their physical coefficients. Those must be
obtained from an action variation:

\[
\boxed{
\Gamma_+
=
\frac{\delta^3S}
{\delta W^+\,\delta\bar\Psi_{u,L}\,\delta\Psi_{d,L}}.
}
\]

For normalized embeddings \(T_u,T_d\) and normalized tensor harmonics
\(M_{Lr}\),

\[
\boxed{
c_{ij}^{Lr}
=
\left\langle
T_ue_i,
P_u\Gamma_+[M_{Lr}]P_dT_de_j
\right\rangle_{\rm common}.
}
\]

The raw current is

\[
K_{ud}=\sum_{L,r}c^{Lr}M_{Lr}.
\]

Only after this kernel is action-owned may whitening and polar extraction be
performed:

\[
V
=
\operatorname{Pol}
\left(
G_{uu}^{-1/2}K_{ud}G_{dd}^{-1/2}
\right).
\]

A full-rank three-family current needs at least three independent separable
channels or one genuinely nonseparable extended kernel.

The foundational \(M_4\) Dirac action currently supplies the family identity
\(I_3\). The \(M_8\) envelopment action and \(\Lambda_{85}\) constraint contain
no chiral fermionic tensor current. Therefore the coefficient functional is not
present in the current action.

An intrinsic \(M_4\) Peter–Weyl tensor-current or quark-Yukawa functional may be
adopted as new foundational effective data, just as the local Dirac sector was
adopted. It must not be described as derived from the existing bosonic parent
action unless a larger action produces its coefficients.

---

## 7. Hindsight 20/20

### Validated

- The minimal Dirac Weyl part of the relative anomaly is exactly evaluable on
  the Berger diagnostic.
- With positive gauge kinetic sign, that component is negative for every
  nonround Berger child relative to a round parent.
- Its first and second Berger derivatives are explicit.
- It has the sign required to stabilize a positive power-law term in the scale
  direction.
- Every currently action-owned family response is a polynomial in the same
  \(C_3\) shift.
- Sector-dependent coefficients inside \(\mathbb C[C_3]\) still commute.
- The normalized Peter–Weyl tensor library is the required noncentral basis.

### Invalidated

- Promoting a single local anomaly component to the full relative anomaly.
- Reconstructing \(A_p,B,Z\) from the reduced energy or Brown–York witnesses.
- Using the nonzero \(G_2/C_3\)-odd coefficient as a complete CKM or CP source.
- Expecting different up/down circulant coefficients to create basis mismatch.
- Expecting \(\Lambda_{85}\), Berger functional calculus, or common holonomy to
  cross distinct family representation blocks.

### Reclassified

- The scale problem now has a demonstrated sign-compatible quantum component,
  but remains a matched-background spectral computation.
- The \(G_2/C_3\)-odd response is a hierarchy/orientation seed, not a CKM source.
- Physical mixing belongs to a noncentral tensor-current or noncommuting Yukawa
  action on the intrinsic fermion stratum.

### Open

- Matched full-preimage child and parent backgrounds.
- The complete relative power coefficients \(A_8,A_6,A_3\).
- The complete relative anomaly and finite determinant.
- A stable nondegenerate \((L_*,a_*)\).
- An action-owned Peter–Weyl coefficient functional.
- Physical quark Yukawa operators, CKM and CP.
- Confinement, neutrino monodromy, and absolute physical scale.

---

## 8. Completion status

BHSM remains physically incomplete. v14.53 evaluates one universal component of
the relative anomaly and proves the complete present \(C_3\)-algebra obstruction.
It does not emit a physical scale, coupling, mass, CKM matrix, or CP phase.
Frozen predictions and official prediction logic are unchanged. The USB remains
untouched.
