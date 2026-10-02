# Current-C2 parent Maxwell velocity density for the muon continuation

1 October 2026. Scientific reference revision:
`524ed90689bd5923c249bba2e699abf627e703cd`.
Checkpoint: `BHSM_MUON_CURRENT_PARENT_LOCAL_VELOCITY_524ED906_20261001`.

## Result and scope

The retained 48-by-98 current-C2 history supplies the parent shape, lapse,
radial metric and radial shift. Reconstructing these fields and projecting the
predecessor's local Maxwell velocity form gives the executable density

\[
 E^{\mathrm{local}}_{b,AB}(τ,ρ)
 =\kappa_1 c_Q\,
 \underbrace{\pi^2 L_F^5\Lambda\frac{C_ρ r}{\nu R_4}}
 _{e_{\mathrm{geom}}(τ,ρ)}G^{\mathrm{Haar}}_{AB},
 \qquad c_Q=\frac{16/3}{I_\jmath}.
\]

The reported computation evaluates **the geometric factor**. The primitive
trace formula is conditional on matching the same mechanical connection to
the retained neutral connection and its U(1) extension. Neither that matching
nor the complete AE4 induced remainder is assigned a value. This is an
operator-coefficient partial result, not a complete positive AE4 electric
Hessian, native resolvent, heat contraction, or physical muon anomaly.

At the first and last retained boundary nodes the fixed-input Arb enclosures
for `e_geom` are respectively

```text
[295.401559109409930283772042072497461228960240 +/- 2.70e-43]
[295.753117875202335636123294155240531432724094 +/- 1.73e-43]
```

The earlier electric checkpoint's statement that only boundary radius data
were recovered is superseded for this local geometric coefficient. The raw
current states supply the necessary shape and multiplier fields. No new
history, photon-mode, charge-trace, or moving-frame solve was run.

## Producers, normalization and physical classification

| Operand | Producer or retained equation | Status here |
|---|---|---|
| Current geometry and clock | `artifacts/current_runtime/dop853_system_integration_current_finer/coupled_children/backreaction/arrays.npz`; N12 states, `log_radius`, `log_lapse`, proper clock and radius rate | Supplied cached realization; evaluated at its retained nodes; no new continuous-history certificate |
| Shape/lapse/shift layout | `aether_sobolev_galerkin_pencil_lift_v15_81.py::generalized_lagrangian` | Derived reconstruction of the retained 98-variable fields |
| Boundary-to-parent scale | `aether_forward_boundary_radius.py::boundary_log_radius` and current cached R4 | Derived; historical `RADIUS0` is not copied as a new normalization |
| Quotient and mechanical connection | `aether_diagonal_sp1_m4_attachment_v15_50.py` | Derived predecessor local geometry and component coefficient |
| Localizing weight and primitive action | `aether_event_weighted_unified_pushforward_v15_71.py` | Supplied predecessor action; component-to-primitive matching remains conditional |
| Lorentz gauge/ghost block | `ae3_c2_lorentzian_gauge_ghost_hessian.py` | Structural source/domain reference; not a numerical positive AE4 operator |
| Positive induced owner | `ae4_stratified_dirac_zeta_induced_owner.py` | Owner selected; current source-coupled operator and matching remainder unevaluated |
| Eight angular mode lifts | Earlier `angular_frame_factors.npz`, injection retained in `inputs.npz`; inherited Haar Gram I8 | Saved mode normalization; no mode rederivation |
| Tr16 Q squared | Earlier same-family charge ledger: 16/3, Q=T3+Y in its existing Y convention | Exact inherited representation trace; used only once after attachment |
| Mechanical-to-neutral attachment | Map jmath_EH_to_Q defined below | Unspecified in the inspected matching route; no index or neutral extension invented |

Input identities are in `input_provenance.json`; the self-contained
`inputs.npz` SHA-256 is
`3535f373df3ad4ec92c82ea8b50482747153e0645c82e53e940284deacac4494`.
The local evidence receipt records the actual source branch, HEAD and diff.
Publishing adds only the focused module, tests, replay, report and compact
evidence. It leaves the original working tree and earlier packets intact.

