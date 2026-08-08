# BHSM v14.42 — Collective Dirac and Coexact Vacuum-Polarization Audit

## Primary verdict

`BHSM_FR_KNOT_PARITY_ROTOR_AND_H1_DOMAIN_DO_NOT_BY_THEMSELVES_DERIVE_AN_ACTION_NORMALIZED_LOCAL_COLLECTIVE_DIRAC_OPERATOR_OR_ITS_L2_L3_VACUUM_POLARIZATION`

## Secondary verdict

`ANY_GAPPED_SELF_ADJOINT_DIRAC_COMPLETION_COUPLED_THROUGH_THE_ADM_KOSMANN_VERTEX_HAS_A_NONPOSITIVE_BARE_COEXACT_TRANSITION_SUSCEPTIBILITY_ZERO_ON_KILLING_MODES_BUT_THE_RENORMALIZED_ZERO_CROSSING_IS_NOT_YET_DEFINED`

## Renormalization verdict

`THE_V14_41_EINSTEIN_ONLY_THRESHOLD_IS_A_RESTRICTED_SCHEME_CONTRACT_BECAUSE_CURVATURE_SQUARED_COUNTERTERMS_ADD_INDEPENDENT_LAMBDA_L_SQUARED_CONTRIBUTIONS`

## Exact next object

`MODULI_DERIVED_RELATIVISTIC_FR_KNOT_PRINCIPAL_SYMBOL_AND_CANONICAL_NORMALIZATION_WITH_UNITARY_CORE_WALL_SPINOR_MATCHER_ZETA_OR_HEAT_KERNEL_RENORMALIZATION_AND_EXPLICIT_L2_L3_KOSMANN_REDUCED_MATRIX_ELEMENTS_ON_THE_COMPACT_CAP`

---

## 1. Starting point

v14.41 proved that the stationary source-free coexact ADM shift is a positive
Killing-operator square.  On a round `S3(R)`,

\[
\lambda_L^{\rm shift}
=
\frac{(L-1)(L+3)}{R^2},
\]

so

\[
\lambda_2^{\rm shift}=\frac5{R^2},
\qquad
\lambda_3^{\rm shift}=\frac{12}{R^2}.
\]

The only remaining source-free route was a collective-fermion determinant.
This sprint audits whether the existing FR-knot construction actually defines
that determinant and, where possible, derives its sign and crossing contract.

---

## 2. FR quantization does not yet derive a local Dirac action

The odd-degree FR line fixes the wavefunction equivariance and hence the
integer/half-integer spin parity.  Together with a collective inertia tensor it
produces the rotor Hamiltonian

\[
H_{\rm rot}
=
-\frac1{2I_T}\Delta_{\mathcal M}
\]

on the knot moduli space with FR boundary conditions.

This is a second-order quantum-mechanical operator on collective coordinates.
It does not by itself derive:

- a local `Spin(1,3)` Clifford principal symbol on `M4`;
- the coefficient relating temporal and spatial derivatives;
- a canonically normalized local Grassmann field;
- the response endomorphism `Phi_response`;
- the fermionic functional measure or determinant regulator.

The conditional normal form

\[
D_\eta
=
i\gamma^\mu\nabla_\mu^{\rm total}
+\Phi_{\rm response}
\]

remains a valid low-energy interface, but its first-order principal symbol is
not yet derived from the Path-B eta moduli dynamics.

The no-double-counting rule remains mandatory: `Psi_eta` may represent the
second-quantized knot sector, but it cannot be integrated as an unrelated
ultraviolet fermion in addition to the complete classical eta zero mode.

---

## 3. Compact self-adjoint domain

Assume the conditional Dirac normal form has been supplied on

\[
\Sigma=S^3(R)
\]

with a smooth unitary total connection and a bounded Hermitian mass/response
endomorphism.  Then

\[
H_0
=
-i\alpha^i\nabla_i^{\rm total}
+\beta M_\eta
+\Phi_{\rm response}
\]

has a unique self-adjoint closure on

\[
\boxed{\operatorname{Dom}(H_0)=H^1(S^3,E_{\rm total})}
\]

and compact resolvent.

For the untwisted massless round sphere,

\[
\operatorname{spec}(\slashed D_{S^3})
=
\left\{
\pm\frac{n+3/2}{R}
\right\}_{n=0}^{\infty},
\]

with multiplicity

\[
(n+1)(n+2)
\]

for each sign.

This closes the operator-domain question only **conditional on the supplied
Dirac normal form**.  It does not establish action ownership of that operator.
APS data are not required for the Lorentzian spatial evolution problem on the
boundaryless `S3`; a separate Euclidean index or determinant-phase calculation
remains open.

---

## 4. Matched tetrad and coexact stress vertex

Once a Dirac action is admitted, varying the ADM shift and the Levi-Civita spin
connection together fixes the spinor momentum vertex without a new coupling.
For a divergence-free spatial shift `beta`, use the spinorial Lie derivative

\[
\mathcal L_\beta^K\psi
=
\beta^i\nabla_i\psi
+
\frac14(D_i\beta_j)\gamma^{ij}\psi,
\qquad
\gamma^{ij}=\frac12[\gamma^i,\gamma^j].
\]

The Hermitian stationary vertex is

\[
\boxed{V_\beta=-i\mathcal L_\beta^K.}
\]

It contains both the orbital momentum and the tetrad/spin-connection response.
No independent fermion-rotation coefficient is allowed.

For an exact Killing vector preserving every background field,

\[
[H_0,V_\beta]=0.
\]

