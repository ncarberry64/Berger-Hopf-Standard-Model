# AE3.1 capture-source to neutrino-propagation gate

Electron capture selects an initial electron-flavor weak source. It does not
select a fixed mass eigenstate or the operator that governs later
propagation:

```text
p+e -> n+nu_e
     -> outgoing nu_e boundary trace
     -> neutral exterior Green/Calderon map
     -> K_nu(x)
     -> subtracted pole or cycle quasi-energy.
```

The stronger propagation-dependent BHSM hypothesis has an exact necessary
condition. If all curvature, weak, and environmental terms act as
`kappa(x) I3` on family space, path ordering cannot create flavor change:

```text
U(x_f,x_i)=exp(-i Phi) I3.
```

Likewise, adding any position-dependent common scalar to a Hermitian family
operator shifts all three eigenvalues equally and leaves both independent
eigenvalue gaps unchanged. Scalar curvature illustrates the point. The
Lichnerowicz term is `(R/4) I3`; curvature can alter a common phase or local
dispersion, but curvature alone cannot generate neutrino splittings.

Therefore BHSM needs a genuinely family-noncentral returned neutral operator
with at least two nonzero transported eigenvalue differences. Noncentrality
alone is not sufficient: the operator must also fail to commute with the
produced `nu_e` projector somewhere along the path, or generate equivalent
nontrivial path-ordered monodromy. This is exactly the missing owner already
recorded by the current physical inverse closure.

There is also a mass-semantics correction. An arbitrary local eigenvalue of
`D_nu_eff^2` is not automatically a mass squared because it includes momentum,
curvature, gauge potential, boundary, and state data. The admissible BHSM
readout is a subtracted zero-momentum pole or the parent-relative cycle
quasi-energy of the propagating mode. That readout may depend on environment,
but the current action has not yet derived that dependence.

The v14.55 pair-wake work is retained as a hypothesis-level ontology:
environmental phase response can vary, instantaneous wake response is not a
primitive mass, and cycle quasi-energy is the candidate invariant. It is not
substituted for the missing current-C2 neutral self-energy and monodromy.

Promoted:

- capture selects the initial `nu_e` family source;
- exact family-central propagation no-oscillation theorem;
- exact common-environment gap-invariance theorem;
- curvature-alone neutrino-splitting no-go.

Not promoted:

- an outgoing physical neutrino boundary mode;
- propagation-dependent mass support;
- two neutrino splittings, PMNS, or a detector map.

`FULL_BHSM_COMPLETE = FALSE`.
