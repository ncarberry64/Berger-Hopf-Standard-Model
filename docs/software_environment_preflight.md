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

Phase Three-M extends this into a live-attempt preflight. In the current
environment Python is available, while Mathematica, WolframScript, FeynRules,
MadGraph, optional HepMC, and optional ROOT are not detected.

Phase Three-N performs a runtime provisioning scan across PATH, common local
install locations, and FeynRules environment variables. Python is detected;
WolframScript, WolframKernel/Mathematica, FeynRules, and MadGraph are not.

Phase Three-O expands this into a runtime asset manifest and handoff protocol.
It supports explicit environment variables for institutional runtime mapping
without requiring proprietary tools for basic repository tests.
