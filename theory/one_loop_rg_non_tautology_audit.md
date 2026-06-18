# One-Loop RG Non-Tautology Audit

| step | theorem claim | possible imported structure | non-tautology check | result | remaining blocker |
| --- | --- | --- | --- | --- | --- |
| one-loop QFT formula | uses representation beta formula | coefficient table could be imported | formula is QFT infrastructure, not a BHSM-specific table | conditional pass | higher-loop theorem open |
| boundary fermion trace sums | one-generation traces are (2,2,2) | known matter table could be imported | uses prior boundary trace-normalization layer | conditional pass | prior trace layer conditional |
| three-generation multiplicity | N_gen=3 | known family count could be imported | uses existing three-generation branch result | conditional pass | depends on branch theorem status |
| gauge self-interaction terms | C2=(0,2,3) | known gauge data could be imported | uses boundary gauge algebra skeleton | conditional pass | full gauge dynamics still open if not discharged |
| scalar active-orientation doublet | b_scalar=(1/10,1/6,0) | known scalar content could be imported | marked conditional scalar-sector input | conditional pass | full scalar theorem open |
| beta coefficient totals | b=(41/10,-19/6,-7) | known beta table could be copied | computed from preceding rows before comparison | pass | measured matching open |
| comparison to known low-energy SM one-loop coefficients | agreement can be checked after derivation | comparison could feed back into construction | comparison is after derivation only | guarded | do not use as premise |

Conclusion: The branch does not use known SM beta coefficients as input. If the active scalar doublet or three-generation input remains conditional, that dependency is explicit.