Consequently the vertex has no matrix element between the filled negative and
empty positive spectral subspaces, and the transition susceptibility vanishes.
This reproduces the v14.41 statement that the rigid `L=1` rotation is a zero
mode rather than a flavor-instability source.

The true relative core-wall vertex must be

\[
\boxed{
V_{\rm rel}
=
V_{\rm core}
-
U_{cw}^{\dagger}V_{\rm wall}U_{cw},
}
\]

where `U_cw` is a unitary seam identification of the normalized spinor bundles.
That matcher has not been derived.  Therefore the single-cap Kosmann vertex is
fixed conditionally, while the relative determinant remains open.

---

## 5. Exact sign of the filled-sea transition term

Let `H0` be self-adjoint and gapped at zero.  Let `a` label occupied
negative-energy states and `b` empty positive-energy states.  Standard
second-order perturbation theory gives the static filled-sea transition term

\[
\boxed{
Q_{\rm para}[\beta]
=
-\sum_{a<0}\sum_{b>0}
\frac{
|\langle b|V_\beta|a\rangle|^2
}{E_b-E_a}
\leq0.
}
\]

This is an exact sign theorem at any finite symmetry-preserving cutoff.
Therefore a non-Killing collective-Dirac vacuum contribution has the correct
**bare paramagnetic sign** to oppose the positive classical ADM stiffness.

For a Killing shift, the positive-negative transition block vanishes and

\[
Q_{\rm para}=0.
\]

For `L=2` and `L=3`, the Wigner-Eckart selection rules permit nonzero matrix
elements, but the required normalized reduced matrix elements on the compact
Path-B cap have not been calculated.

---

## 6. Why the bare sign does not decide the bifurcation

The continuum spectral sum is ultraviolet divergent.  Integrating out a
four-dimensional fermion renormalizes not only the Einstein term but also
independent curvature-squared operators.  In a fixed coexact harmonic channel,
the conservative dimensionless quadratic normal form is

\[
\boxed{
\Lambda_L^{\rm ren}
=
c_2^{\rm ren}q_L
+c_4^{\rm ren}q_L^2
+\Pi_L^{\rm nonlocal},
\qquad
q_L=(L-1)(L+3).
}
\]

Thus the actual crossing equations are

\[
\boxed{
5c_2^{\rm ren}
+25c_4^{\rm ren}
+\Pi_2^{\rm nonlocal}=0,
}
\]

and

\[
\boxed{
12c_2^{\rm ren}
+144c_4^{\rm ren}
+\Pi_3^{\rm nonlocal}=0.
}
\]

The v14.41 form

\[
c_G\lambda_L+\Pi_L^{\rm ren}=0
\]

is therefore a restricted Einstein-only renormalization contract.  It becomes
complete only after all four-derivative coefficients have been fixed or proved
absent in the chosen effective action.

Only the **total** renormalized Hessian is scheme independent.  A standalone
number called `Pi_L^ren` is not physical until the local subtraction convention
and gravitational coefficients are declared.

No numerical crossing can be calculated without:

1. an action-derived collective Dirac principal symbol and normalization;
2. the physical compact cap and seam matcher;
3. normalized `L=2,3` Kosmann reduced matrix elements;
4. the complete species, mass, and response spectrum;
5. a zeta-function or heat-kernel regulator;
6. renormalization conditions for Einstein and curvature-squared terms.

---

## 7. CP orientation

The quadratic determinant around `beta=0` is real and even under

\[
\beta\rightarrow-\beta.
\]

It can create a nonzero amplitude if a channel crosses zero, but it cannot at
quadratic order choose between conjugate relative orientations.  The v12/v14.37
relative-holonomy or `Z6` mechanism remains a possible **post-crossing branch
orientation**, not the source of the crossing itself.

---

## 8. Hindsight 20/20

### Validated

- The conditional compact twisted Dirac operator has domain `H1(S3,E_total)`
  and compact resolvent.
- The matched single-cap shift vertex is the coefficient-free Kosmann/ADM
  momentum operator.
- The filled-sea transition term is nonpositive.
- The transition term vanishes for invariant Killing shifts.
- A fermionic determinant can, in principle, oppose the positive classical
  `L=2,3` stiffness.
- Independent curvature-squared counterterms modify the zero-crossing test.

### Invalidated

- Treating FR parity plus rotor inertia as a derivation of the local Dirac
  principal symbol.
- Treating the `H1` domain theorem as proof of action ownership.
- Treating the bare negative spectral sum as a finite physical polarization.
- Treating the v14.41 Einstein-only threshold as a regulator-independent final
  equation.
- Extracting CKM or CP before the relative seam matcher and reduced matrix
  elements exist.

### Reclassified

- The compact Dirac-domain gate is conditionally closed.
- The action-normalized collective-Dirac gate remains open.
- The determinant route has the correct bare sign but no physical magnitude.
- The physical bifurcation criterion belongs to the complete renormalized
  gravitational-plus-fermionic Hessian.

### Open

- Moduli-to-relativistic principal-symbol derivation.
- Canonical field normalization and determinant measure.
- Core-wall unitary spinor matcher.
- Physical `L=2,3` reduced Kosmann matrix elements.
- Heat-kernel/zeta determinant and counterterm ledger.
- Total renormalized `L=2,3` eigenvalues.
- Nonlinear branch and relative-holonomy orientation after a crossing.
- Physical CKM, CP, masses, couplings, and scale.

---

## 9. Completion status

BHSM remains incomplete.  Frozen predictions are unchanged.  No physical
Dirac determinant, `Pi_2`, `Pi_3`, CKM matrix, CP phase, mass, coupling, radius,
or dimensional scale is emitted.  The USB remains untouched.
