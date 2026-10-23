# Dynamic Higgs contribution to the retained Maxwell wall response

Norman P. Carberry / BHSM continuation — 17 October 2026

## Result and boundary of the result

The saved Maxwell causal maps are reused without recomputing their action matrices
or their large stage solves. The actual intrinsic Higgs action is expanded and
propagated on the SAME twelve exported provisional backgrounds and four-stage
chronological rule. Its returned wall covectors and scalar canonical endpoints
are combined with the Maxwell results in one common action convention.

This evaluates an additional **classical finite response component**, not a new
physical collider, exterior, quantum, or formation solution. The two arms remain
separate, the wall fields remain inputs, and every scalar initial condition is an
explicit input rather than an imposed vacuum. No force is invented to confine a
carrier pattern. No magnetic anomaly, physical pole or complete uncertainty is
calculated. The old stricter Maxwell gauge-reconstruction discrepancies are not
repaired or recertified here.

The repository was read at `70e82fd4dbe5f53ff27ae17f6aaac7a4727c1fde`, PR #465.
No repository or Windows-worktree change is made. A direct container-network
attempt to copy the public source files failed DNS resolution. The action formulas
were read through the connected GitHub tool; this new implementation is a
source-derived reimplementation, not execution of a complete repository checkout.

## 1. Original action, fields, and common normalization

The source functions are:

- `muon_material_higgs_gauge_action.material_intrinsic_higgs_gauge_action_jet`
- `muon_intrinsic_higgs_gauge_action.intrinsic_higgs_gauge_action_jet`
- `muon_intrinsic_m4_normal_pullback.intrinsic_m4_weight_jet`
- `muon_parent_gauge_geometry_correction.retained_scalar_matching_coefficients`

They define, with the original real doublet convention,

    S_H = (1/(2 pi^2)) int dt dHaar [
             wT |D_t H|^2 - wS sum_i |D_i H|^2
             - wV lambda_H (H^T H - nu2)^2 ],
    wT = R4^3 / Nind,
    wS = Nind R4,
    wV = Nind R4^3.

Here the real field is `(Re H1, Re H2, Im H1, Im H2)`. `Nind` is the induced
moving-wall lapse, NOT the ambient bulk lapse. The factor `1/(2 pi^2)` follows
from the source action's physical S3 measure `2 pi^2` divided by the existing
cap orbit normalization `(2 pi^2)^2`. It is not the Maxwell-to-cap factor and
is not a new coupling.

The material temporal trace is `A_t,ref`, with no additional `2 wall_rate A_rho`
added to it. The source proves that Eulerian radial advection cancels the
coordinate conversion. Spatial fields include the mechanical connection exactly
once. The actual total wall connection is reconstructed from the last independent
radial coefficient and that original mechanical term. The exporter records that
the source-complement and two interior profiles have zero wall value.

The homogeneous original values H and Hdot are taken from the export's raw268,
and checked against its separately exported intrinsic scalar values and rates.
The gauge generators are the owned realification of

    G_i = -i sigma_i/(2 sqrt(2)),
    G_Y = -i I/(2 sqrt(10/3)).

No free Higgs axis or mass is selected.

The retained scalar matching has

    G_F = 1.1663774240217167e-5 GeV^-2,
    m_h = 125.11 GeV,
    lambda_H = G_F m_h^2 / sqrt(2) = 0.1290946235307726.

Those values are copied from the existing calibrated matching files read through
GitHub. This is inherited calibration, not a first-principles derivation or a new
fit. The two exported original phase receipts both explicitly have `nu_squared_action=4.0`.
That existing action value is retained. No common physical energy unit is inferred
from it. The nu2 derivative below is a mathematical partial, not a new choice of
nu2 or a completed scale-calibration calculation.

## 2. Full scalar and gauge Hessian in the same angular space

Let `v` be a real Higgs variation and `a_mu` a gauge variation. At fixed supplied
geometry and base fields,

    delta(D_mu H) = D_mu v + G(a_mu) H,
    delta_u delta_v(D_mu H) = G(a_mu,u) v_H + G(a_mu,v) u_H.

Thus, writing c=1/(2 pi^2) and signed weights w_mu=(wT,-wS,-wS,-wS),

    S_H''[u,v] = 2c int dHaar sum_mu w_mu [
          delta_u(D_mu H)^T delta_v(D_mu H)
          + (D_mu H)^T delta_u delta_v(D_mu H)]
       - c wV int dHaar u_H^T V_HH v_H,

    V_HH = 4 lambda_H [(H^T H-nu2) I + 2 H H^T].

The second covariant-derivative term is retained on the unmatched backgrounds.
Dropping it is not justified by a small projected or original n1 residual.

