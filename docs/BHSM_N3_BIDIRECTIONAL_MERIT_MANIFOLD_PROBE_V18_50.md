# BHSM N=3 bidirectional merit-manifold probe v18.50

This calculation treats the bounded Krylov vector only as a local geometric
probe and scans both line orientations using the unchanged exact nonlinear
merit and eta. The solver interpretation is invalidated: the resulting
direction response mismatch is `0.486016184155312`, GMRES returns `info=1`,
and the exact linear residual is `0.791166274267834`.

The best positive state has norm `0.817749466104251`, reduction
`0.001535853269021`, alpha `0.03125`, and positive eta. The best negative state
improves only at numerical-scale alpha. Any selected state remains pending the
complete-child gate.
