# Incoming C1 active-Higgs restriction: bounded source audit and response reduction

Repository: `ncarberry64/Berger-Hopf-Standard-Model`.
Pinned commit: `ad750077f1a3138418a2dc4ee65f7c50236b5608`.
Task: derive the retained incoming C1 LR/Higgs contribution without copying the conditional C2 vacuum, selecting a carrier amplitude or covariance, changing action ownership, or replacing scalar domain data with the fermion reference condition.

## Result

The retained action supplies an active-Higgs Euler equation, a fixed family Yukawa structure, and the normalized collar pullback. These suffice to derive the incoming scalar Jacobi forcing and an adjoint reduction of its consumed first variation. In the inspected incoming enclosure/energy producers, the propagated state contains geometry/rates/lapse/shift and a free conformal Casimir term; it contains no active-Higgs value, Cauchy data, or Higgs energy enclosure. Consequently this bounded audit supplies no numeric `H_C1` or consumed scalar response. It is not a global absence theorem and does not establish a need to select a physical carrier member or covariance.

The precise scalar operand is the actual incoming residual/domain binding

`F_H,C1[H;theta]=0`, `B_H,C1[H;theta]=0`,

together with its directional source and an inverse/retarded/adjoint estimate on the already retained parameter family. Here `B_H,C1` means the action-owned incoming scalar trace/Cauchy/reset graph in the *active intrinsic M4 Higgs representation*. It is not the product-carrier `u_E0=0` reference, an internal profile normalization, or an arbitrary diagonal scalar graph.

## 1. Source facts and exact scope

1. `src/bhsm/interface/ae31_c2_intrinsic_m4_lepton_action.py:29-63` defines H as an intrinsic M4 active field, T_l as a fixed internal family operator, the additive lepton-Higgs block, and `V_BH=kappa (H†H-nu²)²` with `kappa>0`. Its lines 66-88 give `Y_l=(16 sqrt(2 pi)/3969)T_l`. Its lines 91-112 give an explicitly conditional current-C2 vacuum saddle, not the incoming scalar solution. Lines 148-173 give the scalar Euler equation used below.
2. `src/bhsm/interface/completion/foundational_dirac_spin_glue_v14_45.py:92-134,185-227` gives the adopted collar action and exact normalized normal pullback. `A_eta u0=0`, `integral J|u0|² ds=1`; the two-sheet Higgs normal overlap is one and leaves Y_f unchanged.
3. `src/bhsm/interface/action_extension_global_spin_reset_ae2.py:156-194` defines the fermion Spin x G_SM graph and opposite normal flux graph. It does not by itself supply an active-Higgs C1 Cauchy solution.
4. `src/bhsm/interface/ae31_c2_chiral_green_domain.py:93-114` proves that the family mass operator and the Spin x G_SM reset act on separate tensor factors. It permits retention of the frozen family factor under a compatible scalar transport; it does not identify an incoming H background with the C2 vacuum.
5. `src/bhsm/interface/full_field_moving_reset_graph_decision.py:59-94,123-152,300-329` records a conditional scalar pullback and density-weighted momentum law when a spatial map and polarization are supplied, and gives their moving-domain derivative. This historical Track-2 result must not be promoted to a selected current scalar graph. It also must not be treated as a prohibition on deriving the current restricted graph from later action data.
6. `src/bhsm/interface/ae31_c2_universal_scalar_profile_transport.py:1-5,171-203` treats internal `Phi(y)`, including its conditional normalization and attachment to H. It is a different object from active `H_C1(lambda,rho)`.

All fetched raw source texts are in `source_snapshot/` under their repository paths. The source manifest records the pinned Git blob hashes and exact byte checks.

## 2. What the incoming family and energy actually enclose

`scripts/certify_n12_incoming_regularized_terminal_segment.py:21,87-105` uses the retained geometric `exact_full_action_jet_at_state` on a 98-coordinate state. `scripts/derive_n12_incoming_finite_amplitude_coefficient_enclosure.py:56-79,180-213` enclose its radius, proper duration, and radius derivative. The scalar coefficient named in that calculation is the *geometric product-channel potential*. `scripts/derive_n12_compact_finite_history_operator.py:163-164` explicitly identifies it as

`K_c=-D_tau²+c exp(-2 x)`, `D_h K_c=-2c exp(-2x)h`.

It is not `V_BH(H)=kappa(H†H-nu²)²`.

The exact local action producer `src/bhsm/interface/aether_n3_exact_full_local_action_jet_v17_60.py:132-225` uses scale and u/w/b harmonic coefficients, their velocities, lapse and shift. Its final matter contribution is

