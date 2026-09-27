# Current-center C2 coefficient transport checkpoint

Base commit: `9f2199be06c930d1289a6dde8f971f0b759c3c1e` on
`theory/gate7-66d-reduced-adjoint-integration`.

The current node-13 C2 flow has been recentered and a finite prefix with its
73 first variations has been enclosed. The requested complete incoming/C2
history response and `R_history_7x73` are **not yet computed**. This is a
transport checkpoint, not promotion of the local seven-row derivative.

## What was actually recentered

The initial state is `gate7_coupled_fiber_center_20260927/neighborhood/arrays.npz`
`left_state_domain`, the certified neighborhood used by the frozen launch
chart. It is not the historical 1,222-center path, nor just a coefficient
midpoint. The parameter order remains 72 inherited reset labels followed by
one current flow phase. The descriptor has physical units.

A fresh action/field evaluation encloses a state-action coordinate box of
radius `2^-65` and a descriptor box of radius `2^-100`. This is a **new**
flow-box evaluation; no frozen endpoint, local shooting proof, Stage-B
campaign, or historical interval-action producer is rerun.

The eigenpair proposal is refined on the Hessian midpoint, then verified
on the entire new Hessian box. A normalized eigenpair inclusion, positive
reference orientation, and two Arb inertia checks certify index 24. The
floating gap returned by the proposal is not used as a uniform certificate.
The bordered hard response and the first field derivative are enclosed by
the existing action machinery.

The first, wider attempted box admitted the normalized eigenpair but had a
descriptor-speed interval containing zero. Tightening the new box gives
`ds/dr = [8.3e-11 +/- 5.88e-13] > 0`. Thus that earlier failed clock test is
enclosure loss; it is not evidence of transversality loss or de-encapsulation.

## Physical proper time and moving duration

For normalized action arc `r`, the existing cancelled-field identity gives

```
q = d tau/dr = N*s/||G||
  = N*F_q0/(w_q0*qdot0),
Dq = q DlogN + N/(w_q0*qdot0) D F_q0
     - q/qdot0 Dqdot0.
```

The second expression uses `G_q0=s*w_q0*qdot0`; it is valid here because
`qdot0` is bounded away from zero. It does not divide by `ds/dr`.
The new uniform clock is

`q = 8.56991320843096e-7 +/- 6.910e-15 > 0`.

For the vector field enclosure `F(B)` and its full first derivative `A(B)`,
the stored exact domain radii define a weighted infinity norm. The new
Picard inclusion proves the entire prefix stays in the field box. Its
variation enclosure retains the signed common product

```
J(t) in J0 + t A(B) J0 + E(t),
|E_ij(t)| <= r_i ||J0[:,j]/r||_infinity (L t)^2 exp(L t)/2.
```

The remainder follows by integrating `A(y(u))(J(u)-J0)` and Gronwall's
inequality. There are no 73 separate action/history integrations. For each
fixed arc cell the duration and its first jet are enclosed as

```
h_i = integral_cell q(y(r)) dr,
D h_i = integral_cell Dq(y(r)) J(r) dr.
```

The duration derivative is retained, not set to zero. Its current bound is
broad: the largest clock-first-jet midpoint is about `4.80225e-6`, while its
largest radius is about `38.0778`. Every duration-jet component currently
contains zero. These are valid enclosures, but their signs are unresolved;
no claim of a sharp signed remainder follows from them.

## Proof-core choice and what the number 1,222 means

The new arc prefix is `[0,2^-69]`. The old relative duration weights are
used only to subdivide that prefix into 1,222 cells. Its proper duration is

`1.4517997685301667e-27 +/- 1.171e-35`.

This is comparable to the old total proper-duration enclosure
`[1.08232011e-27,1.49449957e-27]`. It is **not** the history obtained by
preserving the old descriptor increments. The choice is a new Friedrichs
proof-core truncation, not a physical endpoint, amplitude selection, or
new physical scale. The existing finite-core owner explicitly distinguishes
this truncation from a physical endpoint. This choice was stated during the
work; the alternative descriptor-increment continuation is not completed.