All four real scalar components times all four normalized n1 harmonics are
included: 16 scalar values and 16 scalar momenta. The SAME 64 wall gauge inputs
are used: four tangential one-form components `(At,A1,A2,A3)` times four internal
coefficients times four angular functions. `Ar` remains a normal bulk field; it
is not relabeled as a tangential intrinsic gauge field.

The quadratic matrices have size 80x80, for `(scalar16, wall64)`. Only scalar
rates enter this classical Higgs action. Consequently there is no direct wall
**gauge-rate** momentum from S_H. The scalar temporal canonical momentum is
nevertheless essential and nonzero.

The background is angularly homogeneous, so this n1 *linearized Higgs sector*
is invariant for these supplied coefficients. That statement does not say a
nonlinear solution or localized collider packet is closed in n1. Nor does it
remove n0 background defects.

## 3. Propagate the scalar response without imposing exterior conditions

The time and action rescaling is exactly the preceding Maxwell convention:

    tau=(t-tlo)/T, T=1e-5 in exported coordinate-time units,
    S_hat=T S, At_hat=T At.

The original gauge wall input ordering and all 134 drive functions are reused:
64 wall fields times (1,tau), plus the six inherited magnetic profile columns.
These are response-basis coefficients, not independent particle modes or a
selected switching protocol.

A fixed scalar kinetic normalization at each arm's initial endpoint conditions
the system; it is not a pole, mass or quantum-state normalization. With h the
16 scalar coordinates and g the wall traces, the forced scalar equations are

    p_H=M_H h'+B_H^T h + B_gH^T g,
    h'=M_H^-1(p_H-B_H^T h-B_gH^T g),
    p_H'=B_H h'+K_H h+K_Hg g.

All 32 scalar initial coordinates remain explicit. Four-stage Gauss-Legendre
collocation uses exactly the exported time nodes. Its stage matrix is 128x128.
There is no equation imposed at the final endpoint.

An independent system enforces the original scalar position, momentum and Euler
stage equations without using the canonical first-order matrix. It returns the
same scalar histories and endpoint state to the recorded arithmetic accuracy.
Both implementations use the SAME finite time rule; their agreement is not an
independent temporal-convergence certificate.

## 4. Combine the evaluated response with Maxwell exactly once

At fixed g, the bulk Maxwell fields and intrinsic Higgs modes have separate
interior response problems. They communicate through their common wall inputs
and returned action. This is not yet a closed wall-feedback solution.

Let theta be the 134 drive coefficients, u_M the 408 Maxwell initial coordinates,
and u_H the 32 scalar initial coordinates. The new combined classical wall map is

    W_classical = B_M u_M + B_H u_H + (Z_M+Z_H) theta.

The saved Maxwell maps provide B_M,Z_M. The new scalar solves provide B_H,Z_H.
No Maxwell coefficients are recalculated and no interaction already in that
Maxwell-only block is added again. The Higgs spatial, kinetic and potential terms
are all from its own original action with the common normalization in section 1.

The combined final-state map has size **440x574**. The combined wall map has size
**134x574**. Initial-data order is `(Maxwell408,Higgs32,drive134)`; final-state
order is `(Maxwell canonical408,Higgs canonical32)`.

The full discrete Green identity includes BOTH canonical endpoint terms:

    W-W^T + X_Mf^T P_Mf-P_Mf^T X_Mf
            + X_Hf^T P_Hf-P_Hf^T X_Hf = 0

on zero-initial response columns. Its discrepancies are 3.35e-15 incoming and
6.03e-15 outgoing. The matrices are not symmetrized by dropping the temporal
term. Their nonsymmetry is part of the initial-value response accounting.

The remaining wall equation is still

    W_classical + W_geometry/interface + W_matter
                + W_exterior/native/reference = 0

in a genuinely compatible common weak chart, together with the relevant initial
and transition equations. The unspecified terms are not assumed zero. The two
arms are NOT identified by an identity map and their wall operators are NOT
summed across a supposed common event before its actual pullback is supplied.

## 5. The exact aligned-Higgs cancellation survives this calculation

The source-selected electromagnetic generator obeys `G(s(H)) H=0`. This implies
that the original Higgs action is unchanged by the full field-dependent insertion
`A -> A+a s(H)` when the corresponding internal direction is consistently varied.

A fixed-generator scalar/gauge Hessian can still be nonzero at an off-shell base.
The total derivative of the neutral insertion has the additional term

    S_H,HA[v, a s(H)] + S_H,A[a Ds(H)[v]] = 0.

Both terms are now evaluated on the actual retained fields. At the first samples,
the maximum fixed-axis scalar/gauge entries are about 0.0136083 incoming and
0.00857123 outgoing. The actual moving-axis gradient contacts cancel them; across
all twelve samples the remaining discrepancy is at most 6.94e-18.

