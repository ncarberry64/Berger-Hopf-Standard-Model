# BHSM Canonical Field Target Conventions v0.6

Machine-readable artifact:

```text
artifacts/BHSM_canonical_field_target_conventions_v0_6.json
```

Canonical target forms:

```text
scalar:  +1/2 partial_mu phi partial^mu phi
vector:  -1/4 F_munu F^munu
fermion: i psibar gamma^mu D_mu psi
```

Current classifications:

| convention | Z symbol | classification | UFO ready |
| --- | --- | --- | --- |
| scalar field | `Z_H = 1` | `BHSM_DERIVED_VALUE` | false |
| vector gauge field | `Z_A,target = 1` | `STANDARD_HEP_TARGET_CONVENTION` | false |
| fermion field | `Z_psi,target = 1` | `STANDARD_HEP_TARGET_CONVENTION` | false |

Setting `Z_A,target = 1` or `Z_psi,target = 1` is a canonical field convention
for FeynRules-style interfaces, not a BHSM empirical fit and not a BHSM
dynamical prediction.
