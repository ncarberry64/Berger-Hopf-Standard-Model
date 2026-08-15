# BHSM N=3 direct residual JFNK audit v18.35

The v18.34 measured direct-residual response is used in a bounded right-mapped
GMRES solve.  The resulting direction does not remain on the measured response
plateau and the linear solve does not converge, so the JFNK/Newton claim is
invalidated.

An independently evaluated line state nevertheless reduces the exact 376-row
norm from `0.828979109495249` to `0.825951014247091` with positive eta.  It is
retained only as a proposal pending the complete-child gate.
