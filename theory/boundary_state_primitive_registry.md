# Boundary-State Primitive Registry

Candidate state classes:

```text
channel_class:
  three_channel_active
  single_channel_boundary

closure_class:
  leptonic_closure
  hadronic_closure

orientation:
  upper
  lower

interface_activity:
  active
  inactive
```

| state component | candidate BHSM meaning | output primitive | output value | derivation status |
| --- | --- | --- | --- | --- |
| three_channel_active | active three-channel boundary sector | C | 1 | candidate, not derived |
| single_channel_boundary | single boundary channel sector | C | 0 | candidate, not derived |
| leptonic_closure | lepton-sector closure class | ell | 1 | candidate, not derived |
| hadronic_closure | hadron/quark-sector closure class | ell | 0 | candidate, not derived |
| upper | upper weak-interface orientation | sigma | +1 | candidate, not derived |
| lower | lower weak-interface orientation | sigma | -1 | candidate, not derived |
| active | weak-interface active/doublet-like | w | 1 | candidate, not derived |
| inactive | weak-interface inactive/singlet-like | w | 0 | candidate, not derived |
