# Rate-consistent ambient block predictor

This is the standard 98-dimensional block-bidiagonal Hermite--Simpson Newton
recurrence applied to the repaired endpoint-rate-consistent source.  The
endpoint and midpoint graph Jacobians are evaluated on the same unchanged
first-HS endpoint center.  The predictor is only linear numerical data.

Its nonlinear replay must project and recenter every endpoint and then
reevaluate the endpoint field rate at the recentered descriptor.  Retaining a
pre-recenter rate would reproduce the superseded provenance defect.
