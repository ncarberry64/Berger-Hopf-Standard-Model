# N12 C2 exact fixed-s field oracle

The retained action supplies an executable desingularized C2 vector field at
every regular state with simple selected eigenline and positive denominator.
The construction diagonalizes the reduced Euler--Dirac Hessian, solves only
on the uniformly invertible selected-line complement, and evaluates
`D lambda[Psi]` and `D lambda[V_hard]` by Hellmann--Feynman directional
derivatives of the exact action Hessian.  It never inverts the singular full
Euler--Dirac block.

With `c=D lambda[Psi]`, `b=<Psi,rhs>`, and
`R=D lambda[V_hard]`, the exact field is

`F_s=(s qdot, b Psi+s V_hard)/(c b+s R)`.

Consequently `D lambda[F_s]=1`.  The evaluator reproduces the independently
stored exact 1214-center field within its numerical realization error.

This closes the state-generator diagram slot.  It does not turn the 1,222
stored proof centers into an exact physical history.  Those nodes are
explicitly enclosure centers, and differentiating their adaptive proof
algorithm would not produce a physical signed covector.  The next action is a
parametric reset-chart multiple-shooting solve or the equivalent coupled
forward-adjoint KKT system using this oracle.  No reset member is selected.
