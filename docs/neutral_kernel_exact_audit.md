# Exact Neutral-Kernel Audit

The artifact-backed matrix is

```text
K_nu = [[0,1/3,0],[1/3,3,1/6],[0,1/6,5/3]].
```

Its characteristic polynomial is
`lambda^3-(14/3)lambda^2+(175/36)lambda+5/27`. Its numerical eigenvalues are
approximately `(-0.036785922, 1.647109652, 3.056342936)`. The raw kernel is
therefore indefinite, and the mixed-sign negative eigendirection is retained
in the audit.

The raw neutral kernel is not assumed to be positive semidefinite.

