# Frozen-ray environmental boundary test: HE 0435

Re-evaluate the archived R1 cored-star-plus-group nonlinear solution
for the two published group centroids. Export joint minus isolated
scalar deflection on all four observed image coordinates and the
apparent G1 center. Overlay that difference on the previously
calibrated ordinary round-plus-fixed-tide map, with the same G1
propagation and center subtraction. Do not adjust the primary,
group, G1, masses, coordinates, or strength using image D.

At 0.8 Mpc LOS half length the HE 0435 D–A source discrepancy:
* Nominal group: 21.6710 mas before the overlay, 21.6688 mas
  after. The 2.34 µas vector points mostly toward closure.
* Nearer group center: 19.9677 mas before, 19.9705 mas after.
  The 4.23 µas vector points partly away from closure.

Changing grid, domain, or LOS length preserves the qualitative sign
and shortfall. Under each tested geometry the residual-to-correction
norm ratio exceeds 4,000. Treating the correction as a fixed vector,
even arbitrary scalar rescaling cannot remove the perpendicular
miss (roughly 7.7–8.0 mas and 14.7–14.8 mas, respectively). This
is a local vector diagnostic, not an actual huge-coupling solve.
The direction of the residual *and* of the correction can depend
on the input group geometry. No physical time delay is claimed.

The independent archived sharp-seam model still does not supply
the missing interaction: at matched traces, varying a pure
difference penalty along a common displacement with fixed
transport and geometry gives zero. That says nothing about varying
the geometry/transport jointly; the physical shared-mode stress
and its normalization are the missing input, not the lensing
projection itself. R1 is a configured scalar control, not a
substitute for that native BHSM term.

Reproduce: `OPENBLAS_NUM_THREADS=1 python -W error boundary_frozen_ray_test.py`.