Therefore this new Higgs block is NOT a direct neutral-photon trapping force.
The generic original-field-coordinate wall response is valid at its declared
scope, but the six fixed-base magnetic trace columns alone are NOT the full
field-dependent, geometry-moving, physical magnetic derivative. Completing that
pullback requires the total source and background response, including the
second-map action-residual contacts. They cannot be reconstructed by interpreting
this fixed-axis cross term as a Higgs magnetic mass.

The original Higgs gauge identity is also checked on all 16 n1 internal gauge
parameters and every value/scalar-rate test. With the actual residual contact
included it holds to at most 5.47e-17; the incomplete Hessian-only expression is
nonzero. No stationary background assumption is used to delete the contact.

## 6. An explicit potential-center sensitivity

For the existing scalar potential-center slot nu2,

    partial_nu2 K_HH = 4c wV lambda_H I16

in unscaled physical scalar coordinates. Its properly transformed derivative is
inserted into the SAME implicit chronological system:

    A_stage Z_s = - (A_stage)_s Z.

The wall and terminal readout derivatives then use the resulting source response.
This is a fixed-background, fixed-domain **nu2 partial**. It does not differentiate
the complete scale equation, physical packet, metric, source frame or reference.
It is not the complete outgoing derivative.

Independent reruns at nu2=4 plus/minus a finite step check both terminal and wall
maps. At step 0.2 their terminal discrepancies are at most 4.16e-16. Smaller
steps increase roundoff to about 1.12e-15, which is preserved, not described as
monotone convergence. The derivative amplitudes and all steps are recorded so an
absolute-error check cannot be confused with a relative or physical error bound.

## 7. Executed checks

All original export hashes (47) and the preceding port package hashes (30) were
verified. The 12 actual H/Hdot samples were cross-checked against their independent
exported fields. The reported new local matrices are independently checked by an
explicit complex-doublet scalar-action evaluator. Five-point second differences
are exact on that quartic polynomial up to arithmetic error; this does not rely
on the Hessian implementation itself.

| Check | Incoming | Outgoing |
|---|---:|---:|
| Original scalar action vs Hessian | <=3.76e-15 | <=5.80e-16 |
| Independent angular rules | <=3.34e-16 | <=1.67e-16 |
| Independent original stage solve | <=3.34e-16 | <=1.12e-16 |
| Independent terminal state | <=2.23e-16 | <=1.39e-17 |
| Scalar canonical momentum | <=2.23e-16 | <=1.12e-16 |
| Complete scalar gauge identity | <=5.47e-17 | <=4.17e-17 |
| Moving neutral-axis cross cancellation | <=6.94e-18 | <=3.47e-18 |
| Combined wall/temporal Green identity | <=3.35e-15 | <=6.03e-15 |

Ten scoped check categories pass on each arm. Two independent executions produce
eight byte-identical result/array files. A development output serialization failure
caused by NumPy booleans was repaired; its partial files and script are retained.
No physical equation was changed to cure that output error.

The tiny trace-driven Higgs wall-map entries in the scaled short-time chart do
NOT prove the Higgs field negligible. The arbitrary-initial-scalar maps are
nonzero, the original physical scaling is explicit, and the physical field history
and response are not solved. No branchwise uncertainty estimate is inferred from
coefficient maxima.

## 8. Remaining work and what has not changed

The finite intrinsic classical Higgs response is no longer an unimplemented slot
in this particular open-wall calculation. However, the actual wall-law closure,
field-to-quantum-operator correspondence, inherited reference, current projection,
source-dependent geometry and interface response remain unresolved.

No complete physical derivative, coupled background correction, fresh collider
Maxwell/all226 admission, pole/residue normalization or magnetic moment is
reported. The physical 2e-10 guard remains unchanged. The stricter Maxwell
gauge-reconstruction failure from the preceding package remains a limitation of
the reused response and has not been repaired by this scalar calculation.

## Reproduction

With numpy and scipy installed, run:

    python run_higgs_response.py --output replay_new

The provided `inputs/` makes that command self-contained. It does not request
another user export or contact GitHub. `prepare_inputs.py` documents extraction
from the already-supplied source packages, rather than being a prerequisite to
rerunning the packaged calculation. It does not regenerate the Maxwell matrices.

## Source readings

At the pinned revision, the GitHub connector supplied the four modules listed in
section 1 and the existing matching files:

- `artifacts/muon_calibrated_pauli_20261009/inputs.json`
- `artifacts/muon_calibrated_weak_decay_20261010/run_1/weak_decay.json`

The field data and original phase receipts come from the attached
`BHSM_RETAINED_HISTORY_INPUTS_20261017.zip`. The unchanged Maxwell causal maps and
conditioning conventions come from
`BHSM_port_preserving_retarded_response_20261017.zip`. The existing wall-geometry
formula implementation is copied from the earlier integrated-source package and
hashed in this package. A production integration must compare these reconstructed
source-defined formulas with the live original owner functions before physical
promotion. No new quantum, fluid, or reconnection law is introduced here.
