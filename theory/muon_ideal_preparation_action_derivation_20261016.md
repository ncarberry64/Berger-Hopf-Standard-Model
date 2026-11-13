# Action derivation for the adopted ideal collider preparation

The adopted Gaussian target fixes the beam design. Its physical realization
requires one coupled background, incoming-mode and unit solve. The local
Euler equations and current maps follow from the supplied action. They do
not by themselves define either the full microscopic positive operator or
a preferred inherited quantum reference.

## Coupled physical unit and preparation

`UniversalGFScaleMap` owns the shared calibration `G_F=c_F/Lambda^2`, with
`c_F` obtained from the physical charged-current low-energy contraction.
There is no new calibration choice. Write `e=log(Lambda_GeV)`, where
`Lambda_GeV` is the numerical value of the common energy unit in GeV.
The adopted preparation then enters the dimensionless action chart as

```text
E_beam_chart = 0.5 exp(-e)
sigma_chart = (100 fm) exp(e) / (hbar*c in GeV*fm)
X3_e_chart = -10 sigma_chart
X3_p_chart = +10 sigma_chart
F_scale = G_F[in GeV^-2] exp(2e) - c_F[Phi, modes, domain] = 0.
```

Thus `D F_scale = 2 G_F exp(2e) D e - D c_F`. The last term includes the
total variation of background, normalized physical modes, sources and
domain; the preparation maps also move as `D E_chart=-E_chart D e` and
`D sigma_chart=sigma_chart D e`. An old conditional scale may be an initial
guess while `e` remains unknown. Freezing it would skip the calibration
equation; holding its chart packet fixed while `e` changes would alter the
adopted physical preparation.

The existing charged-current route retains all 24 gauge/Higgs Green legs
and their mixed contractions in `muon_static_coupled_charged_current.py`.
Physical pole/residue normalization and the full low-energy contraction
must produce `c_F`; fitting its finite-cell tensor to a V-minus-A template
does not do so. In `muon_charged_current_fermi_reduction_20261010/run_4`,
both `physical_c_F` and `E_kappa_GeV` remain null. They are unevaluated
action-solution values, not additional experimental inputs.

## Operators forced by local variation

For the retained scalar density, set `a(sigma)=Zchi(1+g sigma^2)`,
`b=Zsigma`, and `V=A0 sigma^2/2+G0 sigma^4/4`. Varying
`-a |dchi|^2/2-b |dsigma|^2/2-V` at fixed metric gives

```text
E_chi   = div(a dchi)
E_sigma = b Box(sigma) - (a'/2)|dchi|^2 - V'.
```

For variations `(u,v)=(Dchi,Dsigma)`, its exact scalar Jacobi expressions are

```text
D E_chi   = div(a du + a' v dchi)
D E_sigma = b Box(v) - a'<dchi,du>
            - [(a''/2)|dchi|^2 + V'']v.
```

Metric, moving measure, domain and boundary variations must be added when
those operands move. These expressions follow directly from
`master_action/terms.py` and `master_action/variations.py`; they do not assign
new coefficients. Similarly the retained bilinear lepton action fixes its
Dirac Euler expression and all spin, Yukawa and gauge insertions. The current
interaction-dependent two-trace law fixes the local fermion transmission.

The microscopic owner instead specifies
`Gamma_ind=-1/2 STr E1(ell^2 P_strat)` with
`P_strat=D_strat^dagger D_strat` on a closed graded domain and quotient.
A local Jacobi Hessian is not automatically this generating operator.
Squaring a second-order Hessian would change its differential order;
identifying it with the microscopic carrier requires an explicit action
correspondence and a compatible statistics and quotient prescription.

For a fixed positive invertible realization, trace-class relative
variation and a fixed grading, differentiating the proper-time integral gives

```text
D Gamma_ind|fixed_domain
  = (1/2) STr[P^-1 exp(-ell^2 P) DP]
    + (D ell / ell) STr[exp(-ell^2 P)].
```

