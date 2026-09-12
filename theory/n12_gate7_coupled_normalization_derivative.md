# Differentiating the coupled physical normalization

For the same verified coupled family as in
`n12_gate7_coupled_physical_normalization.md`, let

    t=s/b, a=psi+t*hard,
    U=(t*configuration, W*a), v=cpsi+t*remainder,
    N^2=1+sum((W_i^2-1)*a_i^2)
        +t^2*(||hard||^2+||configuration||^2).

Then F=sign(b)*(U,v)/N. A verified nonzero border sign is constant on the
connected domain. Differentiate the identities supplied by the normalized
eigenpair and the last row of the physical response system. In particular,

    dt=(ds-t*db)/b,
    da=dpsi+dt*hard+t*dhard,
    d(N^2)/2=sum((W_i^2-1)*a_i*da_i)
        +t*dt*(||hard||^2+||configuration||^2)
        +t^2*(hard^T dhard+configuration^T dconfiguration),
    dU=(dt*configuration+t*dconfiguration, W*da),
    dv=dcpsi+dt*remainder+t*dremainder,
    dF=sign(b)*((dU,dv)-(U,v)*d(N^2)/(2*N^2))/N.

This removes the common border-scale cancellation before interval evaluation.
It does not change the physical field, trial radii, normalization or eigenline
selection. All variations must belong to the same actual coupled family;
independent component boxes cannot establish the differentiated identities.

The refinement helper recomputes the original complete rate variation and
retains all four original contraction groups: the two primal descriptor
contractions, the three directional actions, the dynamic third-action terms
and the fourth-action terms. It reuses the actual bounded selected-line and
physical-response variations from that invocation. Both formulas must overlap.
No descriptor, configuration or fourth-action term is dropped.

This is an enclosure method. It needs a source-bound numerical evaluation and
independent byte-identical recomputation before any refined uniform derivative
certificate is accepted. It does not establish useful local/global operator
bounds, higher remainders, a physical quotient, Gate 7 or full BHSM completion.
