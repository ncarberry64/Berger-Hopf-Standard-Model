# X_ch Charged Boundary-Response Theorem

Phase Three-I audits whether the separate charged boundary-response matrix can
be promoted to an interaction vertex by identifying or deriving `X_ch`.

## Finding

The repo supports the standard `W_mu` charged-current target convention for
CKM/PMNS target currents. It does not provide a theorem identifying the
separate charged boundary-response carrier with `W_mu`.

For the separate charged boundary response, `X_ch` remains a distinct projected
boundary-response carrier candidate:

```text
X_ch^mu
```

Its production use requires the missing theorem assigning:

- spin;
- gauge representation;
- Lorentz index structure;
- field content;
- coupling normalization.

## Status

```text
theorem_status = OPEN_EXACT_MISSING_THEOREM
promotes_charged_boundary_response = false
feynrules_ready = false
ufo_ready = false
```

Promoting `charged_boundary_response_matrix` without this theorem is forbidden.

