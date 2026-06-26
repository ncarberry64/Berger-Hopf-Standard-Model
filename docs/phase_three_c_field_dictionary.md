# BHSM Phase Three-C Field Dictionary v0.5

Phase Three-C imports the uploaded analytical working packet as a preserved
source artifact and exports candidate field, gauge, parameter, matrix, and
vertex-target ledgers.

Source packet:

```text
artifacts/BHSM_phase_three_c_analytical_working_packet_v0_5.json
```

Source checksum:

```text
8384772C492162326C215449201175792E663DFC7807A41CDDBC7E322126F4ED
```

Current status:

```text
field_dictionary_target_exported = true
BHSM_internal_parameter_card_candidate_exported = true
boundary_source_vertex_matrices_exported = true
standard_collider_vertex_targets_identified = true
complete_4d_lagrangian_exported = false
feynrules_ready = false
ufo_ready = false
```

This sprint narrows the UFO/FeynRules blocker to explicit missing objects:
vector and fermion normalizations, full gauge/Lorentz structures, mass-width
schemes, and renormalization conventions.

It does not claim MadGraph, LHE, HepMC, Athena, or CMSSW readiness.
