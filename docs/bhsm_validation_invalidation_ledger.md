# PO-BH-64 - Validation / Invalidation Ledger

Current public status: structural architecture integrated conditional; numerical closure open.

## Validated Or Strengthened

- sector projector compression survives;
- `Z_virt` dimension-ratio path strengthened;
- down-sector extra incidence strengthened;
- three-state ladder strengthened;
- `eta_l` as boundary projection factor strengthened;
- `alpha_geom` must be internally derived.

## Invalidated Or Downgraded

- H=I as a locked claim;
- exact `q^2+j^2` costs as unconditional;
- old `eta_l` fitted value as derivation;
- `8/9` `eta_l` route as primary derivation;
- using measured alpha as derivation;
- using `q/2,j` isotropic metric as default charged cost basis.

## Still Open

- `rho_ch`;
- action source for charged Hessian;
- `Pi_l`;
- `alpha_geom`;
- `eta_l` exact value;
- action derivation of target amplitude;
- action derivation of rank-three ladder;
- action derivation of down extra incidence;
- `Z_virt` virtual-pair applicability proof;
- numerical mass closure;
- CKM numerical closure;
- PMNS numerical closure;
- neutral/topographic suppression values.

## Conservative Conclusion

PO-BH-64 strengthens the structural projector and Hessian-fork audit while
keeping numerical closure open. It changes no frozen predictions and makes no
official prediction update.

## PO-BH-65 Update

Validated:

- charged qj cross-term remains absent;
- charged/neutral Hessian split remains valid;
- `rho=1` remains the minimal closure candidate;
- `rho=3` remains possible only if a cyclic j-weight source is later derived.

Invalidated or downgraded:

- claiming `rho=3` is derived merely because 3 is the base cyclic factor;
- claiming `rho=1` is derived merely because old costs used `q^2+j^2`;
- finalizing `eta_l` before `rho_ch` is derived;
- using neutral/topographic anisotropy as charged-sector anisotropy without explicit coupling.

## PO-BH-66 Update

Validated:

- `Z_virt` has a clean dimension-ratio route if the two-door pair applies;
- `dim(V_pair^u)=2`, `rank(A_virt^u)=1`, and `Z_virt^{u,2}=1/2` are formalized as a candidate virtual-door ratio;
- the ratio is independent of observed masses;
- the physical interpretation remains one allowed virtual door out of two possible doors.

Invalidated or downgraded:

- claiming `Z_virt` is fully derived without the applicability proof;
- using charm/top or up/top to justify the factor;
- treating the ratio as a fitted correction.

Still open:

- applicability of the two-door pair to the relevant up-sector virtual correction;
- `rho_ch`;
- `eta_l`;
- numerical mass closure;
- CKM numerical closure;
- PMNS numerical closure;
- neutral/topographic suppression values.

## PO-BH-67 Update

Validated:

- dimension-ratio mechanics from PO-BH-66 remain valid;
- the actual frozen dressed-branch path is localized through `build_bhsm_dressed_v1_candidate`, `pure_fiber_middle_up_rule`, and `apply_virtual_dressing`;
- the two-door virtual interpretation remains a strong candidate;
- no mass input may justify `Z_virt`.

Invalidated or downgraded:

- any source that treats `Z_virt` as derived only because it appears in frozen predictions;
- any source that treats charm/top agreement as derivation;
- any source that uses observed ratios to choose the factor.

Still open:

- actual applicability link between the middle-up dressing source and `V_pair^u`;
- `rho_ch`;
- `eta_l`;
- `Pi_l`;
- `alpha_geom`;
- numerical mass closure;
- CKM numerical closure;
- PMNS numerical closure;
- neutral/topographic suppression values.

## PO-BH-68 Update

Validated:

- `V_weak=span{door_upper,door_lower}` has dimension 2;
- `P_u=diag(1,0)` has rank 1;
- `WEAK_DOUBLE_PROJECTION=rank(P_u)/dim(V_weak)=1/2`;
- the actual middle-up source path uses `WEAK_DOUBLE_PROJECTION`;
- no observed data are used to set the factor.

Invalidated or downgraded:

- treating the old `Z_virt` entry as merely a legacy numerical candidate after
  the weak-double projection bridge;
- using observed ratios to justify the bridge.

Still open:

- full virtual loop/threshold source;
- `rho_ch`;
- `eta_l`;
- `Pi_l`;
- `alpha_geom`;
- numerical mass closure;
- CKM numerical closure;
- PMNS numerical closure;
- neutral/topographic suppression values.

## Full Freeze Protocol / Charged K_f Update

Validated or strengthened:

