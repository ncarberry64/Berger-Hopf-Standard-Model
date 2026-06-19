# Boundary Graded Defect Action Kernel v1

Current public status: structural architecture integrated conditional; numerical closure open.

This sprint packages the sector-defect machinery behind the full freeze
protocol and charged `K_f` candidate generator into an explicit symbolic action
kernel scaffold. It does not add predictions, does not use empirical inputs,
and does not alter frozen or official prediction outputs.

## Relation To PR #25 And PR #26

PR #25 implemented the full freeze protocol and the minimal charged `K_f`
candidate generator. PR #26 audited which of those objects had action/source
support and which remained open.

This sprint turns the sector-defect part into a small deterministic kernel:

```text
Delta_IT(C,sigma;q,j) = Omega(C,sigma;q,j) - Tr(Gamma_T|E_A(C,sigma))
S_index_trace = lambda_IT Delta_IT^2
```

The kernel selects admissible sector modes. It is not a charged hierarchy
Hessian and it does not decide charged masses.

## Sector Labels And Projectors

The kernel uses:

```text
C in {0,1}
sigma in {+1,-1}
P_C = C
P_+ = (1+sigma)/2
P_- = (1-sigma)/2
P_d = P_C P_- = C(1-sigma)/2
```

The sector projectors are:

```text
P_nu = (1-C)(1+sigma)/2
P_l = (1-C)(1-sigma)/2
P_u = C(1+sigma)/2
P_d_sector = C(1-sigma)/2
```

The file distinguishes `P_d` as the color-lower overlap activator from
`P_d_sector` as the down-sector projector.

## Primitive Defect Readouts

| Object | Activator | Readouts | Role | Status |
| --- | --- | --- | --- | --- |
| `D_C` | `P_C` | rank `1+P_C`; orientation `2P_C-1` | quark target doubling and `q` sign flip | `DERIVED_CONDITIONAL_ON_EXPLICIT_BOUNDARY_ACTION_KERNEL` |
| `D_d` | `P_d=P_C P_-` | rank `1+P_d`; Hopf multiplier `1+P_d` | down target factor and down `+4j` coefficient | `DERIVED_CONDITIONAL_ON_EXPLICIT_BOUNDARY_ACTION_KERNEL` |
| `Gamma_sigma` | `sigma` | Hopf sign `-sigma`; leptonic target sign `-(1-C)sigma` | weak-orientation grading | `DERIVED_CONDITIONAL_ON_EXPLICIT_BOUNDARY_ACTION_KERNEL` |
| `Gamma_T` | `tau(C,sigma)=C-(1-C)sigma` | signed target trace | target orientation | `DERIVED_CONDITIONAL_ON_EXPLICIT_BOUNDARY_ACTION_KERNEL` |
| `E3` | universal module | rank `3` | reference slot plus two excitation slots | `DERIVED_CONDITIONAL_ON_EXPLICIT_BOUNDARY_ACTION_KERNEL` |
| `E_A` | `E3 tensor E_C tensor E_d` | rank `3(1+P_C)(1+P_d)` | incidence target module | `DERIVED_CONDITIONAL_ON_EXPLICIT_BOUNDARY_ACTION_KERNEL` |

These are conditional kernel objects. They are not a full derivation from the
complete Berger-Hopf action.

## Unified Sector Formulas

The unified winding index is:

```text
Omega(C,sigma;q,j) = (2P_C-1)q + 2(-sigma)(1+P_d)j
```

Equivalently:

```text
Omega(C,sigma;q,j) = (2C-1)q - 2 sigma [1+C(1-sigma)/2]j
```

The incidence target is:

```text
A(C,sigma)=3(1+P_C)(1+P_d)
```

The target orientation and signed target are:

```text
tau(C,sigma)=C-(1-C)sigma
T(C,sigma)=tau(C,sigma)A(C,sigma)
```

Sector equations:

| Sector | Equation |
| --- | --- |
| neutrino | `-q-2j=-3`, equivalently `q+2j=3` |
| charged lepton | `-q+2j=3` |
| up | `q-2j=6` |
| down | `q+4j=12` |

## Ledgers And Tangents

| Sector | Ledger | Tangent |
| --- | --- | --- |
| neutrino | `[(0,0), (3,0), (1,1)]` | `(-2,1)` |
| lepton | `[(0,0), (1,2), (3,3)]` | `(2,1)` |
| up | `[(0,0), (6,0), (8,1)]` | `(2,1)` |
| down | `[(0,0), (0,3), (4,2)]` | `(4,-1)` |

The reference slot `(0,0)` is not required to satisfy the nonzero excitation
equation. The two non-reference modes in each sector satisfy:

```text
Delta_IT=0
S_index_trace=0
```