## Recovered parent fields

The N12 layout is q37, velocity37, multiplier24, with
q=(q0,u1..u12,w0..w11,v0..v11) and multipliers=(n1..n12,b0..b11).
Set chi=rho/2 on rho in [0,pi/2]. Define

\[
 u=\sum_{k=1}^{12}q_k\cos(4k\chi),\quad
 w=\sin^2(2\chi)\sum_{j=0}^{11}q_{13+j}\cos(4j\chi),\quad
 v=\sin^2(2\chi)\sum_{j=0}^{11}q_{25+j}\cos(4j\chi).
\]

With u_b=sum(-1)^k q_k and v_b=sum(-1)^j q_(25+j), the current scale is

\[
 R_{\mathrm{cap}}=2R_4e^{-u_b}\sqrt{\cosh(2v_b)},\quad
 A=R_{\mathrm{cap}}e^{u+v}\cos\chi,\quad
 B=R_{\mathrm{cap}}e^{u-v}\sin\chi,\quad
 C_ρ=\tfrac12 R_{\mathrm{cap}}e^{u+w}.
\]

Then L_F=sqrt(A squared+B squared), r=AB/L_F. At the boundary r_b=R4 and
L_F,b=2R4 cosh(2v_b). More generally L_F=2r cosh(log(B/A)); boundary R
alone does not determine it.

The raw lapse and shift are

\[
 N=e^{\sum n_k\cos(4k\chi)},\quad
 N_b=e^{\sum(-1)^kn_k},\quad
 \nu=N/N_b,\quad
 \zeta_ρ=2\sin(4\chi)\sum_j b_j\cos(4j\chi)/N_b.
\]

These are expressed in boundary proper time. The predecessor local weight is
Lambda=1-4 sigma squared, sigma=-1/2+rho/pi-sin(2rho)/(2pi), obtained from
the retained f=chi chart. No separate kinetic weight, lapse, cap or thermal
state is inserted. The geometric Hilbert/domain identification with the
selected AE4 positive operator remains part of its actual matching.

## Component-to-primitive action matching

The diagonal Sp(1) predecessor decomposes the angular metric as
A squared theta_u squared+B squared theta_v squared
=L_F squared omega squared+r squared delta squared, with
omega=lambda theta_u+(1-lambda)theta_v and lambda=A squared/L_F squared.
Integrating its EH mechanical curvature over the fibre gives the component
Maxwell coefficient

\[
 K_{\mathrm{comp}}=\kappa_1\pi^2L_F^5,
 \qquad \mathcal L_L\supset-\tfrac14K_{\mathrm{comp}}F^a_{MN}F^{a,MN}.
\]

The weighted pushforward writes a primitive Tr16 action downstream. Equality
of these actions requires the **same component amplitude and generator**:

\[
 \operatorname{Tr}_{16}(\jmath(L_a)^\dagger\jmath(L_b))
 =I_\jmath\delta_{ab},\qquad
 K_{\mathrm{trace}}=K_{\mathrm{comp}}/I_\jmath.
\]

If this matching also supplies the single primitive neutral extension used
by the retained Q connection, then K_Q=K_trace Tr16 Q squared. The factor
16/3 therefore appears exactly once. It cannot be multiplied into
K_comp before resolving I_jmath, nor duplicated by eight modes, three
families, or a second angular volume. The geometric kappa1 remains factored;
the predecessor's example kappa1=1 is not a new physical calibration.
A Pauli/weak generator with a conveniently chosen index does not establish
the mechanical connection's embedding or its U(1) extension.

## Actual eight-mode electric projection and moving frame

For the corresponding positive ADM metric expression
nu squared d_tau squared+C_rho squared(d_rho+zeta d_tau) squared
+r squared dOmega3 squared, direct metric inversion gives

\[
 \sqrt{g_+}(g_+^{\tau\tau}g_+^{ab}
       -g_+^{\tau a}g_+^{\tau b})
 =\frac{C_ρ r}{\nu}\sqrt{\gamma}\,\gamma^{ab}.
\]

