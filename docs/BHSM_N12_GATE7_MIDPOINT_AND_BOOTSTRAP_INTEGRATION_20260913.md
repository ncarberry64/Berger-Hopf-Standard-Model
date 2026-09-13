# Paired midpoint and endpoint bootstrap integration — 2026-09-13

The previous paired local width attribution identified the midpoint center
action as the dominant remaining term in interval 13, trial column 14.
At the same worst output row 73, it contributed radii 59.4584 and 59.5949
against total left/right radii 65.6306 and 63.9145. Endpoint uncertainty
contributed 6.17219 and 4.31964; the original center-shift term contributed
only about 1.6e-6 and 1.1e-6. This motivated the midpoint mixed-variation
calculation. These are interval-width contributions, not measured variation.

| Quantity | Previous maximum radius | Selected maximum radius | Coordinates tightened |
| --- | ---: | ---: | ---: |
| Midpoint center action, left | 1.0351495 | 0.319854856 | 99/99 |
| Midpoint center action, right | 1.03810714 | 0.320674133 | 99/99 |
| Local DL, midpoint refinement | 65.6305919 | 58.1556063 | 74/74 |
| Local DR, midpoint refinement | 63.914549 | 56.4225453 | 74/74 |
| Endpoint seed bootstrap, left | 0.0931377782 | 0.058850968 | 99/99 |
| Endpoint seed bootstrap, right | 0.0632021948 | 0.0406230898 | 99/99 |
| Local DL column | 58.1556064 | 55.9396006 | 74/74 |
| Local DR column | 56.4225453 | 54.9098867 | 74/74 |

The midpoint calculation uses the original exact center direction w0 and all
249 directions of the unchanged actual midpoint domain, including both
longitudinal intervals, both transverse Euclidean groups and the full box
remainder. It retains all seven original bordered solves, scalar contractions
and coupled mixed normalization. The same-family eigenpair and physical-value
certificates establish smoothness for the segment mean-value argument.
The final derivative bound retains the complete verified anchor uncertainty.

The local integration replaces only the midpoint center-action enclosure in
the existing preconditioned split formula. The original w0, full midpoint
first derivative, improved endpoint action and complete center-shift remainder
are retained. That local integration evaluates no new action derivatives.
All prior bounds remain available as candidates and comparison evidence.

The paired endpoint mean-value line and response variations also seed one
additional complete 75-direction endpoint mixed calculation. It preserves the
original scalar contractions, auxiliary line border and physical K response
coordinates. A second local integration combines those paired endpoint bounds
with the paired midpoint mean-value actions. The earlier local result remains
as comparison evidence.

Both midpoint sides, both endpoint bootstrap calculations and both local
integrations independently reproduce with
byte-identical records and data in fresh processes. The companion JSON records
all record/data/receipt hashes and exact LIVE source hashes. These are numerical
enclosures for one local frozen trial column, not experimental data or complete
physical predictions. Full trial coverage, moving-frame terms, physical
quotient, full-path contraction, Gate 7 and BHSM completion remain open.

## Reproduction

The saved attribution producer is
scripts/diagnose_n12_gate7_mean_value_local_term_attribution.py. Its paired run
used the byte-identical path tmp/attribute_mean_value_local_20260913.py,
which is recorded in the evidence binding; restore that path for exact record
reproduction. It reuses the paired inputs and evaluates no new action derivatives.

Run scripts/certify_n12_gate7_midpoint_center_mean_value_derivative.py with
--interval 13 --column 14, separately for --side left and --side right,
--primal-pair tmp/bhsm_midpoint13_direct_primal_pair_20260913/value and
--evidence-root tmp/bhsm_split_directed_trial13_pair_20260913. Require independent
first/repeat agreement before emitting each receipt or consuming the result.

Run scripts/certify_n12_gate7_endpoint_midpoint_mean_value_local_integration.py
with the same interval/column and split evidence root. Use the paired endpoint
mean-value root tmp/bhsm_endpoint_trial_mean_value_pair_20260913,
previous-pair tmp/bhsm_mean_value_trial_local_pair_20260913/value, and the new
midpoint-left-pair and midpoint-right-pair paths recorded in the companion JSON.
Use distinct fresh-process first/repeat outputs and compare record/data bytes.

The endpoint bootstrap producer is
scripts/certify_n12_gate7_trial_mean_value_seed_bootstrap.py, with the original
side-specific primal pair and directed evidence root used by the endpoint
mean-value calculation, plus --bootstrap-pair pointing to its paired original
mean-value side. The final local producer is
scripts/certify_n12_gate7_bootstrap_endpoint_midpoint_local_integration.py.
It consumes --endpoint-left-pair and --endpoint-right-pair from the new
bootstrap pairs, the same midpoint pairs, and --previous-pair pointing to the
first midpoint-refined local pair. Exact paths are in the companion JSON.

The LIVE source bytes are bound to immutable evidence. Git normalization does
not replace those bytes; exact reproduction requires the recorded sources and
prerequisite bindings. The existing Museum scalar certificate and frozen
prediction files remain unchanged.


## Fixed output projection probe

A separate paired saved-data calculation applies the fixed output map before
shared scalar products and normalization. It retains the original unprojected
physical norm and all 249 mixed columns. All projected point columns remain
contained. No new action derivatives are evaluated.

| Projected midpoint center-action radius | Previous | Selected |
| --- | ---: | ---: |
| Left | 311.900512695 | 311.889676571 |
| Right | 312.617422104 | 312.606554985 |

This tightens every output coordinate but reduces the maximum radius by only
about 0.0035%. It is a recorded limitation of this output-reordering route,
not an additional material local-operator improvement. Further refinement of
this route is not justified by this result. The local table above retains the
paired integration before this separate projection probe.

Three focused tests pass: exact cancellation on an entire descriptor interval,
a nonzero projected second derivative against its closed-form expression, and
rejection of incomplete projection dimensions. Both real-data sides reproduce
byte-for-byte in fresh processes. Run the projection producer with the original
midpoint primal pair and each paired midpoint mixed-jet source; exact paths and
hashes are recorded in the companion artifact.
