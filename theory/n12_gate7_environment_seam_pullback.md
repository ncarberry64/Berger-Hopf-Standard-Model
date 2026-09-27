# Fixed-environment moving-seam first variation

Continuation of `8d00989c` on
`theory/gate7-66d-reduced-adjoint-integration`.

The external physical state e0 stays fixed. Its restriction, normal,
canonical momentum density and dynamic flux on the moving seam need not
stay fixed. This is motion within the same envelope branch; it supplies no
new environmental degrees of freedom or de-encapsulation assertion.

## Executable signed composition

`src/bhsm/interface/moving_seam_response.py` implements the first variation
in the conventions already present in the repository:

```
D(P r_E) = DP r_E + P Dr_E,
p_seam = Ws^-1 L^-T We p_native,
D p_seam = Ws^-1 L^-T (DWe p_native + We Dp_native
                        - DL^T L^-T We p_native)
             - Ws^-1 DWs p_seam.
```

Native derivatives include moving-point and normal sampling. Frame,
measure and projector changes belong in the pullback jet; they cannot be
omitted because delta e=0. The momentum identity is differentiated from
the existing weighted cotangent pairing, rather than imposing a new law.

If the environment on-shell functional is obtained by eliminating an
interior variable a from the same action S, its boundary reaction derivative
is composed before support:

```
Da = -S_aa^-1 (S_aq Dq + S_aSigma DSigma),
D Lambda_E = S_qq Dq + S_qSigma DSigma + S_qa Da.
```

This implementation requires the actual Hessian/domain blocks. It neither
constructs W_E by analogy nor identifies the seven heterogeneous rows with
seven components of one unspecified gradient. Three trace, two momentum,
and two dynamic-flux jets are supplied separately in common coordinates.

The full seven-row differentiated balance requires **73 columns**: 66 p
directions and seven q directions. With owner orientation O explicitly
supplied,

```
Kp = Cp + O Ep,   Kq = Cq + O Eq,
Dq = -Kq^-1 Kp,  T_comoving = Tp + Tq Dq.
```

Keeping Ep while dropping Eq would still miss environment feedback when
the slaved reactions move the seam. Singular full Kq is not replaced by
the inverse of the child block. These are conditional assembly routines;
passing matrices is not proof of their physical ownership.

## Frozen node-13 result

The prior weak-boundary packet already stores the signed coefficient

```
nu_rho = -Hzz^-1 [B^T;0].
```

It has rank two, certified on the saved endpoint box by the Gram inverse
defect `<=8.02910e-36`. The complete chain rule is now executable:

```
Dnu = (D_Y nu)|rho DY + nu_rho D rho_env.
```

This compiles frozen arrays only. No action, eigenline, endpoint, midpoint,
Stage-B or nonlinear producer was rerun. Rank two describes the conormal
feedback coefficient, not the full seven-row boundary system or its tangent.

## Reuse search and remaining physical input

The search covered the requested operator terms in the repository's theory,
scripts, interface modules and flagship artifacts, plus the supplied
environment documents in Downloads and the relevant attachment worktrees.
Exact source hashes and function line ranges are saved in the report.

The usable identities are:

- `first_moving_domain_variation`: material pullback, cotangent density and
  moved-projector terms. Its supplied-family formula is explicitly conditional.
- `weighted_cotangent_momentum_map`: the inverse-adjoint weighted pairing.
- `weyl_riccati_rhs` and `weyl_geometry_jet_rhs`: an owned arm-normal transfer
  law given the Weyl value and spatial coefficients. No arbitrary Robin value
  is introduced; the old M(0)=W_phys initialization remains superseded.
- `aether_forward_history_weyl_first_jet`: coefficient/duration transfer on
  a supplied history. Its spectral channel space is not the seven-row
  trace/momentum/dynamic-flux space without an additional owner map.

The v0.4 boundary-graph note in Downloads introduces W_E **schematically**
(lines 165-180); it does not give its numerical Hessian or embedding jet.
The stored spectral parent-response ledger leaves M_E0 and its jet open.
That spectral fact alone is not a reason to demand an entire new global
parent-history campaign for a potentially local seven-row realization.

The exact first unbound object is the **native environment trace/reaction
first jet and its pullback under the interval-13 seam embedding**, in the
same frame as the child rows. Equivalently, supply the owner-bound 7x73
matrix `[Ep Eq]`, including normal, measure and dynamic-momentum-rate terms.
The existing child output derivatives do not determine this matrix. Neither
do fixed external labels or a positive branch gap specify its entries.

No such realized seven-row packet was identified in the inspected sources.
Assigning it zero, copying the child derivative, using a scalar spectral
DtN block as a substitute, or selecting an embedding by convenience would
supply an unsupported physical relation. Consequently the **numerical
environment response, full 66D tangent comparison and Layer-C rebinding
remain open**. This is not a tangent-mismatch or decay conclusion.

Artifacts: `artifacts/flagship_integration/gate7_environment_seam_20260927/`.
Reproducer: `scripts/compile_n12_gate7_environment_seam_pullback.py`.
Focused tests: `tests/test_moving_seam_response.py`.
Synthetic tests are algebra controls only, never N12 environment evidence.

Validation: 23 tests pass across the new test file and the two previous
coupled-center/interface test files, with `--noconftest`. The new report and
array packet reproduce byte-identically in independent compilation runs.

All frozen tolerances and prior physical certificates are retained.
`Gate7_closed=False`; `FULL_BHSM_COMPLETE=False`.
