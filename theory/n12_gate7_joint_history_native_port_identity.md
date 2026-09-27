# N12 joint-history reduction and the native seven-row port

Base checkpoint: `5de35b98247d0005884ffe39c6439f7b4788e40c`, branch
`theory/gate7-66d-reduced-adjoint-integration`.

The historical split is recovered, and the frozen **local** 125-variable
constraint/fiber/HS system gives an exactly zero seven-port adjoint correction.
The stored local 7x73 matrix has certified row rank 7. These results do not
establish the complete joint-history port identity: the recovered historical
records explicitly leave the physical upstream/downstream signed covectors
open. No local response is promoted to the full environment response.

## Recovered owners and the meaning of the historical residual

`derive_n12_c2_reset_launch_adjoint_interface.py:66` supplies deterministic
random **test** covectors. Its report calls the witness
`DETERMINISTIC_LINEAR_ALGEBRA_CROSSCHECK_NOT_A_PHYSICAL_FORCE`.
The recorded relative residual `4.085949076101689e-16` verifies a change of
launch coordinates, not a computed physical seven-row reaction. The absolute
residual is `2.86102294921875e-6`. Both are preserved without changing their
interpretation. The present replay executes only this small algebra control.

With forward product order `(C2,E1)`, let `Z: R139 -> R196` span the reset
tangent and let `B=P_C2 Z: R139 -> R98` have rank 72. If `Kseed` spans
`ker B` (dimension 67), the exact identities are

```
g_reset = Z^T d_upstream_interface + B^T p0,
Kseed^T B^T p0 = 0,
Kseed^T g_reset = (Z Kseed)^T d_upstream_interface,
g_launch = [Q,F0]^T p0.                     (98x73 launch map)
```

The executable contraction is in
`aether_c2_launch_adjoint_pullback.py:86`.
`audit_n12_c2_fixed_seed_upstream_force_owner.py:170` identifies
`K_fixedC2={0}_C2 direct_sum ker(J_E1)`, dimension `98-31=67`.
Its owner is the complete C1-to-E1 upstream heat-minus-zeta history and
retained contacts (`:173`). It is not seven new boundary forces, nor may it
be discarded from full stationarity. The downstream annihilation on this
particular kernel does not imply cancellation on arbitrary seven-port rows.

Hash ledger in `report.json`:

- Launch/adjoint interface: all seven direct historical inputs match.
- Fixed-seed upstream owner: 13 of 14 match. The documentary input
  `BHSM_N12_HISTORICAL_RELATIVE_DETERMINANT_REUSE_AUDIT.json` is unavailable;
  its expected SHA256 is preserved. This does not erase the matched reset
  matrices or the algebra above; it prevents claiming a complete replay of
  that documentary audit.
- Signed C2 adjoint assembly: 16 current inputs match; the exact older
  parametric-family input was recovered from Git commit
  `01f8df8531e05f89b9673efbfe3a7b0321ddff29` and preserved in
  `historical_inputs/`, without replacing its newer repository version.

The signed assembly already owns the reverse recurrence
`p_j = C_x[j] x_Y[j] + C_h[j] h_Y[j] + Phi_Y[j]^T p_(j+1)`.
Its source distinguishes closed coefficient seeds/norm enclosures from the
open signed physical contraction (`derive_n12_c2_1222_signed_adjoint_assembly.py:302`).
In particular its `actual_BHSM_signed_covector` remains `OPEN` (`:351`).
A scalar 73-component launch covector is not a 7x73 reaction derivative.

## Joint operator ledger and conditional reduction theorem

Use the existing replacement convention, schematically

```
Gamma_joint = Gamma_local
            + Gamma_heat[P_joint] - Gamma_SM_zeta
            + owned constraint/descriptor/normal equations,
J_ext = 0.
S_AE2 = M_event + U_R^dagger M_C2 U_R + W_phys.
```

