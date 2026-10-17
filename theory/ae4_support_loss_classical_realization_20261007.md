# AE4 classical support-loss realization: operational event-definition stop

**Historical receipt, superseded 2026-10-08.** Norman's branch-relative support law now supplies `BRANCH_REALIZATION_TRANSFER_EVENT`; the old definition gap below is no longer current. The heat cutoff uses the created muon's side of precursor-loss/muon-birth, while muon decay is a later event. See [the current transition audit](ae4_branch_relative_support_transition_20261008.md). `SupportLossClassicalRealization.report()` publishes that current audit; `historical_report()` preserves this original finding and its committed receipts.

The first missing definition is **OUTWARD_SPACETIME_SUPPORT_CESSATION_EVENT_CONDITION**: an action-derived condition on the oriented full normal section that identifies cessation of outward spacetime support on the transported physical branch, at the first future surface where it and the separate energy equality both hold. No equation in the bounded inspection below operationally defines that condition. This milestone stops there as required; it does not select an event by an arbitrary zero or attempt a physical KKT solve.

Starting HEAD: `00fa89d62e4c74ee9fd0b41611b3468ad035b5db`. Scientific reference: `524ed90689bd5923c249bba2e699abf627e703cd`. Branch: `codex/muon-parent-maxwell-density-review`. The separate retention commit `3ea1ef306c0da8fea7894944a03c5361d83910ae` changes historical-artifact bookkeeping only.

## Owners and one realization contract

The retained classical mechanics owner is `BHSM-AE-3.2.16-COVARIANT-BUBBLE-INTERFACE-MECHANICS`. Its bulk/interface mode equation is

```text
I_lambda D_tau^2 a_lambda + [gamma J_Sigma + H_impedance] a_lambda = f_event,lambda.
```

It supplies the support-loss branch, full kinetic inertia, resistance, displacement, stationary response and reduced curvature. The downstream quantum owner is `BHSM-AE-4.0.0_STRATIFIED_DIRAC_ZETA_HEAT`, with

```text
Gamma_AE4 = -(1/2) STr E1(ell_star^2 P_strat) + relative-zeta/eta completion;
ell_star^2 = c = i/r.
```

The quantum heat consumes the classical cutoff. Its finite-E1 determinant is not added as another classical restoring density. The historical generic KKT/control machinery remains unchanged.

`SupportLossClassicalRealization` binds `Phi_star`, `Sigma_star`, `psi_star`, `xi_psi`, `b_psi`, `S_SL`, constraint map `R`, pairing, domain, stationary base and multipliers to one common requirement identity. That identity records the owner and the required common base/domain/pairing; it is explicitly **not** proof that a physical common pullback or solution has been instantiated. Each output is unevaluated and names the same first missing definition. The seven components of `b_psi` retain exactly three trace, two canonical momentum and two dynamic-flux slots, all null at this stop.

The physical source must use the initiating-event physical formation branch, continuously transported to the separate support-loss event. On each actually active regular stratum,

```text
xi_psi^(s) = psi_star^(s) n_star^(s),    dX/ds|_0 = xi_psi.
```

The registered regular pieces are `M8`, `M5+`, `M5-`, `M4`; their actual activation and mode components at support loss have not been evaluated. Two event/child trace copies belong to one abstract carrier with inherited opposite outward conormals. Non-null pieces use the owned unit normal; null pieces require the owned conormal-density convention. Corners bound the regular pieces and do not provide an independent carrier law. No descriptor, launch, SVD, Gate-7, arbitrary inverse, canonical basis, or N12 ordered-stop eigendirection replaces this section.

The current user's preferred normalization is `<psi_star,I_star psi_star>=1`, with the complete classical physical-clock kinetic form, including its bulk response. The retained spherical membrane Legendre Hessian `gamma_s Omega_p R^p/(1-Rdot^2)^(3/2)` is only a surface contribution. Neither that contribution nor a Euclidean norm substitutes for the full inertia. Base normalization has not been applied, and no vanishing `i_v`, `i_J`, or `i_vJ` is inferred from it.

## Concrete event audit

The adopted event is the conjunction

```text
<psi_star,(R_total-H_event,drive)psi_star> = 0
AND action-defined outward spacetime support ceases.
```

The reduction of energy equality presupposes the same physical mode, pairing and positive inertia on the same surface. Energy equality alone cannot select `Sigma_star`. Formation, an artificial C2 cut, canonical stop, descriptor zero, and the last cached history point remain distinct.

The inspected dynamic/conormal/Noether equations give the following retained progress, with exact source symbols and line references in `outward_support_audit.json`:

