# Retained muon source tail: evaluated numerical component and coupled solve

The entire retained tail from node2/action_arc4 through the canonical stop
at action_arc92.30514373112729 is evaluated in one parent-bulk temporal
minimal-core model. Its nonzero continued source is retained. The tail
return is consumed by the saved144-coefficient system, whose48 joining
equations are eliminated exactly. The resulting72-coordinate model source
solve and its stationary weak conormal are evaluated.

This is an operator-component milestone, not an evaluated native heat
contraction, complete owned exterior response, or physical muon anomaly.
The next explicit unsupplied action is the wall output of the same owned
Dirac operator on these source columns. Unknown owned terms are recorded
as unevaluated, rather than assigned zero.

## Revision, inputs and execution

Production started on `codex/muon-parent-maxwell-density-review` at
`f1201d56bbfdd6ec1020cb0a09c60cff40ad28d9`; scientific reference remains
`524ed90689bd5923c249bba2e699abf627e703cd`. No existing production source or
scientific artifact was changed. The live primary checkout, including its
unrelated work and running calculations, was left intact. Executed new
code snapshots and source hashes are in the dedicated artifact packet;
the new files were untracked at production time. Publication is a later
Git revision, not a claim that it was the executed revision.

The history producer is
`BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz`, SHA256
`6d966cb6c731dc545d520522f897b82250e0a7817c0447f262363d6d22858635`.
The same-state clock/backreaction array has SHA256
`2a271fc6407062b217f4b3c6ed686ae5c91c1f5b59ab54442d0a953cf8330d8d`.
Their actual node2..47 subset, action rates, state weights, signed
descriptors, branch reference, clock values and radius covectors are
saved in `run_1/retained_tail_points.npz`. Original records and full
producer SHA256 hashes accompany it. The sampled history is a numerical
reconnaissance, not a certified continuum trajectory.

Node2's right weak-density moments are reused from `future_run_2`; no
old point or element is rebuilt. There are44 new ordinary point actions
at nodes3..46 and one regularized actual-stop action. The single tail run
took44.7 seconds; there was no new field/Hessian campaign or history solve.
Every new point was saved before elimination. Subsequent coupled solves
use only these caches. The previous ten checks were preserved and not
rerun. Seven new read-only checks passed in1.62 seconds.

## Field, clock and source actions

For every ordinary retained point the current cancellation-preserving
representation gives

\[
Y_\tau={\mathrm{action\_rate}\over W_Y\rho_a},\qquad
\rho_a={N_b\sigma\over\|G\|},\qquad
q_\tau=v/N_b.
\]

The shared normalization and Delta cancel upstream. Each point uses its
own continued branch24 and cached clock; no tiny descriptor is inferred
from a raw eigenvalue or sorted-index selection. The lapse derivative
uses the direct Fourier expression
`L_nu=sum m_tau[k]*(cos(2k rho)-(-1)^k)`. It is not an interpolated nodal
time derivative. The boundary value is exactly zero in that basis.

The inherited `moving_coefficients` and `spatial_weak_actions` evaluate
the actual moving frame `E=(W_rad,p)`:

\[
D_5(Ec)=F_0c+F_1\dot c,\quad
A=F_0^\dagger M_5F_0,\quad B=F_0^\dagger M_5F_1,\quad
C=F_1^\dagger M_5F_1,\quad M=E^\dagger M_5E.
\]

They retain `E_tau`, the action-generated normalization/time jets, shift,
spin and resolved common-A connection, n1/n3 full64-carrier outputs, and
the connected inclusion/complement time cross. Volume and temporal-Cauchy
pairings are saved separately. No source is projected back to the charged
columns or reconstructed by subtracting large W/chi quadratic forms.
Full output contractions are checked on actual newly evaluated points.

For example, node3/action_arc6 has H=0.0887735265105002 and
I=0.276366467174252355175596345251..., with a conditional nodal Arb
enclosure. Its action I_tau=1.31030283886746669... belongs to that actual
point. The evaluated volume projection is0.024964485717262674, while the
Cauchy projection is0.025605919643308477. These are distinct pairings.

The source throughout is the original `p=T_b(tau)*hat/r` and photon
Clifford image, with constant coordinates `c_source=(0,c_p)`.
The numerical forcing is `f=M*c_source` integrated against the temporal
tests. This source-image resolvent load is not the complete induced
AE4 mixed photon forcing `f_Z,A`. It does not introduce a state or a new
physical source continuation.

## Temporal elements and inherited stop