Status:

```text
zero_defect_tangent_adjacency: DERIVED_CONDITIONAL_ON_SECTOR_ENGINE
```

## S_index_trace Constraint

The symbolic kernel includes:

```text
S_index_trace = lambda_IT Delta_IT^2
```

This is an admissibility penalty/constraint. It selects modes satisfying
`Delta_IT=0`.

Important guardrail:

```text
charged_Hessian_from_S_index_trace=INVALIDATED_DO_NOT_CLAIM
```

Reason: the Hessian of `(Omega-T)^2` in `(q,j)` is rank one and generally has
`qj` cross terms. It selects admissible modes, but it is not the charged
hierarchy Hessian and does not produce `N_ch(q,j;rho_ch)=q^2+rho_ch j^2`.
S_index_trace is not the charged Hessian.

## Status Lines

```text
Boundary_Graded_Defect_Action_Kernel_v1: DERIVED_CONDITIONAL_ON_EXPLICIT_BOUNDARY_ACTION_KERNEL
Boundary_Graded_Defect_Theorem: DERIVED_CONDITIONAL_ON_EXPLICIT_BOUNDARY_ACTION_KERNEL
D_C_colored_contact_defect: DERIVED_CONDITIONAL_ON_EXPLICIT_BOUNDARY_ACTION_KERNEL
D_d_color_lower_overlap_contact_defect: DERIVED_CONDITIONAL_ON_EXPLICIT_BOUNDARY_ACTION_KERNEL
Gamma_sigma_weak_orientation_grading: DERIVED_CONDITIONAL_ON_EXPLICIT_BOUNDARY_ACTION_KERNEL
Gamma_T_target_orientation_trace: DERIVED_CONDITIONAL_ON_EXPLICIT_BOUNDARY_ACTION_KERNEL
E3_universal_rank_three_closure: DERIVED_CONDITIONAL_ON_EXPLICIT_BOUNDARY_ACTION_KERNEL
EA_incidence_module_factorization: DERIVED_CONDITIONAL_ON_EXPLICIT_BOUNDARY_ACTION_KERNEL
Delta_IT_index_trace_defect: DERIVED_CONDITIONAL_ON_EXPLICIT_BOUNDARY_ACTION_KERNEL
S_index_trace_constraint: DERIVED_CONDITIONAL_ON_EXPLICIT_BOUNDARY_ACTION_KERNEL
unified_Omega_projector_formula: DERIVED_CONDITIONAL_ON_EXPLICIT_BOUNDARY_ACTION_KERNEL
sector_target_incidence_product_A: DERIVED_CONDITIONAL_ON_EXPLICIT_BOUNDARY_ACTION_KERNEL
orientation_trace_Gamma_T: DERIVED_CONDITIONAL_ON_EXPLICIT_BOUNDARY_ACTION_KERNEL
zero_defect_tangent_adjacency: DERIVED_CONDITIONAL_ON_SECTOR_ENGINE
charged_Hessian_from_S_index_trace=INVALIDATED_DO_NOT_CLAIM
B_supp_universal_suppression_operator: OPEN_LOCALIZABLE
g_ch_phase_normalized_coupling: STRONGLY_SUPPORTED_CANDIDATE
rho_ch_exact_value: OPEN_LOCALIZABLE
full_threshold_operator: OPEN
RG_transport: OPEN
numerical_closure: OPEN
```

## What Moved Closer

The sector action kernel is now explicit as a conditional scaffold. The kernel
contains the projector readouts, incidence rank, oriented target trace,
index-trace defect, and symbolic constraint needed to generate the sector
equations.

## What Remains Open

- full derivation of the primitive objects from the complete Berger-Hopf action;
- charged suppression operator `B_supp`;
- phase-response normalization for `g_ch`;
- exact `rho_ch`;
- charged Hessian source;
- full threshold operator;
- RG transport;
- numerical closure.

## Do Not Claim

- Do not claim full action derivation unless all primitive objects are sourced.
- Do not claim charged-mass derivation from this kernel.
- Do not claim `rho_ch` is selected.
- Do not claim CKM/PMNS closure.
- Do not claim `B_supp` or `g_ch` are derived from this kernel.
- Do not claim `S_index_trace` gives the charged Hessian.
- Do not claim BHSM is complete, proven, numerically closed, empirically
  validated, or a Standard Model replacement.

## Guardrails

No observed charged-lepton masses, observed quark masses, CKM values, PMNS
values, neutrino mass splittings, measured fine-structure alpha, empirical
target ratios, or post-comparison branch selection are used.

Frozen predictions changed: no.

Official predictions changed: no.

Final public status:

```text
structural architecture integrated conditional; numerical closure open
```
