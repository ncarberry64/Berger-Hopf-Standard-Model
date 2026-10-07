# Seven-port forcing: exact cache roles and one-column owner identification

Starting HEAD: `0f13a65082d4df0ba510540a32071bf938c7716e`.
Branch: `codex/muon-parent-maxwell-density-review`, PR #465.
Scientific reference: `524ed90689bd5923c249bba2e699abf627e703cd`.

The existing machinery supports one consumed boundary forcing column. This
continuation recovers that machinery byte-for-byte from the primary scientific
checkout, evaluates the one-column algebra on an exact finite control, and
identifies precisely why the frozen local matrices cannot yet evaluate the
physical column. It produces **zero physical forcing columns, response solves,
heat evaluations or transfer directions**. No control is a BHSM impedance,
cutoff, anomaly or uncertainty estimate.

The new mathematical identification is that a residual-row transformation can
preserve the response equation while failing to preserve the impedance dual
contraction. The consumed row/dual map is required in addition to an action
identification. A concrete control demonstrates this failure and its correction.

## Reuse the established seven-port map

The quotient has three geometric trace rows, two canonical momentum rows and
two dynamic-flux rows. The recovered `geometric_material_port.py` gives

\[
 b_\psi=\begin{bmatrix}
 T u_\psi+(D_\psi T)q\\
 D_\psi P\\
 D_\psi F-D_\psi G-D^2P[X,u_\psi]-DP[D_\psi X]
 \end{bmatrix}\in\mathbb R^7.
\]

Here the source-direction state jet and explicit trace-shape term are supplied
in the same inherited frame; state motion must not also be added as explicit
shape motion. `geometric_trace_jet` and `required_material_jet` are the actual
producer functions for the supplied algebra. They do not generate the
support-loss normal direction or its same-action state/material variation.
The thin muon adapter calls them with exactly one column.

The frozen material producer `bind_n12_gate7_geometric_material_port.py`
retains the action-dependent momentum, force, radial conormal and two
momentum-rate terms. Its sources are `_trace_jacobian_at_order`,
`_attachment_jacobian_at_order`, `_canonical_pair_at_order`,
`_metric_radial_flux_covector_at_order`, and `_child_rows_at_order` in
`aether_cross_resolution_reconnaissance_v21_35.py`. The saved trace map has
shape 3x98. The constant trace section at chi=pi/4 belongs to that retained
local realization; it does not justify a zero shape term for a new moving
normal source. Child/event signs are +/− in the first five rows and −/+ in
the last two. The saved canonical order is momentum, then dynamic flux.

The later 3/4 split explicitly retires the seven-action-seed requirement.
The geometric trace is already the local top output block, not an additional
trace-history reaction. `moving_port_jet` retains
`(DB)[u] Lambda+B D Lambda[u]`. No eighth coordinate, trace-only forcing or
new generic interface framework is introduced.

## What the concrete frozen blocks actually differentiate

`solve_n12_gate7_fiber_constrained_center.py`, function `evaluate`, defines

\[
 F_{\rm local}=\begin{bmatrix}
 C_L/s_L\\C_R/s_R\\T_{\rm test}\,HS_{13}\\
 (\lambda_L-s_{\rm descriptor,L})/10^{-7}
 \end{bmatrix},\qquad
 HS_{13}=z_1-z_0-\frac h6(f_0+4f_m+f_1),\quad h=\frac14.
\]

There are 25+25 constraint rows, 74 Hermite–Simpson flow-matching rows and
one descriptor row. `gate7_coupled_fiber_center_20260927/jet/arrays.npz`
contains its `J125` derivative. This is the corrected historical interval-13
constraint/evolution border, not an exhibited current AE4 mechanical
stationarity Hessian.

The construction in `derive_n12_gate7_joint_port_reduction.py` makes the
roles unambiguous:

