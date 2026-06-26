# Wolfram/FeynRules Runtime Provisioning

Machine-readable artifact:

```text
artifacts/BHSM_runtime_provisioning_report_v1_6.json
```

Current result:

```text
python_detected = true
wolframscript_detected = false
wolfram_kernel_detected = false
mathematica_detected = false
feynrules_detected = false
madgraph_detected = false
environment_ready_for_feynrules_validation = false
```

Provisioning actions attempted:

- PATH lookup for WolframScript, WolframKernel, and MadGraph;
- common local path scan for Mathematica, FeynRules, and MadGraph;
- environment variable scan for `FEYNRULES_PATH` and `FEYNRULES_HOME`.

No Wolfram license bypass, unauthorized key, or improper installer was used.
If a licensed Wolfram runtime and FeynRules package are installed later, this
gate can be rerun.

