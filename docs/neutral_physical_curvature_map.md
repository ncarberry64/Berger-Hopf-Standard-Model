# BHSM Neutral Physical Curvature Map

Status: `CONDITIONAL_PHYSICAL_CURVATURE_MAP_CANDIDATE`.

BHSM provides the dimensionless response

```text
R_nu = max(0, p g_nu ||K_nu psi||/||psi|| - kappa_nu).
```

The legacy corpus separately defines `K[rho] = -nabla^2 ln rho`, which has
dimension `length^-2` on a physical spatial metric. The conditional neutral
map is therefore written

```text
k_neutral,eff = kappa_curv R_nu,
[kappa_curv] = m^-2.
```

The form is explicit, but `kappa_curv` is not derived. Boundary stiffness and
physical transport normalization remain missing.

A dimensionless neutral kernel response is not by itself a curvature in m^-2.

