# Charged-Current Transport Space

Status: `OPEN_MISSING_CHARGED_CURRENT_TRANSPORT_SPACE`.

Overall transport audit status: `MULTIPLE_COMPETING_TRANSPORT_SPACES`.

Candidate spaces:

| space | dimension | status |
| --- | ---: | --- |
| `Hom(V_u,V_d)` | 8 | `OPEN_MISSING_CHARGED_CURRENT_TRANSPORT_SPACE` |
| `Hom(V_u,V_d) direct_sum Hom(V_d,V_u)` | 16 | `OPEN_MISSING_HERMITIAN_ADJOINT_PAIR_TRANSPORT_SPACE` |
| `End(V_l) direct_sum End(V_u) direct_sum End(V_d)` | 21 | `OPEN_MISSING_CHARGED_CURRENT_TRANSPORT_SPACE` |
| `End(V_ch)` | 49 | `OPEN_MISSING_CHARGED_CURRENT_TRANSPORT_SPACE` |
| `End(V_d)` | 16 | `RETIRED_MAXIMAL_SELF_RESPONSE_AS_PRIMARY_CKM_SOURCE` |

Same numerical dimension does not establish the physical source.

The Hermitian adjoint-pair channel count is 16, but the CKM exponent remains not derived unless BHSM proves CKM acts on that selected transport space.

The v2.7 projector-domain audit leaves the selected space and dimension unset because no projector sandwich is attached to the bounded term.
