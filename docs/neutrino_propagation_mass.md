# BHSM Neutrino Propagation Mass

In BHSM, the neutrino mass contribution is modeled as a propagation-locked
curvature response, not as an ordinary static rest-mass primitive.

The v0.9 candidate acts on a normalized physical neutral boundary field with
the artifact-backed kernel `K_nu`. The propagation variable `p >= 0` is a
dimensionless response activity, not an observed speed or fitted mass input.

```text
m_eff_dimless(psi,p)
  = tau max(0, p g_nu ||K_nu psi||/||psi|| - kappa_nu)
```

If the neutral propagation response is zero, the BHSM neutrino mass
contribution vanishes. The positive-part threshold law and its use as an
effective mass are author-ontology conditional. `K_nu`, `g_nu`, `kappa_nu`,
and dimensionless `tau` are local no-fit artifacts.

Status: `CONDITIONAL_NUMERICAL_CLOSURE_CANDIDATE`, dimensionless only.
