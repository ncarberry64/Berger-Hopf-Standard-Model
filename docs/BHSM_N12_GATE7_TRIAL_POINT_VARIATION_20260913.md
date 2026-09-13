# Paired trial-action point diagnostics — 2026-09-13

The verified samples and complete point Hessian show small sensitivity at the
anchor and two longitudinal samples. They motivate a uniform mixed-Hessian
mean-value calculation on the actual trial direction. They do not establish
a uniform neighborhood bound or rule out larger variation elsewhere.

## Same-coordinate numerical comparison

All quantities refer to endpoint 13 and frozen trial column 14. The maximum
sample variation and maximum uniform action radius both occur in output row 55.
These are weighted numerical derivative coordinates, not experimental measurements.

| Quantity | Numerical value, approximately |
| --- | ---: |
| Current uniform action radius, row 55 | 0.600448 |
| Absolute point change at longitudinal parameter -3/4 | 7.457443599780067e-6 |
| Absolute point change at longitudinal parameter +3/4 | 7.457472299271703e-6 |
| Point-linearized longitudinal support, full radius | 9.943277266004833e-6 |
| Point-linearized transverse Euclidean support | 1.6834865205917522e-5 |
| Total point-linearized support | 2.6778142471922355e-5 |
| Largest sampled discrepancy from the point linearization | 1.4349768079234401e-11 |

Every transverse coordinate is zero in the displaced point samples. Transverse
sensitivity is assessed only by the anchor Hessian, through all 74 transverse
axes; it has not been sampled throughout the transverse ball. The last row is
a discrepancy at the sampled points, not a neighborhood remainder estimate.
Consequently the disparity with the current radius cannot be advertised as a
proved factor of overestimation over the whole tube.

## Verified scope

Each point sample retains construction rounding in its raw state and descriptor.
Its normalized index-24 eigenpair and all three original physical linear solves
are verified. The eigenpair and response belong to the exact paired primal family,
and the paired uniform trial action contains the complete computed derivative.
The derivative at the paired anchor retains its full uncertainty in every
difference. The proven coordinate difference implies a necessary radius lower
bound of about 3.72872e-6 for an interval covering that anchor/sample pair.
A lower bound from two points is not a uniform upper bound.

The complete existing paired point Hessian is consumed only after matching the
exact anchor, weights, reference, and original graph. Its complete 99-row upper
triangle inventory, records, data, and fresh-worker receipt are verified.
Contract it against the actual frozen trial direction and all 75 scaled tube
directions. This evaluates no new action derivatives. The longitudinal absolute
coefficient plus the transverse Euclidean support is a POINT LINEARIZATION
quantity; no uniform Hessian or neighborhood remainder is asserted.

Both point samples and the point-Hessian contraction independently reproduce
with byte-identical records and data. Three focused difference-bound tests pass,
including overlap, incompatible shapes, and conservative outward rounding.
The [companion report](../artifacts/flagship_integration/BHSM_N12_GATE7_TRIAL_POINT_VARIATION_20260913.json)
contains all source, record, data, and receipt hashes.

## Reproduction and next step

Point evidence is under `tmp/bhsm_endpoint13_trial_point_variation_pair_20260913`
with separate minus/plus first/repeat pairs. The producer is
`scripts/diagnose_n12_gate7_endpoint_trial_point_variation.py`, using interval 13,
column 14, left side, multipliers -3 and 3, and the unchanged paired primal and
directional evidence roots. Use separate fresh processes and compare record/data
bytes before issuing receipts.

The contraction pair is under
`tmp/bhsm_endpoint13_trial_point_hessian_support_pair_20260913/value`, produced by
`scripts/diagnose_n12_gate7_trial_point_hessian_support.py` with the paired sample
root and identical primal pair. It also requires the existing complete endpoint
13 physical Hessian and its original immutable baseline dependencies.

Proceed to a complete UNIFORM mixed-variation calculation against all 75 tube
directions, integrating the Hessian enclosure to bound the same trial derivative.
Retain the original primal pair, lambda, fixed frames, radii, and action. Do not
replace the uniform calculation with these point values or scale to all 74 trial
columns before the bounded test supplies evidence of useful improvement.

Physical quotient and moving-frame derivatives, global contraction, Gate7, and
full BHSM completion remain open. No measured data or fitting enters, and no
Museum or manuscript completion status changes for these local diagnostics.
