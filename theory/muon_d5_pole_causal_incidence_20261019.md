# Original D5 pole domain and causal parent data

Continuation from `f9285d08`. The original angular-constant D5 pole
admissibility condition is derived and applied, including a short
Frobenius solution and a bounded global trial. The global trial fails
the original differential equations and is rejected as an accurate
boundary operand. An independent characteristic application then
identifies the actual incoming and initial-face rows acting on the
saved homogeneous family. No new incoming selector, vacuum, beam
preparation or physical boundary state is chosen.

## A pole condition from the original operator and pairing

At the genuine cap endpoint `rho=0`, the original regular coframe obeys

\[
 C_\rho=C_0+O(\rho^2),\quad R=C_0\rho+O(\rho^3),\quad
 N=N_0+O(\rho^2),\quad\zeta=O(\rho).
\]

The same anchored eta field has `f=k rho+O(rho^3)`, with nonzero `k`.
The original geometric radial contact is `3/(2 C0 rho)`, the combined
eta contact contributes `-i epsilon Gamma4/(C0 rho)`, and the retained
n0 right-frame angular spin term is `-3i Gamma123/(2R)`. The mechanical
connection is `O(rho^2)` and the original independent gauge basis has
positive pole power, so neither changes the leading matrix. Therefore

\[
 \rho\partial_\rho\Psi=A_0\Psi+\rho G_{\rm reg}\Psi,
 \qquad A_0=-\tfrac12I-\tfrac32\epsilon\Gamma^4\Gamma^{123}.
\]

The Clifford involution `K=epsilon Gamma4 Gamma123` has square one.
Its projectors `P_reg=(I-K)/2` and `P_sing=(I+K)/2` have exponents
`+1` and `-2`, each of rank 32 on the original 64-component block.
The actual positive Cauchy measure is `C_rho R^3 d rho`, proportional
to `rho^3`. The `-2` solution has logarithmically divergent norm;
finite Cauchy norm excludes its coefficient. This is a domain law
from the differential expression and pairing, not an arbitrary
spectral polarization. The leading conical/eta identities persist
under the supplied regular background variations, giving `delta A0=0`;
the source dependence of the remainder is retained.

For `Psi=rho Z`, the first two regular Frobenius orders satisfy

\[
 Z=V+\rho B_1+\cdots,\quad A_0V=V,\qquad
 (2I-A_0)B_1=G_{\rm reg}(0)V .
\]

There is no resonance when constructing the branch starting at `+1`:
subsequent exponents cannot equal `-2`. The finite-start estimate of
the nonsingular remainder and the omitted orders still need error
control. The fermionic localization equation and its full normal
normalization remain distinct:

\[
 (\partial_s+\tfrac12\partial_s\log J
       -\partial_s\log\sin f)u_\eta=0,\qquad
 \int_{\text{actual normal domain}}J|u_\eta|^2ds=1 .
\]

Neither that integral nor the full normal-collar/exterior incidence is
replaced by a cap-radial norm. The pole is not the numerical strip face.
The existing Higgs interaction remains its once-only intrinsic seam.

The owners are [original D5 coefficients](../src/bhsm/interface/muon_holomorphic_d5_trace_action.py),
[full differential expression](../src/bhsm/interface/muon_full_d5_differential_form.py),
and [new pole application](../src/bhsm/interface/muon_d5_pole_admissibility.py).

## Executed short application and rejected global trial

`PARENT_POLE_SHORT_v1` evaluates the original parent ten-node temporal
operator and its corrected-Xi source, using all 40 regular columns of
an eight-carrier block. Its first two Frobenius orders are propagated
from `rho=1e-10` to `8e-10`. Original independent matrix-component
D5/source residuals are `5.29925e-16` and `6.62091e-15`. The regular
boundary coordinate pivot has condition `1.00055`; its value/source
identity residuals are `1.78284e-16` and `4.33681e-19`. These check the
finite provisional application, not its omitted-start error or a
physical normalization. A report-serialization error occurred after
the numerical arrays were saved; its receipt was repaired from those
arrays without repeating the application. Both driver/error evidence
are preserved.

