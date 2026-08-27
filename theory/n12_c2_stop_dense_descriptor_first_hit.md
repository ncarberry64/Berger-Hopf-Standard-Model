# N=12 dense-center descriptor first-hit certificate

Status: `STORED_CENTER_FIRST_HIT_CERTIFIED; EXACT_HISTORY_TRANSFER_OPEN`.

The retained high-order stop center stores, on every fixed action substep,
the native seventh-degree DOP853 dense polynomial for the augmented state.
The scalar component is the already retained signed selected descriptor
`s`; no event function or selector is added.

`scripts/audit_n12_c2_stop_dense_descriptor_first_hit.py` converts every
binary64 input coefficient to an exact rational number and converts the
resulting power polynomial to Bernstein form.  Recursive Bernstein range
inclusion proves:

1. every complete segment before the terminal segment has `s>0`;
2. the terminal polynomial has `ds/dtheta<0` throughout its full unit
   fraction interval;
3. exact rational bisection encloses its unique zero between a positive left
   value and a negative right value.

For the retained half-action center there are 184 complete preterminal
segments.  The terminal derivative Bernstein upper bound is
`-1.3991710865594509e-11`, and the exact rational root fraction is centered
at `0.6103987818808413`.  Floating evaluation of the dense polynomial had
placed that fraction only `1.9182094228018606e-14` higher; this is a numerical
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
