# Boundary Topographic/Excess Functional

The topographic scaffold keeps the existing fourth-order form

```text
L_T = nabla^2 - B*nabla^4
```

with the stable finite diagnostic convention

```text
lambda_n(k) = k^2 + B*k^4
```

The candidate branch interpretation is:

- reference branch;
- orientation branch;
- cyclic-channel branch;
- excess branch gapped.

The excess term is

```text
S_excess(d) = gamma * max(d - 3, 0)^2
```

Guardrail: higher `d` values are gapped/excess in the candidate low-energy scaffold, not impossible.

Status: `TOPOGRAPHIC_EXCESS_GAP_FUNCTIONAL_CANDIDATE`.
