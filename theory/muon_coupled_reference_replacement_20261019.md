# Coupled reference equations: an evaluated missing reference contribution

This application starts from42ce332a and consumes the saved52-direction
interior solution, enriched temporal basis, endpoint momenta and classical
response. It evaluates a previously unconsumed reference subtraction and
takes one provisional Newton trial of the actual known coupled rows.
It does not recompute or refine the old interior solution.

## 1. The missing contribution actually evaluated

The committed v16 quantum accounting identity is

\[
\Gamma_Q=\Gamma_{attached,\zeta}-\Gamma_{SM,\zeta}[0]
             +\Gamma_{SM,heat}[\Phi;A,H,\Psi].
\]

The old comparison calls `moving_cap_action_jet`, whose total still contains
exactly one attached SM term
\(L_{SM,\zeta}=-(59/30)N_b/R_4\). Its coefficient is the existing exact
sum of4 real conformal scalars,12 physical gauge vectors with their
quotient and48 two-component Weyl species. It is not a fitted load.
Removing this term therefore contributes

\[
\boxed{\Delta L_{ref}=+\frac{59}{30}\frac{N_b}{R_4}},\qquad
\Delta g=D\Delta L_{ref},\quad \Delta K=D^2\Delta L_{ref}.
\]

Both derivatives use the complete original geometry two-jet, including
normal position, lapse, shift and mixed derivatives. The lapse here is
the original **ambient** \(N_b\), not the induced wall lapse. No extra
orbit-volume or Maxwell factor multiplies this already normalized cap term.
An independent expression using the intrinsic radius and ambient lapse
agrees with the literal negative cap component through second order within
3.55e-15. The evaluated value is **2.267664383622318**; the geometry62
covector norm is11.14005893, the multiplier24 maximum is2.266903607,
and the common151 Hessian norm is98.11737246.

Its independent gauge, Higgs and log-unit partials vanish because this
particular original term depends only on dimensionless geometry. This is
not an assignment of zero to a native current or inherited correlation.
Geometry/unit/domain dependence induced by the full coupled solution must
still be composed with this two-jet.

Removing the attached zeta term does not select an empty physical sea, and
does not evaluate the replacement heat. The known action still retains its
local Maxwell/Higgs terms. The remaining quantum functional must consequently
retain the already-owned local-overlap subtraction, at its actual matching
order. Adding the full heat again on top of those same local pieces would
double count. The rank20 reference-current contribution below is a represented
part of this remainder, not another independently added determinant.

## 2. One compatible coupled chart and the Jacobian actually used

The static comparison chart is

\[
z=(q_{37},m_{24},s,a_{84},H_4,e),\qquad e=\log(\Lambda/\mathrm{GeV}).
\]

The original84 gauge coordinates retain the extra temporal constant
directions and every old coefficient/test. The scalar uses the unchanged
matching and \(u=\nu_{GeV}^2e^{-2e}\). All geometry/gauge/Higgs/unit cross
derivatives are assembled from the original cap, background-subtracted
Maxwell and material Higgs action. No mechanical gauge energy is added twice.
Ordinary rates vanish only in this stationary comparison ansatz; the complete
known canonical momentum covectors are exported rather than set to zero.

The known subtotal and complete unresolved equation are distinct:

\[
R_{known}=D(S_{old}+\Delta L_{ref}),\qquad
R_{physical}=R_{known}+\gamma R_{area}
             +\ell_{native/ref,\,minus\ overlap}+\ell_{exterior/interface}.
\]
\[
J_{physical}=K_{old}+\Delta K+\gamma K_{area}
             +D\ell_{native/ref,\,minus\ overlap}+D\ell_{exterior/interface}.
\]

The computed Jacobian includes \(\Delta K\); the newly evaluated load is
not frozen. Unknown values and derivatives in the second line remain unknown.
The known matrix is not called the complete interacting inverse.

There are150 original known Euler/constraint rows and151 columns. The
action's derivative with respect to \(e\) is **not** a calibration equation
and is excluded from these rows. The physical GF equation remains separate.

For the initial unchanged seed, the subtraction has no gauge dependence,
so the saved classical52 block remains identical. With52 eliminated
coordinates \(a\) and99 remaining columns \(b\), the actual trial uses

\[
S=K_{bb}-K_{ba}K_{aa}^{-1}K_{ab},\quad
S\delta b=-(g_b-K_{ba}K_{aa}^{-1}g_a),\quad
\delta a=-K_{aa}^{-1}(g_a+K_{ab}\delta b).
\]

The reduced rows number98 because the extra unit column has no Euler row.
The saved52 inverse is used only here, at matching inputs. The changed
background, field rows, open vertices and endpoint momenta are then freshly
evaluated. A later solve cannot reuse this inverse as a new interacting
factorization without checking its actual changed operator.

The numerical SVD uses the exported reduced-coordinate metric, threshold
1e-10 relative to its largest singular value, and retains rank93. All left
and right nullspaces and unscaled residuals are exported. This is a numerical
minimum-norm initializer, not a physical BRST quotient or a unique state
selection. The maximum scaled coordinate step is0.02; accepted damping is
0.0005725897598. No unknown load is chosen to cancel the classical residual.

## 3. Fresh original-row results and nonpasses

Final run_2 and run_3 are byte-identical. These are original weak-coordinate
diagnostics of the known subtotal, not complete physical residual norms.

