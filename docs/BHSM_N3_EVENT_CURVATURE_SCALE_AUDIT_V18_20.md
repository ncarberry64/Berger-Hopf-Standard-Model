# BHSM N=3 event-curvature scale audit v18.20

The v18.19 action block validates, but its event Hessian does not.  A uniform
raw-coordinate second-difference step mixes vastly different H6/Sobolev
amplitudes and gives a nonlocal or noise-dominated event curvature.

This audit keeps the exact accepted v18.12 event and evaluates first and second
directional variations in action-owned scaled coordinates.  Four physical
directions cover coherent reconstruction scale, terminal u, terminal
multipliers and a mixed complete event-support displacement.  Scales from
`1e-2` through `1e-5` are measured rather than assumed.

The audit changes no event, KKT equation, eta condition, or complete-child
gate.  It determines whether a resolved scalar-curvature plateau exists before
another square-KKT matrix can be claimed.
