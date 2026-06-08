# BHSM v1.6 Scalar/Topographic Screening Note

BHSM v1.6 builds a scalar/topographic screening proof scaffold by deriving or constraining derivative-screening and curvature-screening channels. It does not claim a full scalar-screening theorem unless all matter-coupling and fifth-force risks are closed from the complete action.

## Status

| Item | Result |
| --- | --- |
| Scalar/topographic screening status | `SCREENING_SCAFFOLD_PASSES` |
| Theorem complete | `False` |
| v1.5 modes audited | `6` |
| Current `OPEN_SCALAR_RISK` rows | `0` |
| Direct light scalar falsifier retained | `True` |
| Frozen BHSM predictions changed | `False` |

## Derivative Screening

The derivative-screening scaffold constrains topographic/scalar modes to current-type interactions:

```text
L_int ~ (1/M_*) partial_mu phi J^mu_topo
```

In the static, long-wavelength fifth-force limit, the derivative factor suppresses ordinary scalar-charge mediation, provided no direct `phi psi_bar psi` term is reintroduced by boundary terms.

## Curvature Screening

The curvature-screening scaffold constrains topographic modes to curvature/topographic sources:

```text
L_int ~ phi R_topo
```

In the local flat or low-curvature comparison limit, `R_topo -> 0`, so the screened mode is not treated as an ordinary long-range fifth-force mediator.

## Matter-Coupling Audit

Every v1.5 scalar/topographic mode receives a matter-coupling classification:

- Higgs projection: allowed SM scalar.
- Hopf/H_T complement modes: excluded by lift/mass gap.
- Derivative-screened mode: not an ordinary static fifth-force mediator.
- Curvature-screened mode: suppressed in the local flat limit.
- Virtual-only topographic mode: not an on-shell mediator.
- Direct unscreened light scalar: retained as a forbidden falsifier channel.

## Claim Boundary

The v1.6 scaffold is stronger than the v1.5 channel inventory, but it remains a scaffold. It does not prove global scalar/topographic decoupling from the complete Berger-Hopf action, and it does not alter `BHSM_BARE_V1`, `BHSM_DRESSED_V1_CANDIDATE`, canonical constants, frozen outputs, tolerances, mode ledgers, QCD/RG outputs, or `Z_virt^{u,2}=1/2`.