| Known quantity | After exact replacement at saved seed | After joint trial |
|---|---:|---:|
| All150 original known rows, maximum | 258.7976448 | 258.6494038 |
| Multiplier24 maximum | 27.65396763 | 27.63813678 |
| Multiplier component outside area direction | 27.65501325 | **27.63919050** |
| Previously held radial/wall32 maximum | 0.719987105 | **0.719571847** |
| Interior52 maximum | 7.10543e-15 | **6.93178e-6** |
| Higgs4 maximum | 6.74935e-17 | **2.42915e-6** |
| Literal outward radial conormal maximum | 6.23937472 | 6.23567576 |
| Temporal gauge momentum maximum | 6.65621753 | 6.65195835 |

Before replacement, the saved component outside area tension is
27.65302801. Its replacement value and new trial value are retained above;
gamma alone still cannot repair the iterate. Gamma remains unassigned and
its full gradient/Hessian coefficients are exported.

The full linearized150-row solve has maximum residual4.79947e-10; the
eliminated52 subset is2.25e-13. The larger linear residual is retained as a
numerical nonpass, not hidden by row scaling. The nonlinear finite trial
disturbs the old52 solution and Higgs equation, as the table shows. This
application therefore does not transfer the old tiny residual onto the new
background or claim physical admission. The known residual decreases only
slightly; no complete physical decrease has been established.

Run_1 is preserved as an earlier off-shell source diagnostic, with exact
execution-owner snapshots. Its shifted-residual homotopy was not an Euler
solve; its known maximum increased. It is not promoted to the final result.
The final trial instead uses the actual known150-row right-hand side.

## 4. Reference20, bulk remainder and higher correlations

The exported24 canonical open vertices have real span20 both before and
after the step. Their changed matrices are reevaluated; their difference
norm is0.001007972. The intrinsic radial vertices and zero-wall52 images
vanish by this first-order wall action. This does not remove the independent
bulk native remainder, radial conormals or interface loads.

The occupation convention matters. For the saved canonical Hamiltonian
vertices \(V_a=\partial_a H_{can}\), the fixed-Cauchy-measure Lorentz field
load is

\[
\ell_a^{field}=-N_{ind}\operatorname{Tr}(N_{occ}V_a),
\]

with the original action normalization, volume/normal inclusion, domain and
clock contacts retained on their actual carriers. In the positive-frequency
CAR convention \(C_+\), \(N_{occ}=I-C_+\); its CAR contact and sign cannot
be dropped. The shorthand `Tr(C_reference V_a)` in the run receipts means
the **signed action-weighted occupation cotangent**, not the unweighted
positive-frequency covariance. The versioned convention addendum records
this definition without changing numerical or historical hashes.

Its derivative contains both occupation and vertex motion, for example

\[
D\ell_a=-DN_{ind}\operatorname{Tr}(N_{occ}V_a)
-N_{ind}\operatorname{Tr}((DN_{occ})V_a+N_{occ}DV_a)
+\text{remaining measure/domain contacts}.
\]

Those20 state-contraction values have **not** been evaluated here. They
are not inferred from the removed massless reference energy or fitted to
the known residual. The separate bulk native remainder is also unevaluated.
Interacting response, pair conversion and derivatives of the inherited
state can require higher correlations; the rank20 statement does not bound
them or determine the900 outgoing occupation coordinates.

Existing finite closed-lepton heat applications were reviewed. Their old
background/domain identities differ and their cutoffs are probes. A new
proper-Euclidean finite heat load cannot simply be added to these Lorentz
cap equations without its actual continuation, clock, endpoint and
overlap pullbacks. This application consumes the exact same-action
reference subtraction and does not manufacture that further continuation.

## 5. Unit and collider incidence remain one physical problem

The common scale enters the coupled Higgs derivatives, including their
geometry and field cross blocks. Its numerical initializer changes from
83.32706337 to83.16523532GeV. The corresponding **required**, unevaluated
charged-current coefficient changes from0.08098624412 to0.08067198558.
Neither value is adopted as a physical coefficient or physical scale.

The physical row remains

\[
F_{unit}=G_Fe^{2e}-c_F[y,I_{y,e},\mathcal D,
                        \text{normalized external legs}]=0,
\quad DF_{unit}=2G_Fe^{2e}De-Dc_F.
\]

The local incidence follows geodesic flow in the **same assembled physical
Cauchy geometry**, with spin/gauge parallel transport and the Cauchy density
Jacobian. Its initial tangent is scaled by \(e^e/(\hbar c)\), so incidence
and GF matching cannot be solved using independently frozen units. For a
physical local tetrad chart at its origin,

\[
(\hbar c\,e^{-e})^2(DI)^T h_{action}(DI)=I_3.
\]

Away from the origin the actual curved chart metric is retained. The cap
boundary S3 is not identified with the whole collider. Its original
two-collar interacting trace equation, trace/traction maps and embedding
conditions must match to the assembled incoming Cauchy domain; a local
geodesic formula does not complete that matching.

The complete domain incidence and normalized low-energy charged-current
coefficient are still unresolved. The original action-owned four-lepton
kernel, pole residues and derivative remainder are required; a finite
static V-A fit or `UniversalGFScaleMap` cannot supply them. No beam
parameter, covariance or vacuum is reselected to avoid those equations.

The next operand is the actual sourced, overlap-subtracted native/reference
stress and wall/Higgs load, with its complete field/domain derivative and
the shared incidence/GF equation. Physical packets/current, pair conversion,
an admitted correction, fresh physical Maxwell/all226 checks and magnetic
readout have not occurred. The unchanged2e-10 physical guard, independent
calibration, earlier gauge reconstruction7.29e-10/6.33e-10 nonpasses,
membrane finite-step9.34e-8 limitation and continuum/time errors remain.
