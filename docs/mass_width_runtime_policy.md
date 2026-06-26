# Mass-Width Runtime Policy

Machine-readable artifact:

```text
artifacts/BHSM_mass_width_runtime_policy_v0_8.json
```

## Policy

`kappa_H = 64*pi^5` is a BHSM profile Hessian curvature, not automatically a
collider Higgs mass.

`BHSM_PURE_NOFIT` does not import PDG masses or widths.

`BHSM_COLLIDER_INTERFACE` may accept external mass/width cards as runtime
simulation inputs only.

Runtime mass/width inputs do not modify BHSM constants, boundary coefficients,
mixing matrices, or frozen predictions.

A production UFO may require runtime mass/width cards for practical event
generation, but those cards are not derivation inputs.

No fake mass or width numbers are inserted.

## Phase Three-G Follow-On

Phase Three-G attaches this runtime policy to candidate vertices and symbolic
Lagrangian terms. The policy does not close pure no-fit mass-width closure and
does not create event-generation readiness.
