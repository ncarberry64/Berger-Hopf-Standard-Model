# BHSM v14.43 — Moduli-to-Clifford, Core–Wall Matcher, and Zeta Audit

## Primary verdict

`BHSM_BOSONIC_FR_KNOT_MODULI_QUANTIZATION_AND_THE_FLAT_Z2_FR_LINE_DO_NOT_DERIVE_A_UNIQUE_LOCAL_SPACETIME_CLIFFORD_PRINCIPAL_SYMBOL_OR_CANONICAL_SECOND_QUANTIZED_FIELD_NORMALIZATION`

## Secondary verdict

`BHSM_SELF_ADJOINT_CORE_WALL_DIRAC_TRANSMISSION_REQUIRES_A_UNITARY_CLIFFORD_INTERTWINER_FAMILY_BUT_THE_ACTION_DOES_NOT_SELECT_ITS_RELATIVE_HOLONOMY`

## Spinor-lift verdict

`THE_V12_1_L2_L3_CLEBSCH_FACTORS_ARE_EXACT_ORBITAL_FACTORS_BUT_FULL_KOSMANN_MATRIX_ELEMENTS_REQUIRE_AN_ACTION_SELECTED_SPINOR_HARMONIC_LIFT_AND_RADIAL_REDUCED_ELEMENTS`

## Zeta verdict

`ROUND_S3_ZETA_DIAGNOSTICS_ARE_EXACT_AND_SCHEME_CONSISTENT_BUT_DO_NOT_FIX_THE_FOUR_DIMENSIONAL_RENORMALIZED_COEXACT_STRESS_POLARIZATION`

---

## 1. The exact moduli-space output

Let \(q^A\) denote normalized collective coordinates of a localized degree-one
eta configuration. Substitution into the bosonic Path-B action produces a
collective action of the form

\[
L_{\rm mod}
=
-M_\eta
+
\frac12G_{AB}(q)\dot q^A\dot q^B
+\cdots,
\]

or, for the translational zero mode before expansion,

\[
S_{\rm trans}
=
-M_\eta\int ds.
\]

Quantization therefore supplies a scalar mass-shell or Laplace–Beltrami
operator:

\[
\sigma_2(H_{\rm mod})(q,p)
=
G^{AB}p_Ap_B\,I.
\]

The FR line changes the global equivariance condition:

\[
\Psi(\gamma q)
=
(-1)^{N\nu(\gamma)}\Psi(q).
\]

It selects fermionic rotation/exchange signs and half-integer spin parity in an
odd-degree sector. It does not change the local differential order of the
collective Hamiltonian.

---

## 2. Clifford-rank obstruction

The FR object is a complex line bundle:

\[
\operatorname{rank}_{\mathbb C}L_{\rm FR}=1.
\]

A complex spatial Clifford module for three dimensions has minimum rank two,
and a full complex four-dimensional spacetime Clifford module has minimum rank
four:

\[
\operatorname{rank}_{\mathbb C}S_3\ge2,
\qquad
\operatorname{rank}_{\mathbb C}S_{1,3}\ge4.
\]

Thus the flat FR line cannot itself support matrices obeying

\[
\{\gamma^\mu,\gamma^\nu\}=2g^{\mu\nu}I.
\]

This is a rank obstruction, not merely an absent numerical coefficient.

A Clifford linearization can certainly be supplied after adding a spinor
module:

\[
(\gamma^\mu p_\mu)^2
=
p^2I.
\]

But the bosonic moduli metric and FR character do not choose:

- the spacetime Clifford module;
- Dirac versus Weyl realization;
- chirality;
- the total connection;
- the local first-order action coefficient;
- the response endomorphism.

---

## 3. The canonical Hodge–Dirac does not solve the spacetime problem

Given the moduli-space metric and FR line connection, one may construct
canonically

\[
D_{\mathcal M}
=
d_{L_{\rm FR}}+d_{L_{\rm FR}}^\dagger,
\]

with

\[
D_{\mathcal M}^2
=
\Delta_{\mathcal M}.
\]

This is a genuine first-order square root. However, it acts on

\[
\Lambda^\bullet T^*\mathcal M\otimes L_{\rm FR},
\]

and its principal symbol is Clifford multiplication by
\(T^*\mathcal M\), not by \(T^*M_4\). It enlarges the state space to
moduli differential forms and does not select a local Lorentz spinor.

Therefore:

\[
\boxed{
D_{\mathcal M}\text{ exists canonically}
\quad\not\Rightarrow\quad
D_{M_4}=i\gamma^\mu\nabla_\mu\text{ is action derived}.
}
\]

---

## 4. Canonical local-field normalization remains open

Suppose the effective action is written conditionally as

\[
S_{\rm eff}
=
Z_\Psi\int d^4x\sqrt{-h}\,
\bar\Psi i\slashed D\Psi+\cdots.
\]

