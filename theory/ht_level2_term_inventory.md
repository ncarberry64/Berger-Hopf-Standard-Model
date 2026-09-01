# BHSM v1.3A Level 2 H_T Term Inventory

Model level: `DIRAC_PROXY_LEVEL_2`
Theorem complete: `False`

This inventory records the terms already present in the Level 2 finite-basis H_T scaffold. It does not prove the full no-extra-light-state theorem.

| Term | Classification | Preserves zero modes | Can lower complement gap | Lower-bound method |
| --- | --- | --- | --- | --- |
| `berger_dirac_kinetic` | `DIAGONAL_EXACT` | `True` | `False` | exact diagonal minimum after complement restriction; min-max check after squaring |
| `hopf_twist` | `SIGN_INDEFINITE_BOUNDED` | `True` | `True` | Weyl bound with explicit coefficient and finite q range |
| `boundary_term` | `SIGN_INDEFINITE_BOUNDED` | `True` | `True` | Weyl bound using the bounded residual range in the finite basis |
| `chirality_term` | `SIGN_INDEFINITE_BOUNDED` | `True` | `True` | Weyl bound from explicit chirality coefficient |
| `sector_coupling` | `OFF_DIAGONAL_BOUNDED` | `True` | `True` | Gershgorin bound and restricted min-max finite-basis check |
| `heat_lift` | `PSD_EXACT` | `True` | `False` | PSD nonnegative monotone heat-lift inequality |
| `psd_profile` | `PSD_EXACT` | `True` | `False` | PSD nonnegative Weyl contribution |
| `zero_complement_projector` | `FINITE_BASIS_ONLY` | `True` | `False` | min-max restricted complement in finite basis |

## Term Limitations

- `berger_dirac_kinetic`: The term is exact only inside DIRAC_PROXY_LEVEL_2. A closed analytic Berger twisted-Dirac spectrum is not derived here.
- `hopf_twist`: The current lower bound is finite-basis bounded, not a global analytic q-bound.
- `boundary_term`: The full action-level uniqueness of the complete internal action remains open. A global analytic residual bound beyond the finite basis is not proven here.
- `chirality_term`: The chirality splitting is still a Level 2 proxy term.
- `sector_coupling`: This is the weakest matrix term for analytic upgrade because the present control is finite-basis. No infinite-basis operator-norm bound is proven here.
- `heat_lift`: The heat lift inherits any incompleteness in the lower bound for D^dagger D on the complement.
- `psd_profile`: The full curvature/profile operator from the action is not computed here.
- `zero_complement_projector`: This is the weakest analytic block: dim ker D_twist = 3 is not proven in the full action. The infinite-dimensional complement separation remains open.

## Global Limitations

- This inventory classifies the current Level 2 finite-basis proxy; it is not the full analytic H_T spectrum.
- Frozen v1.0/v1.1 predictions, constants, tolerances, and mode ledgers are not changed.
