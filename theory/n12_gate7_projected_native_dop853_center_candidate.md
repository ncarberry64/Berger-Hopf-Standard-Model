# N12 Gate-7 projected native DOP853 center candidate

The native fixed-step DOP853 center is the retained numerical integration of
the denominator-free action field.  Its seventh-order dense polynomial has a
small smooth action-constraint drift, unlike the much larger defect introduced
by the later cubic-Hermite reconstruction.

Retain every native quarter-action node through `92.25` and the native dense
`s=0` endpoint.  At each state, form the direct 25-row action constraint
differential and take one minimum action-norm Newton step.  This creates a
discrete constraint-accurate candidate without rerunning the 6,015 action-field
evaluations.

Projection is not integration.  The projected nodes are not promoted to a
continuous orbit, and neither the propagated descriptor-fiber identity nor the
old first-hit time is inherited.  Promotion requires an outward collocation or
shadowing theorem for the projected dense path, simultaneous control of
`lambda_24(Y)-s`, and a new terminal first-hit enclosure.

`FULL_BHSM_COMPLETE = FALSE`.
