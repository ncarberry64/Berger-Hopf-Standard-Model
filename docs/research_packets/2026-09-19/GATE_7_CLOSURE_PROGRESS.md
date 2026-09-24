# Gate 7: projected action progress

**GATE 7: OPEN. Full BHSM completion is not established.**

## Mathematical result

For the original interval-13 midpoint family, fixed direction w0 and frozen
output row z^T = row_73[(2 dt/3) Q P], define

    Y(theta) = z^T DF(Z_M(theta)) w0.

The new outward Arb/Taylor calculation proves the scalar bounds

    |Y(theta)-Y0| <= 0.341177266859,
    |Y(theta)|    <= 0.384496713820,

on all original 249 midpoint parameters, conditional on the source-bound
retained action and inherited certified physical solution boxes. These
decimal bounds round upward from the exact rational artifact endpoints.
There are an additional 248 correction coordinates, one for every coupled
implicit unknown. No physical domain, parameter, projector or tolerance
has been reduced or retuned.

The proof evaluates V=Y-beta G before taking support. Since G=0 on the
inherited physical solution graph, V=Y there for any exact fixed beta.
The full anchor adjoint suppresses the linear correction support below
4.666e-138; the complete nonlinear remainder, at most 0.341154344930, is
retained. This is a physical scalar enclosure, beyond the previously small
normalization or action-equation residuals. It is not a vector-norm bound.

The action includes its boundary and global inverse-inertia terms. The
readout includes physical normalization and all third/fourth descriptor
contractions. The proof and reproduction commands are in
`theory/n12_gate7_residual_cancelled_scalar_output.md`.

## Smallest remaining local obstruction

The complete projected Hermite--Simpson column is built from

    D = u14 - P e + (dt/6) P A
        + (2 dt/3) P [DF_M w0 + M(e/2-dt A/8-w0)].

All endpoint terms and the midpoint correction term must be bounded on
the same original parameters, then combined with Q before taking the
74-component norm. With the existing point/anchor budget, the required
complete vector remainder is

    epsilon < 0.9997125743857969.

The new scalar bound controls only one row of the DF_M w0 contribution.
Subtracting it from the vector budget would not produce a certified
remaining allowance. The old independent-coefficient relaxation's gain
at least 48.720352347851 is not the gain of this new physical scalar model,
nor has a new full-column gain been established.

The next focused calculation is a shared-parameter enclosure of this
complete column, reusing the same residual identity and saved action
contractions where their covectors agree. It must preserve endpoint and
midpoint dependence and include every output row. A broad Hessian or
sampling campaign is not justified by the present result.

## Closure dependency graph

Original endpoint/midpoint domains and certified solution boxes
-> shared action/normalization equations
-> complete normalized projected physical column
-> full-history causal coefficient bounds
-> same-map two-radius self-map and contraction inequalities
-> remaining physical quotient/operator, signed force, KKT/constrained
Hessian and continuum obligations in the existing Gate-7 ledger.

The scalar result supplies part of the third step. It does not replace the
later steps. The two-radius inequalities retain their existing form:

    B_i(r)=Y_i+sum_j Z_ij r_j+C_i r_L^2+2 M_i r_L r_T+T_i r_T^2 < r_i,
    max_i sum_j (partial_j B_i(r)) r_j/r_i < 1.

The local radii (9.160189721418071e-7, 1.9369612593815614e-9) and external
September 14--15 witness radii (7.138494894595709e-7, 7.706743304268299e-10)
belong to different saved calculations. The external Hessian budget
1.76875845739832e8 and sufficient coefficient cap 0.14566258071899124 are
not substituted for the missing uniform physical proof.

## Evidence and repository state

Work is on `codex/bhsm-gate7-projected-action-20260919` in the canonical
`Berger-Hopf-Standard-Model` checkout, based on `02e3bb4c`.
Commit `ca2b0284` contains the first shared-action and triangular-transport
implementation. The subsequent commit containing this packet adds the
full anchor adjoint, the physical scalar certificate and the correction
for tiny nonzero state-direction coefficient radii.

