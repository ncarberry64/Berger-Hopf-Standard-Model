# Phase Three-N Runtime Execution Gate

BHSM Phase Three-N is the runtime execution gate for the bounded minimal
collider-interface FeynRules path.

It attempts to move from repository static checks to actual local runtime
evidence by detecting:

- Python;
- WolframScript;
- WolframKernel or Mathematica;
- FeynRules;
- MadGraph.

The current environment detects Python but does not detect WolframScript,
WolframKernel/Mathematica, FeynRules, or MadGraph. Therefore live FeynRules
validation is not attempted, the minimal FeynRules model remains disabled, UFO
export is not attempted, and MadGraph smoke testing is not attempted.

This sprint does not install proprietary software, bypass Wolfram licensing,
fabricate validation logs, create fake LHE/HepMC outputs, or claim readiness
without live evidence.

## Phase Three-O Follow-On

Phase Three-O packages the runtime asset manifest, legal download policy,
setup scripts, model card, and CERN-like institutional HEP handoff protocol.
It does not change the Phase Three-N runtime result: Wolfram/FeynRules/MadGraph
execution remains gated by external runtime availability.
