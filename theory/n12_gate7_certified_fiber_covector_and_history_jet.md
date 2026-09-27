# Certified fiber covector and the next history-jet solve

Base: `eef4149c7d0df292eb40731df2e35490dfafa18c`, branch
`theory/gate7-66d-reduced-adjoint-integration`.

**NUMERICALLY CERTIFIED:** the full signed 98-component Euler--Dirac
Rayleigh covector at node 13, and a uniform enclosure over its already
certified affine state domain. **OPEN:** the fiber-consistent shooting center
and complete first-order physical history jet. No old tangent is reclassified
as a newly certified physical tangent.

## New reusable derivative

Use the existing normalized, positively oriented, selected index-24 eigenpair
witness of the raw 61-dimensional Euler--Dirac Hessian. For weighted action
state directions v, the derivative is

```
g13(v) = D3 A_N12(Y13)[(0,psi13),(0,psi13),W_state^-1 v].
```

Two new 98-output third-action contractions evaluate this formula: one at
exactly the stored binary64 state with its certified eigenline ball, and one
on the saved affine state's outer hull with the saved uniform eigenline box.
All signed coefficients and their rational radii are saved before norms.
The raw action uses the existing 96-point retained model and Arb512 machinery;
the small radii describe that finite action and its frozen coefficients.
They are not discretization or continuum-error estimates.

No Hessian, eigenpair, Stage-B, or shooting producer is rerun. Order-zero
affine geometry supplies the contraction maps. The point run took seconds.

| Quantity | Result |
| --- | ---: |
| Point covector radius, Frobenius upper | 7.667570142e-124 |
| Difference from old diagnostic covector, Frobenius upper | 7.529108433e-13 |
| Point derivative in action coordinate 86 (zero-based) | 2.263864399624304e-6 |
| Radius of that point derivative | 1.155498776e-124 |
| Uniform affine-domain coordinate-86 radius | 1.537365843e-8 |
| Uniform affine-domain covector radius, Frobenius upper | 1.061360088e-7 |
| Point Dlambda[Psi] | 6.649840684424045e-11 |
| Corrected fiber defect on old left-history columns, proof norm upper | 9.663116622e-7 |
| Fiber-row residual on previous owner-consistent left columns, proof norm upper | 1.514093477e-7 |

The uniform coordinate-86 interval is strictly positive; its lower endpoint
exceeds 2e-6. This is a coordinate transversality witness, not a declaration
that coordinate 86 alone is an admissible physical/reaction motion.
The point Dlambda[Psi] enclosure is contained in the independently frozen
uniform contraction. This checks the action/raw-state scaling convention.
The uniform covector contains the complete new point enclosure.

The last two rows apply the new point covector to the SAME saved columns and
retain the 1e-7 proof conversion. They do not propagate those columns onto a
corrected history. In particular, the 1.51409e-7 result shows why replacing the
previous diagnostic derivative is worthwhile, without resolving the physical
tangent comparison by itself. The historical tolerance remains unchanged.

## Fiber graph point versus a common shooting center

At the unchanged Y13, define s_star to be the SAME certified selected
eigenvalue object, approximately `4.273927314680651e-10`. Then
`lambda_event(Y13)-s_star=0` by the graph identity, preserving correlation.
This does not assert that (Y13,s_star) solves the shooting, constraint and
boundary equations. No frozen center file is altered.

The saved endpoint-13 derivative domain has descriptor radius
`6.017800981634328e-15`, about the old value `4.274863922115819e-10`.
At this fixed state, lambda(Y13) lies below that descriptor domain by at least
`8.764294253522779e-14`; its center displacement is at least
`15.5639483264` descriptor radii. Hence a simple s relabel cannot reuse that
saved full-rate derivative packet unchanged. This is not a claim that the
affine state tube has no fiber-consistent state.

The new uniform g depends on Y, not on an independent s; it remains usable on
the certified affine state domain. A corrected history must still be proved
to belong to that domain, or supplied with its own bound domain.

At a fixed physical fiber label, ds/dxi=0 and g J=0 belongs inside the
differentiated solve. The old arc-parameterized reset-plus-flow family is not
silently relabelled as that fixed-label parameter lift. No new physical
descriptor column is introduced.

## Saved-operand search and exact next object

The repository, the crossing-correction and singular-reset evidence
worktrees, the oriented-event worktree's artifact location, and relevant
Downloads names were checked before either new contraction.

* The historical signed Dlambda packet is for C2 node 1214. Its state differs
  from Gate-7 node 13 by about 3.249978310 action units. Its small radius cannot
  be transferred without a center-transfer certificate.
* The 48-node/72-parameter first-hit jet explicitly certifies an affine
  carrier; its nonlinear exact-family transfer remains OPEN. The copy in the
  singular-reset worktree is byte-identical.
* Endpoint first-variation packets retain the projected selected-line solve,
  but not the complete unprojected Rayleigh slope. In
  `certify_n12_gate7_accepted_replay_center_outward_74d.py:1183`, the slope is
  computed separately and projected out of the eigenline RHS. Thus the 62nd
  line row is an auxiliary border, not Dlambda. A focused test exhibits two
  H' matrices with different Rayleigh slopes and identical line/border solves.
* The new point/tube covectors now fill that export gap for the state domains
  described above. The prerequisite-audit packet records the saved inputs
  before this new contraction; it is not the final derivative status.

The next single owner is the **fiber-constrained interval-13 center/Jacobian
packet**: a validated common shooting/constraint/interface/fiber center,
with the fixed-label physical parameter lift and the signed Jacobian blocks
bound to that same center. Feed the new g row into that solve; retain its
enclosure and prove the solve's domain inclusion. Then form the signed Schur
history jet there. This is a local task, not a new global producer campaign.

Old-versus-owner angles remain those in the eef4149c checkpoint. Comparisons
to the requested new history tangent (C), its rank/orientation, and certified
projector uncertainties are **not yet available** because C has not been
constructed. Neither equivalence nor genuine physical tangent correction is
adjudicated from the point calculation. No Layer-C rebinding occurs yet.

## Provenance and validation

Reproducers:
`scripts/certify_n12_gate7_point_fiber_covector.py` and
`scripts/audit_n12_gate7_history_jet_prerequisites.py`.
All consumed source hashes, exact interval endpoints, and preserved claim
flags are in the reports.

New covector packet: `artifacts/flagship_integration/gate7_fiber_covector_20260927/`.

* report SHA256: `F2D1D8388041B891469400B652806CC3FF98EB152EF865FC93B02420D7634C43`
* arrays SHA256: `7564BA078CDA38567E0DEAA7406D3A4B920D96AE22DB28F4BF71D175F9F74DE8`

Saved-input prerequisite packet:
`artifacts/flagship_integration/gate7_history_jet_prerequisites_20260927/`.
Report SHA256: `6DCFD5D7D6532AD72DFB7046498BEDB1B3F18623CF87A737667D803B59B61E8D`.

Both packets reproduce byte-identically in independent fresh processes.
The covector, prerequisites, reduced-tangent and descriptor-owner suites pass
**16 tests** with `python -m pytest --noconftest`. Initial source comparison
encountered Windows line-ending differences; exact external hashes were
retained and normalized source text equality verified before proceeding.

`Gate7_closed=False`; `FULL_BHSM_COMPLETE=False`.
`SURFACE_CORE_COMPACTIFICATION=CONDITIONAL`. No tolerance was relaxed and no
nonlinear history campaign or numerical surface/core continuation was run.
