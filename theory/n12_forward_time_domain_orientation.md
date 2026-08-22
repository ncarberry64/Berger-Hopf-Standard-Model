# N12 forward-time domain orientation

BHSM admits one physical time orientation. On every retained child history the
existing clock relation is

    d tau_child = N_boundary dt,

with `dt>0` and positive boundary lapse `N_boundary>0`. Hence physical
admissibility requires `d tau_child>0`. This is already part of the positive-
duration persistence domain; it is not a new equation or selector.

The formal state reflection

    R(q,v,log N,beta) = (q,-v,log N,-beta)

does not act on `dt` and leaves the positive lapse unchanged. Two distinct
uses must therefore be separated:

1. interpreting `R` together with `t -> -t` as physical backward evolution is
   inadmissible, because it reverses the allowed clock orientation;
2. re-expressing `R Y` as new Cauchy data and evolving it with the same
   `dt>0` is a forward-oriented algebraic/chiral partner whenever it satisfies
   the same child domain.

For the certified N12 event/child root, the second test passes. The retained
row parity preserves the zero set; metric, lapse, eta, gauge, rank, and Dirac
gaps are preserved; and the reflected state has its own local positive-
duration forward solution. Thus the reflection may relate two physical
forward histories, but they are not two temporal orientations. No action
selection between “forward” and “backward” is required.

The reflection is still not proved gauge and is not quotiented. Any later
distinction between its paired histories is a state/chirality/family question,
not a clock-orientation ambiguity. Likewise the sign of
`c_psi b_psi` labels terminal versus emergent singular-boundary behavior; it
does not choose the direction of physical time.

The admissible child-history manifold is therefore the existing child domain
intersected with

    dt>0, N_boundary>0, d tau_child=N_boundary dt>0.

After this correction, the intrinsic-state obstruction remains global forward
reachability and action-owned orbit/state selection. It is not selection of a
temporal-orientation sector.
