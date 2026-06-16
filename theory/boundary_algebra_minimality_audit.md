# Boundary Algebra Minimality Audit

Diagnostic requirements:

- must distinguish lepton-like single-channel closure from quark-like three-channel closure;
- must include the three-channel active closure block;
- must provide channel multiplicity 1 vs 3;
- must provide upper/lower orientation signs;
- must provide active weak two-state interface;
- must provide active two-orientation interface;
- must provide inactive orientation singlets;
- must provide inactive upper orientation;
- must provide inactive lower orientation;
- must reproduce the existing `(C,ell,sigma,w)` bridge;
- must reproduce `(T3,Y,Q)`;
- must preserve anomaly closure diagnostic.

| requirement | minimal block needed | candidate block | status | supplied |
| --- | --- | --- | --- | --- |
| single_channel_closure | C | C_ell | diagnostic | true |
| three_channel_active_closure | M3(C) or End(C^3) | M3(C)_C | diagnostic | true |
| active_two_orientation_interface | M2(C) or End(C^2) | M2(C)_{w=1} | diagnostic | true |
| inactive_upper_orientation | C | C_{sigma=+} | diagnostic | true |
| inactive_lower_orientation | C | C_{sigma=-} | diagnostic | true |

Conclusion: this finite algebra is minimal with respect to the current diagnostic bridge, but not yet uniquely derived from first-principles Berger-Hopf geometry.

## Related Closure Spectrum Gate

- [Admissible boundary closure spectrum gate](admissible_boundary_closure_spectrum_gate.md)
