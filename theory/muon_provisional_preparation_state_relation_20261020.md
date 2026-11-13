# Preparation equations, conditional first iterate and the consumed state relation

This document treats `UNCOMPLETED_ATTEMPT_v1.json` as a dependency receipt:
it records no new numerical preparation equations. It supplies no failed
preparation solve and no numerical initial residual for a new application.
The companion numerical application owns its actual sections, source,
iterations and residual values. The equations here specify their scope.
The dressed stationary-past prescription is already adopted. No additional
selector decision, beam input, vacuum choice or factorization is made here.

## 1. Smallest physical preparation and its unknowns

One common incoming Cauchy domain is needed, rather than an independent
background for each beam. Its unknowns are:

* The background fields and momenta on that domain: intrinsic metric/frame,
  lapse/shift and their cap/matcher variables; gauge connection and electric
  momentum; Higgs doublet and momentum; the other retained scalar and
  constraint fields. In the existing static comparison chart these are
  `z=(q37,m24,s,a84,H4,e)`, with `e=log(Lambda_GeV)`. A Cauchy application
  also retains their time jets and normal/endpoint conormals; ordinary
  stationarity is a comparison ansatz, not a physical boundary condition.
* Four sections `F=(U_up,U_down,V_up,V_down)` on this same domain, with their
  complete Cauchy pairing and incoming comparison maps. The point fiber has
  all 18 components; the electron-family subspace has six. Its charged
  four-component fiber does not reduce the actual comparison Hamiltonian.
* The collision-chart incidence `I`, its tetrad/spin/gauge/density
  identification, and the normal inclusion and complement. These are maps
  on sections and their derivatives, not numerical labels of cap nodes.
* The physical common unit `e`, the action-derived low-energy coefficient
  `c_F`, and the native cutoff/domain data wherever consumed. `dS/de` is not
  the GF calibration equation.
* Only the inherited-state contractions consumed by the retained equations,
  with their matched subtraction and joint dressing. These are distinct
  from the exact four-mode pair density and from its known CAR products.

Two field conventions must be kept explicit. Write
`xi=R4^(3/2) psi` for the density-rescaled geometric field and
`chi_cap=xi/V`, `V=2 pi^2`, for the common cap-action canonical field.
The constant factor does not change the local Dirac operator. The
conditional four-column application below uses `chi_cap` and its unit
CAR pairing. The original local Dirac applications are

\[
 (i\partial_\tau-h_y)U_s=0,\qquad
 (i\partial_\tau-h_y)V_s=0,
\]
\[
 H_y=-{i\alpha^a\over R_4}(E_a+\Omega_a)
       +{3\gamma_5\over2R_4}+M_Y(H)-i\Omega_\tau,
 \qquad h_y=T_yH_yT_y^{-1}+i\dot T_yT_y^{-1}.
\]

`T_y` is the action isometry to a fixed Cauchy pairing, including actual
frame/density/domain motion. The displayed round-S3 formula is the existing
local operator on that declared comparison; an arbitrary spatially varying
conformal radius requires its actual coframe/spin terms. The residual is
the original application to each supplied column, not an inferred heat
eigenvalue. The complete four-column pairing for the common canonical
sections is

\[
 \int_{\Sigma}\!d\mu_C\,U^\dagger U=I_2,\quad
 \int_{\Sigma}\!d\mu_C\,V^\dagger V=I_2,\quad
 \int_{\Sigma}\!d\mu_C\,U^\dagger V=0.
\]

The already-adopted boundary equations are

\[
 f(\tau)-J(\tau)U_{as}(\tau,0)f_{as,\pm}\longrightarrow0
 \quad(\tau\to-\infty),\qquad
 f_{as,\pm}\in\operatorname{Ran}{\bf1}_{\mathbb R_\pm}(h_-^{phys}),
\]
\[
 \Omega_-^{(T)}=U_y(0,-T)J(-T)U_{as}(-T,0).
\]

The physical clock/gauge lift, long-range dressing, complete domain and
normalization belong inside this construction. Zero, bound and scattering
complement sectors retain their own conditions. A finite local comparison
application establishes no infinite-past limit or full scattering domain.

The fixed external design remains the coherent Gaussian spectral amplitude
in the adopted local collision frame,

