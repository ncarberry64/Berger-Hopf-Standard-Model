# BHSM reset/charge/carrier dependency-cycle adjudication

## Result

The live Track-2 dependencies contain one 25-node strongly connected
component.  The reset/charge/carrier obstruction is therefore a true directed
dependency cycle, not merely an inconvenient ordering.  No recovered BHSM
authority breaks it.  The earned classification is `LOOP3`.

The minimum graph-theoretic feedback vertex cut has cardinality two: every
minimum cut contains `reset_graph` plus one node on the independent
charge/projector/carrier return path.  This does **not** imply two independent
physical laws.  One action functional on the joint boundary-field and
carrier-embedding configuration space can provide coupled Euler-Lagrange
equations for both cut locations.  The minimum independent physical primitive
set therefore has cardinality one: `P-A*`.

`P-A*` is a constrained version of candidate P-A: an action-owned covariant
full-field interface generating functional varied with respect to the carrier
embedding as well as the reset relation.  Its value is not present in the
repository and is not supplied here.

## Graph convention

Every edge is directed from prerequisite to dependent.  Live SCC analysis
includes `DERIVED`, `CONDITIONAL`, `OWNER_SEMANTICS`,
`HISTORICAL_HYPOTHESIS`, and `MISSING` edges.  `INVALIDATED` and `REDUNDANT`
edges remain in the artifact as provenance but do not participate in SCCs.

The complete node and edge ledger is machine-readable in
`artifacts/action_extension/BHSM_RESET_CHARGE_CARRIER_DEPENDENCY_CYCLE_ADJUDICATION.json`.
The principal cycle is

\[
F_B\to \delta_{\rm shape}F_B\to T\mathcal D_{ec}\to\Theta
\to\xi\to H_\xi\to Q_{\rm mode}\to Q_{\rm avail}
\to\rho_{\rm hold}\to\Sigma_{\rm enc}\to\mathcal I_{ec}\to F_B.
\]

The SCC also contains the nonfermion relation, reference-dependent
child/seam charge, envelopment increment, actual stabilizer, physical
projectors, boundary-HJ and global-envelopment alternatives, graph jets,
S1--S4, and the full-field attachment.  The registered reference and retained
charge ledger are prerequisite sources outside the SCC.  Response reduction
and beta are downstream sinks outside it.

## Minimum cut versus minimum primitive

The deterministic graph algorithm finds minimum feedback-vertex sets of size
two.  Representative cuts are

```text
{reset_graph, energetic_carrier}
{reset_graph, rho_hold}
{reset_graph, event_mode_charge}
{reset_graph, physical_projectors}
```

Deleting nodes is only a topological diagnostic.  A physical cycle breaker
must supply equations.  `P-A*` supplies one coupled variational law with
stationarity in `F_B`, `L_s`, trace fields, and the carrier embedding.  Thus a
single functional can select the reset relation and carrier without using a
charge computed from that same unselected carrier.  Zero new primitives cannot
do this because the registered action has no `F_B`, `L_s`, or carrier-embedding
variation.

## Candidate ranking

1. `P-A*`: scientifically sufficient and minimal.  It would select the
   carrier, reset relation, nonfermion polarization, and first moving-domain
   variation in one coupled variational system.  Only the allowed functional
   class is partially described; its physical content is new.
2. `P-C`: hypothetically sufficient but overcomplete.  A full
   \(C_A\rightarrow G_A\) law could output every required structure, but no
   operative law exists and specifying one would add much more physics than
   the minimum cycle breaker.
3. `P-D`: the AE4/Calderón/Wentzell architecture helps with a conditional child
   BVP but leaves carrier, polarization, reference, and projectors independent.
4. `P-E`: reduced incidence is partially present, but a full functor would
   still not select canonical momentum/polarization or the energetic law.
5. `P-B`: a carrier alone leaves `F_B`, `L_s`, their first variation,
   incidence, reference, and projectors open.
6. `P-F`: no additional qualifying object was recovered.

## Targeted lineage recovery

The v6.10 action-selected junction sprint is decisive historical evidence: the
minimal action has no junction mixing term and selects no self-adjoint graph;
the reduced `U(1)` family survives.  The historical boundary-action and cyclic
monodromy branches are structural candidates whose coframe/winding rules,
primitive quotient, normalization, and physical channel identification remain
unproved.

