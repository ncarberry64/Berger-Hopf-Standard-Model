# BHSM v15.38 — nonround semiclassical Hamiltonian constraint

## Exact round obstruction

On the v14.91 coefficient locus, let \(X_c^3=5\kappa_1\),
\(\kappa_0=(15/4)\kappa_1X_c\), and \(y=X/X_c\). The round static
Hamiltonian-constraint density is

\[
 C_{\rm round}
 =\frac{5\kappa_1X_c}{8}(4y-3-y^4).
\]

Since

\[
 y^4-4y+3=(y-1)^2(y^2+2y+3)\ge0,
\]

\[
 \boxed{C_{\rm round}\le0}
\]

with equality only at the identity radius. Adding any positive skin or FR
energy makes the round time-symmetric constraint strictly negative. Changing
only the global radius cannot restore it. The child geometry must respond
nonroundly; this is not a license to add pressure.

## Conformal constraint companion

Use

\[
 h_7=R^2e^{2u(\chi)}
 [d\chi^2+\cos^2\chi\,d\Omega_{3,u}^2
 +\sin^2\chi\,d\Omega_{3,v}^2].
\]

Its scalar curvature is

\[
 R_h=\frac{e^{-2u}}{R^2}
 \left[42-12\{u''+3(\cot\chi-\tan\chi)u'\}-30u'^2\right].
\]

The retained identity eta map has \(X_\eta=7e^{-2u}/R^2\). The fixed v15.34
off-seam sigma profile contributes its canonical gradient and inverse-Euler
potential energy. The zero-current FR ground state contributes

\[
 \rho_{\rm FR}
 =\frac{(\kappa_1+X_\eta^3)(1-4\sigma^2)}{8I^2},
\]

where \(I\) is solved simultaneously as a nonlocal integral state.

The nonlinear lapse constraint

\[
 \frac{\kappa_1}{2}R_h-rac{\kappa_0}{2}
 -\rho_\eta-\rho_\sigma-\rho_{\rm FR}=0
\]

is solved with regular pole conditions \(u'(0)=u'(\pi/2)=0\). A homotopy from
zero added child stress selects the branch connected to the round identity
solution. The deterministic solve produces a nonconstant conformal response,
closes the FR normalization, and controls the pointwise constraint residual.

This is the first explicit enclosed-spacetime response on the off-seam child
branch. It is action/constraint driven and contains no buoyancy coefficient,
spring, or inserted pressure.

## Claim boundary

Closed:

- the exact no-round-radius theorem after positive child energy is added;
- a nonround conformal Hamiltonian-constraint companion connected to the
  round branch;
- zero-current FR normalization on that constraint solution.

Still open:

- the independent spatial Einstein equations;
- the eta and sigma Euler equations on the backreacted metric;
- the nonconformal \(A-B\) shape;
- the complete physical Hessian and Floquet spectrum.

Solving the lapse constraint alone is not a stationary child solution.
`FULL_BHSM_COMPLETE = FALSE`.

Active dependency:

`JOINT_NONCONFORMAL_A_B_F_SIGMA_SPATIAL_EINSTEIN_AND_MATTER_EULER_BVP_WITH_COMPLETE_PHYSICAL_HESSIAN`
