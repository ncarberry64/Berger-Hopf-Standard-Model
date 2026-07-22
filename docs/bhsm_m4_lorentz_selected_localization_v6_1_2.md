# BHSM v6.1.2 M4 Lorentz-selected boundary localization

## Result and scope

Primary result:
`BHSM_M4_LORENTZ_SELECTED_LOCALIZATION_DERIVED`.

Action status:
`BHSM_M4_EQUATORIAL_LOCALIZATION_SOURCE_SELECTED_ACTION_OPEN`.

The exact Lorentz-normalization condition is stronger than the v6.1.1
constant-profile obstruction. For every admissible nonnegative scalar,
connection, or principal tensor profile, the spatial or magnetic kinetic
normalization is no smaller than its temporal or electric counterpart.
Finite nonzero equality excludes the collapsed polar orbits and selects
support on a totally geodesic equatorial great `S3`. All such equators lie in
one `SO(5)` orbit, so the support class is selected but no preferred axis is.

This theorem does not supply the action that realizes distributional
equatorial fields. The frozen P1 action plus GHY completion, a smooth Z2 cut,
the round collar geometry, the unspecialized sigma sector, P2/P3 boundary
completions, and controlled tree-level bulk-mode integration do not generate
the needed independent intrinsic kinetic terms. The smallest presently
identified boundary-action family has at least three independent coefficients
and remains unsourced. No term or coefficient is added in this sprint.

## Exact geometry and scalar theorem

Use the round M5 line element already derived in v6.1.1,

\[
 ds_5^2=-dt^2+a(t)^2\left(d\chi^2+\sin^2\chi\,d\Omega_3^2\right).
\]

For a scalar profile density `w(chi)>=0`, the temporal and spatial kinetic
weights, after the common `S3` volume and field factors are removed, are

\[
 N_t=a\int_I\sin^3\chi\,w(\chi)d\chi,
 \qquad
 N_s=a\int_I\sin\chi\,w(\chi)d\chi.
\]

Their exact difference is

\[
 N_s-N_t
 =a\int_I\sin\chi\cos^2\chi\,w(\chi)d\chi\ge 0.
\]

Thus exact Lorentz equality requires the measure defined by `w` to be
supported where `sin(chi) cos^2(chi)=0`. The candidates are the equator and
the two poles. At a pole the `S3` orbit collapses, so pole support supplies no
finite nonzero M4 kinetic normalization. The physically admissible equality
support is therefore `chi=pi/2`. Every ordinary smooth nonzero bulk profile,
and every finite-width collar profile, has strict positive mismatch.

## Connection and principal tensor theorems

For a tangential connection profile `u_A`, the electric and magnetic weights
are

\[
 N_E=a\int_I\sin\chi\,|u_A|^2d\chi,
 \qquad
 N_B=a\int_I\frac{|u_A|^2}{\sin\chi}d\chi,
\]

so

\[
 N_B-N_E
 =a\int_I\frac{\cos^2\chi}{\sin\chi}|u_A|^2d\chi\ge0.
\]

When both norms are finite, nonzero equality again selects equatorial
support. Polar support is divergent or degenerate and is not an M4 gauge
sector.

The temporal and `S3`-gradient terms in the tangential transverse-traceless
tensor principal symbol carry the scalar weights `sin^3(chi)` and
`sin(chi)`. The same support theorem therefore applies to that principal
symbol. This is not a completed graviton claim: lapse, normal, and scalar
metric components are constrained, and the full gauge-fixed tensor Hessian
and boundary domain remain open.

## Exact finite-width diagnostic

Let

\[
 |u_p|^2=\sin^p\chi=\cos^p y,
 \qquad y=\chi-\frac\pi2,
 \qquad p>0.
\]

With

\[
 I_q=\int_{-\pi/2}^{\pi/2}\cos^q y\,dy
 =\sqrt\pi\,\frac{\Gamma((q+1)/2)}{\Gamma((q+2)/2)},
\]

the exact ratios are

\[
 \delta_{L,\sigma}=\delta_{L,T}
 =\frac{N_s}{N_t}-1=\frac1{p+2},
 \qquad
 \delta_{L,A}=\frac{N_B}{N_E}-1=\frac1p.
\]

Defining the diagnostic width ratio `epsilon=ell_p/a=p^(-1/2)` gives

\[
 \delta_{L,\sigma}=\delta_{L,T}
 =\epsilon^2-2\epsilon^4+O(\epsilon^6),
 \qquad
 \delta_{L,A}=\epsilon^2.
\]

Every finite `p` fails exact equality. The `p -> infinity` limit is a
distributional equatorial-support limit, not a smooth bound state generated
by the frozen action. No measured Lorentz bound is used.

Adding a finite intrinsic kinetic coefficient `B>=0` equally to the temporal
and spatial normalizations yields

\[
 \frac{N_s+B}{N_t+B}-1=\frac{N_s-N_t}{N_t+B}>0.
\]

It can dilute a bulk mismatch but cannot cancel it exactly. Exact closure
requires boundary-only fields, vanishing bulk support, a distributional
support theorem, or an independently derived compensating structure.

## Exact collar and inverse diagnostic

In the exact collar coordinate `y=chi-pi/2`, the metric and measure are

