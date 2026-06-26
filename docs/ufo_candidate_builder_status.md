# BHSM UFO Candidate Builder Status v0.2

The UFO candidate builder is gated. It reads the Phase Two-A field-content,
parameter-card, vertex-source, and FeynRules blocker artifacts.

If blockers remain, the manifest reports:

```text
ufo_candidate_built = false
loadable_ufo_model = false
madgraph_ready = false
lhe_generation_ready = false
hepmc_generation_ready = false
```

The builder does not produce a production/loadable UFO model unless all required
physics prerequisites are present and validated.

If a documentation-only blocked candidate directory is requested, it must be
named:

```text
ufo_candidate_BLOCKED_NOT_FOR_ANALYSIS/
```

and must state that it is not for MadGraph production, detector simulation, or
physics analysis.
