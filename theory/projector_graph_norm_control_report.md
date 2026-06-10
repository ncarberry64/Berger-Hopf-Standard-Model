# BHSM v2.15 Projector Graph-Norm Control Report

Status: `PROJECTOR_GRAPH_NORM_CONTROL_PROVEN`
Theorem complete: `True`
Inequality: `||P_perp psi||_(A0+V) <= C ||psi||_(A0+V)`
Control constant: `2.0476067054442755`

| Property | Value |
| --- | --- |
| interacting domain | `INTERACTING_DOMAIN_EQUALS_REFERENCE_DOMAIN_PROVEN` |
| domain invariance | `PROJECTOR_DOMAIN_INVARIANCE_PROVEN` |
| graph norm equivalence | `True` |
| bounded on H | `True` |
| bounded on D(A0) | `True` |
| bounded on D(A0+V) | `True` |

## Assumptions

- P_perp is an orthogonal bounded projector on the formal sector-labeled Hilbert space.
- D(A0+V)=D(A0) and the graph norms are equivalent.
- All nonzero commutators are controlled by v2.14.

## Limitations

- The graph-norm control closes projector-domain stability only.
- Lower-bound transfer and index/mirror theorem gates remain separate.
