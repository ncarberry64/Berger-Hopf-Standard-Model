# Interval 14: exact source-term reproduction repair

The fourteen affected terms are `response_28_source`, `response_30_source`,
`response_33_source`, `response_36_source`, `response_38_source`,
`response_41_source`, `response_44_source`, `response_46_source`,
`response_49_source`, `response_52_source`, `response_54_source`,
`response_57_source`, `response_59_source`, and `response_61_source`.

The complete first/repeat values are in
`tmp/gate7_vector_20260919/interval14_midpoint14_exact_14_term_inventory.json`.
For each term it lists all 251 Taylor-model ball slots, their exact rational
midpoints/radii and lower/upper endpoints, and the differing slot IDs.
No formatted decimal comparison is used.

Two fresh serial processes reconstructed only these fourteen action
source-Hessian contractions from the original operand archives. For every
term, the complete reconstructed state, both contraction legs, maps, domain,
precision, implementation sources, and raw operand archives were hashed.
All fourteen input payloads and output records match byte-for-byte between
the serial runs. Every resulting ball also equals the original first-run
ball exactly. The output directories are `interval14_midpoint14_raw_serial_first`
and `interval14_midpoint14_raw_serial_repeat` under the same work directory.

The discrepancy enters at the source-contraction cache boundary, before
the response solve, physical normalization, or output adjoint. The original
prefetch job overlapped the producer; its receipt's `response_61_source`
digest differs from the subsequently saved term. Cached-ball reconstruction
adds outward radius rounding. Treating all later rows as cache reads thus
does not reproduce the original mixed execution.

The dependent response accumulation was rebuilt without new action
contractions. Seven further response rows required recovery of their
in-memory/cache-read schedule. This recovery enumerates the eight rigorous
serialization variants of each fixed three-term expression, records every
exact match, and selects the lowest matching mask. It changes no operand,
physical parameter, equation, or domain. This is a reconstructed execution
schedule, not a claim that the original run recorded that schedule.
The schedule is then fixed and applied to the second independently computed
input set, without another search. Both repaired accumulations reproduce
the original complete base record byte-for-byte.

`interval14_midpoint14_exact_raw_repair_v2/repair_receipt.json` records the
input/output hashes, recovered schedule, implementation hashes, and repaired
records. Original evidence is unchanged; the repair is an overlay containing
fourteen source records and their dependent base record. Exact restoration
checks both midpoint and radius equality after construction. No numerical
tolerance, outward certificate coarsening, domain shrinking, or interval-13
recomputation was used.

The subsequent directional/scalar reproduction chain completed using this
verified overlay. The interval-14 entry and transport are now frozen and
booked exactly once in the current ledger. See
`docs/GATE7_CURRENT_REPRODUCTION.md` and the packaged frozen history ledger
for the current state. This source-repair account is historical; it does not
reopen interval 14. The global physical remainder and Gate 7 remain open.
