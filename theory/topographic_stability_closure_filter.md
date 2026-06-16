# Topographic Stability Closure Filter

Candidate fourth-order operator:

```text
L_T = nabla^2 - B*nabla^4
```

Existing generation-count candidate:

```text
zero/reference closure + two stable nonzero topographic branches
```

Candidate diagnostic rule:

```text
topographic_stability_pass(d) = d in {1,2,3}
```

Interpretation:

- `d=1` corresponds to reference/single closure.
- `d=2` corresponds to paired orientation/interface closure.
- `d=3` corresponds to three-channel stable closure.

Required guardrail: the full stability derivation requires the complete Berger-Hopf boundary Hessian and cannot be claimed closed here.
