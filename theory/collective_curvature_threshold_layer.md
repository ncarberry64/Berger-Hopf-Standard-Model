# Collective Curvature Threshold Layer

Status: `candidate_only`

Claim labels:

- `COLLECTIVE_CURVATURE_THRESHOLD_LAYER_CANDIDATE`
- `MASS_AS_COLLECTIVE_THRESHOLD_RESPONSE_CANDIDATE`
- `LOG_THRESHOLD_SCALE_COMPRESSED_RESPONSE_CANDIDATE`
- `BRANCH_TYPE_CURVATURE_SPECIALNESS_CANDIDATE`

## Motivation

The isolated heat-kernel spectral-action mass screen did not reproduce the
existing BHSM charged-fermion outputs as well as the frozen bare engine. The
minimal branch-threshold reconstruction found `D_log_threshold_plus_type`
as the strongest diagnostic law, with RMS log error
`0.510697459271581` and maximum absolute log error
`1.0380747597108453` against existing bare predictions. That result
kept explicit warnings: hidden response remains, overfit risk remains,
reference-scheme limitations remain, and numerical closure was not achieved.

## Candidate Interpretation

The candidate reading is that the mass engine behaves more like a collective
curvature threshold response than an isolated single-mode spectral decay. In
this view, local mass thresholds contribute to a shared topographic curvature
field, and a mode opens only after its effective curvature passes a threshold.

```text
L_T T = S_total
L_T = nabla^2 - B*nabla^4
S_total = S_visible + S_internal_modes + S_boundary + S_interaction
```

Each mode contributes to and samples an effective field:

```text
K_i_eff = K_i_self + sum_j G_ij m_j + K_i_boundary + K_i_envelope
```

The candidate threshold-opening rule is:

```text
m_i = M_f * [K_i_eff - K_i_crit]_+^p * Z_i
```

where `[x]_+ = max(x,0)`. This is not an official mass formula.

## Branch Identity

The previous branch-threshold audit found branch identity and branch type to be
diagnostically important. Pure-fiber and pure-base modes may sit on special
threshold channels, while mixed modes retain a hidden response term. This
supports the candidate label:

`BRANCH_TYPE_CURVATURE_SPECIALNESS_CANDIDATE`

## Scale Compression

The strongest diagnostic law used a log threshold:

```text
S_eff ~ a * log(1 + N) - b_fiber*I_fiber - b_base*I_base + hidden_response
```

so:

```text
m_shape ~ (1+N)^(-a) * exp(b_fiber*I_fiber + b_base*I_base) * R_hidden
```

This suggests scale-compressed collective response, not a completed derivation.

## Topographic Stability

The fourth-order topographic operator supplies a natural place for envelope and
stability behavior. In this candidate layer, the fourth-order term damps
runaway short-scale response while allowing collective curvature envelopes.

## Guardrails

- Candidate only.
- No frozen predictions are changed.
- No official predictions are changed.
- No new official mass formula is introduced.
- Numerical closure is not claimed.
