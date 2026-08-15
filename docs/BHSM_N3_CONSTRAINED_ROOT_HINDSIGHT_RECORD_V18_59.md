# BHSM N=3 constrained-root hindsight record v18.59

Status: **VALIDATED record; N=3 root remains ACTIVE/OPEN.**

The retained event state is `z in R^376`, its unchanged exact physical residual is `F(z) in R^376`, and the complete-child reconstruction chart is `c in R^26`. The established child correspondence `G(z,c)=0` contains 14 physical rows: three trace, seven local-constraint, two canonical-momentum, and two dynamic-flux rows. Repeated rank 14 therefore gives regular local chart nullity 12. That nullity is chart freedom under the existing equations, not twelve new physical parameters.

The actual target is:

`find z* in A such that F(z*)=0`,

where `A` is the already implemented eta, fresh complete-child reconstruction, unchanged two-scale flux, and positive-duration persistence gate. This description adds no equation 377, does not promote the flux inequality into the KKT system, and does not change the physical solve.

## State hindsight

The deterministic artifact preserves six accepted and two rejected candidates from v18.33 through v18.58. In particular, v18.43/v18.45 reached exact norm `0.816723990665515` but was rejected solely by its `2.2758236534e-5` flux envelope; v18.50/v18.52 reached `0.817749466104251` but was likewise rejected at `2.0920371105e-5`. Both are lower in scalar residual than at least one later accepted state. Thus physical admissibility is not scalar residual ordering, and the complete-child gate is nonredundant.

## Admissible-corridor measurement

Across accepted v18.33, v18.37, v18.41, v18.47, v18.54, and v18.58 states, none of the following is observed monotonically: collapse of flux margin, approach of eta to zero, degradation of child rank, or degradation of persistence residual.

The currently observed admissible corridor does not show a monotonic collapse toward the flux, eta, rank, or persistence boundaries over the measured accepted frontier.

This finite record is not proof that `A intersection F^{-1}(0)` is nonempty. That statement remains open until the N=3 root closes.

## Durable classifications

- **VALIDATED:** moving complete-child reconstruction, rank-14 child rows, nullity-12 regular local chart, positive-duration nonzero relative evolution, direct-response plateaus, and lower-merit admissible continuation through v18.58.
- **INVALIDATED:** equation 377, staticity/fixed return, terminal-only child solvability, componentwise or event-row monotonicity, decreasing motion, and raw step size or condition number as physical-stiffness proof.
- **RECLASSIFIED:** Krylov/JFNK vectors propose geometry; exact nonlinear `F_376` decides merit; eta, fresh child, flux, and persistence decide physical promotion.
- **ACTIVE:** `CONTINUE_PHYSICALLY_ADMISSIBLE_EXACT_376_ROW_DESCENT_FROM_THE_LATEST_ACCEPTED_FRONTIER_TO_F376_ZERO`.

Machine-readable source: `artifacts/BHSM_aether_n3_constrained_root_hindsight_record_v18_59.json`.
