# Neutral Mass-Gap Action

The bundled scalar topographic EFT supplies an artifact-backed analogue:

```text
L = 1/2(dt phi)^2 - 1/2(grad phi)^2
    - lambda/2(-nabla^2 phi-k_loc)^2,
m_gap = sqrt(lambda) k_loc.
```

BHSM v1.3 records the conditional neutral generalization

```text
L_nu = 1/2 Z_nu(dt phi_nu)^2 - 1/2 Z_nu(grad phi_nu)^2
     - 1/2 A_nu(-nabla^2 phi_nu-K_neutral,eff)^2.
```

The scalar action shape is `ARTIFACT_BACKED_MASS_GAP_ACTION`. Its use in the
neutral sector is conditional: the repository does not derive numeric neutral
coefficients `A_nu` or `Z_nu` from that scalar analogue.

The v1.5 action inventory finds partial boundary/collar variational support but
does not identify normalized numeric `Z_nu` or neutral `A_nu_gap`.

BHSM does not use neutrino limits, PDG values, W calibration, empirical fitting, or legacy particle threshold tables to set the neutral spectral scale.