| Saved array | Shape | Actual derivative |
|---|---:|---|
| `J125` | 125x125 | local residual derivative F_n |
| `local125_forcing` | 125x73 | launch forcing F_p |
| `local125_port_normal_derivative` | 7x125 | output derivative g_n |
| `native_event_7x98` | 7x98 | local event output/state derivative |
| `trace_action_3x98` | 3x98 | geometric trace/state map |
| `local_required_material_4x73` | 4x73 | local material launch output |

In particular the seven-row matrix is not F_b, and the 125x73 forcing does
not acquire a physical normal input by multiplication with a convenient
right inverse. No launch, canonical seed, SVD gain vector or descriptor
normal is selected as xi_psi. The retained caches provide local coordinate
scaffolding, not a source-selection equation for this support-loss branch.

`evaluate_n12_gate7_current_contractions.py` also retains the signed ledger

\[
 \Gamma_{\rm attached}-\Gamma_{\rm SM\,zeta}+\Gamma_{\rm heat}
 =\Gamma_{\rm classical}+\Gamma_{\rm heat},
\]

and explicitly does not assume that the attached-action flow is stationary
for the classical action after subtraction. A flow-matching border therefore
cannot be relabeled as the owner Euler derivative from its dimensions.
Nonsymmetry alone would not settle this identification either. The old
supplied-matrix heat/zeta adapters do not themselves supply the current AE4
support-loss base, length, domain, grading or completion.

## The exact condition for reusing the local solve

Let E_owner be the same-owner Euler/constraint residual in common internal
coordinates. A possible reuse needs a row/dual identification

\[
 F_{\rm local}=C\,E_{\rm owner}.
\]

For source partial differentiation at fixed internal coordinates,

\[
 D_sF_{\rm local}=C h_\psi+(D_sC)E_{\rm owner},\qquad
 F_n=C H_{\rm owner}+(D_nC)E_{\rm owner},
 \quad h_\psi=D_bE_{\rm owner}[b_\psi].
\]

At an **owned stationary base**, the gradient terms vanish. If C identifies
the relevant residual/quotient spaces, the old local solve can then supply
the same response from one column `f_local=C h_psi`. Away from that base,
the displayed gradient terms remain. A consumed row/dual action can suffice;
neither a full global C nor all seven columns is required for a justified
contracted calculation. No examined producer supplies this identification.

Even when the response is identical, the physical quadratic contraction is

\[
 z_\psi=Q_{XX}[\xi_\psi,\xi_\psi]
       -h_\psi^\dagger H_{\rm owner}^{-1}h_\psi,
 \qquad
 h_\psi^\dagger H_{\rm owner}^{-1}h_\psi
 =f_{\rm local}^\dagger C^{-\dagger}F_n^{-1}f_{\rm local}.
\]

The inverses in these equations denote applications of linear solves.
The implementation forms no inverse. A row transformation is not a form
congruence; even unitarity alone would not justify dropping C's dual factor.
The recovered `reduce_seven_port` instead provides the valid general implicit
output reduction `g_b b_psi+g_n deltaPhi_psi` through its existing adjoint
solve. No Hermitian or positive interpretation is imposed on causal outputs.

For a source-dependent constraint R(eta,s)=0, use the full KKT variation of
L=Gamma+lambda^dagger R:

\[
 H=\begin{pmatrix}L_{\eta\eta}&R_\eta^\dagger\\R_\eta&0\end{pmatrix},
 \quad h=\binom{L_{\eta s}}{R_s},\qquad
 z=L_{ss}-h^\dagger\operatorname{solve}(H,h).
\]

Constraint-source rows, multiplier contacts and L_ss stay present. Positivity
belongs to the allowed physical tangent, not to the indefinite KKT matrix.
The geometric/action dual pairing must already be encoded in these weak
form entries; Euclidean coordinates cannot replace it by default.

## New execution and error scope