`PARENT_LEPTON_POLE_GLOBAL_v1` then executes a bounded 36-cell outward
trial on the Spin4/internal6,7 weak block. Every regular amplitude,
value/source transition and row-coordinate change is retained. The
actual original coefficient callbacks are evaluated in batches; no
old near-wall or native calculation is rerun. Recharting changes basis
by `Y -> Y(Y_pivot)^-1`, with the full derivative and amplitude
transition retained. It does not select an amplitude or take a
minimum-norm solution.

The global trial fails:

| Evaluated quantity | Maximum |
| --- | ---: |
| Original independent D5 matrix component | 4.79337e30 |
| Original independent source matrix component | 4.12914e41 |
| Stage value/source arithmetic | 2.12567e18 / 2.07642e29 |
| Regular-frame pivot condition | 1.14630e35 |

Failure is visible before final condition collapse: on
`rho=[3.40102e-6,6.52882e-6]`, independent D5/source residuals are
`0.193218` and `1.68290`, with pivot condition `744.1`. At
`rho=[1.25331e-5,2.40594e-5]` they are `56.5692` and `427.862`.
The original near-wall response is sewn to this trial only as a
diagnostic. Its formal 40-row h pivot has condition `1.67756e10`;
the conditional coefficient reaches `3.15547e8`, with reconstructed
value/source errors `1.96590e-7` and `4.35062e11`. The appended
admission interpretation explicitly rejects that h correction as
accurate or physical. Small final annihilator arithmetic cannot
repair the failed propagated field.

All arrays, actual source owners, inputs and failures are retained.
This failed sidewise temporal-polynomial approximation is not a
physical no-go, evidence for another vacuum, or permission to delete
homogeneous columns. Its shared 64-factor propagation is family
independent; the diagnostic sewing used family 0. The following actual
parent characteristic application uses muon family 1 explicitly.

## Actual hyperbolic incidence and a well-conditioned h row

The original principal coefficients are

\[
 T=i\Gamma^0/N,\quad
 R=i\epsilon\Gamma^4/C_\rho-i\zeta\Gamma^0/N,\qquad
 T^{-1}R=\epsilon(N/C_\rho)\Gamma^0\Gamma^4-\zeta I .
\]

The characteristic speeds are `-zeta +/- N/C_rho`. On the timelike
material wall there are 32 incoming and 32 outgoing components per
64-dimensional block. In the original fixed coframe the outer incoming
projector is `(I-epsilon Gamma0 Gamma4)/2`. This characteristic
projector is not an incoming particle/antiparticle polarization.

`PARENT_CHARACTERISTIC_v1` recovers the actual principal matrix and
its source from already evaluated off-time blocks
`G_ij=-R_i^-1 T_i D_ij`; no new coefficient solve is performed.
Its characteristic eigenvector residual is `6.67069e-16`. Evaluated
speeds range from `-2.23152` to `2.76741`. Triangle bounds on the
exact held affine/trigonometric coefficient formulas give speed bound
`5.70571` over the represented cap/time slab. This is binary64
evaluation of an algebraic bound, not an interval rounding enclosure.
Over its `1e-5` parent time span the backward radial reach is at most
`5.70571e-5`, compared with pole distance `1.5707962`.

Consequently the backward domain of dependence of the E1 near-wall
response meets the earliest time face and/or incoming timelike face,
not the pole, on this local slab. A global pole law cannot replace
those causal data. The original physical rows are

\[
 \Pi_{\rm in}\Phi_{p,\rm wall}(g,h)=d_{\rm in},\qquad
 \Gamma_{\Sigma_{t_0}}\Phi_p(g,h)=\Psi_{\rm prep}|_{\Sigma_{t_0}}.
\]

