# BHSM Chiral Current Attachment Map v0.6

Machine-readable artifact:

```text
artifacts/BHSM_chiral_current_attachment_map_v0_6.json
```

Target current families:

```text
L_CC,q = (g_2 / sqrt(2)) * ubar_i gamma^mu P_L V_CKM_BH[i,j] d_j W_plus_mu + h.c.
L_CC,l = (g_2 / sqrt(2)) * ellbar_i gamma^mu P_L U_PMNS_BH[i,j] nu_j W_minus_mu + h.c.
```

Current statuses:

```text
lorentz_structure_status = STANDARD_HEP_TARGET_CONVENTION
mixing_matrix_status = DERIVED_FROM_REPO_ARTIFACT
coupling_status = SCHEME_CONDITIONAL
field_dictionary_status = CANDIDATE
canonical_normalization_status = TARGET_CONVENTION_PARTIAL
mass_width_scheme_status = OPEN
renormalization_scheme_status = OPEN
feynrules_ready = false
ufo_ready = false
```

The CKM/PMNS matrices are carried as BHSM sources. The standard charged-current
Lorentz structure is a target convention, not empirical validation and not a
complete production FeynRules vertex.

The charged boundary response and neutral kernel remain boundary-source objects:

```text
Psi_bar_ch C_ch_boundary Psi_ch X_ch
Psi_bar_nu K_nu Psi_nu
```

Both remain `feynrules_ready = false` and `ufo_ready = false`.

## Phase Three-E Follow-On

Phase Three-E keeps the CKM/PMNS target currents as source-traced target maps
while exporting gauge-fixing and production-coupling scheme candidates. The
candidate couplings remain `SCHEME_CONDITIONAL`; no production vertex table is
claimed.
