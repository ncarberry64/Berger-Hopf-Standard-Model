# Software Environment Preflight

Machine-readable artifact:

```text
artifacts/BHSM_software_environment_preflight_v1_4.json
```

Preflight checks:

- Python;
- Mathematica kernel;
- `wolframscript`;
- FeynRules;
- optional FeynArts;
- MadGraph;
- HepMC;
- optional ROOT.

Missing external software does not fail the repository sprint. It keeps
downstream readiness gates false until the tools are installed and the runners
are executed successfully.