The last line is the existing covariant seam assembly, not an identification
of every historically named `M_f`. The `M_event` here is the restricted
joint Weyl/Calderon event-side operator from the previous ownership ledger,
not the local native action Hessian. The inherited source/function hashes
are in `gate7_environment_ownership_20260927/report.json`.

| Ledger | Treatment before reduction |
|---|---|
| Ten local event terms | Already included in the frozen native derivative |
| Upstream/local seam history | Retain complete heat-minus-zeta dependence |
| Transported C2 response | Retain child load inside the joint seam inverse |
| Reset/pullback | Retain common source incidence and covariant `U_R` transport |
| Pair/contact | Retain owned gauge, scalar/topographic and AE2 vertices once in the joint assembly |
| Descriptor/eigenline/response | Compose through their common owned normal system |
| Constraint/KKT and HS history | Compose before projection; local subset tested below |
| Other retained internal blocks | Remain in the joint operator; none deleted by `J_ext=0` |
| Independent external birth arm | IDENTICALLY ZERO / absent in the declared model |

This is an inclusion ledger, not eight independent additive copies of the
action. In particular the zeta replacement is subtracted once, and transport
and contact terms already inside `P_joint` are not added again as a new
`Lambda_E`. The previous ledger's sector-specific zero fermion contact does
not make all contacts zero.

For the **complete** internal equations `F(p,n)=0`, put `K=F_n` and define
the actual seven-output functional `g(p,n)=B7(p,n) Lambda_joint(p,n)`.
At a common center where K is invertible,

```
Phi_p = -K^-1 F_p,
K^T lambda = g_n^T,                 (seven adjoint right-hand sides)
D_p g(p,Phi(p)) = g_p - lambda^T F_p,
g_a = (D_a B7) Lambda_joint + B7 D_a Lambda_joint,   a=p,n.
```

`joint_boundary_port_reduction.py` implements this conditional identity. It
sums signed output sectors before the one common solve, takes no support or
norm of them, and requires explicit derivatives rather than filling missing
ones with zeros. Its moving-port helper retains the `DB7` term.
Stationarity alone does not remove mixed reaction derivatives: for
`Gamma=n^2+3np+(5/2)p^2`, `Gamma_n=0` gives `n=-3p/2`, but the reduced
derivative of `Gamma_p` is `1/2`, not its direct derivative `5`.

## Actual current-center local control

The frozen center packet supplies a 125-variable border with 25 left
constraints, 25 right constraints, 74 interval-13 HS rows and the left
descriptor fiber. It is not the complete upstream/C2/contact KKT operator.
For this subproblem only, use the stored launch chart, frozen native
`J_event_7x98`, frozen local `R_7x73`, and left normal lift `N`:

```
g_p = R_7x73,
g_n = [J_event N, 0],
F_p = [0_left_constraints; 0_right_constraints; Te14^T L13 T_launch_aug;
       0_left_fiber].
L13 = -I - h J_left/6 - (2h/3) J_mid (I/2+h J_left/8), h=1/4.
```

The zero constraint/fiber derivatives follow symbolically from the defined
chart projection and `ds=Dlambda T`; they are not obtained by rounding small
coefficient residuals. The descriptor test scale remains `1e6`; the stored
center border preserves the historical trial scale `1e-7`. No scale changes.
The local output depends on left state only. The left constraints and fiber
determine its normal corrections independently of the right HS solve.
Consequently its adjoint correction `-lambda^T F_p` is **exactly zero**.
The computation verifies this structural cancellation using Arb512 and also
performs a small 125x73 forward linear solve as an independent control.
This is not an all-history forward-column campaign.

| Current-center result | Bound/result |
|---|---:|
| Frozen local 7x73 rank | 7 |
| Local right-inverse defect | <= 2.250366e-11 |
| Local 125 adjoint equation replay | <= 1.499809e-24 |
| Local normal equation replay | <= 3.488557e-12 |
| Local adjoint-versus-forward enclosure | <= 4.121918e-8, contains zero |
| Local 125 correction | Exactly zero |
| Complete joint 7x73 rank | Not established |
| Complete-minus-local 7x73 | Not established |
| History/contact correction row norms | Not established |

