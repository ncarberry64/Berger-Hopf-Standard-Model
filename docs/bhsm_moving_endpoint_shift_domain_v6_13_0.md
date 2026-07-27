# BHSM v6.13.0 moving-endpoint scalar-shift domain

Primary result:
`BHSM_EXISTING_B1_VARIATION_DOES_NOT_SUPPLY_SHIFT_BOUNDARY_DATA`.

The existing P1+GHY+B1+scalar action determines the matched metric junction
condition and the bulk radial momentum constraint. It does not determine an
independent scalar radial-shift/longitudinal condition at an \(x\)-dependent
moving endpoint. The reason is variational, not numerical: the frozen B1
domain fixes its embedding \(\iota\), while varying the independent intrinsic
metric and the matching multiplier. An endpoint displacement \(\zeta(x)\) is
therefore a coordinate representation of that fixed support, not a freely
varied action field.

No boundary condition is added to repair this omission. Consequently no
constraint Green operator or fold kinetic Schur complement is constructed.

## Repository variational domain

B1 is the provisional intrinsic \(M_4\) boundary/interface. The Z2
background uses the fixed Gaussian-normal support \(y=0\) and glues two
regular caps. Its independent intrinsic metric is tied to the bulk trace by

\[
S_{\rm match}=\int_\Sigma\sqrt{|\gamma|}\,
\Lambda^{\mu\nu}\bigl(h_{\mu\nu}-\iota^*g_{\mu\nu}\bigr).
\]

The prescribed variation is: vary \(g\), \(h\), and \(\Lambda\); impose
\(h=\iota^*g\); eliminate \(\Lambda\). The embedding \(\iota\) is not in the
variation list. The homogeneous scalar-wall problem solves its cap length
\(\rho_J(X)\), and v6.1.7 includes its one-dimensional moving-upper-limit
transversality response. The frozen ensemble simultaneously lists the
boundary domains as fixed. Thus a family of homogeneous static domains is
not an \(x\)-dependent brane-bending field.

## Moving-endpoint pullback

Introduce the diagnostic embedding

\[
X^A(x)=(\rho_J+\zeta(x),x^\mu)
\]

in the radial ADM metric

\[
ds_5^2=N^2d\rho^2+
h_{\mu\nu}(dx^\mu+N^\mu d\rho)(dx^\nu+N^\nu d\rho).
\]

The exact induced metric is

\[
\gamma_{\mu\nu}=
\left[
h_{\mu\nu}+N_\mu D_\nu\zeta+N_\nu D_\mu\zeta+
(N^2+N_\alpha N^\alpha)D_\mu\zeta D_\nu\zeta
\right]_\Sigma .
\]

At linear amplitude order,

\[
\delta\gamma_{\mu\nu}
=\delta h_{\mu\nu}+\zeta\,\partial_\rho h_{\mu\nu}^{(0)}.
\]

The shift first enters the pullback at quadratic derivative order. For the
level set \(s=\rho-\rho_J-\zeta(x)\),

\[
s_A=(1,-D_\mu\zeta),
\qquad
n^\mu=-\frac{N^\mu+N^2D^\mu\zeta}{N}+O(2).
\]

The scalar pullback is

\[
\sigma_\Sigma=\sigma_0+\delta\sigma+\zeta\sigma_0'.
\]

The effective normal lapse is

\[
N_\Sigma=\left[
N^{-2}+\frac{2N^\mu D_\mu\zeta}{N^2}
+\left(h^{\mu\nu}+\frac{N^\mu N^\nu}{N^2}\right)
D_\mu\zeta D_\nu\zeta
\right]^{-1/2}.
\]

## Gauge transformations and endpoint invariant

Use

\[
\delta g_{AB}\mapsto\delta g_{AB}-\mathcal L_\xi g^{(0)}_{AB},
\qquad
\xi^A=(\xi^\rho,D^\mu\xi).
\]

Because the endpoint is written as \(\rho_J+\zeta\), its displacement
transforms with the opposite compensation to the metric perturbation:

\[
\zeta\mapsto\zeta+\xi^\rho_\Sigma.
\]

The scalar transformations are

