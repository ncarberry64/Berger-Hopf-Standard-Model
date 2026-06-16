# Derived Hypercharge Normalization Factor

The exact boundary trace weights are:

```text
K1 = 10/3
K2 = 2
K3 = 2
```

Define:

```text
eta_Y = K2/K1 = 3/5
```

Then:

```text
eta_Y*K1 = 2
eta_Y*K1 = K2 = K3
```

Therefore the normalized residual Abelian generator is:

```text
T_Y_norm = sqrt(3/5) * Y/2
```

The exact rational check uses squared normalization:

```text
Tr(T_Y_norm^2) = (3/5) Tr((Y/2)^2) = 2
```

Coupling-convention relation:

```text
g1^2 = (5/3) gY^2
alpha1 = (5/3) alphaY
```

Guardrail: This is a normalization theorem, not a measured coupling prediction.

Status: `BOUNDARY_HYPERCHARGE_NORMALIZATION_DERIVED_CONDITIONAL`.

Follow-up theorem layer: [Theorem discharge: one-loop RG from boundary content](theorem_discharge_one_loop_rg_boundary_content.md).