`-C_SM exp(log N_boundary)/R4`,

with `C_SM=59/30`. The imported owner `src/bhsm/interface/aether_m4_standard_model_zeta_backreaction_v15_51.py:1-6,53-103,135-152` explicitly identifies the scalar/vector/Weyl contribution as a free conformal vacuum spectral sum. It is not a bound on the active-Higgs quartic, gradient energy, source, or boundary value. The local producer contains no active H coordinate.

Therefore no H upper bound follows from that particular action-ball certificate. Merely knowing `kappa>0` supplies no numerical energy upper bound, boundary bound, or uniform scalar response inverse. The historical `theory/scalar_higgs_gap_full_solution.md` explicitly describes a scalar scaffold/gap proxy and an open full-spectrum proof; it is not an incoming active-Higgs solution.

## 3. Differentiate the owned active-Higgs equation

Use `kappa=lambda_H` for the Higgs quartic coefficient, to distinguish it from the carrier amplitude `lambda`. Let

`s=H†H`, `J=bar(e_R)Y_l†L_L`.

The action-owned equation is

`F_H=-D²H-2 kappa(s-nu²)H-J=0`.

Let `h_alpha=delta_alpha H`. At fixed independent fermion coordinates, the real-linear scalar Jacobi operator is

`L_H h=-D²h-2 kappa[(s-nu²)h+(H†h+h†H)H]`.

The exact first variation yields

`L_H h_alpha=(delta_alpha D²)H+delta_alpha J`
`             +2 delta_alpha kappa (s-nu²)H`
`             -2 kappa delta_alpha(nu²) H`.

The h† term is essential: this is a real-linear operator, or a complex-linear operator on the doubled (h,conjugate(h)) space. It cannot be replaced by a complex-linear scalar multiplier. If the consumed direction owner fixes kappa and nu², the last two terms vanish. They must remain until that ownership is established; the physical common-scale direction is not removed by the carrier construction.

If the fermion source has already been eliminated or evaluated self-consistently, write `delta J=D_H J[h]+delta J|_H`. Then the scalar operator becomes `L_H-D_HJ`, and its forcing uses `delta J|_H`. Other induced gauge/HS/constraint responses belong in the corresponding coupled Hessian or its justified Schur reduction. This does not require selecting a numerical covariance merely to define the kernel of that source response.

In a fixed real coordinate representation `H=(x1+i x2,x3+i x4)`, with `r=(x1,x2,x3,x4)`, the potential part of the Jacobi operator is

`-2 kappa[(r.r-nu²) I4+2 r r^T]`.

At a potential minimum `r.r=nu²` its tangential directions are zero, while the radial coefficient is `-4 kappa nu²` in the displayed Euler sign convention. Positive quartic stiffness therefore cannot serve as a uniform inverse estimate for the full constrained, Lorentzian, gauge-covariant scalar response. The existing action/domain must supply the gauge quotient and the appropriate retarded or boundary estimate.

## 4. Metric, gauge and time-pullback forcing

Writing `D²H=mu^(-1)D_mu(mu g^(mu nu)D_nu H)`, `b=delta log(mu)`, and `A_mu` for the connection in the Higgs representation, its coefficient derivative at fixed H is

`(delta D²)H = -b D²H`
` + (delta A_mu)g^(mu nu)D_nu H`
` + mu^(-1)D_mu{mu[(b g^(mu nu)+delta g^(mu nu))D_nu H`
`                         +g^(mu nu)(delta A_nu)H]}`.

This retains the derivative of the volume measure and both covariant-derivative factors. H has no spin representation, but its gauge connection and the metric derivative remain.

The incoming family uses normalized forward time rho, with rho=1 at E1 and rho=0 at the formation-side edge. In a terminal-centered chart,

`tau(rho,lambda)=tau_E1+(rho-1)T(lambda)`.

Consequently the pulled-back variation includes

`h_alpha^material = h_alpha|_tau + [delta_alpha tau_E1+(rho-1)delta_alpha T] D_tau H`,

with the compatible connection/frame transport when using a gauge-covariant material derivative. The duration dependence must enter the same normalized operator and pairing once. A bounded radius path does not determine this scalar time derivative.

## 5. Scalar boundary graph and its first variation

Suppose the existing action supplies an actual trace transport `T_H` in the Higgs-associated representation, written in the convention

`Gamma_c H_c=T_H Gamma_e H_e`.

Its derivative is

