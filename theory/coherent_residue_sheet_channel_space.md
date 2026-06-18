# Coherent Residue-Sheet Channel Space

This audit reframes BHSM cyclic boundary channels as covering-map sheet multiplicities rather than total Wilson-loop phase order.

## Summary

Covering-map theorem status: `BOUNDARY_COVERING_MAP_CHANNEL_THEOREM_PARTIAL`
Omega-as-degree status: `OMEGA_AS_COVERING_DEGREE_CONDITIONAL`
Primitive covering status: `PRIMITIVE_COVERING_CONDITIONAL`
Residue sheet status: `RESIDUE_SHEET_CHANNELS_PARTIAL`
Deck transformation status: `DECK_TRANSFORMATION_ORDER_PARTIAL`
Channel dimension status: `DIM_H_EQUALS_ABS_OMEGA_COVERING_MAP_PARTIAL`
Wilson-loop trap status: `WILSON_LOOP_TRIVIALITY_TRAP_RESOLVED_BY_COVERING_DEGREE`
Coherent channel-space status: `COHERENT_RESIDUE_SHEET_CHANNEL_SPACE_PARTIAL`
Simplex-vs-EndH status: `SIMPLEX_VS_ENDH_DISTINCTION_PARTIAL`
Lepton 8/9 consequence: `LEPTON_8_9_CHANNEL_RULE_COVERING_MAP_PARTIAL_STRENGTHENED`

## Covering-Map Theorem

```text
u_f:S^1_boundary -> U(1)
Omega_f = deg(u_f) = (1/(2*pi)) integral dphi_f
N = |Omega_f|
generic preimage count = N
T:s_r -> s_{r+1}, T^N=I
H_f^chan ~= C[Z_N]
dim(H_f^chan)=N
```

## Wilson-Loop Trap

The total phase `exp(i integral dphi_f)=exp(2*pi*i*N)` is globally single-valued for integer `N`. That fact does not erase the `N` preimage sheets of the degree-`N` boundary phase map.

Wilson phase trivial for degree 3: `True`
Sheet count for degree 3: `3`

## Sector Covering Table

| Sector | Omega | Degree | Sheets | Deck order | dim H | Simplex rel dim | dim End(H) | Traceless | Active fraction | Status | Official update |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `charged_lepton` | `3` | `3` | `3` | `3` | `3` | `2` | `9` | `8` | `8/9` | `LEPTON_8_9_CHANNEL_RULE_COVERING_MAP_PARTIAL_STRENGTHENED` | `False` |
| `up_candidate_only` | `6` | `6` | `6` | `6` | `6` | `5` | `36` | `35` | `35/36` | `QUARK_COVERING_CONSEQUENCE_CANDIDATE_ONLY` | `False` |
| `down_candidate_only` | `12` | `12` | `12` | `12` | `12` | `11` | `144` | `143` | `143/144` | `QUARK_COVERING_CONSEQUENCE_CANDIDATE_ONLY` | `False` |

## Coherent Channels vs Classical Simplex

The classical probability simplex over `N` sheets has relative dimension `N-1`. BHSM's lepton `8/9` channel factor uses coherent amplitude/density operators on `H_f=C[Z_N]`, where `dim End(H_f)=N^2` and the trace-preserving relative sector has dimension `N^2-1`.

## Dimension Route

Preferred dimension route: `cyclic_boundary_monodromy`
Preferred interpretation: `cyclic_boundary_covering_degree`
Geometric quantization plus-one hazard: `True`
Rejected/limited route note: `S2_GEOMETRIC_QUANTIZATION_NOT_USED_FOR_CHANNEL_DIMENSION`

Ordinary S2 geometric quantization is used only as a hazard comparison, not as the channel-dimension proof route.

## Blockers Closed

- degree_N_covering_has_N_generic_preimages
- deck_shift_order_equals_N_for_primitive_cover
- integer_Wilson_loop_global_phase_is_trivial
- End_H_traceless_dimension_formula_N_squared_minus_one

## Open Blockers

1. derive boundary phase map u_f from completed BHSM boundary action
2. prove Omega_f is exactly the degree of u_f, not only a symbolic sector number
3. prove primitive covering rather than reducible/imprimitive covering
4. prove residue sheets are physical coherent amplitude channels from full dynamics
5. derive stochastic residue sampling from completed topographic dynamics
6. derive full Brownian generator/rates on End(H_f)
7. resolve stochastic alpha/pi factor-of-two normalization from completed path integral
8. fix A_j normalization/global bundle coupling without convention dependence

## Claim Safety

- No official frozen outputs are changed.
- No retuning is performed.
- No frozen lepton or quark dressing rule is changed.
- No claim is made that BHSM replaces the Standard Model.
- The lepton 8/9 chain is strengthened only as a partial/candidate result.
