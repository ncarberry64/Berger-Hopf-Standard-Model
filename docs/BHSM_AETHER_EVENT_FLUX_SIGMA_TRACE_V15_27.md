# BHSM v15.27: distributional event flux and sigma trace

## Distributional theorem

Let the normalized transgressed current on the two regular sides of an
oriented event hypersurface be

\[
j_3=N(t)\,\omega_3,
\qquad
\int_{\Sigma^3}\omega_3=1.
\]

For a jump from degree \(N_-\) to \(N_+\), a smooth approximation gives

\[
N_\epsilon(t)=N_-+\frac{N_+-N_-}{2}
\left(1+\tanh\frac{t}{\epsilon}\right),
\]

and therefore

\[
dj_3\longrightarrow Q_\Gamma\,\delta_\Gamma,
\qquad
Q_\Gamma=N_+-N_-\in\mathbb Z.
\]

Stokes fixes this normalization exactly:

\[
\int_{U_\epsilon(\Gamma)}dj_3
=\int_{\partial U_\epsilon(\Gamma)}j_3
=N_+-N_-.
\]

Orientation reversal changes the sign of \(Q_\Gamma\).  A genuine
zero-to-degree-one reconstruction would therefore have \(Q_\Gamma=+1\) in
the chosen orientation.  The repository has not yet constructed the outgoing
full-preimage Hopf child or selected the actual incoming/outgoing event pair;
degree arithmetic alone does not prove that this event occurs.

## Event variation

The most general local linear pairing has a dimensionless coefficient:

\[
S_{\Gamma\sigma}
=-\lambda_\Gamma\int \sigma\,dj_3.
\]

Here sigma is a zero-form and \(dj_3\) is a distributional four-form, so no
metric, volume form, external clock, or preferred frame is inserted.  With
the jump convention

\[
[\Pi_\sigma]_\Gamma=\Pi_{\sigma,-}-\Pi_{\sigma,+},
\]

variation gives

\[
\boxed{[\Pi_\sigma]_\Gamma=\lambda_\Gamma Q_\Gamma.}
\]

Backgrounds satisfying the same fixed source form an affine space.
Fluctuations obey continuous trace and homogeneous momentum transmission, so
their Green form vanishes and the fluctuation operator remains self-adjoint.

## Normalization boundary

Topology fixes \(Q_\Gamma\), not \(\lambda_\Gamma\).  Every real
\(\lambda_\Gamma\) preserves covariance, orientation reversal, the
self-adjoint homogeneous fluctuation domain, conservation after including the
opposite core flux, and exact regular recovery when \(Q_\Gamma=0\).

The eta zero-mode endpoint candidates \((-1/2,+1/2)\) orient the trace but do
not prove that the material scalar is the canonical Pontryagin-dual coordinate
of the integer transition current.  Nor does the material scalar presently
have a derived compact period that could quantize the event coefficient.
Choosing \(\lambda_\Gamma=1\) is minimal, but it is not an action derivation.

The additive integer event group does have a canonical Pontryagin dual:

\[
\widehat{\mathbb Z}=U(1),
\qquad
\chi_\theta(Q)=e^{i\theta Q}.
\]

This does not identify the retained material sigma.  Under the standard
period-one lift \(\theta=2\pi\sigma\), the candidate endpoints
\(-1/2\) and \(+1/2\) give the same character for every integer charge.  In
addition, the retained polynomial material action is not invariant under
\(\sigma\mapsto\sigma+1\).  Choosing a different lift such as
\(\theta=\pi\sigma\) distinguishes the endpoints but inserts an unselected
period and normalization.  The natural existing dual variable is a Hopf or
relative-holonomy phase; earlier work proved that it can orient a branch but
does not create material amplitude.

Conditional Hamiltonian integrations confirm that the event impulse removes
the exact sigma-zero trajectory, but different allowed values of
\(\lambda_\Gamma\) and of the retained sigma response data produce different
nonlinear trajectories.  Those controls are not predictions and do not define
a unique material skin.

## Completion ledger

Validated: the distributional form degree, signed integer Stokes flux,
canonical momentum jump, orientation reversal, and self-adjoint affine trace
structure.

Invalidated: the claim that integer topology, self-adjointness, or eta endpoint
normalization alone fixes the event coupling.

Active dependency: a parent-event action or canonical symplectic-pairing
theorem must identify material sigma as the dual coordinate of the integer
transition current and simultaneously select the actual zero-to-one
reconstruction correspondence.  Until then the event impulse and downstream
skin cannot be promoted as physical BHSM outputs.
