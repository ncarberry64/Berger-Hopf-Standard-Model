# Gauge-connection reset from the event–child bundle lift

Status: `AE2_ABSTRACT_RESET_LIFT_EXISTS_BUT_AE4_CONNECTION_TRANSPORT_IS_NOT_EVALUABLE_WITHOUT_ITS_LOCAL_ONE_JET`.

This adjudication attacks only the missing nonzero gauge-connection trace map. It does not repeat the preceding reset-boundary canonicality audit.

## Three different geometric objects

The retained lineage owns the following objects at different strengths.

1. **Bundle isomorphism class — exists.** v15.53 returns the Standard Model bundle to the same isomorphism class, transports the representation labels, the three family projectors, hypercharge, and FR parity, and explicitly does not transport connection one-forms as pregeometric primitives.
2. **Actual equivariant boundary lift — exists abstractly.** The owner-authorized AE2 action/domain extension promotes the returned class to a smooth spin–gauge boundary lift

   \[
   U_R=\rho(\operatorname{SpinLift}\Lambda_R)\otimes G_R
   \]

   on the last regular event trace and first regular child trace. AE3.1 reuses this abstract lift for CAR/Hadamard transport. This is stronger than the v15.53 class, so the claim that BHSM owns no lift at all is rejected.
3. **Induced connection transport — not evaluable.** No retained source materializes a local principal-bundle representative

   \[
   \widehat F_B:(x,h)\longmapsto(F_B(x),g_B(x)h)
   \]

   or its local one-jet. In particular, the sources do not supply `F_B(x)`, `D F_B(x)`, `g_B(x)`, and `d g_B(x)` in overlapping event and child boundary charts.

Thus the exact missing datum is

`ACTION_OWNED_EVALUABLE_LOCAL_ONE_JET_J1_FHAT_B_OF_THE_AE2_EVENT_CHILD_GAUGE_EQUIVARIANT_PRINCIPAL_BUNDLE_LIFT_ABSENT`.

## Conditional connection law

The repository already uses the transition convention

\[
 dU_R+(F_B^*A_c)U_R-U_RA_e=0.
\]

For supplied local one-jet data this gives

\[
 F_B^*A_c=U_RA_eU_R^\dagger-(dU_R)U_R^\dagger.
\]

Writing (J^\mu{}_i=\partial F_B^\mu/\partial x^i), the child components obey

\[
 J^\mu{}_i(A_c)_\mu
 =U_R(A_e)_iU_R^\dagger-(\partial_iU_R)U_R^\dagger.
\]

The implementation verifies this identity for supplied theorem-class data. It also separates the affine term from the fixed-background derivative:

\[
 D_{A_e}R_A=J^{-T}\otimes\operatorname{Ad}_{U_R}.
\]

Neither the finite witness nor this standard identity is promoted to a retained BHSM reset map.

## Why the abstract lift is insufficient

At a seam point, the two smooth (U(1)) representatives (g_0(x)=1) and (g_1(x)=e^{ix}) have the same value and the same bundle class, but different first derivatives. For (A_e=0), the affine term therefore gives different child potentials. Likewise, two base maps can share the same incidence point and orientation while having different nonsingular derivatives; a one-form then has different child components. Pointwise trace unitarity, boundary identity, first-hit incidence, and orientation do not remove either ambiguity.

The later statement `NABLA_Phi_U_R=0` occurs in a parameter-space Calderón response witness. Its randomly supplied connection matrices verify covariant frame bookkeeping; they do not instantiate the physical spacetime gauge connection, the seam transition, or the base cotangent map.

## Consequences

The rank-16 (U(1)\oplus SU(2)\oplus SU(3)) representation algebra and the three family slots would be preserved if the missing representative were (G_{SM})-valued: the adjoint term and Maurer–Cartan term remain in its Lie algebra, while the family factor stays (I_3). This is conditional, not an evaluated representation check.

The fermion covariant-derivative intertwining equation is the same missing connection-preserving equation in the associated representation. It therefore cannot select the absent local one-jet from the retained fermion trace map alone. Curvature and holonomy functoriality are also conditional; no mapped loop and evaluable lift representative are retained.

For a supplied derivative (L=D R_A) and weighted boundary pairing (p^\dagger W\,dq), the Maxwell momentum rule would be

\[
 p_c=W_c^{-1}L^{-\dagger}W_e p_e.
\]

The code verifies this conditional weighted cotangent identity. The actual (L), event/child pairing weights, and measures cannot be evaluated before the missing local one-jet is supplied. Consequently the Maxwell cotangent lift, BRST-induced ghost map, full symplectic reset, `beta`, `S_RESET_GFHS`, and its first three graph derivatives remain open.

The HS normal Legendre rank remains zero and `pi_H=0`; no HS canonical momentum or mixed reset term is manufactured.

## Hindsight 20/20

### VALIDATED

- v15.53 owns the returned Standard Model bundle isomorphism class.
- AE2 owns an abstract smooth spin–gauge boundary lift, modulo common gauge frame and global spin sign.
- supplied local one-jet data canonically produce an affine connection transport and a nonzero derivative.
- the identity representative recovers the retained zero-field reference slice.

### INVALIDATED

- a bundle isomorphism class is an evaluable connection transport;
- the AE2 pointwise trace unitary supplies `d g_B` or `D F_B`;
- the parameter-space `nabla_Phi U_R=0` witness instantiates the spacetime gauge reset;
- boundary incidence or orientation determines the pullback of a one-form;
- the v15.57 constant reconstruction extends the reset to nonzero connections.

### OPEN

- the evaluable local one-jet `j1 Fhat_B`;
- `R_A[B;Gamma0_A_event]`, its affine term, and `D R_A[B;0]` at admissible backgrounds;
- the weighted Maxwell cotangent lift, BRST transport, symplecticity, exactness, and reset generating functional;
- the resulting global event balance and global `S2`–`S4` derivatives.

### EXACT NEXT OBJECT

`ACTION_OWNED_EVALUABLE_LOCAL_ONE_JET_J1_FHAT_B_OF_THE_AE2_EVENT_CHILD_GAUGE_EQUIVARIANT_PRINCIPAL_BUNDLE_LIFT_ABSENT`

Materialize the retained principal-bundle lift in overlapping boundary charts as `F_B`, `D F_B`, `g_B`, and `d g_B`. No new reset matrix or fitted coefficient is admissible.