On the44 ordinary remaining elements, the four temporal weak densities
`rho_a A`, `B`, `C/rho_a`, `rho_a M` have the declared degree1 model.
Their integrals are exact polynomial moments up to arithmetic. Field
values are not frozen at the cut. No interpolation remainder is certified.
Hierarchical-to-endpoint congruences transform matrices, source loads and
dual traces together.

The stop owner is
`ae4_current_c2_canonical_stop_domain_bridge.py`, and the selected
`endpoint_load_adjudication.canonical_stop` in
`BHSM_N12_ACTION_OWNED_ENDPOINT_LOAD_REDUCTION.json` specifies the
Friedrichs closure of the retained minimal form. No independent terminal
load is selected. Motion/bulk jets are not zeroed by this statement.

At node47, both sigma and the proper clock density vanish. The retained
arc derivative is finite: `Y_arc=action_rate/W_Y`, with `q_arc=0` and
nonzero multiplier rates. The action is evaluated without0/0. In the
terminal moment model, `rho_a=rho46*(1-x)`,

\[
\rho_a F_{0,W}=-u\,i\Gamma^0L_{\nu,a}/(2\nu),\qquad
\rho_a F_{0,p}=0,
\]

and `F1` remains finite. Put `j=Delta_arc*rho46`, and use the temporal
minimal-core trial `phi=(1-x)^2`. Its cutoff approximation has graph
error O(epsilon^2) in this coefficient model; arc-P1 would instead have
log-divergent derivative energy. This establishes temporal trial-core
membership in the declared model, not the exhaustive owned wall/reset
domain pullback for the radial inclusion.

Linearly interpolate the *regular* moment matrices
`Areg=(rho_x F0)^dagger M5(rho_x F0)`,
`Breg=(rho_x F0)^dagger M5 F1`, `C`, `M` between left and stop. Then

\[
K={A_L/5+A_R/20-(B_L+B_L^\dagger)/2
 -(B_R+B_R^\dagger)/6+4C_L/3+2C_R/3\over j},
\]
\[
M_{\rm el}=j(M_L/7+M_R/42),\qquad
f_{\rm el}=j(M_L/5+M_R/20)c_{\rm source}.
\]

An independent four-point Gauss evaluation checks these formulas. This
terminal trial limit follows the existing minimal core; it is not a
chosen physical Dirichlet, Neumann, absorbing or reflected endpoint law.
The independent spinor reset contact remains zero. AE2 total-field reset
and opposite conormal graphs, smooth material transmission and the
constraint complex remain requirements on the full owned realization.

## Tail return and coupled solve

The full tail component has45x24 nodal coefficients. Backward elimination
retains distinct upper/lower mixed blocks and the nonzero tail load:

\[
S=H_{gg}-H_{gz}\operatorname{solve}(H_{zz},H_{zg}),\qquad
r=f_g-H_{gz}\operatorname{solve}(H_{zz},f_z).
\]

The stored stationary tail return is `S*g-r`, with tail-left outward
orientation; the adjacent core has the opposite outward orientation.
The response code does not impose a mixed-block adjoint equality.
It applies this return to the actual source-reached node2 trace.

| Diagnostic or output | Evaluated value |
|---|---:|
| Retained tail proper duration | 0.00014537708940443175 |
| Interior equation absolute residual | 1.38348e-10 |
| Maximum local backward residual | 1.52113e-18 |
| Input trace residual | 0 |
| Stationary conormal identity residual | 2.36611e-11 |
| Affine source return norm | 2.90483e-5 |
| Maximum interior pivot condition | 287.926 |
| Node2 source/return contraction | 472.56446637454354 -7.11028e-10 i |

The dual conormal norm is3644.3161015045303. Its Cauchy-Riesz norm is
6434.202308410835; these are different objects. The independently sampled
trial conormal differs by509.1891144208076 and is neither substituted for
the weak stationary return nor used to certify it.

At the saved partial-system node2 injection L, attachment is

\[
H_{\rm component}=K_{\rm partial}+sM_{\rm partial}+L^\dagger SL,
\qquad f=f_{\rm partial}+L^\dagger r.
\]

Both K and M are retained; the executed reference model uses s=0. The
shift is an explicit resolvent argument, never identified with physical
momentum squared. No native spectral length or physical scale is inserted.

The first coupled KKT chart had condition1.95e17; its small backward
residual did not establish a reliable response. That failed attempt is
preserved in `coupled_run_1`. Exact algebraic elimination of the48
joining equations gives free coordinates (prefix proper-time slope,
node1 trace,node2 trace), without rank threshold or regularizer. Its
72-dimensional congruent form has condition2.3342595657862777.

