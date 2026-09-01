# BHSM v2.15 Interacting Graph-Domain Report

Status: `INTERACTING_DOMAIN_EQUALS_REFERENCE_DOMAIN_PROVEN`
Theorem complete: `True`
D(A0+V) = D(A0): `True`
Graph norms equivalent: `True`

| Dependency | Status/Value |
| --- | --- |
| definitions | `GRAPH_DOMAIN_DEFINITIONS_PROVEN` |
| reference graph domain | `GRAPH_NORM_DOMAIN_PROVEN` |
| complete operator | `COMPLETE_OPERATOR_IDENTIFICATION_PROVEN` |
| action uniqueness | `COMPLETE_OPERATOR_ACTION_UNIQUENESS_CLOSED` |
| commutator control | `PROJECTOR_COMMUTATOR_CONTROL_CLOSED` |
| total relative a | `0.015621013485509948` |
| total relative b | `1.0` |
| a < 1 | `True` |
| lower graph-norm constant | `0.9843789865144901` |
| upper graph-norm constant | `2.01562101348551` |

## Assumptions

- A0 is the proven diagonal self-adjoint reference operator.
- The v2.13 complete-operator action-uniqueness result discharges missing-term ambiguity.
- The complete perturbation package has total relative bound a < 1.
- The v2.14 projector commutator control result is closed.

## Limitations

- This proves the graph-domain equality route inside the current BHSM complete-operator scaffold.
- It does not prove lower-bound transfer, index theorem, or mirror exclusion.
