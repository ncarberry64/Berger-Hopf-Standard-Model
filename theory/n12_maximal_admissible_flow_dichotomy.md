# N12 maximal admissible-flow dichotomy

Let \(z=(q,v,m)\in\mathbb R^{98}\) and let \(U_{12}\) be the open part of the
existing child phase domain on which the retained fields are finite, the
metric and lapse are positive, the eta-Legendre margin is positive, and the
gauge-fixed Euler--Dirac Hessian \(D(z)\) is invertible. No new condition is
introduced: these are precisely the domains already required for the child
flow.

The implemented retained vector field is

\[
 V_{12}(z)=\bigl(v,D(z)^{-1}b(z)\bigr),
\]

where \(D\) and \(b\) are assembled from the exact retained action gradient
and Hessian. The finite quadrature action jet is smooth on \(U_{12}\), matrix
inversion is smooth on the invertible locus, and hence \(V_{12}\) is locally
Lipschitz there. Picard--Lindelof therefore gives a unique maximal solution
\(z:[0,T_{\max})\to U_{12}\) from the certified N12 child. The existing
Euler--Dirac constraint propagation identity keeps this solution on the
existing constraint manifold while it remains in \(U_{12}\).

If \(T_{\max}<\infty\), then at least one of the following occurs:

1. \(\|z(t)\|\to\infty\) along a sequence \(t\uparrow T_{\max}\);
2. the trajectory approaches the existing physical-domain boundary, including
   eta, metric/lapse, or another retained child-domain boundary;
3. the smallest singular value of \(D(z(t))\) tends to zero.

Indeed, if the state were bounded and stayed a positive distance from every
boundary above, its closure would be a compact subset of \(U_{12}\). A finite
subcover of local existence neighborhoods would extend the solution past
\(T_{\max}\), a contradiction. This is the standard finite-dimensional
continuation alternative applied to the unchanged retained action.

On the further open locus where the ordered Hessian eigenvalue is simple, its
eigenline and eigenvalue are differentiable. For normalized eigenvector
\(\psi\),

\[
 \dot e_{\rm ord}
 =\langle\psi,D H(z)[V_{12}(z)]\psi\rangle .
\]

Thus the N12 return question is rigorously reduced to tracking this scalar
until the first of: a transverse zero, an admissible-domain exit, a Dirac
singularity, state blowup, or loss of ordered-eigenline simplicity. The
theorem does not assert which alternative occurs.

The continuum lift is still open. The static inverse-square normal tail and
positive-duration observation theorem do not yet provide uniform local-
Lipschitz bounds and Galerkin convergence for the nonlinear vector field along
every bounded admissible flow segment. Those dynamic estimates are the exact
next lemma needed to transfer this maximal-flow dichotomy to the certified
continuum child.