\[
\begin{aligned}
A&\mapsto A-(N_0\xi^\rho)',\\
B&\mapsto B-N_0^2\xi^\rho-a_0^2\xi',\\
\psi&\mapsto\psi-\frac{a_0'}{a_0}\xi^\rho,\\
E&\mapsto E-\xi,\\
\delta\sigma&\mapsto\delta\sigma-\sigma_0'\xi^\rho,\\
\delta X&\mapsto\delta X-X_0'\xi^\rho .
\end{aligned}
\]

The exact linear gauge-invariant endpoint threading is

\[
\boxed{
\mathcal S_\Sigma=
\left[B+N_0^2\zeta-a_0^2\partial_\rho E\right]_\Sigma .
}
\]

The endpoint pullbacks

\[
\Psi_\Sigma=\psi+\frac{a_0'}{a_0}\zeta,\qquad
\delta\sigma_\Sigma=\delta\sigma+\sigma_0'\zeta,\qquad
\delta X_\Sigma=\delta X+X_0'\zeta
\]

are radially gauge invariant. Four-dimensional scalar diffeomorphisms act on
the last expression by the Lie derivative of the background \(X\), which
vanishes on the homogeneous constant-\(X\) fold. Thus \(\delta X_\Sigma\)
remains intrinsic.

One may choose \(\zeta=0\) and \(E=0\), but neither choice changes
\(\mathcal S_\Sigma\). An undetermined \(\mathcal S_\Sigma\) is therefore not
a residual gauge transformation.

## First variation

After GHY cancels normal derivatives of \(\delta g\), the combined metric
boundary coefficient is

\[
\mathcal J_{\mu\nu}
=\kappa_1[Q_{\mu\nu}]
+2C_\partial G_{\mu\nu}^{(4)}
-T_{\partial,\mu\nu}.
\]

Variation of the matched induced metrics gives

\[
\mathcal J_{\mu\nu}=0.
\]

This is the metric junction equation. It is not an independent boundary
condition for \(\mathcal S_\Sigma\). In particular, its tangential
longitudinal projection is the Codazzi/Bianchi Ward identity

\[
D^\mu\mathcal J_{\mu\nu}=-[T_{{\rm bulk},n\nu}],
\]

after the bulk momentum constraint is imposed. It supplies momentum balance,
not an additional endpoint-domain equation.

The ADM shift enters \(K_{\mu\nu}\) through tangential derivatives,

\[
K_{\mu\nu}=\frac{1}{2N}
\left(\partial_\rho h_{\mu\nu}-D_\mu N_\nu-D_\nu N_\mu\right),
\]

and has no radial derivative. Its variation therefore gives the bulk
momentum constraint,

\[
D_\nu(K^\nu{}_\mu-\delta^\nu{}_\mu K)
=\kappa_1^{-1}Z_5(n\sigma)D_\mu\sigma,
\]

without a radial endpoint term. At fixed embedding,
\(\gamma_{\mu\nu}=h_{\mu\nu}\), so GHY, B1, and the metric matcher contain no
separate freely varied \(\delta\mathcal S_\Sigma\). The scalar endpoint term
also vanishes in the stored Dirichlet wall domain
\(\delta\sigma_\Sigma=0\).

If an embedding variation were declared, tangential displacement would
produce the Codazzi/Ward momentum balance and normal displacement a shape
equation. That declaration is absent from the frozen action domain and is
not made here.

## Boundary-data ledger

- Fixed: B1 support and embedding, coefficients, topology, Z2 gluing, normal
  orientation, and the bulk-scalar Dirichlet trace.
- Freely varied: bulk metric, independent intrinsic metric, matching
  multiplier, and interior radial shift as a constraint multiplier.
- Constrained: exact metric matching, Hamiltonian and momentum constraints,
  metric junction equation, \(a_\Sigma=1\), and stored wall traces.
- Gauge: the coordinate displacement \(\zeta\) used to represent fixed
  support and the longitudinal scalar \(E\).
- Dynamical: the already declared constraint-reduced bulk and intrinsic B1
  fields.
- Unspecified: \(\mathcal S_\Sigma\) and any variational rule for
  \(x\)-dependent embedding deformations.

The homogeneous \(\mathcal S_\Sigma\) trace is gauge invariant, but it cannot
be called a physical radion, residual gauge trace, or genuine zero mode
without a domain principle.

## Constraint and kinetic consequence

The exact v6.12 source remains

\[
J_{\rm shift}(t)=
-\frac{3\tau\chi_1t}{4\sin^2(\pi t/4)}.
\]

Because no endpoint condition follows from the action, this sprint does not
construct

\[
\mathcal L_CY=J_{\rm shift}.
\]

Its differential domain, kernel, adjoint kernel, and solvability condition
remain undefined. A pseudoinverse would silently choose a boundary
condition, so no Green operator is introduced.

The preserved kinetic decomposition is

\[
k_q^E=K_{\rm scalar}+K_{\rm shift+endpoint}^{\rm red}+K_{\rm Weyl},
\]

\[
K_{\rm scalar}\ge2,\qquad
K_{\rm Weyl}=\frac{3\chi_1^2(4-\pi)^2}{16\pi}>0,\qquad
F_0=M_4^2=\frac{\pi}{2}.
\]

\(K_{\rm shift+endpoint}^{\rm red}\) and the sign of \(k_q^E\) remain
undetermined. No Einstein-frame curvature or mass is calculated.

The exact next input is a repository-level declaration of whether
\(\iota\) is fixed or freely varied under \(x\)-dependent deformations. If it
is varied, its action-derived shape/momentum domain must be supplied. If it
is fixed, an action-derived boundary threading domain for
\(\mathcal S_\Sigma\) is required.

No new action term, primitive, `tau_J`, tension, radion potential, measured
input, neutral work, or arbitrary boundary condition is introduced.