The angular indices a,b have no angular shift. The actual quotient orbit is
round and all density factors depend on tau,rho alone. Contracting the saved
one-form lifts gives their supplied Haar Gram. Its I8 is thus a local
electric result of this angular geometry and normalization, **not** a
consequence of curl squared=9 I8. Curl squared=4 belongs to the historical
lowest sector and is not used here. The background mechanical connection
has nonzero curvature; a complete covariant magnetic/domain operator is not
replaced by free curl squared=9.

With Haar measure normalized to one, the unit orbit volume 2 pi squared
occurs once. In beta coordinate-one-form coefficients the result is

\[
 E^{\mathrm{local}}_{\beta,AB}
 =2\pi^2K_Q\Lambda C_ρr/\nu\;G^{\mathrm{Haar}}_{AB}.
\]

The inherited physical boundary normalization has
beta=T_b b, T_b=R4 f_R4=(2 pi squared R4)^(-1/2). Pulling the velocity
bilinear back once gives the b coefficient stated at the start and
D_tau b=b_tau-H_b b/2, H_b=partial_tau log R4. Including radial shift,
Db=b_tau-zeta b_rho-H_b b/2. The boundary moving-frame normalization is
retained for the radial profiles; no independently normalized bulk source
or profile is selected here.

The positive ADM computation certifies an algebraic local density formula;
it does not choose a Wick rotation or prove equality to the complete
selected positive AE4 realization. The Lorentz Maxwell velocity Hessian is
positive with the same local coefficient. Its radial sign is separate.

## Same bilinear, distinct fluxes and induced remainder

For the retained local bilinear
L=1/2[e |Db| squared+epsilon r_local |b_rho| squared]+other action terms,
where r_local=K_Q Lambda nu r/(C_rho R4), its fluxes are

\[
 \pi_\tau=eDb,\qquad
 \pi_ρ=-\zeta\pi_\tau+\epsilon r_{\mathrm{local}}b_ρ.
\]

Lorentz Maxwell has epsilon=-1. A positive spatial form has +1 only when
its owned realization establishes that identification; the executable
helper requires the sign. Variation retains
-partial_tau pi_tau-partial_rho pi_rho-H_b pi_tau/2 and the separate
temporal and radial boundary pairings. Thus coefficient derivatives, frame
terms, shift terms and endpoint terms are not dropped. These are local
contributions to the flux; full reset, interface, moving-endpoint and
induced contributions still belong to the same common domain. No terminal
wall is imposed at the last cached node. The existing selected-stop
Friedrichs contract is preserved; an arbitrary cache end is not that stop.

For Z=ell_star squared P and h(Z)=exp(-Z)/(2Z), the selected AE4 owner has
Gamma_heat=-1/2 STr E1(Z), plus its relative-zeta/eta pieces. For even gauge
sources its full quadratic response is

\[
 \mathcal H^{AE4}_{ij}
 =\operatorname{STr}(Dh(Z)[Z_j]Z_i+h(Z)Z_{ij})
   +\mathcal H^{\mathrm{relative}/\eta}_{ij},\qquad
 \mathcal R_{ij}=\mathcal H^{AE4}_{ij}-\mathcal H^{\mathrm{primitive}}_{ij}.
\]

The remainder is defined by the same owner, not by adding an independent
Wilson coefficient or a second determinant. It includes source contacts,
the moving geometric Gram, length, domain/interface and completion terms
as required by that owner. Its electric projection can be a nonlocal kernel;
it is unevaluated, not zero. A local Maxwell expansion alone is insufficient
to identify the full induced operator or cancel its matching dependence.

## Execution, error control and reproducibility

Two deterministic replays evaluated the cached geometry on 48 history nodes
and 65 fixed radial sample points. Four Arb192 evaluations use exact cached
binary64 inputs at nodes 0 and 47 and rho=pi/4,pi/2, achieving 184-bit
relative arithmetic accuracy. All generated scientific artifacts were
compared byte-for-byte; receipts give the exact hashes and test results.

