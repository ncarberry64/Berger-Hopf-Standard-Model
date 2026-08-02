# BHSM v11.1 Historical Recovery Audit: Support Representation

## Exact object and search scope

The object is a strong monoidal functor from the stratified BHSM action
category to `Rep(G_D)`, modulo physical natural/canonical equivalence. It must
assign primitive characters and equivariant derivatives, measures, boundary
maps, core data, and dimensional reduction while preserving the complete
action and symplectic structure.

The live tree, artifacts, tests, scripts, theory, documentation, Git content
history, tags, local/remote branches, all 214 GitHub PR records, GitHub issues,
available author attachments, the read-only USB mirror, and verified v8.3,
v10.4, and v11.0 bundles were searched. Synonyms included support/sector/carrier
weight, depth/Haar character, boundary/fiber/wall incidence, dimensional
support, measure scaling, primitive coframe, active-generator count, and
normalized boundary measure.

## Historical routes exhausted

| Candidate | Provenance | Classification | Reconciliation |
| --- | --- | --- | --- |
| Multiplicative characters `upsilon^w` | PR #214, v11.0 | Partial ingredient | Derives the character family, not primitive ownership or quotient. |
| General support action `Z,U,F_C,F_W` | PR #213, v10.4 | Partial ingredient | Supplies the derivative-action class; coefficients and core domain remain open. |
| Covariant bulk-boundary reduction | PR #200, v7.1 | Partial ingredient | Pushes normalized measures/modes, but declares no `G_D` action. |
| `1:2:7` active-generator weights | PRs #163/#199 | Invalidated for this use | Explicitly rejected as action/representation trace weights. |
| Primitive lattice `(3,6,12)->(1,2,4)` | PR #103 | Conditional candidate | Its own action quotient under common rescaling is explicitly open. |
| Coframe multiplier and winding | branch `820198f` | Conditional candidate | Tests enforce `COFRAME_MULTIPLIER_NOT_DERIVED` and `SECTOR_WINDING_RULE_NOT_DERIVED`. |
| Boundary representation connection | branch `75894b9` | Partial ingredient | `A_q` is partial and `A_j` convention-dependent; this is not the support group. |
| Collar/normalized boundary measures | PR #13 and later | Partial ingredient | Local Jacobians/normalizations do not define their transformation under `G_D`. |

The v8.3 bundle verifies main `0721ee6`; v10.4 verifies `04a38d9`; v11.0
verifies `76ca770`. Their histories agree with the live provenance and contain
no later hidden primitive support assignment. The USB mirror at v11.0 repeats
the explicit statement that support weights remain missing.

## Reusable historical kernel

The valid pieces retained are the v10.4 local supported-action class, the v7.1
normalized reduction maps, exact boundary/projector incidence ledgers, and the
v11.0 character law. They narrow the quotient but do not close it. Discrete
sector incidence cannot silently become the continuous `G_D` generator.

Audit verdict:
`BHSM_HISTORICAL_RECOVERY_NARROWS_BUT_DOES_NOT_CLOSE_CURRENT_OBJECT`.

The first truly missing mathematical object remains
`COMPLETE_LOCAL_SUPPORTED_ACTION_WITH_SUPPORT_DERIVATIVE_COUPLINGS_AND_BOUNDARY_CORE_CANONICAL_DOMAIN`.
This conclusion is now licensed by a complete recovery gate; it is not an
inference from current terminology alone.
