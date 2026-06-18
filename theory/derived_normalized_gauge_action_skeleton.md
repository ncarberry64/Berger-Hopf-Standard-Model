# Derived Normalized Gauge-Action Skeleton

Starting skeleton:

```text
S_gauge_boundary =
k3 Tr(F_cyc wedge *F_cyc)
+ k2 Tr(F_orient wedge *F_orient)
+ k1 F_Y wedge *F_Y
```

The boundary trace-weight derivation gives:

```text
K1 = 10/3
K2 = 2
K3 = 2
eta_Y = 3/5
```

After normalization, the Abelian kinetic term is placed on the same trace-normalized footing as the cyclic and active-orientation terms:

```text
S_gauge_boundary_norm =
k [
  Tr_cyc(F_cyc wedge *F_cyc)
  + Tr_orient(F_orient wedge *F_orient)
  + eta_Y F_Y wedge *F_Y
]
```

Equivalent compact convention:

```text
k[Tr(F_cyc^2)+Tr(F_orient^2)+eta_Y F_Y^2]
```

Guardrail: This does not derive RG running or measured values.

Status: `NORMALIZED_GAUGE_ACTION_SKELETON_DERIVED_CONDITIONAL`.

Follow-up theorem layer: [Theorem discharge: one-loop RG from boundary content](theorem_discharge_one_loop_rg_boundary_content.md).
