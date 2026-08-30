# Rate-consistent Hermite--Simpson source

The repaired endpoint state, descriptor, and exact field rate are used to
construct each Hermite--Simpson midpoint.  The exact retained field oracle is
then evaluated directly at all 370 midpoint augmented states.  This produces
the current 99-dimensional nonlinear shooting source.

The earlier source combined a recentered descriptor with a field rate
evaluated before recentering and is superseded.  No reduction claim is inferred
from comparing the repaired and superseded residual magnitudes; the repaired
source is the new baseline for a separately replayed Newton correction.
