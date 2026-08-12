# BHSM v15.34 — complete-child mode embedding and localized Hopf-fiber Routhian

## Result

The v15.32 wall-translation mode has now been embedded in the full regular
cohomogeneity-one field tangent space

\[
 ds^2=-N^2dt^2+C^2(d\chi+\beta^\chi dt)^2
 +A^2d\Omega_{3,u}^2+B^2d\Omega_{3,v}^2,
 \qquad \eta=(\cos f\,u,\sin f\,v),
\]

with \(\sigma=\sigma(t,\chi)\). A common radial displacement of
\((A,B,C,f,\sigma)\) is a diffeomorphism. The invariant material-relative
tangent is

\[
 \delta\sigma_{\rm GI}
 =\delta\sigma-\frac{\sigma'}{f'}\delta f.
\]

For

\[
 \tan\widetilde\chi=e^{-\ell}\tan\chi,
 \qquad \xi_{\rm wall}=-\sin\chi\cos\chi,
\]

the v15.32 skin-only variation has \(\delta f=0\) and
\(\delta\sigma_{\rm GI}=\xi_{\rm wall}\sigma'\ne0\). It is therefore not
removed by the lapse, shift, or radial-diffeomorphism constraint. The
\(-14.20\) skin eigenmode remains an admissible physical relative direction
of the complete field space.

## Enclosed-geometry contribution

For a pure moving partition of one smooth on-shell parent,

\[
 \Gamma_{\rm parent}
 =\Gamma_-(\ell)+\Gamma_+(\ell).
\]

The opposite-normal internal GHY terms cancel, so both the first and second
partition variations vanish. A homogeneous enclosed volume therefore cannot
be relabelled as a free pressure or spring. Regular positive metric/eta
companions give the already established subtractive Schur response. A direct
collective term, or a genuinely separated child geometry after the event, is
needed.

## Minimal localized Hopf completion

The existing degree-one full-preimage geometry has a cyclic Hopf \(U(1)\)
Killing coordinate \(\theta\). In the minimal class of even polynomials of
degree at most two, the conditions

\[
 \Lambda(0)=1,
 \qquad \Lambda(\pm\tfrac12)=0,
 \qquad \Lambda>0\quad (|\sigma|<\tfrac12)
\]

have the unique solution

\[
 \boxed{\Lambda(\sigma)=1-4\sigma^2.}
\]

Weighting the Hopf-fiber cyclic kinetic density by \(\Lambda\) adds no field
and no continuous coefficient. It is classified as

`BHSM_ACTION_COMPLETION_DERIVED_FROM_EXISTING_BHSM_STRUCTURE`.

It was not present in the historical retained action. Uniqueness is proved
only in the declared minimal even-quadratic class; higher-polynomial and
higher-derivative invariants remain part of the provenance audit.

## Odd-degree FR domain

On

\[
 \Psi(\theta+2\pi)=-\Psi(\theta),
\]

the self-adjoint generator \(J=-i\partial_\theta\) has normalized
eigenfunctions

\[
 \frac{e^{i(n+1/2)\theta}}{\sqrt{2\pi}},
 \qquad J_n=n+\frac12.
\]

The Hamiltonian domain also makes the derivative antiperiodic. Thus the
lowest physical sector is derived from the domain:

\[
 \boxed{|J|=\tfrac12,\qquad J^2=\tfrac14.}
\]

No event degree is used as a canonical momentum.

## Controlled child Routhian

At the compact formation radius, the localized inertia is

\[
 I_{\rm skin}(\ell)
 =(\kappa_1+X_\eta^3)R^7\operatorname{Vol}(S^3)^2
 \int_0^{\pi/2}\!\sin^3\chi\cos^3\chi
 [1-4\sigma_\ell(\chi)^2]d\chi.
\]

It is maximal at the seam and tends to zero at either collapse pole. Hence

\[
 E_{\rm cyc}=\frac{J^2}{2I_{\rm skin}}
\]

has positive seam curvature and diverges at both pole limits. The reduced
Routhian is

\[
 \boxed{H_{\rm red}(\ell)=E_{\rm skin}(\ell)
 +\frac{J^2}{2I_{\rm skin}(\ell)}.}
\]

For the deterministic normalization
\(\kappa_1=Z_\sigma=1\),
\(R^6=343/5\), and the derived \(|J|=1/2\), its stable branches are

\[
 \ell_*=\pm4.78752,
 \qquad k_\ell\simeq3.1005>0.
\]

On the child branch

\[
 \boxed{x=\log(R_c/R_p)=-4.78752<0.}
\]

The wall-translation instability is therefore reclassified in this
controlled completion as the transition direction from the seam saddle to a
finite fixed-charge enclosure. The collective sigma kinetic norm is positive,
and the local enclosure frequency squared is positive.

Because the cyclic energy diverges at both endpoints, a nonzero FR charge
forces at least one finite interior minimum for every positive retained
\(\kappa_1\) and \(Z_\sigma\); their values move the minimum but are not fitted
here.

## Claim boundary and continuation

Derived here:

- the full-field gauge-invariant embedding of the negative skin mode;
- zero direct curvature for pure smooth cap repartition;
- the unique minimal even-quadratic localized Hopf factor;
- the antiperiodic self-adjoint FR spectrum;
- a finite, stable reduced child Routhian branch with \(x<0\).

Not yet derived:

- uniqueness of the action completion in the unrestricted local operator
  basis;
- the nonlinear Einstein–eta–sigma constraints on the off-seam branch;
- persistence/Floquet multipliers of the complete reconstructed child;
- the physical M4 attachment and downstream Standard Model operators.

Accordingly the stable reduced enclosure is not yet promoted to the complete
particle, and `FULL_BHSM_COMPLETE = FALSE`.

Active dependency:

`FULL_NONLINEAR_EINSTEIN_ETA_SIGMA_LOCALIZED_HOPF_FIBER_CONSTRAINT_CONTINUATION_AND_FLOQUET_PERSISTENCE_OF_THE_OFF_SEAM_CHILD_BRANCH`
