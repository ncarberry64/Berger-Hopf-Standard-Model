# BHSM v15.25: moving forced-join constraint and symplectic theorem

## Regular moving coordinate

The exact critical coefficients of the aligned scalar shift sector are

\[
L=A\dot a^2+B\dot a b+C_2q^2b^2+D_1q\dot q,b+\cdots,
\]

\[
A=-21\kappa_1,quad B=-\frac{96\kappa_1}{R_c^2},quad
C_2=-\frac{49\kappa_1}{9R_c^4},quad
D_1=\frac{343\kappa_1}{9R_c^2}.
\]

With

\[
c=\frac{343}{1728}\zeta,qquad s=a-cq^2,
\]

the coefficients obey the exact identity

\[
\boxed{D_1+2cB=0}.
\]

Therefore the shift source is

\[
B(\dot a-2cq\dot q)b=B\dot s,b.
\]

The apparent singular \(q\)-to-\(a\) cross response vanishes identically on
the forced tangent \(s=\dot s=0\). It was a poor-coordinate artifact, not a
physical divergence.

## Positive normal kinetic direction

Eliminating the shift gives

\[
\boxed{
-\frac{B^2}{4C_2q^2}\dot s^2
=\frac{20736}{49}\frac{\kappa_1}{q^2}\dot s^2>0.
}
\]

Thus the normal shape direction is infinitely stiff at onset but has a finite
positive Legendre coefficient at every formed \(q\ne0\). The local
\((s,p_s)\) symplectic block has rank two. This establishes a local canonical
shape pair, not yet the full \((q,\sigma,s)\) canonical system.

## Transfer claim boundary

In the nonorthogonal \((q,s)\) chart, the direct finite kinetic term can give
\(p_s\ne0\) even on \(\dot s=0\). That raw momentum is not yet invariant
formation-to-shape transfer. The complete constraint-reduced Gram operator
must be assembled and whitened before the normal and tangential directions
can be compared.

At leading small-\(q\) order that common normalization can be restored. After
dividing by the common positive factor
\(\kappa_1R_c^7\operatorname{Vol}(S^7)\), the \((q,s)\) Gram block is

\[
G_{qq}=\frac{21}{4}+8Ac^2q^2,\qquad
G_{qs}=4Acq,\qquad
G_{ss}=2A+\frac{2K}{q^2},
\]

where

\[
A=-\frac{21}{5},\qquad K=\frac{20736}{245}.
\]

It is positive definite throughout the controlled small-\(q\) branch. Its
whitened invariant cross correlation is

\[
\boxed{
\rho_{qs}=-\frac{2401\sqrt{210}}{311040}\,\zeta q^2+O(q^4).
}
\]

This is the first nonzero invariant formation-to-shape kinetic transfer. It
reverses with the internal orientation branch and vanishes for the balanced
\(\zeta=0\) projection. The \((q,s)\) phase form has rank four; adjoining the
positive sigma kinetic pair at \(\sigma=0\) gives rank six.

At \(\sigma=0\), retained sigma reflection symmetry gives

\[
G_{q\sigma}=G_{s\sigma}=G_{a\sigma}=0.
\]

Sigma still couples through the coordinate dependence of the eta and shape
inertias and through its nonautonomous tangent potential. A localized nonzero
sigma profile can generate additional reduced cross structure.

## Status

`FULL_BHSM_COMPLETE = FALSE`.

Exact next object:

`ACTION_OWNED_DYNAMIC_SIGMA_TRANSFER_BACKREACTION_ON_THE_WHITENED_Q_S_SYMPLECTIC_SYSTEM_WITH_NONLINEAR_FORCED_JOIN_CONTINUATION_MATERIAL_SKIN_AND_DERIVED_GEOMETRIC_SEPARATION`

All variables remain in reconstructed spacetime. No Aether metric, empirical
input, fitted coefficient, frozen prediction, Git operation, or removable
medium was used.
