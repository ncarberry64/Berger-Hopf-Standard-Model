# BHSM Sobolev-metric soft-mode lift v16.07

The v15.84 nested constraint projection minimized Euclidean coefficient
distance.  That norm changes with spectral order and makes a newly introduced
high-frequency coefficient as cheap as a low mode.  It therefore does not
define the full-(H^s) lift requested by the BHSM phase-space contract.

For (s=6>11/2), write the radial basis frequency as \(\nu_k\).  The corrected
selector minimizes

\[
 \|\dot q_N-\iota\dot q_{N-1}\|_{H^{s-1}}^2
 +\|m_N-\iota m_{N-1}\|_{H^s}^2
\]

subject to all (2N) lapse/shift equations and the Hamiltonian constraint.
In coefficient form the weights are

\[
 w^{(v)}_k=(1+\nu_k^2)^{(s-1)/2},\qquad
 w^{(m)}_k=(1+\nu_k^2)^{s/2}.
\]

The scaled optimization variables are the weighted coefficient corrections,
so the numerical problem implements this topology directly.  The measured
v15.80 (N=2) state remains the base point.  No surrogate event variable and
no alternative Yukawa normalization is introduced.

The first \(N=2\to3\) constrained extension closes its equations below
\(10^{-13}\), but its squared \(H^5\) rate correction is about
\(1.0460\times10^7\).  Hence the static zero-high-mode embedding is not a
Sobolev-Cauchy sequence.  The correct upstream continuation is to reintegrate
the \(N=3\) constraint-solved Euler--Dirac orbit from the selected reset and
measure its own event pencil.  Only those reintegrated event states may form
the full-Sobolev limit used by the nonlinear broken branch.
