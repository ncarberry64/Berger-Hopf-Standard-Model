# BHSM v18.69 N=3 child-fiber ownership audit

## Result

`VALIDATED` at the accepted v18.68 frontier. The unchanged 14-row complete-child
map has rank 14 and nullity 12 at raw Jacobian steps `1e-4`, `2e-4`, and
`4e-4`. The largest measured principal angle from the reference nullspace is
`1.290323208981357` degrees. This supports the finite-dimensional local
surjectivity result: the 14 child equalities do not generically obstruct a
sufficiently small event displacement.

The 26 variables were put in the already-owned H6-coordinate, H5-rate, and
H6-multiplier Sobolev amplitudes. Inside the resulting nullspace, the basis
was rotated only by the declared ownership projector: 20 gauge-fixed Cauchy
variables versus three lapse and three shift coefficients. It was not
rotated or selected using an observable.

The ownership result is:

- six directions are exactly Cauchy in the action-owned coordinates and are
  classified `GENUINE_PHYSICAL_CAUCHY_FREEDOM`;
- six are `UNRESOLVED_CAUCHY_MULTIPLIER_MIXTURE`;
- no direction is classified as a pure lapse/shift-owned direction;
- no direction is classified as gauge or chart freedom, because the retained
  26-variable formulation supplies no such generator after the monotone
  `f=chi` gauge and time/radial diffeomorphism quotient.

## Exact fiber check

Both signs of all 12 dimensionless directions were perturbed and reprojected
onto the same 14 equations. Across those 24 states, the worst retained rows
were:

- trace: `6.2187e-11`;
- seven constraints: `2.04421e-10`;
- canonical momentum: `1.9221358e-8`;
- dynamic flux: `4.332445308e-6`.

Every state retained positive eta and successful one-step projected
persistence with nonzero relative evolution. These checks add no equation to
the 376-variable global KKT system and do not modify the independent two-scale
flux promotion gate.

## Ownership conclusion

The centered retained-action response reaches
`1.134104041789e-3` per unit dimensionless fiber amplitude, and the eta response
reaches `6.1650518e-7`. Thus the equality fiber is not an observable-invariant
gauge/chart fiber. The result does **not** license optimizing an observable
over the 12 directions and does not provide a new selector.

`OPEN_ACTION_DERIVED_CHILD_FIBER_SELECTION_OR_UNIQUE_ACTUALIZATION_OWNER`
remains the honest downstream ownership question. It does not block local
event continuation because fresh complete children remain solvable and
persistent. The direct N=3 dependency therefore returns to exact admissible
descent of the unchanged 376-row residual from v18.68.

Reproduce the full measurement with:

```bash
python scripts/materialize_aether_n3_child_fiber_ownership_v18_69.py
```