Under

\[
\Psi_{\rm new}=c\Psi_{\rm old},
\]

one has

\[
Z_{\Psi,{\rm new}}
=
\frac{Z_{\Psi,{\rm old}}}{|c|^2}.
\]

The normalized one-particle rays, FR sign, and spin parity are unchanged after
wavefunction renormalization. They therefore do not determine the local pole
residue \(Z_\Psi\).

Canonical field normalization requires at least one of:

1. an action-derived map from eta fluctuations to \(\Psi_\eta\);
2. a derived equal-time anticommutator;
3. a two-point pole-residue theorem;
4. action-normalized stress and gauge currents.

None is produced by FR parity alone.

---

## 5. Exact core–wall self-adjoint transmission theorem

Let \(D_c\) and \(D_w\) be first-order Dirac Hamiltonians on the core and wall
pieces. Their seam Green form is

\[
\mathfrak B(\psi,\phi)
=
-i\int_\Sigma
\left[
\psi_c^\dagger\alpha_{n_c}^{c}\phi_c
+
\psi_w^\dagger\alpha_{n_w}^{w}\phi_w
\right].
\]

Impose a transmission condition

\[
\psi_w=U_{cw}\psi_c.
\]

With outward normals, self-adjointness requires

\[
\boxed{
U_{cw}^\dagger\alpha_{n_w}^{w}U_{cw}
=
-\alpha_{n_c}^{c}.
}
\]

Using one common normal from core to wall, this becomes

\[
\boxed{
U_{cw}^\dagger\alpha_n^{w}U_{cw}
=
\alpha_n^{c}.
}
\]

The matcher must also be unitary for the seam Hermitian metrics and intertwine
the retained color, weak, hypercharge, FR, and regularity structures.

### Nonuniqueness

If \(U_0\) is one solution, then

\[
U=U_0C
\]

is another whenever \(C\) is unitary and commutes with the normal Clifford
symbol and every retained seam structure.

For a rank-four normal symbol with two positive and two negative eigenvalues,
the unrestricted normal-symbol commutant contains

\[
U(2)_+\times U(2)_-.
\]

Internal-bundle constraints reduce this group but do not generally collapse it
to a unique element.

Therefore self-adjointness derives a **matcher class**, not the physical
relative holonomy.

The relative shift vertex remains

\[
V_{\rm rel}
=
V_c-U_{cw}^\dagger V_wU_{cw}.
\]

Its value cannot be evaluated until the action selects \(U_{cw}\).

---

## 6. Orbital versus spinorial \(L=2,L=3\) coefficients

The frozen Berger blocks used in v12.1 are orbital modules:

\[
\begin{aligned}
\text{up}:&(J,m)=(0,0),(3,3),(5,4),\\
\text{down}:&(J,m)=(0,0),(3,0),(4,2).
\end{aligned}
\]

The exact orbital Clebsch factors are

\[
C(0,0;3,3|3,3)=1,
\]

\[
C(3,3;2,1|5,4)=\frac{\sqrt{10}}5,
\]

\[
C(0,0;3,0|3,0)=1,
\]

\[
C(3,0;2,2|4,2)=-\frac{\sqrt{21}}7.
\]

These remain valid.

A local spinor lift tensors each orbital module with spin \(1/2\):

\[
J\otimes\frac12
=
\left(J-\frac12\right)
\oplus
\left(J+\frac12\right),
\]

with only \(1/2\) for \(J=0\).

For an orbital tensor \(T^{(L)}\), the spinorial reduced matrix element is

\[
\begin{aligned}
&\langle(j_t,\tfrac12)\mathcal J_t
\Vert T^{(L)}\Vert
(j_s,\tfrac12)\mathcal J_s\rangle\\
&\quad=
(-1)^{j_t+1/2+\mathcal J_s+L}
\sqrt{(2\mathcal J_t+1)(2\mathcal J_s+1)}
\begin{Bmatrix}
 j_t&\mathcal J_t&\tfrac12\\
 \mathcal J_s&j_s&L
\end{Bmatrix}
\langle j_t\Vert T^{(L)}\Vert j_s\rangle.
\end{aligned}
\]

The v14.43 implementation evaluates these exact 6j factors for all branches
of the three minimal transitions. One nominal up-sector \(L=2\) branch
vanishes identically after recoupling.

The full Kosmann operator is

\[
V_\beta
=
-i\beta^i\nabla_i
-
\frac{i}{4}(D_i\beta_j)\gamma^{ij}.
\]

Its reduced element contains:

- orbital transport recoupling;
- spin-connection recoupling;
- radial/collar overlap;
- normalized shift-harmonic amplitude;
- core–wall transmission data.

Thus the old orbital Clebsch numbers are not yet the final local-Dirac
coefficients.

Rigid \(L=1\) remains a Killing generator and is block diagonal in the full
symmetry representation. The new recoupling audit does not promote a rigid
rotation into a flavor source.