The v14.60--v14.61 global-envelopment system is executable only as a synthetic
theorem fixture.  Its physical coefficients, complete gauge-fixed operators,
domain, incidence, and branch-exhaustion data remain missing.  Synthetic
witness coefficients were not reused.

The v14.68 scalar incidence and v14.69 round common tensor incidence are real
algebraic progress, but neither is the full physical event-child incidence on
the selected carrier with complete projectors and Cauchy data.

The v15.0--v15.5 pregeometry/master lineage contains typed reconstruction,
actualization, category, and owner semantics.  It explicitly leaves the
physical emergence functor, pregeometric generator, clock, carrier, canonical
data, and regular-to-foundation reconstruction unselected.  Unique
Actualization is an authorial criterion, not an action-derived transition.

## Required route classifications

- `CG3`: \(C_A\to G_A\) is typed/owner ontology only.  No operative map
  simultaneously produces geometry, carrier, orientation, boundary data,
  scale, incidence, and canonical data.
- `GE3`: global envelopment remains synthetic/conditional.  Its modern
  physical Euler-Lagrange/KKT problem cannot be run with owned inputs.
- `HJ3`: a regional on-shell principal function requires the event-child
  domain/BVP whose canonical relation it is proposed to select.  It is an
  equivalent formulation of the missing reset graph, not an independent
  derivation.  No seam action was created.
- `INC3`: owner semantics and partial local algebraic transport exist, but no
  full physical incidence functor supplies sufficient Cauchy data for the
  moving graph.

## Most constrained form of the missing primitive

Without adopting it, the admissible object has the schematic form

\[
S_{\rm enc}[F_B,L_s,\iota_{\rm enc},X_e,X_c;E,\sigma]
=\int_{\Sigma_{\rm enc}}\!\mu_{\rm enc}\,
\mathcal L_{\rm enc}(j^rF_B,j^r\iota_{\rm enc},\Delta,\Pi,A,
\text{corner},P;E,\sigma)+T_{\rm top}.
\]

Its domain is the space of admissible Spin\(\times G_{SM}\)-equivariant
event/child trace fields, carrier embeddings, orientation-preserving reset
maps, nonfermion Lagrangian relations, declared environment/scale data, and
compatible finite jets.  Its codomain is real action values modulo canonical
exact boundary terms and, where relevant, a quantized topological phase.

It must respect diagonal orientation/spin-preserving diffeomorphisms, bundle
and BRST covariance, family/projector intertwining, incidence/topological
compatibility, and AE4 retarded causality.  Its variations must preserve the
bulk Hamiltonian/momentum constraints, Gauss law, complete parent-child
Noether balance, and compact total Hopf momentum.

At least one `F_B` derivative is required for connection transport.  Second
embedding/geometric derivatives are permitted if extrinsic-curvature terms
enter; higher derivative order is not authorized without a separate action
extension.  Field-amplitude nonlinearity is otherwise constrained by
covariance, regularity, and well-posedness.  Local scalar densities may control
trace/stress matching, while global incidence or holonomy can require a
topological/nonlocal component.

This is one real invariant functional equivalence class, not one numerical
coefficient.  It is infinite-dimensional.  Existing EH/GHY/Hayward
coefficients and the zero independent AE2 fermion seam action remain fixed;
they do not fix the nonfermion polarization, `F_B` selector, or mapping-sector
weight.

## Consequences and firewalls

No physical downstream object is unlocked because `P-A*` was not selected.
Reset remains blocked; charge remains `XI5/CHG4/REF5/MODEE5/ENVH5/DOMH4/AE4R5`;
carrier and response remain `RSP5`; reduced reset, beta, graph jets, S1--S4,
and the full-field action attachment remain undefined.

No independent N12 equation was added.  The residual remains \(98-31=67\),
or 66 after the already-owned time quotient.  Frozen predictions and their
fingerprints are unchanged.  Gate 7 is not promoted and full BHSM completion
is not claimed.

## Morning owner question

What single covariant action-owned interface generating functional
\(S_{\rm enc}\), if any, governs the carrier embedding, full-field
event-to-child reset map \(F_B\), and nonfermion boundary relation \(L_s\), so
that its first variation selects all three without fitted data?

## Exact next object

`OWNER_SELECTION_OF_ONE_ACTION_OWNED_COVARIANT_FULL_FIELD_INTERFACE_GENERATING_FUNCTIONAL_WITH_CARRIER_EMBEDDING_RESET_RELATION_AND_FIRST_MOVING_DOMAIN_VARIATION`