These balls enclose arithmetic at fixed inputs. They do not enclose
continuous-history interpolation, input realization error, full operator
matching, spectral complement, radial/temporal quadrature or physical
theory uncertainty. Sample minima/maxima are not continuum extrema.
No integrated generated-profile contraction, shifted resolvent, heat trace,
physical signed transfer direction or muon LSZ state was evaluated.
Binary64 outputs need not lie in the much smaller Arb arithmetic balls.

Standalone packet reproduction:

```text
python replay.py --input inputs.npz --output <new-directory>
python -m pytest test_muon_parent_maxwell_velocity.py -q
```

Repository reproduction (numpy, pytest and python-flint required):

```text
python scripts/replay_muon_parent_maxwell_velocity.py --output <new-directory>
python -m pytest tests/test_muon_parent_maxwell_velocity.py -q
```

The three new tests check the current quotient/clock identity, an independent
metric determinant/inverse projection with radial shift and frame pullback,
and fluxes differentiated from one bilinear plus the missing-attachment
guard. These are geometry/algebra tests, not physical-operator evaluations.
The earlier three checks, six deterministic scientific artifacts and
22-hash record are preserved, not counted as native evaluations.

## Frozen contribution ledger and next operand

The inherited conditional local values remain unchanged:
a_mu_QED_local=0.00116550200495813; calibration-only standard uncertainty
1.79e-13 under alpha inverse=137.035999084 and its standard uncertainty
2.1e-8 with other original conditional inputs fixed;
0<delta_a_mu_h_local_1<3.500331e-9; and
0.0011655039493<a_mu_selected_local<0.0011655109506.
The selected interval already combines its selected local contributions.
No QED, Higgs, W/Z or new native term is added again. The calibration-only
uncertainty is not a rigorous total uncertainty. No experimental anomaly or
new measured mass/coupling is used in this computation.

| Native signed ledger | Value |
|---|---|
| native_bulk_heat | null / unevaluated |
| state_variation | null / unevaluated |
| contact | null / unevaluated |
| domain_boundary | null / unevaluated |
| completion_counterterm | null / unevaluated |
| strong_within_native | null / unevaluated subset; no independent addend |

Physical a_mu, g_mu=2(1+a_mu), and their total uncertainty remain unevaluated.
No dimensionful magnetic moment is reported. The generic heat/graded-trace/
linear-solve machinery is reusable; this module belongs to the muon/current
history realization. It does not create a second universal child framework.
Other children must supply their own fields, state/domain, insertions and
observable. The muon Pauli readout remains separate.

**One next operand:** materialize the same-action map jmath_EH_to_Q,
including its neutral extension and induced source insertion,

\[
 \operatorname{Tr}_{16}(\jmath(L_a)^\dagger\jmath(L_b))
 =I_\jmath\delta_{ab},\qquad
 D_{\mathrm{strat}}[\beta]=D_{\mathrm{strat}}[0]
       +\sum_A\beta_A\Xi_{Q,A}+\cdots
\]

on the existing common domain. Its missing value is an unspecified
mechanical-to-retained-connection realization in the inspected source
route, not an uncomputed geometry consequence of A,B,lapse or shift.
Once this attachment is supplied, use it in the same-owner quadratic
response above, retain its induced remainder and then apply K+sM with
geometric source duality and complement control. No arbitrary normalization,
positive realization, boundary condition or new full-history solve fills it.


## Publication validation and byte conventions

The repository-layout focused tests also passed (3 tests, 4.14 seconds).
The status, forbidden-claim, frozen-integrity and precision audits passed.
Public-readiness exited 1 on baseline tracked-file hygiene; its other eight
categories passed. The exact new additions passed the same hygiene function
in a focused check. No baseline hygiene repair or full test suite is included.

The two original replays and raw hashes remain intact in the standalone
packet. Published JSON uses the repository's canonical LF convention; its
reference hash manifest is recomputed for those exact published bytes.
`publication_byte_conventions.json` records both original and published
hashes. This is a declared text/path-label transfer, not another physical
evaluation. Across hosts compare JSON values or canonical LF text before
treating a byte difference as mathematical disagreement.
