# Normalized Charged-Current Action Term

Status: `OPEN_MISSING_NORMALIZED_CHARGED_CURRENT_ACTION_TERM`.

Located candidate term: `L_CKM_charged_current_bounded`.

Symbolic target form:

```text
(g2_BH_runtime / sqrt(2)) * ubar_i gamma^mu P_L V_CKM_BH[i,j] d_j W_plus_mu + h.c.
```

The repository contains charged-current target/interface terms, including a bounded collider-interface term and a `+ h.c.` target convention. These sources do not yet constitute a normalized BHSM charged-current action term with an action-derived operator domain and codomain.

The normalized charged-current action term, not arithmetic channel-count coincidence, must select the CKM transport space.

No empirical CKM fitting, charged-mass fitting, PDG values, W calibration, neutrino limits, or legacy threshold tables are used as theorem inputs.

The v2.7 audit promotes the candidate only to `ARTIFACT_BACKED_BOUNDED_CKM_INTERFACE_TERM`. L_CKM_charged_current_bounded is a bounded interface term, not automatically a normalized action-selected transport operator.