For the saved affine wall family `Phi=P a+Q h`, the first is

\[
 (\Pi_{\rm in}Q)h=d_{\rm in}-(\Pi_{\rm in}P)a .
\]

The actual muon-family weak8 block gives 40 incoming rows on **all
3660** h coordinates. Its explicit pivot has rank 40 and condition
`1.000000232`; all remaining 3620 coordinates and their independent
variations remain represented. The conditional coefficient mapping
the saved particular slots to those pivots has max `1.13707`;
reconstructed known particular/source rows are `1.11023e-16` and
`4.62224e-33`. The incoming datum is an independent retained term,
not zero. No h, g, normal profile or physical state has been selected.
The source row retains both coefficient/state placements and the
independent incoming/amplitude/h sources.

In particular the 40 pivot h coordinates are replaced by **40 free
incoming characteristic coordinates**, together with the unchanged
3620 free h coordinates. The net physical-data dimension is unchanged.
For coefficient maps `H_a,H_d,H_f`, their actual source law is
`delta h_p=H_a delta a+H_d delta d_in+H_f delta h_free`
plus `H_a,Xi a+H_d,Xi d_in+H_f,Xi h_free`. No datum or source in this
equation is fixed by the coordinate reparameterization.

Actual earliest-time field, source, time and radial coefficients are
also evaluated at three saved-strip radii. They are finite restrictions
of the Cauchy-face equation, not the full physical initial section or
a preparation norm. The old bulk/source nonpasses remain applicable.

## The adopted preparation determines the required right-hand side

For a specified incoming linear section, use the already adopted
dressed stationary-past prescription, with its wave operator anchored
at the **adopted** preparation slice:

\[
 \Omega_{-,\tau_{\rm prep}}
 =\lim_{\tau\to-\infty}U_y(\tau_{\rm prep},\tau)
       J(\tau)U_{\rm as}(\tau,\tau_{\rm prep}),\quad
 P_{{\rm as},\pm}={\bf1}_{\mathbb R_\pm}(h_-^{\rm phys}).
\]
\[
 \Psi_{\rm prep}|_{\Sigma_{t_0}}
 =\mathcal I_{{\rm coll}\to\Sigma_{t_0}}\,
 U_y(\tau(t_0),\tau_{\rm prep})\,
 \Omega_{-,\tau_{\rm prep}}P_{{\rm as},\pm}f_{{\rm as},a} .
\]

The comparison and physical time/gauge generator must be those of the
same constrained action, with the required long-range dressing. The
map `I` is the actual collider-to-parent Cauchy/domain, spin/gauge,
density and unit incidence; the cap boundary S3 is not the entire
collider. The initial-face derivative includes these map/section
derivatives and the moving time/radial point contacts already saved
as separate coefficients. Neither an identity incidence nor a scalar
Gram normalization supplies that equation.

This is the remaining **adopted construction**, not another selector
adjudication. The current checkpoint does not evaluate its complete
stationary generator, wave-operator limit or collider incidence.
The fixed beam envelopes, energies, widths, centers and exact
unpolarized pair are not changed or requested again. Four beam legs
are used in their actual charge/family sectors; they are not copied
as a muon-family initial field. The same interacting transition
determines pair conversion and occupation. A one-particle propagation
or a nonzero odd field expectation does not replace that state
calculation. Complementary inherited reference contractions remain
where consumed; no homogeneous reference field is silently removed.

The next physical consumer is the joint parent initial/incoming and
child event/corner system, using these actual coefficients and the
computed child Cauchy response. It must retain the original outer,
normalization and constrained formation rows, all h/delta-h and
independent source/domain variations. The adopted selector,
calibration, historical nonpasses, once-only local/native accounting
and `2e-10` physical guard are unchanged. No full physical residual,
coupled correction or magnetic readout is admitted by this checkpoint.