\[
 g_a(k)=(2\pi\sigma_k^2)^{-3/4}
   \exp[-|k-k_a|^2/(4\sigma_k^2)-ik\cdot X_a/(\hbar c)],
 \qquad\sigma_k={\hbar c\over2(100\,\mathrm{fm})},
\]

with opposite central directions, central on-shell total energy 500 MeV per
beam, centers `X3_e=-1000 fm`, `X3_p=+1000 fm`, zero extra chirp and phases,
and the exact independent unpolarized pair mixture. Actual pole/dispersion,
measure conversion, sign-space projection and complete normalization must
be applied before reporting achieved energy, widths and centers. The scalar
design moments are targets, not achieved relativistic charge moments.

## 2. Original source, gauge, Higgs and constraint rows

The retained exact Fock16 mixture supplies the signed bilinear expectation
`diag(1/2,1/2,-1/2,-1/2)`. Consequently the original material source is

\[
 j_c(x)={\mu(x)\over2}\sum_s
   \{U_s^\dagger(iG_c)U_s-V_s^\dagger(iG_c)V_s\}.
\]

`G_c` are the original unit-Tr16 generators. For the material temporal
coordinate, `dH_can/dA_t^c=-iG_c/N_ind`: the action factor `N_ind` cancels
once. No extra electromagnetic coupling, family multiplicity or Haar
volume is inserted. The exact pair current and its ordered products are
evaluated from the retained density; they are not replaced by Wick products
of a mean covariance.

The scalar and raw intrinsic lepton actions enter the common cap action
with `1/V^2`. This factor is present before the fermion field is made
canonical. Up to the original symmetric-kinetic endpoint term, the actual
rescaling is

\[
 S_{\ell,cap}={1\over V^2}S_{\ell,raw}
 ={1\over V^2}\int dt\,d\Omega\,
       \xi^\dagger(i\partial_t-N_{ind}H_{can})\xi
 =\int dt\,d\Omega\,
       \chi_{cap}^\dagger(i\partial_t-N_{ind}H_{can})\chi_{cap}.
\]

The corresponding action symplectic/CAR pairing is
`V^-2 integral xi^dagger xi dOmega = integral chi_cap^dagger chi_cap dOmega`.
Thus complete Haar-normalized sections of `chi_cap` with the exact
unit-CAR pair annihilators have `mu=1` relative to the existing cap gauge
rows. Multiplying these sections' source by another `V^-2` would count
the raw-to-cap normalization twice. Sections normalized instead as
`integral xi^dagger xi=1` would have the raw-field coefficient `mu=V^-2`
and would require the corresponding CAR rescaling; the two conventions
cannot be mixed. This conclusion follows from the action's kinetic
pairing and field rescaling, not from an 18-by18 point Gram identity.
The explicit inherited anchors are
`muon_charged_current_fermi_reduction.transported_fermi_template`
(`S4/V^2`, `chi_hat=R4^(3/2)psi/V`, `Y0=1/sqrt(V)`),
`muon_primal_charged_current_response.charged_current_action_source`
and `muon_magnetic_open_lepton_vertex.canonical_open_field_vertices`.

The original gauge equations, including the temporal constraint, are

\[
 {\delta S_M\over\delta A_\nu^c}
 +{\delta S_H\over\delta A_\nu^c}
 +{\delta S_\ell\over\delta A_\nu^c}
 +\ell_{\mathrm{matched\ native/state},\nu c}
 +\ell_{\mathrm{exterior/interface},\nu c}=0,
\]
\[
 D_i\Pi^i+j_{\rm pair}+j_{\rm other}=0.
\]

These derivatives are actual original-action applications. In the existing
constant-angular radial chart their literal Maxwell integrand is

\[
 L_M={1\over2}\{k|X|^2+e_M\sum_i|T_i-\beta R_i|^2
                    -r_M\sum_i|R_i|^2-d_M\sum_i|B_i|^2\},
\]
\[
 X=\dot A_\rho-\partial_\rho A_t+[A_t,A_\rho],\quad
 T_i=\dot A_i+[A_t,A_i],\quad
 R_i=\partial_\rho A_i+[A_\rho,A_i],
\]
\[
 B_i=2A_i+\tfrac12\epsilon_{ijh}[A_j,A_h].
\]