- the derive -> freeze -> predict -> compare rule is recorded as the required
  protocol before any external comparison;
- the unified `Omega(C,sigma)` projector formula is implemented as a
  `STRONGLY_SUPPORTED_CANDIDATE`;
- the incidence target `A(C,sigma)` and oriented target `T(C,sigma)` are
  implemented as `STRONGLY_SUPPORTED_CANDIDATE` objects;
- the boundary graded defect equation `Delta_IT=Omega-T` reproduces the
  non-reference ledger modes conditionally on the sector engine;
- `rho_ch in {1,2,3}` is emitted as a branch set while
  `rho_ch_exact_value` remains `OPEN_LOCALIZABLE`;
- charged suppression fractions are exact structural candidates:
  `g_ch=1/21`, `Pi_l=1/7`, `Pi_u=2/7`, `Pi_d=4/7`,
  `eta_l=20/3087`, `eta_u=38/3087`, and `eta_d=68/3087`;
- the minimal real tridiagonal charged `K_f` generator is implemented as
  `minimal_charged_Kf_generator: STRONGLY_SUPPORTED_CANDIDATE`;
- the only threshold insertion is operator-level `(ln 2)` on the up-sector
  `(6,0)` construction-basis slot.

Invalidated or downgraded:

- choosing `rho_ch` by mass, CKM, PMNS, neutrino, measured-alpha, target-ratio,
  or post-comparison residual data;
- applying threshold factors after diagonalization without an operator theorem;
- treating the candidate charged matrix spectra as numerical mass closure.

Still open:

- derivation of `D_C`, `D_d`, `Gamma_sigma`, `Gamma_T`, `E_3`, `E_A`, and the
  zero-defect constraint from the action;
- derivation of `B_supp` and phase response normalization;
- exact `rho_ch`;
- full threshold operator;
- RG transport;
- numerical closure.

## Boundary Action Source Audit for Charged K_f Update

Validated or strengthened:

- `D_C_colored_contact_defect`, `D_d_color_lower_overlap_contact_defect`, and
  `Gamma_sigma_weak_orientation_grading` have conditional support from the
  existing sector/projector scaffold;
- `Z_virt_u1` remains `DERIVED_CONDITIONAL`;
- tangent adjacency remains `DERIVED_CONDITIONAL_ON_SECTOR_ENGINE`;
- the minimal charged `K_f` generator remains a strong candidate with explicit
  source references and blocking notes;
- the audit table is machine-readable in
  `data/boundary_action_source_audit_kf_v1.json`.

Invalidated or downgraded:

- treating `B_supp` as action-derived without a direct boundary action source;
- treating `g_ch=1/21` as derived without phase-response normalization;
- treating `beta_f=g_ch Pi_f` or `kappa_f=g_ch/||v_f||^2` as derived without
  their charged action source;
- selecting exact `rho_ch` from down-sector near-degeneracy or any empirical
  residual;
- treating the single local threshold insertion as a full threshold operator.

Still open:

- action source for `Gamma_T`, `E_3`, `E_A`, and `Delta_IT`;
- `B_supp`;
- phase-response normalization for `g_ch`;
- exact `rho_ch`;
- action sources for `beta_f` and `kappa_f`;
- full threshold operator;
- RG transport;
- numerical closure.

## Boundary Graded Defect Action Kernel v1 Update

Validated or strengthened:

- an explicit symbolic action-kernel scaffold now contains `D_C`, `D_d`,
  `Gamma_sigma`, `Gamma_T`, `E_3`, `E_A`, `Delta_IT`, and
  `S_index_trace`;
- the unified formula
  `Omega(C,sigma;q,j)=(2P_C-1)q+2(-sigma)(1+P_d)j` reproduces the
  neutrino, lepton, up, and down sector equations;
- `A(C,sigma)=3(1+P_C)(1+P_d)`, `tau=C-(1-C)sigma`, and `T=tau A`
  reproduce the sector targets;
- the non-reference mode ledgers are zero-defect under `Delta_IT=Omega-T`;
- the zero-defect tangent-adjacency pattern is recorded as conditional on the
  sector engine.

Invalidated or downgraded:

- `charged_Hessian_from_S_index_trace=INVALIDATED_DO_NOT_CLAIM`;
- `S_index_trace` is an admissibility constraint, not the charged Hessian;
- no charged-mass, CKM, PMNS, or numerical closure claim follows from this
  kernel.

Still open:

- action source for `B_supp`;
- phase-response normalization for `g_ch`;
- exact `rho_ch`;
- action sources for `beta_f` and `kappa_f`;
- full threshold operator;
- RG transport;
- numerical closure.