| Retained equation | Actual role and limit for this event |
| --- | --- |
| `P=v_lift^T L_v`, `F=q_lift^T L_q`, `M=F-G-DP[X]`; child matching `G_child+DP[X]-F+G_event=0` | Action-derived momenta and dynamic-flux matching. A zero matching residual balances two sides; it does not establish that outward support has ceased. |
| `Pi_parent+Pi_child_return+J+C^dagger lambda=0`; `sum_i 2 Re<Tq,Pi_i>=0` | Event stationarity and Noether conservation. The sum can vanish with nonzero individual currents. |
| AE3 internal `[Pi^n]=[T_nn]=[nJ]=0` | Smooth internal joining with opposite orientations, expressly distinct from a terminal/reset surface. |
| `q_D=-lambda_D log upsilon`, `L_D=-|dq_D|^2/2` | The selected Haar support kinetic action already exists. `upsilon=0` lies outside its regular chart at `q_D=+infinity`; this is not a supplied finite-event evaluator. |
| `S_attach=int_M5 <Lambda85,upsilon^(-1/2) I_W-upsilon^(1/2) I_C>`; `I_W=upsilon I_C`; `Box_G q_D=J_shift,inherited+J_attach` | The later v11.3 reciprocal attachment defines actual regular support evolution and compatibility. It is retained, not called missing. Its algebraic attachment adds no new derivative normal momentum; that does not zero inherited momentum or flux. |
| `I_W/I_C=upsilon -> 0`, `q_D -> +infinity`, bounded `I_C` | Conditional asymptotic wall-incidence suppression. Its source requires a separate topology-changing/de-envelopment domain; it does not identify a finite first-future cessation surface or prove equivalence to energy equality. |
| Zero regular symplectic flux in Neumann/terminal Dirichlet ensembles | Compatible with reflection or fixed boundary data; conservation alone does not imply support extinction. |
| `FUTURE_RETARDED_REGULARITY_OR_OUTGOING_SUPPORT_ONLY` | Allows outgoing causal support; does not establish its cessation. The canonical-stop Friedrichs closure is a separate endpoint-domain result. |
| `tau_decay=inf{tau>0:z_child(tau) notin B_child}` | Historical persistence-domain exit. No retained equivalence to the adopted energy-equality/cessation conjunction is proved. |

The minimal membrane normal traction and mode equation likewise balance support while it persists. Their retained instruction to compute outward Noether/radiative flux does not itself give the needed cessation predicate. This is a bounded inspection of the cited owner functions, not a theorem that no such definition could exist anywhere. The missing definition is one operational event condition, not absence of the support action or generic KKT algebra.

The later retained `aether_haar_barrier_v15_0.py` sharpens the endpoint distinction. On the regular domain with positive finite `lambda_D`,

```text
ds_D^2=lambda_D^2 dupsilon^2/upsilon^2=dq_D^2;
d(u,v)=lambda_D |log(u/v)|;
K_D=int_(tau0)^tau1 |dq_D/dtau|^2 dtau < infinity;
L_D=int |dq_D/dtau| dtau <= sqrt((tau1-tau0) K_D) < infinity.
```

Thus `upsilon=0` has infinite Haar distance and cannot be reached over finite exterior duration with finite positive regular Haar kinetic action. This conditional result concerns the positive kinetic path integral, not an arbitrary indefinite Lorentzian action. A bounded coordinate does not change the distance. The separate `C_A` schema expressly has no `upsilon` coordinate and is not identified with this endpoint. Neither result supplies a transition or a support-cessation predicate. A finite regular cessation event could have a different owned definition; none is chosen here.

Likewise, zero isolated shift current means `nabla q_D=0`, which only makes the regular `upsilon` constant; it does not make it vanish. Conservation constrains a sum of outward/return/interface/environment currents and does not force an individual outward current to zero. These are structural nonimplications of the retained equations, not newly simulated flux controls.

The expanded audit also retains the later attachment Gram/Wentzell response, tensor incidence differential/adjoint and second-shape/Jacobi equations. They provide conditional response and boundary-matching laws, with a strictly positive local attachment pencil under its stated assumptions. They do not add an equation selecting support extinction. The callable historical terminal `lambda_6(H_EulerDirac)` evaluator computes a different event. No retained equivalence to the adopted two-condition event is established.

## Classical scalar and constraint accounting

The inspected composition is

```text
S_SL = S_bulk,event + S_bulk,child + S_owned_boundary_corner
       - sum_s integral_(W_s) gamma_s dmu_h;
R(eta,X)=0;    L=S_SL+lambda^dagger R.
```