The evidence checkout `../BHSM-ae32-crossing-correction` and the separate
museum checkout are preserved. Their untracked calculations were not
deleted or rewritten. Saved seven-solve models, original physical graphs,
paired midpoint/endpoint results and prior Hessians were reused. The old
failed endpoint-71 curvature campaign was not restarted.

Artifact names below are under `artifacts/flagship_integration/`:

- `BHSM_N12_GATE7_SHARED_ACTION_RESIDUAL_MIDPOINT_V2_20260919.json`
- `BHSM_N12_GATE7_SHARED_ACTION_RESIDUAL_ENDPOINT_V2_20260919.json`
- `BHSM_N12_GATE7_FULL_MIDPOINT_OUTPUT_ADJOINT_20260919.json`
- `BHSM_N12_GATE7_SHARED_ACTION_ADJOINT_REPRODUCTION_V2_20260919.json`
- `BHSM_N12_GATE7_RESIDUAL_CANCELLED_MIDPOINT_SCALAR_20260919.json`
- `BHSM_N12_GATE7_RESIDUAL_CANCELLED_MIDPOINT_SCALAR_REPRODUCTION_20260919.json`
- `BHSM_N12_GATE7_RESIDUAL_CANCELLED_MIDPOINT_TAYLOR_COEFFICIENTS_20260919.json`

The physical scalar artifact independently reproduced byte-for-byte in
fresh processes with distinct action-checkpoint directories. Its SHA256 is
`906DDD0BEB1C9A14BEF7547E9C52E3115564C8A60228A01A64B4A74DABF886C3`.
The midpoint/endpoint V2 action probes and full midpoint anchor adjoint also
independently reproduced byte-for-byte. The reproduction receipts retain
the exact bounds and runtime versions.

The full signed Taylor coefficients are also saved. Their checkpoint
recovery matched the original certificate byte-for-byte and the export
reproduced twice. This is algebraic recovery of existing action terms,
separate from the fresh independent arithmetic pair for the scalar proof.

The focused regression set passed all 28 tests, covering the original
retained-action adapter, shared Taylor remainders, coupled anchor adjoint,
triangular correction propagation and physical joint-input columns. Unit
tests support the implementation; the source-bound outward calculation
and its independent reproduction supply the stated scalar result.

The forbidden-claim, BHSM-status, frozen-prediction-integrity and
public-readiness audits pass. The existing precision check also passes
(1.066e-14 <= 1e-13); it is not the proof of the new scalar bound. The new
bound uses its own exact outward rational endpoints. Frozen prediction
files are unchanged.

The V1 action probes used midpoint-only state-direction coefficients;
their original-domain coverage claim is superseded by V2, which retains
the complete Arb coefficient balls. The original files remain as evidence.

The external handoffs in `C:/Users/carbe/Downloads/`, including
`Codex_Spark_Gate7_Handoff_20260914.md`,
`BHSM_Gate7_Resume_Addendum_20260914.md` and
`BHSM_AI_Handoff_State_20260915.json`, were reconciled with the repository.
They do not supply the missing complete physical column certificate.

## Complete physical input block, 2026-09-20

The interval-13 right block now covers all 74 physical inputs and 74 projected outputs. Shared base cancellation before interval transport and certified directional-error intersections give original two-radius weighted rows 0.0005576922403983423 and 0.5832743292213708. The local margin is at least 0.4167256707786291. Both independent transport runs and norm replays are byte-identical. See `GATE_7_FULL_INPUT_LOCAL_VECTOR.md` and `GATE_7_FINAL_VERDICT.md`. Gate 7 remains open at the full nonlinear history first-Jacobi/operator-force boundary; the canonical geometric stop is not reopened.
