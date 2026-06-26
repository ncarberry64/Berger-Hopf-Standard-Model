# Software-Track Readiness Gates

Machine-readable artifact:

```text
artifacts/BHSM_software_track_readiness_gates_v1_3.json
```

Tracked gates:

- bounded FeynRules model file;
- FeynRules syntax validation;
- UFO export;
- UFO loadability;
- MadGraph import;
- MadGraph smoke process;
- LHE generation;
- HepMC generation;
- Athena boundary;
- CMSSW boundary.

Only a disabled bounded draft is exported. All downstream software gates remain
blocked until actual validation is performed.

## Phase Three-L Environment Preflight

Phase Three-L adds a repository preflight for Python, Mathematica/Wolfram,
FeynRules, optional FeynArts, MadGraph, HepMC, and optional ROOT. In the
current environment Python is available for repository tooling, while
Mathematica, FeynRules, MadGraph, and HepMC are not detected.

The absence of those external tools keeps real FeynRules validation, UFO
export, UFO loadability, MadGraph smoke testing, and event generation blocked.

## Phase Three-M Live Attempt Gates

Phase Three-M exports live-attempt artifacts for FeynRules, UFO, and MadGraph.
The current result keeps every downstream readiness gate false because the
required external tools were not detected and no live software run succeeded.
