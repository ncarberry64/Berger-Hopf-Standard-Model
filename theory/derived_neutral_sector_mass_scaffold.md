# Derived Neutral Sector Mass Scaffold

Because `S_ref_neutral` is boundary neutral, a neutral singlet mass matrix may be symbolically defined:

```text
M_N[j,k]=N_N*I_N(S_ref_neutral[j],S_ref_neutral[k])
```

If a future theorem derives the relevant scale and invertibility conditions, an effective neutral mass operator may be written:

```text
M_eff=-M_D*M_N^{-1}*M_D^T
```

Guardrails:

- no neutral mass scale is predicted;
- no measured neutral masses are derived;
- no PMNS values are derived.

Status: `NEUTRAL_SECTOR_MASS_SCAFFOLD_DERIVED_CONDITIONAL`.
