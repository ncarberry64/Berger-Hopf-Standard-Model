# Boundary-State To SM Bridge

This file maps candidate boundary states to the existing integer primitive charge bridge. It is diagnostic, not a full derivation.

```text
T3 = w*sigma/2
Y = C/3 - ell + (1-w)*sigma
Q = sigma/2 + C/6 - ell/2
```

Physical field boundary-state registry:

| field | boundary state | C | ell | sigma | w | T3 | Y | Q |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| nu_L | channel=single_channel_boundary, closure=leptonic_closure, orientation=upper, interface=active | 0 | 1 | 1 | 1 | 1/2 | -1 | 0 |
| e_L | channel=single_channel_boundary, closure=leptonic_closure, orientation=lower, interface=active | 0 | 1 | -1 | 1 | -1/2 | -1 | -1 |
| u_L | channel=three_channel_active, closure=hadronic_closure, orientation=upper, interface=active | 1 | 0 | 1 | 1 | 1/2 | 1/3 | 2/3 |
| d_L | channel=three_channel_active, closure=hadronic_closure, orientation=lower, interface=active | 1 | 0 | -1 | 1 | -1/2 | 1/3 | -1/3 |
| e_R | channel=single_channel_boundary, closure=leptonic_closure, orientation=lower, interface=inactive | 0 | 1 | -1 | 0 | 0 | -2 | -1 |
| u_R | channel=three_channel_active, closure=hadronic_closure, orientation=upper, interface=inactive | 1 | 0 | 1 | 0 | 0 | 4/3 | 2/3 |
| d_R | channel=three_channel_active, closure=hadronic_closure, orientation=lower, interface=inactive | 1 | 0 | -1 | 0 | 0 | -2/3 | -1/3 |
| nu_R | channel=single_channel_boundary, closure=leptonic_closure, orientation=upper, interface=inactive | 0 | 1 | 1 | 0 | 0 | 0 | 0 |

Interface activity `w` changes `T3` and `Y`, but not `Q`, for fixed channel/closure/orientation. This is the diagnostic bridge between weak doublet/singlet activity and conserved electric charge.
