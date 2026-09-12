# Normalize the same physical field with its proved coupled identities

The paired endpoint eigenpair solves (H*p-lambda*p,(p^T*p-1)/2)=0, so p^T*p=1.
The paired physical bordered response solves

    [H-lambda*I,p; p^T,0] * (h,b) = (rhs,0),

so p^T*h=0 for the same actual eigenpair and response. These are consequences of
the already certified coupled systems, not assumptions about arbitrary vectors
inside their component boxes. They do not introduce a physical quotient.

The retained field has

    G = (s*configuration, W*(b*p+s*h)),
    delta = b*cpsi+s*remainder.

When the enclosure of b has a verified nonzero sign, put t=s/b and factor out
b. Then G=b*Gtilde, delta=b*(cpsi+t*remainder), and normalization cancels |b|:

    F = sign(b)*(Gtilde,cpsi+t*remainder)/||Gtilde||.

Retain sign(b), including for negative b. Factoring is not justified if its
enclosure crosses zero. The original unrefined value certificate remains intact.

The two proved identities give the exact squared norm

    ||Gtilde||^2 = 1 + sum_i (W_i^2-1)*(p_i+t*h_i)^2
                    + t^2*(sum_i h_i^2 + sum_j configuration_j^2).

The implemented Sobolev weights are at least one. The producer checks that
condition, the border sign, positivity and finiteness of the resulting norm,
and overlap with the independently paired original field enclosure. It retains
the full original cpsi and remainder third-action contractions. All interval
uncertainties are retained; no measured input or physical radius is adjusted.

Each refinement invocation consumes independently paired eigenpair and response
evidence and recomputes the complete third-action terms and normalized field.
The refinement must itself reproduce independently. Its component boxes may be
used to construct a tighter actual-HS midpoint outer domain, but this does not
by itself prove a midpoint eigenpair, response, uniform derivative, remainder,
physical quotient, Gate7 closure or observable prediction.