`classical_owner_audit.json` inventories the 13 registered geometric/scalar/cap/GHY/intrinsic matter/matcher terms at their original levels. They are not an instruction to sum duplicate `S8`, `S5|4` and `S4` descriptions across unowned reduction arrows. A current pullback and actually active terms still await the event. The current Path-B gauged eta replaces the older eta description, rather than adding a second co-varied physical scalar.

| Sector | Count once as |
| --- | --- |
| Active bulk geometry, scalars/topography, matter and minimal membrane | Originating classical scalar density on the selected compatible domain. Minimal membrane uses selected `W_s=1`, `gamma_s=alpha_FSC ell_s^(-m_s)`; no new bending, viscosity or seam density. |
| EH/GHY/Hayward | Existing coefficient-locked scalar completion, including `S_Hayward=kappa1 A_joint theta`. |
| Metric matcher, uneliminated gauge/BRST and reset/incidence constraints | Existing multiplier reaction or admissible domain. Metric matcher is in `lambda^dagger R`, not also multiplier-free `S_SL`. |
| AE2 fermion reset | Existing transmission-domain graph; independent seam scalar is the owned `S_Sigma,F,AE2=0`. |
| Trace, canonical momentum, conormal, dynamic flux | Derived Legendre/Green/material outputs of the originating scalar, not extra scalar densities. |
| Contacts and source-dependent constraint jets | Directional derivatives of the originating scalar or constraint, counted once. |
| Finite-E1 and relative-zeta/eta | Downstream quantum owner. |

Stationarity requires `L_eta=0` and `R=0` at the selected surface with actual multipliers and an explicit chart pullback if needed. This milestone records those requirements together; it borrows no historical lapse/shift/event coordinates. The actual base, domain, pairing and multiplier values remain null because the event definition has not been supplied.

The compatible-domain class is `C_reset(F_B,{L_sref})`: compatible event/child traces, owned constraints and AE4 future-retarded admissibility. The fermionic transmission graph is `Gamma0,c=U_R Gamma0,e`, `Gamma1,c=-U_R Gamma1,e` on `Dom(D^2)`; this does not silently construct the nonfermionic graph. The full reset decision explicitly leaves the single graph unconstructed. The actual regular carrier, reset map and common pullback have not been evaluated. They remain requirements to solve after a cessation definition is supplied; the first missing event definition is not a sufficiency theorem that everything else is already solved.

## Answers to the seven physical questions

| Question | Retained answer | Claim status |
| --- | --- | --- |
| 1. Exact classical action/domain? | The displayed total bulk/minimal-area/boundary-corner action and compatible regular reset/retarded domain class are selected. Registered strata require their original compatibility maps and once accounting. No evaluated current support-loss pullback/base/domain is supplied by the local kernel. | `DERIVED` laws; actual realization `UNEVALUATED` |
| 2. Operational outward-support-cessation equation? | Stress, canonical/conormal matching, dynamic-flux rows and Noether/support-current equations exist. None of the inspected equations defines the cessation predicate at the adopted energy equality. | `OWNER_DEFINITION_GAP` |
| 3. Actual first-future event on the retained branch? | No: the two-condition event cannot be selected without its second predicate. The historical terminal evaluator is a different event; the regular Haar endpoint is excluded under the finite-time/finite-positive-action hypotheses. | `UNEVALUATED` |
| 4. Transported `psi_star` there? | No event surface exists to restrict the continuous physical formation branch to. A local reduced-Hessian/reference-matched terminal eigenvector is not this complete interface normal section. | `UNEVALUATED` |
| 5. Normalized `xi_psi=psi_star n_star`? | The geometric rule and preferred full-action kinetic normalization are defined. At the unselected event neither the mode, normal nor full kinetic pairing has been evaluated. | `DERIVED` rule; value `UNEVALUATED` |
| 6. Existing 3+2+2 image? | Its exact kinematic operator is retained below. No physical seven-port values can be produced without the selected full normal source and same-base field/material response. | `DERIVED` map; physical image `UNEVALUATED` |
| 7. Actual stationary classical KKT base? | No evaluated base with `L_eta=0`, `R=0` and matching multipliers/pairing/domain is supplied at this event. Historical lapse/shift coordinates are not a canonical pullback to it. | `UNEVALUATED` |

For question 6 the retained operator is

```text
b_psi = [ T u_psi + (D_psi T)q                         ]  (3)
        [ D_psi P                                    ]  (2)
        [ D_psi F-D_psi G-D2P[X_flow,u_psi]
                         -DP[D_psi X_flow]           ]  (2).
```

`X_flow` is the full Euler-Dirac phase-flow tangent `(qdot,acceleration,multiplier_rate)` in the momentum rate. It is distinct from the carrier embedding `X_embed` displaced by `dX_embed/ds=xi_psi`. This operator retains the explicit shape/frame trace derivative and both momentum-rate derivatives exactly once. The scalar bordered reaction named `b_psi` in the historical C2 graph is not this seven-entry object. No full-history or precision requirement is used as the stopping reason.

