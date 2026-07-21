# BHSM v5.11 Full Geometric and Gauge-Fixed Hessian

Primary result: `BHSM_QUADRATIC_OPERATOR_COMPLEX_PARTIAL`.

## Scope

BHSM v5.11 constructs the strongest source-qualified quadratic-operator architecture supported by v5.4-v5.10. It inventories every declared field and symmetry, classifies all 36 blocks of the six-sector Hessian, derives formal ghost operators from explicitly conventional gauge candidates, and audits domains, boundary forms, symbols, zero/negative modes, and heat-kernel inputs.

This is not a complete gauge-fixed Hessian. The geometric Hessian remains a symbolic action slot; gauge functionals and compatible ghost boundary conditions are not BHSM-derived; the fermion source, domain, and eta phase are open; and charged/neutral operators are incomplete. No total determinant or Casimir energy is calculated.

## Background and stationarity

The declared background is `B0=(g0=L^2 ghat(a0),a0,collar,T0=Phi0=1/(2 sqrt(2)),sigma_scale=1/2,A0=0,psi0=0,Jch0=0,N0=0)`. The scalar/topographic background is exactly stationary only in the v5.7 homogeneous reduced model. Other zero fields are conditional on source-free equations and closed domains. Geometry, squashing, and full collar equations remain unresolved, so the complete background is off shell. Unresolved first variations remain tadpoles; they are not masses or stability data. The classical global scale remains flat.

## Operator architecture

The ledger includes metric/collar geometry, `U(1)`, `SU(2)`, and `SU(3)` connections, fermions, `T`, `Phi`, the charged-current composite, neutral response, collective variables `(L,a_Berger,sigma_scale,rho_star)`, ghosts, and candidate auxiliaries. Diffeomorphisms and local internal transformations are present. No scalar shift or independent collar gauge symmetry is introduced.

Every block in the ordered `(g,A,psi,ST,ch,nu)` matrix records its formula or source gap, order, symbol, domain/codomain, adjoint relation, and coefficient source. Nonzero stress and response mixings remain explicit; zero blocks require a stored-action, projector, or background argument.

The conventional geometric gauge is `F_A=nabla^B h_AB-(1/2)nabla_A h`, with formal FP operator `M_A^B=-nabla^2 delta_A^B-R_A^B`. The internal candidate `G_i=D_i^dagger a_i` gives `M_i=D_i^dagger D_i`. These are candidate architectures, not BHSM-derived gauges. No boundary completion is selected, and the conformal mode remains unresolved. Numerical gauge couplings are not introduced.

The strongest fermion formula is `D_BHSM=gamma^A(nabla_A^spin+sum_i A_A^(i)P_i)`, with symbol `i gamma^A k_A`. No closed Yukawa/topographic mass source exists. Bag, chiral, APS, and collar boundary candidates remain unselected; index, eta, and determinant phase are open.

## Scalar, charged, and neutral sectors

The formal scalar matrix is `diag(-partial_rho^2+5,-Delta_B+5)` with off-diagonal trace/extension maps `-I_mix` and `-I_mix^dagger`. Those maps need a domain connecting collar `T` to boundary `Phi`. On the exact homogeneous v5.7 subspace, the matrix is `[[5,-1],[-1,5]]`, with parallel eigenvalue `4/L^2` and orthogonal eigenvalue `6/L^2`. This recovers v5.10 exactly. The complete nonhomogeneous zero/negative spectrum is open.

The charged-current object is a projected composite and has no independent determinant. No mediator is invented. The neutral sector retains symbolic `K_neu`; its normalization, domain, auxiliary elimination, and determinant ownership remain open. Dimensionless neutral structure is kept separate from any physical neutrino scale.

## Boundary and spectral readiness

Only the homogeneous scalar Robin domain has a closed vanishing boundary form. Full geometric, gauge/ghost, fermion, and neutral self-adjoint domains are open. Formal bulk symbols are elliptic after candidate gauge fixing, but strong ellipticity with boundary is not established. Pure gauge kernels need compatible FP quotients; physical collective variables are retained with Jacobians. The known `L` measure is `dL/L`; other collective Jacobians remain open. No unresolved negative mode is silently removed.

## Reduced consistency model

The finite model uses `(h_phys,h_gauge,A_phys,A_gauge,T,Phi)`. Its positive physical sample coefficients `2` and `3` are diagnostic conventions, not action-derived spectra. The raw matrix is `diag(2,0,3,0)` direct-sum `[[5,-1],[-1,5]]`. Gauge fixing replaces the two gauge zeros by `1/xi_g` and `1/xi_i`; unit ghosts follow from `delta x_gauge/d epsilon=1`. The physical eigenvalues `(2,3,4,6)` and normalized quotient `144` are gauge-parameter independent. This is bookkeeping, not a field-theory determinant or Casimir calculation.

## Preserved results and blockers

The v5.10 result remains `BHSM_QUANTUM_EFFECTIVE_ACTION_PARTIAL` and its `6/L^2` determinant is not promoted to the official effective action. No matter-only, gauge-plus-ghost, fermionic, or full one-loop calculation is permitted. `sigma_scale=1/2`, `M_BH/M_star=1/2`, and `R_BH/ell_star=2` remain relative. The old curvature-threshold mass-gap theorem remains invalidated.

Open gates include `OPEN_MISSING_ACTION_DERIVED_GEOMETRIC_HESSIAN`, `OPEN_MISSING_FULL_GAUGE_FIXED_DOMAIN`, `OPEN_MISSING_FADDEEV_POPOV_GHOST_OPERATOR`, `OPEN_MISSING_FERMION_DIRAC_OPERATOR_ACTION_SOURCE`, `OPEN_MISSING_FERMION_DETERMINANT_PHASE_ETA_INVARIANT`, `OPEN_MISSING_STRONG_ELLIPTICITY_WITH_BOUNDARY`, `OPEN_MISSING_FIELD_THEORETIC_HEAT_KERNEL_COEFFICIENTS`, `OPEN_MISSING_ABSOLUTE_UNIT_ANCHOR`, and `FULL_BHSM_NOT_COMPLETE`.

No physical validation, Casimir energy, absolute unit, particle mass, gauge coupling, CKM completion, rare-B prediction, Yang-Mills mass gap, full Standard Model derivation, or full BHSM completion is claimed.

Command: `python -m bhsm.interface full-geometric-gauge-fixed-hessian-status --format markdown`.