---

## 7. Exact round-\(S^3\) zeta diagnostic

For one intrinsic two-component complex spinor on a round sphere,

\[
|\lambda_n|
=
\frac{n+3/2}{R},
\qquad
d_n=(n+1)(n+2).
\]

Counting both signs,

\[
\boxed{
\zeta_{|D|}(s)
=
2R^s
\left[
\zeta_H(s-2,\tfrac32)
-
\frac14\zeta_H(s,\tfrac32)
\right].
}
\]

Exact values are

\[
\boxed{\zeta_{|D|}(0)=0,}
\]

\[
\boxed{R\zeta_{|D|}(-1)=-\frac{17}{480},}
\]

and therefore

\[
\boxed{
R E_{\rm Casimir}^{(2\text{-component})}
=
-\frac12R\zeta_{|D|}(-1)
=
\frac{17}{960}.
}
\]

These values validate the free round-cap spectral convention. They are not a
BHSM mass or vacuum-energy prediction: species multiplicity, response terms,
mass, seam matching, and the physical radius are unresolved.

Most importantly, the \(L=2,L=3\) quantity is not the unperturbed Casimir
energy. It is the second variation of the complete four-dimensional
determinant. Its physical channel coefficient remains

\[
\Lambda_L^{\rm ren}
=
c_2^{\rm ren}q_L
+c_4^{\rm ren}q_L^2
+\Pi_L^{\rm nonlocal},
\qquad
q_L=(L-1)(L+3).
\]

Zeta regularization supplies a definite analytic prescription after the full
operator is known, but it does not remove the freedom to choose finite local
gravitational and seam counterterms. Those coefficients must be fixed by the
parent action or explicit renormalization conditions.

---

## 8. Bifurcation status

The v14.41 classical stiffness remains positive:

\[
q_2=5,
\qquad
q_3=12.
\]

The v14.42 filled-sea transition term retains the correct nonpositive bare
sign. But the present audit finds that its physical evaluation still lacks:

1. an action-owned local spacetime Clifford module and principal symbol;
2. canonical local field normalization;
3. an action-selected core–wall transmission intertwiner;
4. a selected spinor-harmonic lift of every frozen Berger block;
5. normalized radial and seam matrix elements;
6. the full heat-kernel operator and finite renormalization conditions.

Therefore no \(L=2\) or \(L=3\) zero crossing can yet be calculated.

---

## Hindsight 20/20

### Validated

- The bosonic moduli action produces a scalar mass-shell/Laplace principal
  symbol.
- The FR line supplies global spin/statistics parity but cannot carry the local
  spacetime Clifford algebra.
- A Hodge–Dirac square root exists on moduli space but has the wrong base for a
  local \(M_4\) field.
- The self-adjoint core–wall transmission condition is an exact unitary
  Clifford-intertwining theorem.
- The v12.1 orbital Clebsch factors are exact.
- Spinor lifting introduces exact 6j recoupling factors and branch dependence.
- The free round-\(S^3\) zeta values above are exact.

### Invalidated

- Treating FR parity as a derivation of gamma matrices.
- Treating the normalized knot Hilbert norm as the local field residue.
- Treating self-adjointness as a unique seam-holonomy selector.
- Treating the v12.1 orbital Clebsch factors as already-complete Dirac/Kosmann
  reduced matrix elements.
- Treating the free spatial zeta determinant as the renormalized
  \(L=2,L=3\) polarization.

### Reclassified

- The v14.5 Dirac operator remains a conditional minimal local realization of
  a spin-\(1/2\) one-particle sector.
- The next true derivation requires a Clifford superconnection, worldline spin
  factor, or equivalent first-order structure whose square is owned by the
  knot dynamics.
- The seam problem is now a selection problem inside a derived matcher class.

### Open

- Action-owned spacetime Clifford principal symbol.
- Canonical local-field normalization and measure.
- Action-selected core–wall matcher.
- Spinor branch and total magnetic-state lift of frozen family modules.
- Full normalized Kosmann reduced elements.
- Complete heat-kernel coefficients and finite renormalization conditions.
- Physical \(L=2,L=3\) crossing, CKM, CP, masses, and scale.

---

## Exact next object

`ACTION_OWNED_CLIFFORD_SUPERCONNECTION_OR_WORLDLINE_SPIN_FACTOR_WHOSE_SQUARE_RECOVERS_THE_FR_KNOT_MODULI_HAMILTONIAN_TOGETHER_WITH_AN_ACTION_SELECTED_CORE_WALL_TRANSMISSION_INTERTWINER_AND_NORMALIZED_SPINOR_HARMONIC_EMBEDDINGS_FOR_THE_L2_L3_KOSMANN_POLARIZATION`

BHSM remains incomplete. Frozen predictions are unchanged. The USB remains
untouched.
