# Universal multi-body decay phase space

The universal decay readout now supports deterministic `1 -> n` phase-space
integration for every `n >= 2`.  It recursively applies

\[
 d\Phi_n(P)=\frac{ds}{2\pi}\,d\Phi_2(P;Q,p_n)\,d\Phi_{n-1}(Q)
\]

and reconstructs every daughter four-momentum in the parent rest frame with
rotationless Lorentz boosts.  The root solid angle supplies `4*pi`, so the
input squared amplitude must already be spin summed or initial-state averaged
and invariant under a common spatial rotation.  Lower sequential splits keep
both polar and azimuthal angles and therefore retain momentum correlations.

Invariant masses and polar cosines use fixed Gauss-Legendre rules; azimuths
use a fixed periodic midpoint rule.  The massless constant-amplitude
four-body check reproduces

\[
 \Phi_4(M)=\frac{M^4}{24576\pi^5},\qquad
 \Gamma_{1\to4}=\frac{|\mathcal A|^2M^3}{49152\pi^5}.
\]

This closes the missing deterministic four-or-more-body phase-space API, not
the physical decay prediction.  Quadrature error is not outward enclosed, and
the spectrum, LSZ factors, channel ledger, renormalized amplitudes, symmetry
factors, and dimensional scale must still come from one frozen BHSM action.
