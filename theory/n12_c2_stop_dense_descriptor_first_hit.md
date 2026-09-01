# N=12 dense-center descriptor first-hit certificate

Status: `STORED_CENTER_FIRST_HIT_CERTIFIED; EXACT_HISTORY_TRANSFER_OPEN`.

The retained high-order stop center stores, on every fixed action substep,
the native seventh-degree DOP853 dense polynomial for the augmented state.
The scalar component is the already retained signed selected descriptor
`s`; no event function or selector is added.

The selected-center replay wrapper
`scripts/replay_n12_gate7_quarter_step_common_frame_operands.py` invokes
`scripts/audit_n12_c2_stop_dense_descriptor_first_hit.py` with the explicit
quarter-step center.  The first-hit implementation converts every
binary64 input coefficient to an exact rational number and converts the
resulting power polynomial to Bernstein form.  Recursive Bernstein range
inclusion proves:

1. every complete segment before the terminal segment has `s>0`;
2. the terminal polynomial has `ds/dtheta<0` throughout its full unit
   fraction interval;
3. exact rational bisection encloses its unique zero between a positive left
   value and a negative right value.

For the selected quarter-action center there are 369 complete preterminal
segments.  The terminal derivative Bernstein upper bound is
`-7.0741157363388825e-12`, and the exact rational root fraction is centered
at `0.2205569616025703`.  Floating evaluation of the dense polynomial had
placed that fraction only `2.6566836038711177e-14` higher; this is a numerical
evaluation effect and does not change the center history.

This is an exact algebraic statement about the stored numerical center, not
an existence theorem for an exact retained-action orbit.  Promotion requires
the correlated defect--Krawczyk enclosure to transfer positivity outside a
terminal interval and an interval Newton argument to transfer the unique
descending zero inside it.  Initial reset positivity remains owned by the
already certified positive-duration reset theorem and is not reopened.

Thus the former point-sampling ambiguity in the center's terminal event is
closed.  The remaining Gate-7 obligation is precisely the global shadowing
radius and its domain-margin transfer; universal terminal recurrence is not
required.
