# Boundary Phase Closure Functional

The candidate phase closure term is

```text
S_phase(d, theta) = |exp(i d theta) - 1|^2
```

Using `|exp(i x)-1|^2 = (cos x - 1)^2 + sin(x)^2`, the diagnostic is nonnegative.

- For `theta = 2*pi/d`, `S_phase = 0`.
- For an off-closure phase, `S_phase > 0`.
- This enforces closure but does not alone select `d=1,2,3`.

Status: `PHASE_CLOSURE_FUNCTIONAL_CANDIDATE`.

Related: [Phase closure second variation](phase_closure_second_variation.md).
