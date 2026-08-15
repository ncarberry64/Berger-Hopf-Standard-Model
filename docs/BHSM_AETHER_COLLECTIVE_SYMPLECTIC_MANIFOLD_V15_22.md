# BHSM v15.22: collective symplectic manifold and round-branch theorem

## Correct symplectic domain

The physical collective configuration map is only the first half of the
construction. A two-form pulled onto a configuration-only family \(Q^A\) does
not establish canonical partners. The correct pullback lives on the
collective velocity or phase bundle.

For

\[
L_{\rm red}
=\frac12\mathbb G_{AB}(Q)\dot Q^A\dot Q^B
+\mathcal A_A(Q)\dot Q^A-V(Q),
\]

the local Cartan two-form on \((Q,\dot Q)\) has block matrix

\[
\Omega_L=
\begin{pmatrix}
\mathcal F&\mathbb G\\
-\mathbb G&0
\end{pmatrix},
\qquad \mathcal F=d\mathcal A.
\]

There is an exact rank theorem:

\[
\boxed{
\operatorname{rank}\Omega_L=2n
\iff
\operatorname{rank}\mathbb G=n.
}
\]

An antisymmetric or Berry-like term cannot repair a null velocity direction:
every vector in \(\ker\mathbb G\) supplies a vertical null vector of
\(\Omega_L\).

## Round separation is a branch problem

The v14.70 result has the local form

\[
\Phi(d)=\Phi_0+\frac12d^2\Phi_{dd}+O(d^4).
\]

Consequently

\[
D_d\Phi=d\Phi_{dd}+O(d^3),
\qquad
\mathbb G_{dd}=d^2
\langle\Phi_{dd},\mathbb K\Phi_{dd}\rangle+O(d^4).
\]

At \(d=0\), the immersion rank, kinetic coefficient, Legendre rank, and
collective two-form rank all vanish. Thus ordinary round \(d\) is not a
canonical coordinate there.

The even invariant \(s=d^2\) gives

\[
D_s\Phi\big|_0=\frac12\Phi_{dd},
\qquad
\mathbb G_{ss}\big|_0
=\frac14\langle\Phi_{dd},\mathbb K\Phi_{dd}\rangle.
\]

This can regularize the even state map on the half-line \(s\ge0\), but it is
physical only if cap exchange is an actual quotient. The retained archive
contains background cap exchange and fixed-support orbifold parity, while its
moving covariant reflection is explicitly absent. Therefore two possibilities
remain:

1. If cap exchange is gauge-quotiented, the local orbit space is
   \(\mathbb R/\mathbb Z_2\simeq[0,\infty)\), with \(s=d^2\).
2. If parent and child labels are physical, \(d>0\) and \(d<0\) are distinct
   branches and replacing them by \(s\) loses physical information.

BHSM presently selects neither case. Calling the physical state an orbifold is
therefore premature, although ordinary first-order \(d\) is excluded in both
cases at the round point.

## Sigma response operator

The invariant response is

\[
\boxed{
\mathcal G_\sigma=
\mathbb I_0^{-1/2}
\frac{D_\sigma^2\mathbb I}{2}
\mathbb I_0^{-1/2}.
}
\]

For the uniformly weighted retained eta block it reduces exactly to
\(gI\). A general globally reduced operator need not be proportional to the
identity; its spectrum, not an imposed scalar \(g\), is the physical object.
The full operator is still unavailable because \(\Phi_*(Q)\) has not been
constructed.

## Integrated transient instability

v15.22 evaluates the linear amplification screen

\[
\mathcal A_\sigma
=\int_{\omega_{\rm eff}^2<0}
\sqrt{-\omega_{\rm eff}^2(\tau)}\,d\tau
\]

on the exact v15.9 sigma-zero homoclinic control. It is zero below the exact
peak threshold and positive above it. The two equal flank contributions are
integrated explicitly. This is not yet a material skin: sigma backreaction,
turning-point matching, the physical response operator, and the evolving
static curvature remain absent.

## Existing phase-space lineage

The retained theory contains:

- sectorwise P1, eta, and sigma momenta;
- the Hayward area/relative-angle corner pair;
- a structural nine-dimensional \(\ell=2\) shape space.

It does not contain:

- a seam-embedding canonical momentum;
- one coupled reduced symplectic form;
- an action-selected nonround shape background;
- an evaluated collective state map.

The Hayward pair cannot be relabeled as the separation pair.

## Smallest candidate domain completion

The coefficient-free candidate is to promote the already-existing embedding
map \(X_{\rm emb}\) from fixed geometric data to a varied argument of the same
bulk, GHY, Hayward, matcher, and material action. It must be varied jointly
with eta, sigma, and the metric. This is a candidate variational-domain
completion, not an established or unique BHSM law.

The collective coordinates should initially be

\[
Q=(q,\sigma,u^\alpha),
\]

where \(u\) is an action-selected nonround or second-shape center mode. Only
after solving that branch should geometric separation be defined.

## Status

`FULL_BHSM_COMPLETE = FALSE`.

The single next object is:

`ACTION_OWNED_COUPLED_ETA_SIGMA_METRIC_VARIED_EMBEDDING_NONROUND_CENTER_MANIFOLD_BIFURCATION_SOLUTION_WITH_COMPLEMENT_HESSIAN_INVERTIBLE_FULL_LORENTZIAN_LEGENDRE_MAP_AND_ACTION_SELECTED_SHAPE_MODE`

No field, coefficient, empirical input, moving quotient, separation momentum,
wall tension, or impulse was introduced.
