# Generation Count from Fourth-Order Stability

Status: `GENERATION_COUNT_FOURTH_ORDER_STABILITY_STRUCTURAL_CANDIDATE`

Candidate topographic stability operator:

```text
L_T = nabla^2 - B*nabla^4
```

The structural proposal is that a linearized fourth-order stability problem
has two physical decaying nonzero branches in the stable window after growing
solutions are removed by regularity and boundedness. The candidate generation
rule is:

```text
three generations =
zero-boundary reference attractor
+ two stable nonzero topographic branches
```

This is not yet a proof. Required missing ingredients:

1. the full Hessian around the BHSM attractor;
2. the complete boundary conditions;
3. a map from the two stable branches to the two lowest admissible lattice
   representatives;
4. exclusion of higher admissible modes as complement, unstable, or overtone
   states.

The rule is used here only as an organizing candidate for the mode-ledger
tests.
