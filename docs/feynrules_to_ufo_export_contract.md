# FeynRules to UFO Export Contract

Machine-readable artifact:

```text
artifacts/BHSM_feynrules_to_ufo_export_contract_v1_3.json
```

The future export path requires:

- an enabled validated `.fr` file;
- Mathematica;
- FeynRules;
- complete particle and parameter declarations;
- FeynRules syntax validation.

Current status:

```text
ufo_export_attempted = false
ufo_export_passed = false
ufo_loadability_tested = false
ufo_loadability_passed = false
```

No UFO model is generated in Phase Three-K.

## Phase Three-L Runner Contract

Phase Three-L adds the local runner contract:

```text
wolframscript -file scripts/feynrules/export_bhsm_minimal_to_ufo.m
```

The command is documented for future local execution only. The current
artifact records `ufo_export_attempted=false`, `ufo_export_passed=false`,
`ufo_loadability_tested=false`, and `ufo_loadability_passed=false`.
