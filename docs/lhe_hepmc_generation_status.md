# BHSM LHE / HepMC Generation Status v0.1.0

BHSM v1.0.1 does not currently generate LHE or HepMC event samples.

## Status

| Output | Current status |
| --- | --- |
| LHE files | Not generated |
| HepMC files | Not generated |
| Pythia/Herwig showering | Not configured |
| Detector simulation handoff | Not configured |
| Athena workflow | Not ready |
| CMSSW workflow | Not ready |

## Readiness Check

Use:

```powershell
python tools/check_lhe_hepmc_generation_readiness.py
```

The checker exits cleanly and reports:

```text
event_generation_ready = false
lhe_generation_ready = false
hepmc_generation_ready = false
```

until real validated collider inputs and a UFO model are supplied.

Phase Two-A still reports `lhe_generation_ready = false` and
`hepmc_generation_ready = false`.