Here the operator must first be pulled to fixed input/output Hilbert
pairings by the action-owned density/frame isometries, with their jets:
`Dhat=T_out D_strat T_in^-1`. On that chart, for real field variations,
`DP=(delta Dhat)^dagger Dhat+Dhat^dagger(delta Dhat)`. An analytic
continuation requires the independently continued adjoint leaf, without
conjugating analytic source coefficients. A varying pairing left in the
original chart has additional adjoint/pairing contacts. Moving-domain,
quotient, zero-mode, relative zeta and eta contacts remain separate required
terms. This does not add excluded moving-adjoint terms to the original
fixed-adjoint matching derivative. The formula is a conditional
differentiation identity, not their evaluation or a physical force result.

The explicit geometric M8 constructor supplies the untwisted Spin16
component and says that internal twisting/endomorphisms and native
statistics are not selected. If one proposes a geometric-only `P8(G)` at
fixed metric and domain, its induced scalar variations can enter only
through the actual cutoff, support or relative-completion dependence.
Its claimed local expansion must reproduce the scalar kinetic and Jacobi
work above through those dependencies. That is a necessary matching
identity to derive; naming `D_strat` or adopting a geometric Dirac component
does not establish it. This does not rule out a full BHSM correspondence,
nor establish multiple complete BHSM models.

## Why inherited transport does not select the reference

Fix an admitted Dirac operator/domain and its current-unitary Cauchy
evolution `U_t`. In a normalized Cauchy chart an ordinary positive
two-point covariance `C` gives

```text
W_C^+(t,s) = U_t C U_s^dagger
G_R(t,s)   = -i theta(t-s) U_t U_s^dagger.
```

In the self-dual chart, with `Gamma` the CAR antiunitary, admissible covariances obey
`0<=C<=I` and `C+Gamma C Gamma=I`. For any nonzero admissible smooth change
`X` preserving these conditions, `U_t X U_s^dagger` is a smooth homogeneous
bisolution and changes the two-point function while leaving the retarded
kernel unchanged. Unitary reset transport maps this freedom bijectively.
This is a fixed-operator state-selection issue, not proof of two different
self-consistent BHSM field solutions.

The distinction between causal propagation and state covariances is also
explicit in Gerard and Stoskopf, sections 3.2 to 3.4:
[Hadamard states for quantized Dirac fields](https://arxiv.org/html/2108.11630v3).
Their existence construction supplies admissible state classes, not a BHSM
selection of the inherited reference on the present interacting branch.

The adopted condition says that extra incoming occupation and coherent
radiation vanish relative to the inherited reference. It fixes a relative
excitation after that reference is given; it supplies no equation for `X`.
The Gaussian specifies a spatial beam envelope and does not make the exact
pair mixture a quasifree sea. The FR rotor ground ray acts on a different
carrier and cannot be substituted for the full Dirac reference.

The actual inherited-state receipt still has
`C_C1,E1_minus_BHSM=null` and `owned_selection_found=false`. A derived
stationary/asymptotic or Euclidean construction selecting this state, or a
proof that the particular requested application is independent of it,
would resolve that dependency. A new phenomenological population is not
introduced.

## State dependence of the packet and source application

Once actual normalized incoming sections `U_s,V_s` are constructed, the
existing pair-current consumer gives the finite excitation difference

```text
Delta j_K = (1/2) sum_s [U_s^dagger K U_s - V_s^dagger K V_s].
```

This relative current requires no separately supplied complementary sea
covariance. Ordered higher current products must retain the exact pair
Fock density. Their finite excitation algebra does not replace full
continuum current products and inherited reference contractions.
State-independent retarded kernels and matched internal
Green-current cancellations also remain valid.

Constructing those physical particle/antiparticle sections from the
Gaussian target still needs an actual incoming polarization or an owned
scattering construction and the complete Cauchy pairing. Local principal
projectors, homogeneous constant spinors and eigenvectors of a finite
positive factor cannot be promoted to those physical modes. Absolute
inherited current/stress and state-sensitive interacting contractions need
the owned reference and subtraction wherever their dependence survives.

The downstream physical calculation remains the common-domain source
projection, connected chronological complement solve and terminal return,
followed by fixed-preparation radial/history convergence and the independent
complete derivative at `2e-10`. Only that admission permits one coupled
correction and fresh original Maxwell/all226 validation. The old residuals
are historical diagnostics, not the new preparation's before-values. Both
spin states and the full magnetic matrices are retained through physical
pole/residue and soft Pauli normalization.
