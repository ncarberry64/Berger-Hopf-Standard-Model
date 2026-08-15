# BHSM N=3 second direct-residual scale audit v18.38

This audit repeats the direct finite-difference response measurement after the
accepted v18.37 state change. It differentiates the unchanged nested exact
376-row residual, whose event covector is itself obtained from the ordered
event eigenvalue. It changes no action, residual row, event definition, eta
domain, or complete-child gate.

The finest common stable pair remains `3e-6` and `1e-6`. Across the audited
physical directions the maximum relative response change is
`0.00083332136817`; the maximum event-row absolute change is
`5.5840774134e-05`. The result validates only the local response scale at the
v18.37 state. It is a numerical derivative audit, not a new physical condition
or promotion rule.
