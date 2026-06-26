# Bounded FeynRules-Prep Lagrangian

Machine-readable artifact:

```text
artifacts/BHSM_bounded_feynrules_prep_lagrangian_v1_2.json
```

Model label:

```text
BHSM_MINIMAL_COLLIDER_INTERFACE_PREP
```

The artifact is not a `.fr` file and not a UFO model.

Symbolic charged-current prep terms:

```text
L_CC_q_BHSM_CKM =
(g2_BH_runtime / sqrt(2)) * ubar_i gamma^mu P_L V_CKM_BH[i,j] d_j W_plus_mu + h.c.

L_CC_l_BHSM_PMNS =
(g2_BH_runtime / sqrt(2)) * ellbar_i gamma^mu P_L U_PMNS_BH[i,j] nu_j W_minus_mu + h.c.
```

`g2_BH_runtime` is a runtime/scheme parameter in
`BHSM_COLLIDER_INTERFACE` mode. Runtime values are
simulation/comparison inputs only and do not derive or retune BHSM constants.

`V_CKM_BH` and `U_PMNS_BH` are BHSM source matrices from repo artifacts.

