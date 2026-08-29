# N12 Gate-7 interaction-frame analytic tail

The retained PROP16 generator is affine on every fine cell.  On each of its
5,908 actual substeps write

`A(t)=A0+t B`, `0<=t<=h`.

The large constant generator is factored exactly:

`U(t)=exp(A0 t)V(t)`,

`V'(t)=G(t)V(t)`,

`G(t)=t exp(-ad_A0 t)B`.

This matters because a generic ambient Magnus criterion sees
`||A0|| h > pi` on some substeps, while the action-owned noncommuting part is
small.  Replacing the ambient generator by a continuously projected quotient
would be invalid because the retained construction projects only at macro
constraint seams.  The interaction factorization keeps the actual ambient
flow and removes no direction.

At 256-bit Arb precision, every nested commutator through depth 12 is evaluated
from the exact binary64 retained affine-generator data.  The induced 2-norm is
bounded outward by `sqrt(||.||_1 ||.||_inf)`.  Starting with the exact depth-12
commutator, all further conjugation terms are enclosed by

`||ad_A X|| <= 2||A||||X||`.

Thus each substep has a rigorous value

`beta >= integral_0^h ||G(t)|| dt`.

The order-14 time-ordered Dyson remainder then obeys

`||V-V14|| <= exp(beta) beta^15/15!`,

and multiplication by the constant factor gives

`||U-exp(A0 h)V14|| <= exp(||A0||h) exp(beta) beta^15/15!`.

Across all 5,908 retained substeps the outward extrema are:

- maximum `beta`: `0.021567811917755787`;
- maximum conjugation-series tail: `1.4168446239590066e-41`;
- maximum order-14 Dyson remainder before the constant factor:
  `7.942523064085875e-38`;
- maximum local exact-propagator tail after the constant factor:
  `3.055586410630589e-35`.

This milestone certifies the analytic infinite tail only.  The finite
interaction polynomial `V14` has not yet been outward evaluated or globally
composed, so the exact affine propagator is not yet promoted.  Signed-source
quadrature `Y` remains a separate interval owner.  No action term, source,
selector, scale, event, gate, or chord changes.
