# Topographic/Excess Hessian Bridge

The topographic branch diagnostic uses

```text
lambda_n(k)=k^2+B*k^4
```

Branch interpretation:

- reference-normalized mode;
- orientation stable branch candidate;
- cyclic stable branch candidate;
- excess gapped branch candidate.

The excess term is

```text
S_excess(d)=gamma max(d-3,0)^2
```

For continuous-surrogate classification:

```text
H_excess = 0 for d <= 3
H_excess = 2 gamma for d > 3
```

Guardrail: higher closures are gapped/excess under the diagnostic scaffold, not mathematically impossible.
