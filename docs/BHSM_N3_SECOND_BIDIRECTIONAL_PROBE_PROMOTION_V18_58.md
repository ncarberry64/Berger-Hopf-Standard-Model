# BHSM N=3 second bidirectional probe promotion v18.58

v18.58 independently recomputes the exact 376-row residual and promotes the
v18.56 state only after the complete physical gate passes.  The norm decreases
from `0.817942595938606` to `0.815925953107132`; event magnitude is
`0.084105974509345` and global eta is `0.77423036838536`.

The fresh rank-14 child has maximum trace `9.9e-14`, seven-constraint residual
`4.88063e-10`, attachment momentum mismatch `5.1210406e-8`, and two-scale flux
envelope `1.194931425e-5`.  It persists for `1e-4` with maximum constraint
residual `5.9402e-11`, positive eta, and nonzero relative evolution.

The v18.56 solver interpretation remains invalidated.  `FULL_BHSM_COMPLETE`
remains false because the global 376-row residual is nonzero.