The source/provenance inspection is `EVALUATED`; it does not evaluate physical operands. Previously demonstrated finite KKT/heat controls and diagnostic attachment blocks remain `CONTROL_ONLY` and were not rerun. The report explicitly carries all five labels: `DERIVED`, `EVALUATED`, `CONTROL_ONLY`, `UNEVALUATED`, `OWNER_DEFINITION_GAP`.

## Reproduction and downstream status

`scripts/audit_ae4_support_loss_classical_realization.py` loads the three reviewed provenance audits, verifies Python symbol/line references against the actual AST, binds the requirement contract and hashes the inspected text sources. It executes no numerical owner producer and loads no historical arrays. Materialization to `run_1` and `run_2` must yield byte-identical realization reports, source manifests and output hashes. Tests guard owner separation, the event conjunction, mixed bindings, nested provenance/report mutation, boundary-balance substitutions, full normal requirements, once-only sector accounting and the physical downstream stop.

At this exact definition stop, physical `h_psi`, `H_KKT`, `delta_psi`, `z_psi`, resistance/inertia and total jets are not reached. Consequently `c`, quantum heat, relative completion, subtraction, induced resistance, photon response, paired native heat, Pauli readout, `a_mu` and `g_mu` remain unevaluated. No new generic KKT algebra, finite-control run, Gate-7 campaign, 73-launch recomputation, residual-row reconstruction, optional seam, local QED, primitive-photon or previous family/mass-time calculation is reopened.

The public-readiness retention issue was already resolved at verified local/remote head `3ea1ef306c0da8fea7894944a03c5361d83910ae`; this scientific milestone changes no retention entry or historical array. New scientific audit commands, outputs, hashes and error scope are recorded in `verification.json` after execution.

The scientific result recorded by this milestone is the localization of the first missing definition, with concrete exclusions of the inherited substitutes. The retained action defines minimal-interface stress/mode balance, canonical/dynamic-flux matching, and sourced support evolution, but no inspected equation currently defines **the action-owned operational predicate for outward spacetime support cessation on the transported branch at the adopted energy equality**. Therefore `xi_psi` and support loss cannot yet be physically selected. This result goes beyond a typed object or generic absence statement: the regular Haar endpoint is conditionally inaccessible, balanced currents need not vanish individually, later nonzero shape/attachment response is retained, and the callable terminal event is distinguished explicitly.

### Executed verification

Git commands `git status`, `git rev-parse HEAD`, `git -c gc.auto=0 -c maintenance.auto=false fetch origin`, and `git rev-parse origin/codex/muon-parent-maxwell-density-review` succeeded; both hashes were `3ea1ef306c0da8fea7894944a03c5361d83910ae`. Existing scientific files were preserved.

```text
python -m pytest --noconftest -q tests/test_ae4_support_loss_classical_realization.py
15 passed in 0.77s

python scripts/audit_ae4_support_loss_classical_realization.py --out artifacts/ae4_support_loss_classical_realization_20261007/run_1
python scripts/audit_ae4_support_loss_classical_realization.py --out artifacts/ae4_support_loss_classical_realization_20261007/run_2
```

The resulting `realization_report.json` has 216,730 bytes and SHA-256 `221eb6731d9733c2c963043e207f7e7b1251c0454e0a83daf2840125725a9e72`. The two final directories contain byte-identical reports, source manifests and output-hash receipts. Exact stdout, byte counts, all product hashes and the comparator result are stored in `verification.json`. `source_manifest.json` records portable canonical-LF source hashes; the physical-questions audit distinguishes these from its raw Windows-checkout hash receipts. Product hashes are kept in the receipt so that hashing this theory source does not create a recursive manifest hash.

The initial expanded AST check failed on grouped symbol references and out-of-function citation lines. Group validation was corrected to check each line against the declared function/docstring spans; nine citation records were corrected (10 line-occurrence removals, five symbol-occurrence additions). The final audit verifies the cited symbols and bounds without executing owner functions. The focused tests all pass, including checks that nested report/provenance mutation cannot publish an arbitrary cessation condition. Publication commands and their outputs are recorded separately in `verification.json`; the previously resolved retention issue is unchanged.

Error scope: static equation/provenance and exact deterministic serialization checks only. No numerical event, mode, normal section, KKT source/solve, impedance, kinetic normalization, physical uncertainty bound or continuum truncation error is evaluated. No historical geometry result or finite control is promoted to a physical support-loss operand.
