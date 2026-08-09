# BHSM v14.88 action-selected charge/current-shape Schur gate

## Verdict

No presently retained physical BHSM sector action-selects the required
nonzero reflection-odd coexact L2 charge. This closes the retained
closed-system current route without erasing the conditional response theorem.

On the fixed zero canonical eta-momentum sector, pointwise Legendre
invertibility is valid for every nearby shape in the positive cone. Therefore

\[
D_0\eta(Q)=0,\qquad J_\eta(Q)=0,\qquad
P_{\mathrm{coex},L=2}D_QJ_\eta=0.
\]

This is a theorem about the whole local current map, not merely its value on
one symmetric background.

## Charge selection and FR audit

The physical Path-B eta field is a map into S6 on M4. Its static and
configuration-loop groups relevant here are

\[
\pi_3(S^6)=0,\qquad
\pi_1(\operatorname{Map}_*(S^3,S^6))=\pi_4(S^6)=0.
\]

It consequently has no physical degree-one eta sector and no nontrivial FR
line. The historical S7-to-S7 result remains valid in its original M8 sector:
odd degree conditionally gives the FR rule \(2j=N\pmod 2\) and lowest
\(j=1/2\). It cannot be promoted to physical M4 charge without the missing
action-owned transgression, physical rotation-loop identification, degree-one
background and common domain. Even conditional \(j=1/2\) fixes spin parity and
magnitude, not a preferred magnetic orientation; a nonzero vector current is
not selected by that statement alone.

The adopted effective Dirac sector permits charged states, but its action does
not select occupation number, charge, or state orientation. Those are state or
superselection data. Wilson states are externally sourced. Gauge/color charge
is constrained by the physical singlet architecture or remains a
superselection choice. None is the internally selected nonzero source required
by this gate.

## Fixed-charge Routh theorem

For a collective rotor

\[
L=\frac12 I(Q)\omega^2-V(Q),\qquad p_\theta=C,
\]

positive inertia gives the unique solution \(\omega=C/I(Q)\). The Routhian and
fixed-charge effective potential are

\[
\mathcal R_C=L-C\omega=-V-\frac{C^2}{2I},\qquad
V_C=V+\frac{C^2}{2I}.
\]

Thus zero charge gives zero angular velocity. A nonlinear eta charge-velocity
relation is likewise unique only on a connected branch satisfying the v14.87
pointwise Legendre cone. No retained physical nonzero charge exists on which
to evaluate a global charge bound.

## Representation kill screen

Use doubled Spin(4) weights. The round scalar ell=2 shape is `(2,2)`. A rigid
coexact L=1/Killing current is `(2,0) + (0,2)`. Their products contain

`(0,2), (2,2), (4,2), (2,0), (2,2), (2,4)`,

but the coexact L=2 target `(3,1) + (1,3)` is absent. Hence the round Spin(4)
rigid-rotor vertex has \(B_{L2}=0\). Under only diagonal SO(3), however,
\(1\otimes2=1\oplus2\oplus3\); L2 is allowed. The round no-go is therefore not
extended to an unknown degree-one reduced-symmetry background. That branch
still lacks the background, state selection, domain and reduced matrix
elements.

## Exact common-domain Schur theorem

Let

\[
\Gamma_{\rm eff}(Q)=\frac12Q^THQ-\frac12J(Q)^TK(Q)^{-1}J(Q).
\]

At the reference point define \(G=K_0^{-1}\), \(\beta=GJ_0\),
\(B_a=\partial_aJ\), \(C_{ab}=\partial_a\partial_bJ\), and
\(r_a=B_a-K_a\beta\). The symmetrized response Hessian is

\[
\begin{aligned}
S_{ab}={}&-C_{ab}^T\beta
-\tfrac12(B_a^TGr_b+B_b^TGr_a)\\
&+\tfrac12(r_b^TGK_a\beta+r_a^TGK_b\beta)
+\tfrac12\beta^TK_{ab}\beta .
\end{aligned}
\]

This includes nonzero background current and first/second operator variation.
Projector, zero-mode and moving-domain effects must first be expressed through
a common-domain trivialization and included in J and K. Without that
trivialization the Frechet derivative is not defined.

For \(J_0=0\), all K-variation terms drop out at second order and

\[
S=-B^TK_0^{-1}B\preceq0
\]

when the gauge-reduced momentum operator is positive. On the round L2
reference, \(K_{\beta,L2}=5/(\kappa_{\rm grav}R^2)\), so

\[
\Delta H_{L2}=-\frac{\kappa_{\rm grav}R^2}{5}B_{L2}^TB_{L2}.
\]

The factor follows from eliminating beta in
\(\frac12\beta^TK\beta-\beta^TJ\), not from the field equation alone. The
implementation verifies the general formula by deterministic finite
differences and verifies nonpositivity with a non-diagonal positive operator.

## Reflection and completion boundary

After canonical identification of cap spaces,

\[
B_{\rm rel}=B_+-R_J^TB_-R_Q.
\]

Reflection-even identified vertices cancel and reflection-odd vertices double.
Which case is physical cannot be selected before the full-preimage background
and coupled self-adjoint domain exist.

`FULL_PREIMAGE_CHARGE_MOMENTUM_SHAPE_COMMON_DOMAIN = OPEN_NOT_DERIVED`

Cap inertias, the complete ell=2 Hessian, its eigenvalues, nonlinear locking,
alpha-criticality and Floquet stability remain open. The v11.5 spectral CKM
kernel remains an author-selected no-fit candidate; neither charged-current
provenance nor the action-owned family-noncentral left-handed source is closed.

## Hindsight 20/20

Validated: the fixed-zero-charge eta vertex vanishes as a function of shape;
the fixed-charge Routh theorem; the exact general common-domain Schur Hessian;
and the round Spin(4) representation no-go.

Invalidated: physical M4 S6 FR charge; promotion of a merely allowed conserved
charge to a selected vacuum charge; and the retained zero-momentum eta route to
nonzero current-shape response.

Reclassified: historical M8 FR charge as conditional on physical transgression
and state selection; the negative Schur response as a valid conditional
mechanism with no retained physical source.

Open, exactly:

`ACTION_DERIVED_CONSERVED_REFLECTION_ODD_COEXACT_L2_EXCHANGE_CURRENT_SHAPE_VERTEX_FROM_THE_DRIVER_BHSM_COUPLED_FUNCTIONAL_WITH_NO_ARBITRARY_PROFILE_OR_SUSCEPTIBILITY`

No frozen prediction or official prediction logic is changed. USB
synchronization is not eligible.
