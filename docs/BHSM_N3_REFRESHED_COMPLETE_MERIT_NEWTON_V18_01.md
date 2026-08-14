# BHSM N=3 refreshed complete-merit Newton step (v18.01)

The adopted v17.32 physical Jacobian is refreshed at the v18.00 promoted
state. The unchanged 376-row action is solved in its 375-dimensional reduced
base chart, with the event multiplier projected analytically.

The global trial filter now uses the true coupled residual norm and the
global eta domain. It does not require every named component to decrease on
every intermediate step. Any selected trial remains provisional until its
event is independently shown to reconstruct a complete persistent child.

No handcrafted direction mixture, extra KKT row, refactor, or new numerical
infrastructure is introduced.
