# Collective Curvature Mass-Engine Bridge

Status: `candidate_only`

The diagnostic law `D_log_threshold_plus_type` is not an official
formula. It approximates the existing bare engine better than the failed
isolated heat-kernel baseline, but overfit risk and hidden response remain.

## Bridge

The diagnostic form:

```text
log_pred = A0 - a*log(1+N) + b_fiber*I_fiber + b_base*I_base
```

is consistent with a scale-compressed threshold response:

```text
m_shape ~ (1+N)^(-a) * exp(b_fiber*I_fiber + b_base*I_base) * R_hidden
```

The missing `R_hidden` term is the reason this bridge remains candidate-only.

## Candidate Fixed Point

The next derivation target is a self-consistent curvature fixed point:

```text
m_i = M_f * [K_i^0 + sum_j G_ij m_j - K_i_crit]_+^p * Z_i
```

or in matrix form:

```text
m = M * [K0 + G m - Kcrit]_+^p * Z
```

This sprint does not solve or fit that system as an official model. It only
records the bridge suggested by the prior branch-threshold diagnostics.

## Limitations

- `D_log_threshold_plus_type` remains diagnostic.
- Hidden response remains.
- Overfit risk remains.
- Reference-scheme limitations remain.
- No numerical closure is claimed.