Here `k,e_M,r_M,d_M,beta` are the original geometric densities; `e_M` is
not the log-unit variable. The mechanical spatial connection is included
once in total `A_i`. For stationary temporal tests `zeta`, the actual
original Gauss weak row is

\[
 \int d\rho\,[k\langle D_\rho A_t,D_\rho\zeta\rangle
   +e_M\sum_i\langle[A_t,A_i]-\beta R_i,[\zeta,A_i]\rangle]
 +\delta S_H[\zeta]+J_{\rm pair}[\zeta]
 +\ell_{\rm matched}[\zeta]+\ell_{\rm ext}[\zeta]=0.
\]

Natural central temporal regularity is `lim k D_rho A_t=0`; the singular
branch is excluded. It is not the spatial coexact condition `A_t(0)=0`.
The existing original80 tests and additional four regular temporal
directions are retained. Held wall/radial rows, temporal momentum and
outward radial conormal remain original residuals or boundary loads.

For example, the intrinsic Higgs action actually varied is

\[
 S_H=2\pi^2\int d\bar\Omega\,
 [w_T|D_tH|^2-w_S\sum_i|D_iH|^2
   -w_V\lambda_H(H^\dagger H-\nu_{action}^2)^2].
\]

Its four real Higgs residuals include the original Yukawa contractions and
matched native/state and interface loads. Its gauge rows include both
covariant-Higgs placements. The material temporal trace is `A_t,ref`;
adding its already-cancelled Eulerian radial advection would count motion
twice. The existing constant-H comparison evaluates the original polynomial
`H0+nu_action^2 H1` and the original multiplier polynomial
`C0+nu_action^2 C1+(nu_action^2)^2 C2+gamma C_area`, with all remaining
loads explicit. These evaluated polynomials are not substitutes for the
full coupled Higgs and metric rows.

The cap and intrinsic metric equations retain the original Hamiltonian and
momentum constraints, `h_ab-gamma_eps,ab=0`, the oriented cap traction plus
matcher reaction, and the intrinsic metric/matter equation plus both
matcher reactions. Their represented application is the original
`moving_cap_action_jet`, Maxwell geometry two-jet and material Higgs
two-jet assembled in `assemble_known_coupled`; all 150 known original
rows are retained. Its action is explicitly

\[
 S_{known}=S_{cap,old}+[59N_b/(30R_4)]
            +[S_M(A)-S_M(\bar A)]+S_H.
\]

The displayed replacement removes the old attached SM-zeta reference once.
Its full geometry two-jet is required. Geometry/constraint, Higgs, gauge,
surface-tension and exterior loads are not interchangeable free sources.

The independent physical unit equation remains

\[
 G_Fe^{2e}-c_F[y,I,\mathcal D,\text{normalized low-energy legs}]=0,
 \quad DF=2G_Fe^{2e}De-Dc_F.
\]

Its preparation maps are `E_chart=0.5 exp(-e)`,
`sigma_chart=100 exp(e)/(hbar c)` and centers `+/-10 sigma_chart`.
A continuation initializer for `e` is not a solved calibration or an
achieved central energy.

## 3. Cauchy, collision and normal-domain maps

The collision incidence follows the same assembled metric with its
spin/gauge parallel transport and density Jacobian. At its origin it obeys

\[
 (\hbar c\,e^{-e})^2(DI)^T h_{action}(DI)=I_3.
\]

Its curved metric and normal extension away from the origin must be kept.
The cap boundary S3 has not been identified as the entire collider domain.
The original physical normal trace remains

\[
 \Gamma_0\Psi_5=u_R S_+W R_4^{-3/2}\xi_4+\Gamma_0\chi_{off}
 =V u_R S_+W R_4^{-3/2}\chi_{cap,4}+\Gamma_0\chi_{off}.
\]

Here `xi_4` is the original inherited `chi_4=R4^(3/2)psi_4`; its notation
must not silently be reused for a differently normalized cap CAR field.
`W` is the fixed 384-by18 inclusion, `S_+` the actual boost and `u_R` an
actual normalized normal mode, not one by convention. A volume inclusion
must satisfy `iota^dagger iota=I` in its full normal/Cauchy integral.
The constant-angular projection is
`P_const xi=(2 pi^2)^-1 integral xi dOmega`; it differs from the normalized
`Y0=1/sqrt(2 pi^2)` coefficient. The downstream incoming trace is

