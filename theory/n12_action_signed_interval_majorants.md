# N=12 signed and interval retained-action mixed evaluator

Gate 7 requires cancellations to be retained before norms.  The general
retained-action majorant previously exposed only scalar absolute mixed bounds,
which is insufficient for the selected-line/source and reverse-adjoint
pairings.

The isolated evaluator adds two reproducible modes while leaving the retained
action formula unchanged:

- `exact_signed_output_index` keeps one vector-valued mixed leg signed at a
  fixed state and returns all its output components together;
- `interval_signed_output_index` propagates directed floating-point intervals
  for the same output leg, with explicit state and direction boxes.

All subset product rules are evaluated before an output norm.  The vector
mode agrees column-by-column with independent scalar evaluations, and the
directed interval mode encloses exact signed samples.  The two modes are
mutually exclusive.  This is certificate machinery, not an action change,
new source, selector, scale, endpoint, or physical assumption.
