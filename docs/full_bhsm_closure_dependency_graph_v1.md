# Full BHSM Closure Dependency Graph v1

Current public status: structural architecture integrated conditional;
numerical closure open.

This graph localizes the remaining closure dependencies. It does not compare to
observed masses, CKM, PMNS, neutrino data, measured alpha, or target ratios.

## Current Chain

```text
sector equations
-> mode ledgers
-> boundary graded defect action kernel
-> charged suppression kernel
-> charged K_f operator
-> bridge topology
-> threshold eligibility
-> neutral sector skeleton
-> RG/scheme transport interface
```

## Key Statuses

```text
boundary_graded_defect_action_kernel_v1=DERIVED_CONDITIONAL_ON_EXPLICIT_BOUNDARY_ACTION_KERNEL
B_supp_trace_kernel=DERIVED_CONDITIONAL
Rule_A_single_operator_trace=DERIVED_CONDITIONAL_ON_B_SUPP_TRACE_KERNEL
rho_ch_exact_value=OPEN_LOCALIZABLE
charged_Hessian_from_S_index_trace=INVALIDATED_DO_NOT_CLAIM
charged_Kf_tridiagonal_bridge_topology=DERIVED_CONDITIONAL_ON_E3_LADDER_AND_TANGENT_ADJACENCY
beta_f_reference_bridge_magnitude=OPEN_LOCALIZABLE
kappa_f_tangent_bridge_magnitude=OPEN_LOCALIZABLE
up_6_0_Zvirt_threshold=DERIVED_CONDITIONAL
full_threshold_operator=OPEN
neutral_sector_operator_kernel=STRUCTURALLY_MOTIVATED_CANDIDATE
neutral_Hessian_symbolic_form=OPEN_LOCALIZABLE
PMNS_numerical_closure=OPEN
RG_transport_interface=OPEN
numerical_closure=OPEN
```

## Claim Boundary

The dependency graph says what is derived, candidate, open-localizable, open, or
invalidated. It does not claim numerical closure or comparison-ready
predictions.

Frozen predictions changed: no.

Official predictions changed: no.
