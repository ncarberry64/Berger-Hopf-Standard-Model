# N12 parent action sectors and native boundary derivative

Continuation of `fc7cd287` and Norman's unified completion handoff.
Status: **VALIDATED local native derivative; environment seam composition OPEN**.

## Actual retained sectors

The executable N12 action, not a generic environment model, owns the following
terms. We split its algebra before differentiation and retain the original
quadrature, binary64 constants, coordinates and signs.

| Contribution | Retained expression / ownership |
|---|---|
| Spatial gravity | `3 A^3 B^3 N/C [n'(a'+b')+a'^2+b'^2+3a'b']` |
| Intrinsic curvature | `N V (3/A^2+3/B^2)` |
| Cosmological potential | `-N V kappa0/2` |
| Quadratic topographic eta | `-N V localization X_eta/2` |
| Quartic topographic eta | `-N V localization X_eta^4/8` |
| ADM kinetic | `N V ADM/2` |
| Fixed Hopf inertia | `-c_H/I`, with unchanged `c_H=0.25/(2 HOPF_ORBIT_VOLUME^2)` |
| Boundary scalar vacuum | scalar share of `-C_SM N_boundary/R4` |
| Boundary vector vacuum | physical-vector share of the same term |
| Boundary Weyl vacuum | Weyl share of the same term |

Here V=C A^3 B^3 and I is the existing global eta/metric inertia integral.
The last three terms partition the existing vacuum coefficient. The field
counts in `standard_model_zeta_contract` are four real conformal scalars,
twelve physical vectors and 48 complex two-component Weyl fields, giving
`1/60 + 11/10 + 17/20 = 59/30`. Their exact shares of the stored rounded total
are `1/118`, `33/59`, `51/118`. Multiplying that rounded total by these shares
preserves the frozen coefficient; replacing it by a new rational coefficient
would change the numerical action and is not done.

There are no additional independent gauge-field coordinates in this retained
98-state action. Its vector contribution is the retained boundary vacuum
term, with the source contract's longitudinal/ghost cancellation already
applied. This does not assert that all other BHSM scales have this environment.
The ten labels are additive action contributions, not separately positive,
orthogonal, or independently conserved energy sectors.

## New parent-side computation

The state is `center_state[:98]` from the hash-bound
`BHSM_N12_FULL_RESET_ACTION_JACOBIAN.npz`, whose producer explicitly assigns
that half to the event/parent. The last 98 coordinates are the child and were
not substituted for the environment. The new calculation uses the stored
parent point as exact binary64 data lifted to Arb512. It does not claim a
uniform enclosure of the true parent root or the interval-13 seam image.

The original reset role is not a current environment identification.
`n12_finite_terminal_two_sided_interface.md` explicitly swaps the historical
pair for forward chronology: `E1=C_star`, `C2=E_star`. The packet's historical
event point must therefore **not** be adopted as the fixed environment from
its name. `role_scope.json` records this distinction. The native formulas and
point replays remain valid, but their binding to the actual fixed environment
is not established. No closest-state comparison selects that environment.

Each contribution now has its value, 98-vector raw gradient and 98x98 raw
Hessian saved separately. Their signed sum replays the unchanged action:

| Replay | Outward discrepancy upper bound |
|---|---:|
| Value | `5.20141e-151` |
| Gradient | `2.16781e-149` |
| Hessian | `5.75574e-146` |
| Canonical momentum value | `4.65531e-142` |
| Canonical momentum derivative | `4.03816e-134` |
| Common canonical inverse defect | `4.73489e-135` |

All differences enclose zero. These are precision/replay quantities, not
physical stability budgets or replacements for the transfer tolerance.

The three trace and two canonical-momentum derivatives are instantiated as
a **5x98 native parent operator** in weighted action directions. Canonical
momentum is resolved by the same complete-action KKT lift L for every term:

```
K L = target,
DL[u] = -K^-1 DK[u] L,
P_s = L^T g_s,v,
DP_s[u] = DL[u]^T g_s,v + L^T H_s,v* u.
```

The derivative of L is contracted from the full action D3; no dense D3
archive or independent inverse for each sector is constructed. An independent
direct differentiated-lift formula verifies the summed adjoint formula.

Only the ADM term has direct canonical momentum in these coordinates;
the other nine contribution jets are exactly zero in those two rows. Their
force, constraint and geometry effects remain in the coupled problem. In
particular, a velocity-independent boundary vacuum term can have nonzero
boundary force and Hessian. It must not be discarded from dynamic flux.

## Correct sector assembly for an on-shell environment

The companion `sector_on_shell_response.py` retains one common interior
response. For the sector Hessian blocks of a genuinely owned environment
boundary problem,

```
Da = -(sum_s S_s,aa)^-1
       [(sum_s S_s,aq) Dq + (sum_s S_s,aSigma) DSigma],
D Lambda_s = S_s,qq Dq + S_s,qSigma DSigma + S_s,qa Da,
D Lambda_E = sum_s D Lambda_s.
```

Independent sector Schur complements would lose the cross-sector response.
A focused algebra control covers even a singular individual sector with a
regular total interior block. No arbitrary sector weights enter this solve.

## Exact remaining composition

This step advances from formulas alone to native parent coefficients. It does
not identify a native coefficient variation with a physical environmental
input. External state and labels remain fixed: delta e=0.

To turn the saved native five-row operator into the first five rows on the
73-column child/reaction chart requires the **action-owned environment seam
solution/pullback jet** J_E, including sampling, normal/frame/measure changes
and any retained projection remainder. Schematically,

```
R_E,first5 = B_E,native J_E + frame/measure terms.
```

The two dynamic-flux rows additionally require the material-rate terms of
the same environment realization. They cannot be supplied by the radial
flux alone or by the static boundary Hessian. The known rank-two coefficient
of D rho_E remains available from `fc7cd287`.

The 98-state N12 action and fixed-event reset provide native values and
derivatives. They do not specify which displaced-environment field/domain
represents a given interval-13 child/seam motion. A derivative of the raw
action at the parent point is not automatically the derivative of an
on-shell boundary functional. Choosing J_E, an exterior boundary domain,
or the dynamic-flux material jet to make the system close would add data
not supplied by these owners. No such choice is made.

Thus the next exact object is the **N12 parent/environment seam solution
jet at fixed e0 in the existing 73-column chart**, using these native sector
formulas evaluated at its owned realization, not an assumed reset half.
The final 7x73 environment operator, co-moving 66D tangent,
and Layer-C rebinding remain open. This is not a mismatch with an old tangent,
loss of seam protection, or a decay result.

Artifacts: `artifacts/flagship_integration/gate7_parent_sectors_20260927/`.
Producer: `scripts/derive_n12_gate7_parent_sector_jets.py`.
Tests: `tests/test_gate7_parent_sector_jets.py`.
All 29 focused tests pass across this file and the three preceding
moving-seam/coupled-interface/center test files with `--noconftest`.
The complete new report and array packet reproduce byte-identically in
two independent parent-point calculations.
No frozen endpoint, midpoint, Stage-B or local closure calculation was rerun.
The new work is a local parent-point action/contracted-D3 evaluation only.

`Gate7_closed=False`; `FULL_BHSM_COMPLETE=False`. Tolerances and predictions
are unchanged; N12 is one scale-specific enclosure realization.
