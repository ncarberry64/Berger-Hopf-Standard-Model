# Institutional HEP Quickstart

This quickstart is for a CERN-like institutional HEP handoff package. It is
not an experiment-approved software integration.

Recommended sequence:

```powershell
python scripts/setup/check_bhsm_hep_environment.py
python scripts/setup/bootstrap_bhsm_hep_environment.py
python scripts/setup/run_full_bhsm_hep_validation_chain.py
```

Make targets are also available:

```text
make bhsm-hep-preflight
make bhsm-map-wolfram
make bhsm-map-feynrules
make bhsm-map-madgraph
make bhsm-live-validation
make bhsm-hep-report
```

The complete BHSM 4D Lagrangian and excluded vertex families remain gated
outside this minimal collider-interface handoff.