\[
 d_i=Q_{out,8}^\dagger P_{\mu,L}
 [u_R S_+W R_4^{-3/2}\mathcal P_{const}\xi_4]_{t_i}
 +Q_{out,8}^\dagger P_{\mu,L}\Gamma_0\chi_{off},
\]

with actual collision pullback inside the projection. This is not a map
from electron packet columns directly to a muon occupation.

At a nonzero surface source the existing original two-trace equation is

\[
 q=P_Lb_+x+P_Rb_-z,\qquad
 J_+(U^{-1}z-x)=C_{sum}\,\mathsf T\,q.
\]

The interacting graph is `z=U(I+J_+^-1 C_sum T B_sum)x`, with the original
Green/isotropy conditions and once-only surface kernel. The zero-source
hard-continuity graph cannot replace it. Derivatives must include moving
traces, `u_R`, boost, radius, incidence, normal pairing and complement.

## 4. Conditional executable application specified for this checkpoint

The numerical application uses the actual saved comparison fields as a
continuation seed, including its nonzero gauge and Higgs coefficients. It
restricts sections to the exact represented constant-angular mode
`Y0=1/sqrt(2 pi^2)` in the full18 frame. The complete electron-family6
Hamiltonian has sign spaces of dimensions 3 and 3; the charged4 fiber is
not imposed as an invariant carrier.

For each trial background, let `S_H=(S_L+S_R)/sqrt(2)` contain the two
balanced charged chiral spin seeds, with `S_L` aligned to the actual Higgs
and `S_R` in the same native spin frame. The trial columns follow by sign
projection and complete Gram normalization,

\[
 B_+=P_+S_H,\quad B_-=P_-S_H,\qquad
 C_+=B_+(B_+^\dagger B_+)^{-1/2},\quad
 C_-=B_-(B_-^\dagger B_-)^{-1/2},
\]
\[
 U=Y_0 C_eC_+,\quad V=Y_0 C_eC_-,\qquad
 i\dot U=h(c)U,\quad i\dot V=h(c)V.
\]

`C_e` is the original 18-by6 family inclusion. Rank loss must be reported;
no column or charge-exchange term is dropped to recover two spins. This
is an explicit trial initializer on the represented comparison, not the
adopted localized 500 MeV/100 fm beams. Its achieved moments are computed
from these sections, and `2000 fm` is never inserted as their dipole.

The restricted temporal unknowns `c` are coupled to those sign-projected
sections through the original temporal weak difference equation

\[
 g_{A_t}^{cl}(c)-g_{A_t}^{cl}(c_0)
                         +t\ell_{pair,A_t}(c)=0,\quad t\longrightarrow1.
\]

`g^cl` is evaluated with the literal Maxwell integrand and original Higgs
action above. `ell_pair` uses the computed sections and original temporal
vertices, with the original cap/wall normalization exactly once. The
restricted nonlinear solve recomputes sign projectors, trial sections,
complete Gram and pair source at every evaluation of `c`, including
Newton residual evaluations. The Picard qualification refers only to
holding the unresolved remainder fixed in this difference step; it does
not freeze the pair current inside the nonlinear equation. The source is
therefore neither a fixed target nor a fitted compensator.

The actual geometric continuation completed `t=0.25` at original20-row
maximum `4.754334245936701e-15`; the next `t=0.5` stage stalled at
`0.054138450094354494`. The full-strength target equation remains at
`0.1681825188398802` on the reached iterate. These are different equations
and separately saved coefficient vectors, not a full-strength closure.

This is a **frozen-remainder difference application**. It fixes the change
of the unresolved inherited/native/exterior subtotal to zero for that
restricted step. It neither assigns its absolute value zero nor assumes
the seed is a complete physical reference solution. In the full equation
the omitted change is separately

\[
 \delta\ell_{matched}+\delta\ell_{exterior/interface}
 +\text{geometry/Higgs/unit/domain changes}.
\]

