# Uniform physical HS local Newton-defect blocks

Require independently reproduced uniform physical derivatives on both complete
endpoint tubes and on the actual HS midpoint outer domain constructed from
those endpoints' paired uniform fields. Each derivative covers all 99 weighted
augmented basis directions, including the descriptor. Point derivatives are
insufficient and are rejected by the producer.

For A=DF(z0), B=DF(z1), M=DF(m), and
m=(z0+z1)/2+h(F(z0)-F(z1))/8, use the original chain rule:

    D0 m = I/2+h A/8,      D1 m = I/2-h B/8,
    D0 r = -I-h A/6-(2h/3) M D0 m,
    D1 r =  I-h B/6-(2h/3) M D1 m.

The joint dependencies between these matrices can be enlarged to independent
interval matrices without invalidating an enclosure. The bound may widen.
The paired midpoint construction ensures that the actual image is covered.

Apply the same frozen frames, left block L and right block R as the existing
finite-history calculation:

    C  = R^-1 T L E0,
    DL = R^-1 T (L-D0 r) E0,
    DR = I-R^-1 T D1 r E1.

The initial endpoint is fixed, so its DL block contributes zero. This is an
explicit boundary condition, not a missing-input default. All other blocks
must be present, finite and independently reproduced.

This construction gives local derivative enclosures for the fixed-coordinate
Newton map. It does not identify a physical quotient, differentiate moving
frames, propagate the complete causal inverse, establish a useful global Z1,
bound higher remainders or close Gate 7. The numerical output must remain
conditional on its bound domains and frozen-coordinate foundation.