`Gamma_c h_c-T_H Gamma_e h_e`
`  =(delta T_H)Gamma_e H_e+T_H(delta Gamma_e)H_e-(delta Gamma_c)H_c`.

The ordinary first field variation graph is only the homogeneous left side. Moving maps, frames and evaluation points supply the right side. In an assumed diagonal scalar graph with no scalar seam action, the variation of the displayed +|DH|² action gives the common-pairing momentum balance

`pi_e+T_H* pi_c=0`,

where `pi` is the outward normal covariant scalar momentum, including the actual density/conormal normalization. Differentiating that equation adds `(delta T_H*)pi_c` and the derivatives of normal, density and connection. This is a conditional derivation of what an owned diagonal graph would imply, not proof that the fermion AE2 rule selected that scalar graph.

The additive LR coupling has no H derivatives, so it contributes a bulk scalar source and no additional bare scalar normal momentum. Any induced/contact contribution must still be accounted for in the full action.

## 6. Consumed LR variation and adjoint elimination

Let `X=Y_f H`, `M_LR=[[0,X],[X†,0]]`. In the normalized normal pullback, the overlap equals one identically. Along admissible deformations preserving this normalization its derivative is zero:

`delta integral J|u0|² ds=0`.

Thus there is no additional normal-overlap renormalization of Y_f. Intrinsic H, gauge/frame transport, and any genuinely moving family representation must still be differentiated.

The consumed local density variation is

`K_alpha,LR=-[(b_alpha beta+delta_alpha beta)M_LR+beta delta_alpha M_LR]`,

with `delta X=(delta Y_f)H+Y_f h_alpha`. For a fixed family operator in its compatible trivialization, delta Y_f is zero in that factor; a moving representation must retain its induced commutator rather than adding a fitted derivative.

To avoid computing every `h_alpha`, bundle the scalar Jacobi equation, its incoming boundary/Cauchy equations, and any gauge constraints into one same-domain real-linear map

`A_H h_alpha=f_alpha`.

The lower components of `f_alpha` are exactly the inhomogeneous trace/domain forcing above; they are not zeroed. If the E1 contraction consumes a real-linear scalar functional `ell_alpha(h)`, solve the compatible adjoint

`A_H* p_alpha=ell_alpha`.

Then

`ell_alpha(h_alpha)=<p_alpha,f_alpha>`

in the owned real duality, including boundary multipliers. This is the minimal scalar contraction route. It can remain parametric in the retained carrier amplitude and in admissible state data; it does not require materializing a full scalar matrix or choosing a physical amplitude.

An adjoint residual enclosure is also possible. If `r_alpha=ell_alpha-A_H* p_alpha` and a valid scalar response bound `||h_alpha||<=B_alpha` is available, then the contraction error is at most `||r_alpha|| B_alpha`. The tiny carrier seam inverse factor is not an estimate for `||A_H^{-1}||`; these are distinct action response operators.

## 7. Full-action stationarity can remove induced h only in its actual scope

For a completely supplied stationary scalar solution with the actual boundary graph and vanishing admissible scalar boundary residual, the first derivative of the total reduced action obeys the envelope identity: scalar-induced bulk terms from kinetic, potential and LR pieces cancel in the sum. This can remove explicit h from that *total first derivative*. It does not set H to its C2 vacuum, remove explicit H coefficients, or establish cancellation of the LR summand alone.

E1 covariance sensitivity differentiates an action-variation row again. Its scalar-induced response can re-enter through mixed derivatives; the corresponding reduced Hessian has the familiar constrained Schur term. A first-order envelope argument therefore cannot by itself set the complete CAR kernel to zero. It may be used only after the actual total stationary action and boundary contacts have been supplied.

## 8. Minimal next numeric/scientific inputs

The first new required producer should bind the active-Higgs restriction to C1 by providing:

- the actual source functional J and its consumed directional derivative at fixed H (or its coupled operator representation);
- the incoming H trace/Cauchy/reset constraint and its first variation, in the Higgs representation on the retained C1 geometry;
- the same-family scalar background enclosure and the relevant constrained/retarded/adjoint response estimate, with any moving scale coefficients retained;
- its contraction with the existing E1 LR/DtN readout, including the scalar boundary multipliers.

A direct enclosure of this final projected contraction can replace separate global sup-norm bounds on H and every variation if it is derived from the same action and domain. No available calculation in the inspected producers evaluates that contraction. No physical member-selection necessity, nonzero CAR verdict, moment rank, physical a_mu, or physical g_mu is inferred here.
