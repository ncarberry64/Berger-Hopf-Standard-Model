# BHSM v16.26: post-basin multirank nonlinear continuation

The v16.25 refreshed KKT has four materially different numerical ranks and
unrestricted direction scales. v16.26 evaluates full, half, quarter, eighth,
and sixteenth steps at each rank against the complete nonlinear residual,
with an exact event-multiplier projection and eta-domain check at every
candidate.

This is a continuation of the same independently solved N=3 orbit. It neither
transplants an old event state nor introduces a surrogate event equation or
an alternative mass/Yukawa normalization.
