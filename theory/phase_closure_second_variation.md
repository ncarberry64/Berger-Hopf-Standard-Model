# Phase Closure Second Variation

The phase closure functional is

```text
S_phase(d, theta)=|exp(i d theta)-1|^2
```

At

```text
theta = 2*pi/d + epsilon
```

we obtain

```text
S_phase = 2 - 2 cos(d epsilon)
        = d^2 epsilon^2 + O(epsilon^4)
```

Under the `S ~= 1/2 H epsilon^2` convention,

```text
H_phase(d)=2d^2
```

Guardrail: this enforces local phase-closure stiffness but does not alone select the closure spectrum.