\[
 ds_5^2=-dt^2+a(t)^2\left(dy^2+\cos^2y\,d\Omega_3^2\right),
 \qquad
 \sqrt{-g_5}=a^4\cos^3y\sqrt\gamma_3.
\]

At one reference time, `rho=a(t0)y` is a proper normal coordinate. Replacing
it by `a(t)y` over a time interval produces cross terms and is not the same
coordinate construction. The round measure is largest at the equator but
does not create a normal bound state: the existing scalar zero mode remains
constant and extended.

Inverse-designing the power profile gives the diagnostic trap

\[
 V_p(y)=\frac1{a^2}\left[-\frac p2
 +\frac p2\left(\frac p2+2\right)\tan^2y\right].
\]

This establishes which operator would admit the selected profile. It does
not derive that potential from P1 and it is not inserted into the action.

## P1, GHY, Z2, and junction audit

The P1 Einstein--Hilbert term supplies the bulk equations. GHY is its
coefficient-locked Dirichlet variational completion. At the equator,
`K_mn=K=0`, so the background GHY value and Brown--York tensor vanish, but
the variation remains necessary. Neither restriction nor cutting creates
independent boundary fields.

Joining two smooth round hemispheres, or taking the reflection quotient,
gives zero extrinsic-curvature jump at the equator. In the declared
orientation convention,

\[
 2C_5([K_{\mu\nu}]-[K]h_{\mu\nu})=-S_{\mu\nu}
\]

therefore gives zero background surface stress. Even fields obey Neumann and
odd fields Dirichlet data. These are boundary conditions, not an action for
new boundary degrees of freedom. The Z2 fixed set is not called a brane.

## Existing sigma localization test

For the frozen neutral sigma sector, the exact static normal equation is

\[
 -\frac{Z_\sigma}{\sin^3\chi}
 \partial_\chi(\sin^3\chi\,\partial_\chi\bar\sigma)
 +a^2U'_{\rm parent}(\bar\sigma)=0.
\]

A constant solution requires `U'_parent=0`. For the declared quartic, an
algebraic kink candidate needs `A0<0` and `G0>0`, with vacua
`+-sqrt(-A0/G0)` and flat-wall diagnostic width
`sqrt(2 Z_sigma/(-A0))`. A kink is odd and crosses zero at the equator; a
positive even lump is a different problem. The coefficient signs, boundary
data, exact round-S4 solution, and coupled stability have not been selected.

More decisively, frozen P1 contains no `f_A(sigma)F^2`, `f_g(sigma)R`,
sigma-dependent connection mass, or boundary Robin source for other fields.
Even a conditional sigma wall therefore would not localize the connection or
tensor sectors without new action couplings.

## Higher curvature and controlled induction

P2 and P3 retain independent `kappa_2` and `kappa_3`. Their standard
Lovelock/Myers Dirichlet completions contain extrinsic-curvature factors and
have zero background value at the totally geodesic equator. They cancel
normal variations of the corresponding bulk actions; they are not
independent intrinsic boundary-field kinetics. No coefficient lock to the
needed M4 terms follows.

For a light/heavy split `Phi=phi_0 u_0+sum phi_n u_n`, tree-level elimination
obeys `O_H phi_H=J_H`. A local polynomial of the constant sigma normal mode
has `J_H=0` against orthogonal heavy modes. Boundary data may source the
tower only after a boundary source or domain is supplied. Where controlled,
elimination produces spectral-denominator nonlocal kernels and derivative
corrections, not a new local primitive. Quantum loops are outside this
sprint.

## Minimal action statement still required

The smallest directly identified intrinsic family is

\[
 S_\partial=\int_{M_4}\sqrt{-h}\left[
 C_\partial R_4-
 \frac{\tau_A}{4}F_{\mu\nu}F^{\mu\nu}-
 \frac{Z_\partial}{2}(D_\mu\sigma)(D^\mu\sigma)+\cdots
 \right].
\]

In length units, `[C_partial]=L^-2`, `[tau_A]=L^0`, and
`[Z_partial]=L^-2`. No source or coefficient-lock theorem has been found in
the frozen parent action. At least three independent coefficients therefore
remain. This family is identified as the minimum missing parent statement;
it is not adopted, normalized, or fitted here.

## Downstream status and permanent firewall

Current and charge normalization remains conditional on action-derived
localized matter and connection profiles. The aperture overlap, projector,
`e_eff`, and `alpha` remain open. The v5 scalar/topographic coefficients are
not imported. No Planck scale, measured coupling, mass, CKM/PMNS input,
cosmological parameter, compactification length, or absolute unit is used.

`BHSM_FERMIONIC_CLIFFORD_AND_NO_MONOPOLE_FIREWALL_FROZEN` remains permanent.
The induced spin and Clifford bundles are mathematical readiness data, not a
physical Dirac equation. Hopf and Chern data are bundle geometry, not
magnetic charge. No monopole harmonics, Dirac strings, magnetic-charge
quantization, monopole-generated chirality, or monopole-generated generation
count is admitted.

Completion gate:
`V6_1_2_LORENTZ_SELECTS_GREAT_S3_SUPPORT_MINIMAL_BOUNDARY_ACTION_UNSOURCED`.

Recommended next branch:
`bhsm-minimal-equatorial-boundary-action-freeze-v6-1-3`.

`FULL_BHSM_NOT_COMPLETE`.