The maximum domain excursion ratio is below `0.178`, and
`L * 2^-69 = 6.341188929630227e-12 < 1`.

| Quantity | Result |
|---|---:|
| Historical certificates inherited unchanged at the new base | 0 |
| Historical interval actions rerun | 0 |
| New certified flow boxes used by the prefix | 1 |
| New mesh cells covered by that box | 1,222 |
| Shared first-variation columns | 73 |
| Independent full-history forward solves | 0 |

The current/historical radius difference remains a base-point shift under
the same coefficient law. No channel or grading has been changed. The
remaining scalar/gauge potentials and Weyl superpotentials follow the
already-certified functions `c exp(-2x)` and `chi*mu exp(-x)`.

## Existing transfer and cotangent law

An Arb adapter implements the exact algebra in
`aether_forward_c2_weyl_riccati::_map`. It differentiates each update with
respect to terminal load, midpoint log radius and duration, then applies
one backward coefficient/duration cotangent to all 73 columns. The
independent forward composition and reverse contraction overlap in every
component. The report records their absolute interval residuals; overlap
is not presented as a small sharp numerical defect.

Tests compare local derivatives with the existing independent mpmath law
at 110 decimal digits for scalar and both product-Dirac signs. Separate
tests compare the flow/variation enclosure against the exact nonlinear
flow `y'=y^2` and verify rejection when the flow leaves its domain.

The four new `z=-1` checks are HS `m=1`, transverse gauge `m=2`, and Weyl
`n=0` with both factorization signs. They are checks of the existing
**piecewise-midpoint Riccati model**, not the full graded heat functional.
They do not certify a continuum interpolation remainder or double the
physical Weyl multiplicity. Their leading conormal magnitude is about
`6.888e26`; uncertainty in the duration jets prevents a sharp signed
pullback. The historical `1064 -> 1222` composition and cotangent evidence
is hash-bound and preserved, not replayed at its old base.

## Exact unfinished composition

The incoming formation arm is not the C2-forward prefix with its time
direction reversed. Its owner remains the ordered formation Calderon
block `M_f=M11` after the external zero Dirichlet trace is imposed. The
existing `assemble_ae2_one_seam_descriptor` takes formation and child paths
as separate inputs and requires their reset-frame seam match. The old
incoming amplitude packet explicitly does not select a positive member;
its terminal radius and negative-Delta domain belong to the old base.
Neither that domain nor the old `T~a*lambda0^2` terminal germ has been
relabelled as current-center data.

The next missing numerical object is the **current formation-side
state/history and its first pullback into the common reset frame for this
child realization**, retaining its owned amplitude dependence. It must be
composed with the current C2 path, the `U_R` pullback and active contact
jets before contraction against the seven physical graded outputs. The
existing law has not been declared absent, and no new environment law or
amplitude selector has been introduced.

Also remaining are tightening the duration-jet enclosure and binding the
continuous coefficient/form remainder where required. Only then can the
complete projected adjoint produce `R_history_7x73`. Row norms, completed
rank, and largest seven-row correction are stored as null, not zero.
The local response is not promoted, the co-moving 66D solve is not run,
and Layer C is not rebound in this checkpoint.

## Reproduction

Producers:

```
python scripts/recenter_n12_gate7_current_history_box.py --out <new_box>
python scripts/transport_n12_gate7_current_coefficient_history.py --box <box> --out <new_core>
```

Packet: `artifacts/flagship_integration/gate7_current_history_20260927/`.
Both independent flow-box evaluations and both independent history
compilations reproduce byte-identical arrays and reports. Four hashes
are recorded in `reproduction.json`. Frozen source hashes are retained.
The focused current-center, boundary-owner, shared-port and new transport
suite passes **66 tests** with `pytest --noconftest`; the exact command is
stored in `validation.json`.

No tolerance is relaxed. `Gate7_closed=False`; `FULL_BHSM_COMPLETE=False`.
