# Charged Kf Bridge-Coupling Source Kernel v1

Current public status: structural architecture integrated conditional;
numerical closure open.

This sprint separates the charged `K_f` bridge layer from the diagonal
suppression layer. The previous `rho_ch` selector sprint found:

```text
NO_UNIQUE_ACTION_SELECTOR_FOUND
rho_ch_exact_value=OPEN_LOCALIZABLE
charged_Hessian_from_S_index_trace=INVALIDATED_DO_NOT_CLAIM
```

## Bridge Topology

The charged `K_f` matrix keeps the tridiagonal bridge topology

```text
|0> <-> |1> <-> |2>
```

with no default direct `|0> <-> |2>` bridge.

```text
charged_Kf_tridiagonal_bridge_topology=DERIVED_CONDITIONAL_ON_E3_LADDER_AND_TANGENT_ADJACENCY
E3_reference_ladder_bridge=DERIVED_CONDITIONAL_ON_RANK_THREE_CLOSURE_LADDER
zero_defect_tangent_bridge=DERIVED_CONDITIONAL_ON_ZERO_DEFECT_TANGENT_ADJACENCY
cyclic_0_2_bridge=NOT_ASSUMED_REQUIRES_CYCLIC_E3_ACTION_SOURCE
```

The `|0> <-> |1>` bridge is assigned to the `E3` reference ladder. The
`|1> <-> |2>` bridge is assigned to zero-defect tangent adjacency. A direct
cyclic bridge is not included unless a cyclic `E3` closure source is later
derived.

## Bridge Magnitudes

The existing minimal ansatz remains named explicitly:

```text
BRIDGE_RULE_MINIMAL_ANSATZ
beta_f = (1/21) Pi_f
kappa_f = 1/[21 ||v_f||^2_ch]
```

It gives

```text
beta_l=1/147
beta_u=2/147
beta_d=4/147
```

and

```text
kappa_l=1/[21(4+rho_ch)]
kappa_u=1/[21(4+rho_ch)]
kappa_d=1/[21(16+rho_ch)]
```

The magnitude seeds remain open:

```text
beta_f_reference_bridge_magnitude=OPEN_LOCALIZABLE
beta_f_minimal_1_over_21_ansatz=STRONGLY_SUPPORTED_CANDIDATE
kappa_f_inverse_tangent_stiffness_form=STRONGLY_SUPPORTED_CANDIDATE
kappa_f_magnitude=OPEN_LOCALIZABLE
kappa_f_minimal_1_over_21_ansatz=STRONGLY_SUPPORTED_CANDIDATE
```

## Suppression Versus Bridge Coupling

Rule A diagonal suppression uses

```text
B_supp = I_ch / 21
eta_l = 20/147
eta_u = 38/147
eta_d = 68/147
```

That derives the diagonal suppression branch conditionally. It does not by
itself derive the bridge magnitude seeds `beta_0` or `kappa_0`.

```text
suppression_bridge_coupling_identification=OPEN_LOCALIZABLE
```

## Named Bridge Rules

```text
BRIDGE_RULE_DIAGONAL_ONLY: beta_f=0, kappa_f=0
BRIDGE_RULE_MINIMAL_ANSATZ: beta_f=(1/21)Pi_f, kappa_f=1/[21||v_f||^2_ch]
BRIDGE_RULE_SYMBOLIC_OPEN: topology present, magnitudes open
```

The default diagnostic bridge rule remains `BRIDGE_RULE_MINIMAL_ANSATZ`, but it
is labeled as an ansatz, not as a derived bridge action source.

No observed masses, CKM, PMNS, neutrino data, measured fine-structure alpha, or
empirical target ratios are used.

Frozen predictions changed: no.

Official predictions changed: no.

Numerical closure: `OPEN`.