`coupled_run_2` preserved a further failure: reconstructing the small
traction by separately combining affine port/source maps gave a0.27859
conormal/reaction discrepancy. The accepted calculation instead starts
from the exact saved original source u0 and solves

\[
H_r w=-Z_d^\dagger(Hu_0-f),\qquad u=u_0+Z_dw.
\]

The correlated source is combined before action. An80-digit factorization
of the exact saved binary64 coefficients takes5.33 seconds. Decimal
solutions and source-centered corrections are preserved, as well as
binary64 exports. The incoming port remains a free affine response
argument; applying the saved source trace is not selecting a new physical
incoming boundary condition.

| Accepted coupled model diagnostic or output | Value |
|---|---:|
| Equation absolute residual (80-digit model algebra) | 3.76804e-78 |
| Joining/incoming trace residual | 7.92750e-83 |
| Reduced backward residual | 1.95417e-82 |
| Conormal/reaction identity residual | 3.89227e-77 |
| Incoming source/return contraction | 467.8257710760965 -7.25581e-10 i |
| Solved node2 trace/return contraction | 463.1312040719453 -7.25326e-10 i |

These numbers are arbitrary-unit numerical operator contractions, not
F2, magnetic moments, physical predictions, or uncertainty estimates.
Residuals test the stored model equations only; they do not bound errors
in the stored coefficients.

## First remaining owned action

At actual node3, the first concrete next arrays are

\[
R_{4W}^{(3)}(v,\dot v)
 :=\Pi_4D_{\rm strat}\iota_{Wp}(v,0)
 =R_{4W,0}^{(3)}v+R_{4W,\tau}^{(3)}\dot v.
\]

The input is the12 independent actual n1/n3 photon-generated columns
and their time jets in the inherited full-cap inclusion. The output is
the same-owner wall spinor Hilbert space, with its geometric M4 pairing
and current chiral action. The consumer is the wall Gram contribution
`R4W^dagger M4 R4W` to the WW time-element block and the corresponding
W/p cross `R4W^dagger M4 R4p`. These source-restricted arrays are absent
from the evaluated bulk `F0^dagger M5 F0` and cannot be filled with zero.

The local Euler row is already prescribed by
`ae31_c2_intrinsic_m4_lepton_action.py:first_variation_and_pole_gate`:
`i slashD_L L-Y_l H e_R` and
`i slashD_R e_R-Y_l^dagger H^dagger L`. The normalized wall/normal trace
comes from `aether_unified_m5_m4_pushforward_v15_69.py:
unified_parent_boundary_functional`, current daughter inclusion and
inherited domain equations. The unassembled step is the **same-owner
normalized wall/normal-trace realization of that local row** on these
columns. It is an implementation/matching task, not a new precursor,
coupling, profile or terminal-condition selection.

Geometric pointwise trace, normalized B54=W_eta^sharp, reset graph and
temporal conormal are distinct. The compact p has zero geometric material
trace but nonzero normalized projection; this does not remove its wall
action. AE2 specifies zero *independent* reset matter density, not zero
total transmission/action. No independent M4 determinant or Wilson
coefficient is to be added. The full owned constraint/domain pullback,
completion and propagation complement remain unevaluated in the ledger;
the first executable next operand is the source-restricted wall row above.

## Error scope, accumulation and reproducibility

Conditional nodal normalization Arb bounds, endpoint reconstruction,
temporal density interpolation, retained-point history error, radial
quadrature, terminal cutoff remainder, arithmetic residuals and omitted
propagation complement are kept separate. No continuum, total operator
or post-division soft-limit error bound is claimed. Finite trial sources
are not proven closed under propagation. Canonical test-state outputs
are not physical muon-state outputs.

Frozen local values remain a_QED=0.00116550200495813, calibration-only
standard uncertainty1.79e-13 under the original alpha-inverse convention,
0<delta_a_h<3.500331e-9, and the already-combined selected-local interval
(0.0011655039493,0.0011655109506). No contribution is added again or refit.
All six required native-ledger entries, total native uncertainty and
physical a_mu/g_mu remain null. Zero physical soft-transfer directions
and zero native heat evaluations were executed. There is no experimental
comparison.

See `artifacts/muon_retained_tail_core_20261005/reproduction.md` for exact
commands, `input_hashes.json` for full identities, `executed_source/` for
production snapshots, and `targeted_checks.json` for the seven checks.
The checkpoint distinguishes what was assembled, what was solved, and
the one next source-restricted owned action. No second generic framework
was built; reusable weak elements, linear solves and pairings are reused,
while muon realization/source/domain assumptions remain in this example.