The exact rational finite control has two internal fields, one constraint
multiplier and one prescribed seven-component column. Its action has positive
physical A, a source-dependent constraint and a symmetric indefinite KKT
border. Direct mixed differentiation generates the forcing. At 256-bit Arb
precision the one-column solve encloses the exact solution and its residual
contains zero. The direct physical quadratic equals the Schur expression
exactly. The existing signed seven-output adjoint agrees with the forward
response, and the moving-port product rule retains DB.

A second representation of the same control rescales residual rows. It gives
the same response and a different naive impedance. The targeted row-dual
test evaluates the corrected contraction exactly; the replay control records
the owner contraction and the incorrect row contraction separately.
These values are saved as **control** values only.
They are not the source or environmental resistance of any BHSM child.
Arb errors here cover rounding of supplied finite entries. An interval
residual containing zero is consistency evidence, not a proof of exact
physical cancellation or a continuum/error bound.

Twelve targeted new tests pass. The first attempt had one test API failure
from passing a string to Arb.contains; explicit scalar conversion corrected
that test. The new replay ran once. The historical 7x73 producer, field
campaigns, heat contractions, normalization and muon production were not run.
Frozen caches were read for provenance and shape roles, never regenerated.
The recovered three source modules are byte-identical to the primary copies;
their hashes and original commits are in `run_1/recovered_helpers.json`.
Executed sources and raw/canonical input hashes are retained.

## Assembly stop and one next consumed operand

Physical assembly stops before the right-hand side is formed. The examined
records do not provide the action-selected xi_psi-to-state/material source
column or an identification of the local residual with the current owner
Euler/constraint dual. This is a demonstrated limitation of these concrete
producers, not an exhaustive absence theorem or proof of physical
non-identifiability. No new boundary or constitutive assumption is installed.

The next operand is **one same-owner normal-source Euler column**, represented
in the established seven-port coordinates and, if the local border is used,
its consumed row/dual coordinates:

\[
 \boxed{\quad b_\psi=B_{\rm boundary}[\xi_\psi],\qquad
 \langle\eta,f_{\psi,\mathrm{bulk}}\rangle
 =D_\Phi D_X S_{\rm bulk}^{\rm owner}[\eta,\xi_\psi].\quad}
\]

This boxed covector is the physical bulk mixed-action part. In unreduced
constrained coordinates, the consumed forcing is instead the complete
`h_psi=(L_eta,s,R_s)`, where
`L_eta,s=f_psi,bulk+lambda^dagger R_eta,s` in the common action convention.
The constraint-source row and multiplier contact must be generated by that
same prescription; the boxed bulk formula does not replace them. The packet's
`defining_weak_equation` names this physical bulk part, while its Euler/constraint
column and solver accept the full augmented column when constraints are kept.

Its producer is the same-owner bulk/interface variation with the retained
trace, momentum, conormal, rate, reset and constraint pullbacks. Its immediate
consumer is the one-column solve, then the owned-dual impedance contraction.
This requirement is not the old Gate7 closure label and does not demand all
73 launches. Once supplied, the retained total resistance `gamma J_Sigma+H`,
inertia, quotient jets and AE4 heat lower-limit algebra can consume it.
They remain null here, as do R_ind, the native anomaly and g_mu.

Reset, contact, Wentzell, scalar/topographic and constraint reactions are kept
as shared signed dependencies and counted once. The strong term remains a
subset of the full native owner, not an additional zero or independent addend.
State, domain, pairing and completion terms remain unevaluated explicitly.
All local QED/Higgs/weak contributions and their original calibration-only
uncertainty convention remain frozen; the already combined interval is not
summed again. No external anomaly or discrepancy enters the calculation.

Reproduction uses a fresh output directory and the read-only primary record:

```powershell
C:\Python314\python.exe scripts/replay_muon_native_interface_bulk_forcing.py --output <fresh-directory>
C:\Python314\python.exe -m pytest --noconftest -q tests/test_muon_native_interface_bulk_forcing.py
```

The standalone Downloads launcher points to these retained sources; it is not
a downloadable muon-number prediction. No reset, cleaning, cache overwrite,
new physical state or future tail is performed.
