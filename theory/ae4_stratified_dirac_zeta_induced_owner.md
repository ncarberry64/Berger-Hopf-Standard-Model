# AE4 stratified Dirac–zeta induced-action owner

BHSM now selects one microscopic coefficient owner for the zero-input branch:

```text
P_strat = D_strat^dagger D_strat on the zero-mode/BRST quotient,

Gamma_ind = -(1/2) STr integral_[ell_star^2,infinity]
              ds/s exp(-s P_strat),
```

with the relative zeta/eta prescription supplying the logarithmic order and
determinant phase. The zeta completion is not a second determinant. The old
attached zeta seed is replaced by the sourced proper-time superdeterminant,
as required by the v16.00 no-double-counting identity.

This is the foundational choice left open by v14.63 and isolated more sharply
by v14.64. The canonical exponential heat semigroup and geometric unweighted
direct-sum trace are adopted. The local M8, M5 and M4 actions are therefore
heat-kernel/boundary expansions of one functional, not separately normalized
Wilson sectors.

The retained v15.99–v16 regulator is the integrated heat kernel

```text
f_ell(u) = -(1/2) E1(ell^2 u),
```

not the raw heat trace. For every positive heat order `p`, its normalized
moment is derived exactly:

```text
F_p = -ell_star^(-p)/p.
```

At dimensionless `ell_star=1`, the relevant weights are

```text
F8=-1/8, F6=-1/6, F5=-1/5,
F4=-1/4, F3=-1/3, F2=-1/2.
```

Thus the generic moment freedom proved in v14.63 is removed: the positive
order M8/M5/M4 ratios depend on one common spectral length and no independent
profile moments. Order zero remains the relative zeta/logarithmic sector.

This selection does not manufacture the missing continuum operator. The
global self-adjoint relative-boundary Dirac domain, operator-valued
Calderón/Wentzell seam, eta phase, finite family Dirac operator, and physical
value of `ell_star` remain to be derived. Its owner rule is now fixed without
a new cutoff constant:

```text
Sigma_star = first future surface where
             E_impedance[Phi;Sigma] = E_core[Phi;Sigma]
             and outward spacetime support ceases,

ell_star = 1/E_impedance[Phi_star;Sigma_star]    (hbar=c=1).
```

This is a first inward/future crossing on the regular side, not evaluation of
an eliminated action at a singular endpoint. Black holes, magnetars, neutron
stars and atomic decay do not calibrate the threshold; they are downstream
tests of one native surface rule.

Physical time is future-directed only. The parent endpoint supplies the child
initial surface and all physical Green functions must be retarded. The heat
parameter is spectral proper time, not reversible physical time, and no
periodic-cycle surrogate may replace continuous Lorentzian frequency.

The proposed cross-scale stability variable
`rho_hold=E_mode/E_impedance[Phi;Sigma_enclosure]` is recorded only as a
hypothesis: `rho_hold<1` is the candidate stable side and `rho_hold=1` the
candidate first loss surface. Atomic lifetimes and the proposed increase of
holding instability toward macroscopic scales require an action-Hessian or
resonance-width derivation; they are not yet BHSM predictions. Consequently
no numerical particle coefficient or observable is promoted yet.

Scientific milestones:

```text
AE4_STRATIFIED_DIRAC_ZETA_MICROSCOPIC_OWNER_SELECTED = TRUE
AE4_POSITIVE_ORDER_M8_M5_M4_MOMENT_RATIOS_DERIVED = TRUE
AE4_ELL_STAR_NATIVE_COLLAPSE_SURFACE_OWNER_RULE_SELECTED = TRUE
AE4_FUTURE_DIRECTED_PARENT_CHILD_DOMAIN_SELECTED = TRUE
AE4_GLOBAL_SELF_ADJOINT_STRATIFIED_DIRAC_DOMAIN_DERIVED = FALSE
```

`FULL_BHSM_COMPLETE = FALSE`.