Exact outward rational bounds, not only decimal displays, are stored in
the report. The comparison is below the unchanged `8.915423761304125e-7`.
These bounds concern the supplied local matrices only; they provide no
uncertainty bound for an unevaluated joint-history coefficient.

The canonical complete-child residual is
`[Tq_child-Tq_event; P_child-P_event;
Gamma_child+DP_child[X_child]-F_child+Gamma_event]`.
Thus the unsigned stored event output enters with `diag(-I5,+I2)`.
The algebra test checks that this constant orientation commutes with the
common reduction; it does not assert an unavailable joint physical replay.
Child momentum-rate terms remain child-owned.

## Seven-row accounting

Here **A = ACTIVE** means retained before projection, with its coefficient
on this particular row unresolved. It does not assert a nonzero coefficient
on every row. **I = ALREADY INCLUDED**. **C = INTERNAL-CANCELLED** is restricted
to the tested local 125-variable border. No full-history contribution has
been classified zero or DISTINCT CORRECTION without its signed coefficient.

| Native row | Local | Upstream/history | C2 | Reset/transport | Pair/contact | Descriptor/constraint (local only) | Total joint |
|---|---|---|---|---|---|---|---|
| Trace 1 | I | A | A | A | A | C | A, unresolved |
| Trace 2 | I | A | A | A | A | C | A, unresolved |
| Trace 3 | I | A | A | A | A | C | A, unresolved |
| Momentum 1 | I | A | A | A | A | C | A, unresolved |
| Momentum 2 | I | A | A | A | A | C | A, unresolved |
| Dynamic flux 1 | I | A | A | A | A | C | A, unresolved |
| Dynamic flux 2 | I | A | A | A | A | C | A, unresolved |

The packet includes each local row norm and its zero local correction bound.
Uncomputed full-history norms and rows are JSON `null`, not numerical zero.
This partial accounting preserves the unproved entries rather than claiming
the requested no-omission theorem is finished.

## Exact next representation and checkpoint boundary

The next required object is the **current-center action-owned seven-output
jet** `(g_p,g_n)` for `g=B7 Lambda_joint`, tied to the complete internal
`(F_p,K)` (or an equivalent seven-output signed causal adjoint contraction).
It must include the history/contact mixed derivatives and moving-port terms.
The historical scalar test covectors, a signed-force norm ball, or the local
125 border cannot substitute for that object. An additional environment law
is neither needed nor authorized.

Once those owned blocks are instantiated, the common seven-RHS reducer
computes the correction without a new 73-column history campaign. Only its
signed comparison with the local matrix can decide whether the additional
terms cancel, are already included, or survive. The current data do not
decide that question, so the full child/environment reaction solve and
Layer-C promotion cannot yet use this packet as their physical authority.

Producer: `scripts/derive_n12_gate7_joint_port_reduction.py --out <new-directory>`.
Packet: `artifacts/flagship_integration/gate7_joint_port_20260927/`.
The saved historical input supports replay without the original temporary
recovery directory. No action, Stage-B, frozen native derivative or history
campaign is rerun. `Gate7_closed=False`; `FULL_BHSM_COMPLETE=False`.

Validation: **53 focused tests pass** (`pytest --noconftest -q`) across
`test_gate7_joint_port_reduction`, `test_gate7_environment_action_ownership`,
`test_gate7_recentered_launch_response`, `test_gate7_event_conormal_jet`,
`test_gate7_parent_sector_jets`, `test_moving_seam_response`,
`test_gate7_comoving_interface` and `test_gate7_coupled_fiber_center`.
Two independent producer runs reproduce all three emitted files byte for
byte; `reproduction.json` records their hashes. Algebra fixtures are tests
of the reduction formula, not substitute physical N12 histories.