The Dirac first jets above are the actual initial-slice applications of
`h(c)`. They define Cauchy evolution derivatives for this trial. They do
not show that the packet density, pair current or background is stationary
for a whole time interval: sign-projected columns need not be individual
eigenvectors, and their currents can evolve. In particular the nonzero
original charge-exchange operator remains active. No whole-time
Maxwell/Higgs solution follows from the initial constraint.

Both `g^cl(c)` and `g^cl(c0)`, the achieved pair source, their difference
residual, and every original held field/constraint/Higgs residual must be
reported. Success of this restricted difference does not cancel an
absolute seed residual. Normal profiles, physical collision incidence and
infinite-past error are not computed by a constant-angular Gram identity.
The exact pair density remains unchanged throughout.

## 5. Defining state relation and why the adopted sign is insufficient

Varying the original canonical lepton action gives the first-order field
load, on its actual paired/smeared domain,

\[
 \ell_a^{field}=-N_{ind}\operatorname{Tr}(N_{occ}V_a),\qquad
 V_a=\partial_aH_{can},\qquad N_{occ}=I-C_+.
\]

The original 24 wall/Higgs vertices span 20 real directions. Their intrinsic
radial and zero-wall52 images vanish exactly. This reduces the specific
consumed first-order reference projection; it does not remove bulk native,
geometry/stress or interface terms. The derivative retains both
`Tr((D N_occ) V_a)` and `Tr(N_occ D V_a)`, and lapse, measure and domain
contacts. On a bounded readout `L`, the contact is `G_L=LL^dagger` and
`N_L=G_L-C_L^+`, rather than an assumed identity point-sample Gram.

For the fixed c-number one-body comparison the defining covariance
equation follows directly from the Dirac equation:

\[
 i\dot C_+=[h_y,C_+],\qquad
 C_+(\tau)=U_y(\tau,\tau_0)C_+(\tau_0)U_y^\dagger(\tau,\tau_0).
\]

If the adopted wave operator exists, its scattering-range boundary value
would be

\[
 C_{ref,+}(0)=\Omega_-C_{as,+}\Omega_-^\dagger,
\]

with zero/bound/complement and possible cross pieces retained separately.
This is the attempted source-trail derivation: causal transport determines
the map, while its incoming covariance remains a boundary/state operand.
The adoption receipt specifies sign spaces and explicitly retains inherited
occupations/correlations. It does not impose `C_as,+=P_as,+`. The condition
of no extra occupation over the reference fixes a relative excitation; it
gives no equation setting the reference occupation to zero.

In particular an admissible smooth self-dual CAR perturbation `X`, with
`0<=C+X<=I` and `X+Gamma X Gamma=0`, is transported to `U X U^dagger`.
It solves the same homogeneous covariance transport while changing a
surviving contraction by `+N_ind Tr(V_a U X U^dagger)` at fixed lapse and
pairing. Reset transports this difference, and the retarded kernel remains
fixed. This demonstrates precisely which seed information transport lacks;
it does not establish two complete self-consistent physical solutions.

For the full joint interacting state, even this homogeneous covariance
equation is not a closure assumption. Writing `h[hat Phi]=h[bar Phi]+delta h`
in the Heisenberg equation gives exactly

\[
 i\dot C_+=[h[\bar\Phi],C_+]
 +\langle\delta h\,\hat\chi\hat\chi^\dagger\rangle
 -\langle\hat\chi\hat\chi^\dagger\delta h\rangle.
\]

The last two terms are ordered mixed dressing/reference contractions on
the original domains. They are not factorized into boson and fermion
means. A physical joint preparation must satisfy the operator Gauss law
`(D_i hat Pi^i+hat j_pair+hat j_other) rho_prep^(1/2)=0`, its other
constraints and the adopted incoming condition. The exact spin pair and
Gauss law alone do not specify all transverse/reference correlations.
An additional boundary rule would have to fix the surviving projected
`C_as,+` and, where this mixed equation is consumed, its joint mixed
contractions. It would leave all unconsumed state directions free.
No such extra rule is silently chosen in this checkpoint.

The physical quantum accounting remains

\[
 \Gamma_{replacement}=\Gamma_{0,actual}
 +[\Gamma_{complement,domain,phase}+\Gamma_{matched\ state}
                                      -\Gamma_{retained\ local\ overlap}].
\]

