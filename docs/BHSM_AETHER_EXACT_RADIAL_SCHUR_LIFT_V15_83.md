# BHSM exact radial Schur lift v15.83

The high-order finite-difference Euler--Dirac Hessians are replaced by exact
second variations.  Each scalar in the reduced action is propagated as a jet
((f,df,d^2f)), including the lapse exponential, shift coupling, ADM kinetic
form, nonlinear eta term, reciprocal FR inertia, and boundary Casimir term.
This removes subtractive cancellation from the radial Schur sequence.

The physical source also has an exact angular selection rule.  The lowest
Dirac eigenspinors on the round (S^3) are Killing spinors with constant norm.
For the matched LR scalar channel,

\[
 T_{00}=\text{constant},\qquad T_{ij}\propto h_{ij},
\]

and hence its pairing with every nontrivial angular harmonic is zero.  The
non-axisymmetric Schur tail is therefore exactly absent at quadratic order;
only the radial cohomogeneity-one sequence remains.

The exact full response is evaluated through (N=12).  No near-null direction
is discarded with a numerical eigenvalue threshold: any true constraint
quotient must be derived before inversion.  The calculation also exposes the
remaining defect—higher-order embedded states must first be projected onto all
new lapse/shift and Hamiltonian constraints before a continuum inf--sup bound
can be claimed.
