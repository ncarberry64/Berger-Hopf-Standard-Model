# BHSM Sobolev spectral-Galerkin pencil lift v15.81

The actual (N=2) Euler--Dirac soft eigenmode is embedded into nested
cohomogeneity-one spectral spaces.  At order (N), the basis is

\[
 u=\sum_{k=1}^N u_k\cos(4k\chi),\qquad
 w,v=\sin^2(2\chi)\sum_{j=0}^{N-1}a_j\cos(4j\chi),
\]

with the matching lapse and shift bases.  The full velocity/multiplier pencil
has dimension (1+5N).  The same branch is selected at each order by maximal
overlap with the embedded preceding eigenvector, rather than by repeatedly
choosing whichever unrelated eigenvalue happens to be closest to zero.

The calculation through (N=4) evaluates both the tracked eigenvalue and the
normalized boundary fermion source (g_{s,0}).  These rows diagnose whether
the v15.80 joint crossing persists when higher radial metric, lapse, and shift
modes are admitted.  A full Sobolev claim additionally requires a
Schur-complement tail bound (or norm-resolvent convergence); non-axisymmetric
modes are not silently included by this cohomogeneity-one calculation.