The bracket is not zero. The native0 heat derivative is a regulated
effective-action contraction, not a demonstrated statistical `C_+` or an
initial density functional. Adding a full occupation load independently
would risk counting the same reference twice; a separate state correction
must be the matched difference derived from this same functional/domain.

## 6. What is implemented, what must be applied, and what remains a relation

**Implemented; physical application still required.** The full18 local
Hamiltonian, fixed-Y Higgs/gauge maps, four-column section synthesis,
complete represented Cauchy Gram, exact Fock16 mean/ordered current tensor,
original Gauss source, literal Maxwell gradient/Hessian, enriched84 radial
weak maps, intrinsic/material Higgs jets, original cap/geometry/multiplier
rows, local comparison time/gauge lift, sign projectors and their
derivatives, two-collar graph and trace-incidence formulas. Their finite
conditional application does not instantiate the full physical domain.

**Requires implementation/application on a common physical domain.**
The actual localized Gaussian spectral synthesis and convergence; dressed
finite-past transport; collision geodesic/spin/gauge/density incidence;
normal profiles, normalization, off-mode complement and moving-domain
contacts; coupled packet/background/electric constraints and held rows;
matched native/domain/phase/local-overlap remainder and derivative; the
physical low-energy `c_F`, cutoff chains and calibration; error estimates
for the full spatial/asymptotic/domain problem. These are equations and
maps to construct, not new external beam parameters.

**Genuinely unresolved state relation in the current adoption.** The
inherited incoming boundary covariance or only its surviving matched
vertex/stress projections, plus any joint mixed contractions actually
consumed in the interacting dressing equation above. The adopted
polarization determines subspaces and transport, while explicitly leaving
these occupations/correlations intact. An unavailable numerical array is
not the reason: the homogeneous general solution shows the boundary
operand, and the exact Heisenberg equation shows the mixed operand.
The conditional relative pair source needs neither to be assigned first.

## 7. Downstream scope and source anchors

The exclusive second-order pair amplitude consumes a chronological
two-point current contraction. The corresponding leading inclusive
pair-channel quadratic term consumes the ordered closed-contour
four-point contraction. Neither is the complete matched outgoing
occupation, which retains reference, Pauli, normalization, connected and
interference terms. The preparation source in section 2 is earlier and
does not depend on that production four-point. Kernels are recomputed on
matching actual backgrounds/channels when their applications are reached.
No old retarded array or native heat factor supplies the statistical part,
and no Wick/Gaussian replacement follows from either.

The conditional iterate establishes no physical admission. Calibration,
fixed preparation, inherited information, exact pair statistics and the
unchanged `2e-10` physical guard are preserved.

Source anchors in the current worktree:

* `audits/bhsm_collider_incoming_field_current.py`: `current_algebra`,
  `construct_action_packet_sections`, `validate_action_packet_Cauchy_Gram`,
  `original_material_Gauss_source`.
* `src/bhsm/interface/muon_native_dirac_hamiltonian.py`:
  `canonical_lepton_hamiltonian_maps`.
* `src/bhsm/interface/muon_nonlinear_chronological_n0_action.py`:
  `analytic_constant_maxwell_batch`.
* `src/bhsm/interface/muon_adopted_incoming_reference.py`:
  `stationary_parent_field_realization`, `temporal_enrichment`.
* `src/bhsm/interface/muon_coupled_reference_replacement.py`:
  `assemble_known_coupled`, `reference_subtraction`.
* `src/bhsm/interface/muon_material_higgs_gauge_action.py` and
  `muon_intrinsic_higgs_gauge_action.py`: the original material pullback and
  Higgs action, with their matching coefficients.
* `src/bhsm/interface/muon_two_collar_weak_domain.py`:
  `two_collar_weak_domain_jets`.
* `theory/muon_coupled_reference_replacement_20261019.md`, sections 4--5;
  `theory/muon_stationary_native_reference_load_20261019.md`, native/state
  and local-overlap ledger; `theory/muon_prepared_causal_data_application_20261019.md`,
  exact normal incidence; `theory/muon_ideal_preparation_action_derivation_20261016.md`,
  relative source and reference-transport derivation. Pre-adoption selector
  language in historical files is superseded by the adoption receipt.
