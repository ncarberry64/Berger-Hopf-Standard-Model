# Environment-conditioned full-field reset-selector recovery

Status: `RECOVERY_EXHAUSTED_OWNER_INPUT_REQUIRED`.

This is a provenance and translation audit. It introduces no physical law,
action term, coefficient, boundary functional, reset, or prediction.

## Recovery result

The complete reachable lineage contains the intended *shape* of the missing
rule, and it contains one superseded attempt to instantiate it, but it does
not contain a current full-field selector

\[
K:(X_e,s,\mathcal E_s)\longrightarrow[(F_B,L_s)]
\]

with K4 or K5 authority.

The strongest surviving construction is the N=3 conditional chain

\[
B_{\rm child}=\mathcal E_{\partial}
 (z_{\rm event},I_{\rm environment},B_{\rm SM}),
\qquad
\Phi_{\rm child}=\operatorname{Solve}_{\rm BVP}
 (B_{\rm child},I_{\rm event}),
\]

\[
F_{\rm child}(z_e)=0,
\qquad
z_{\rm return}=\operatorname{Trace}_{\rm return}(\Phi_{\rm child}).
\]

Once a terminal N=3 event trace is supplied, the common action Legendre map,
seven independent constraint directions, scalar child BVP, and homogeneous
zero-background gauge/spinor/ghost/HS blocks determine a local child field
state. That is conditional K5 for that one supplied N=3 field-state problem.
It is only K1 for the present full-field E5 family because
`E_boundary` itself is absent, the physical Wentzell/attachment block is not
generally selected, and neither a spatial base map `F_B` nor a complete
nonfermion correspondence `L_s` follows.

At N=12 the same architecture survives only as a regular set-valued relation.
The fixed-event child block has shape 31 by 98 and rank 31, leaving a
67-dimensional fiber, or 66 dimensions after the existing time quotient.
The certified normal chart is a reproducible proof representative, not a
physical selection rule. N=3 determinacy therefore cannot be promoted to
N=12 uniqueness.

## Historical selectors

The audit classifies nine serious candidates.

1. v11.0 `T_core` records owner target-selection semantics but leaves energy,
   phase, topology, gauge, exit, and target maps unset: P0/P1, K0,
   `OWNER_SEMANTICS_ONLY`.
2. v14.60 global envelopment co-varies parent, child, seam, traction, and
   scale. Strict convexity gives K4 only for a synthetic reduced witness; the
   physical coefficients, gauge-fixed Hessian, and branch exhaustion are
   absent: P2, current K0, `PARTIAL_RULE`.
3. v14.65-v14.68 boundary-triple/Calderon/Wentzell machinery restricts
   admissible boundary graphs but does not select the physical block or base
   map: P2/P3 theorem class, K1, `LOST_TRANSLATION/PARTIAL_RULE`.
4. v15.5-v15.8 `Unique Actualization` is an owner completion criterion. The
   master map, formation/reconstruction arrows, orbit, and generator remain
   absent: P0, K0, `OWNER_SEMANTICS_ONLY`.
5. v15.14-v15.16 clock/skin work proves that clock transport does not select
   initial boundary data; the available selector Jacobian has rank zero:
   P2 negative result, K0, `ABSENT`.
6. v15.52-v15.57 explicitly set reconstruction to the constant map
   `Reconstruct(I_star)=z_star` and claimed a unique hybrid fixed point:
   P2, historical K5. v17.82/v17.84 show that it has zero event-selection
   rank, and v17.87 replaces identical return with finite persistence inside
   `B_child`: current K0, `SUPERSEDED_RULE`.
7. v16.78 types
   `(I_event,I_environment,B_SM)->(sector,R_rec,z_return)`. It creates the E5
   superselection restriction but has K0 power within E5: P1, `PARTIAL_RULE`.
8. v17.82-v17.99 supplies the conditional N=3 Cauchy/Noether BVP mechanism:
   P2/P3 locally, conditional K5 for one supplied event, current full-field
   K1, `LOST_TRANSLATION/PARTIAL_RULE`.
9. N=12 proves local singular hitting and a nonempty set-valued reset relation,
   and types a first-positive-return relation. The return is not executable or
   single-valued and the fixed-event fiber is 67-dimensional: P3 local
   existence, K1, `PARTIAL_RULE`.

There is no recovered `LOST_IMPLEMENTATION`: no historical executable object
already has the complete present signature and authority. The missing content
is physical boundary data, not merely an uncalled function.

## `R_rec` and `z_return`

The exact symbol `R_rec[I_event,I_environment]` first appears in commit
`c10d67e442118ed8a64feaa042886eaa30fffd19` (v16.78, 2026-08-13) as the
post-solution scale in

\[
C_{\rm rec}=q_{\log R}({\rm return})-
\log(R_{\rm rec}/R_\star)=0.
\]

It is an output of the broken reconstruction BVP. It determines scale only;
it does not independently determine boundary data, topology, geometry, or the
child state.

The exact equation
`z_return=Trace_return[Phi_child]` first appears in commit
`02ddaa947aaa1f4a3e486ce4b723047203e37eb0` (v17.82, 2026-08-14).
`z_return` is also an output: the return trace of the solved child. Scale is
projected from it after the solution. Neither symbol can be moved to the input
side and used as a selector without adding the missing physics.

## `SPACETIME_EDGE`

The v11.0 conceptual antecedent is “pure energy without ordinary spacetime
support is the core.” The normalized symbol first enters reachable history in
commit `a506e89b5a423f5f0e17c6a63ae8be2efcec618d` (2026-08-27).
It means the owner-authorized limit where geometric variables cease and pure
energy/Aether is operative. Degree, orientation, FR parity, incidence, and
bundle class can survive; metric, proper time, curvature, local energy density,
and canonical metric momentum are not transported as pregeometric primitives.

No older transition equation was recovered. Action location, core adjacency,
energy/phase/topology/gauge transfer, exit, emergent boundary data, and return
geometry remain open. Firewall, canonical stop, core boundary, and proof cutoff
must not be identified with `SPACETIME_EDGE` without a theorem.

## Decision and downstream status

The current E5 family is unchanged: within-sector base-map and nonfermion
Lagrangian-correspondence freedom remains infinite-dimensional. No physical
reset equivalence class is selected. Consequently the reset tangent domain,
relative generator/charge, beta, graph jets, S1-S4, and full-field action
attachment remain blocked at G4/U/D.

The smallest remaining owner question is:

> Given the gauge-quotiented last-regular event trace and environment
> `(z_event,E_s,B_SM)`, what boundary Cauchy/Noether datum `E_boundary`—or
> equivalently what full-field boundary generating relation—must the
> reconstructed child satisfy?

Until that answer is supplied, the exact next object is

`OWNER_SUPPLY_THE_GAUGE_COVARIANT_EVENT_ENVIRONMENT_TO_CHILD_BOUNDARY_CAUCHY_NOETHER_DATA_RULE_OR_EQUIVALENT_FULL_FIELD_BOUNDARY_GENERATING_RELATION_THAT_SELECTS_ONE_PHYSICAL_RESET_EQUIVALENCE_CLASS`.

`FULL_BHSM_COMPLETE = FALSE`.
