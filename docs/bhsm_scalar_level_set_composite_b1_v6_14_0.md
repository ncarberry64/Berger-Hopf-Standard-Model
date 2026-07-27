# BHSM v6.14.0 scalar-level-set and blow-up composite B1 theorem

Primary result:
`BHSM_COMPOSITE_B1_SUPPORT_LEAVES_ENDPOINT_THREADING_OPEN`.

Subsidiary results:

- `BHSM_DIRECT_SCALAR_LEVEL_SET_IS_SINGULAR_AT_THE_FOLD`;
- `BHSM_B1_LEVEL_SET_IS_ONLY_A_CENTER_MANIFOLD_CHART`;
- `BHSM_PROJECTIVE_SCALAR_SUPPORT_REQUIRES_AN_ADDITIONAL_DOMAIN_AXIOM`.

The scalar wall supplies a regular and locally unique branchwise level set
for sufficiently small \(q>0\). At the fold, however, the bulk scalar
vanishes everywhere and cannot define a hypersurface. Dividing by the
invariant scalar norm produces a regular projective limit \(s u_1\), whose
simple endpoint zero reproduces the exact v6.1.7 endpoint response.

This blow-up is a coefficient-free collective chart on the selected
one-dimensional center manifold. It is not a new field and is not an adopted
support law of the frozen fixed-\(\iota\) B1 action. Adopting it would change
the off-shell configuration-space domain and induce scalar/B1 shape terms.
Even conditionally, it fixes the displacement \(\zeta\), not the remaining
gauge-invariant endpoint threading trace.

## Provenance

| Ingredient | Status | Scope |
| --- | --- | --- |
| Regular-level-set normal, pullback, and shape formulas from PO-BH-58/59 | Adopted from established physics/mathematics | Conditional standard geometry, not an old BHSM profile theorem |
| Normal displacement and shape formulas from v5.11/v5.12 | Adopted from established physics/mathematics | Formula only; old symbolic surface coefficients are not imported |
| Fixed-\(\iota\) intrinsic B1 and exact metric matching | Adopted BHSM axiom | Provisional v6.1.3 boundary ontology |
| Lowest odd Dirichlet scalar mode | Numerically validated | v6.1.5/v6.1.6 bulk \(\sigma\), not \(\sigma_\partial\) |
| Nonlinear Puiseux sheets and moving endpoint | Derived consequence | Conditional v6.1.7 frozen representative |
| Direct level-set failure at the fold | Rejected by calculation | \(\sigma_0=0\), \(\nabla\sigma_0=0\) |
| Missing invariant threading domain | Active construction target | v6.12/v6.13 obstruction |
| \(\iota=\iota[\widehat\sigma]\) | BHSM identification | Candidate tested here, not adopted |

## Direct scalar level set

On a fixed scalar sign \(s=\pm1\) and sheet \(\tau=\pm1\),

\[
\sigma_{\tau,s}(q,\rho)
=s\left[q\,u_1(\rho)+q^2u_{2,\tau}(\rho)+O(q^3)\right].
\]

At its junction zero,

\[
\partial_\rho\sigma|_\Sigma
=s\left[q\,u_1'(\rho_J)+O(q^2)\right].
\]

The stored value

\[
u_1'(\rho_J)=-9.124976903426\ldots
\]

is nonzero. Therefore zero is a regular value for every sufficiently small
\(q>0\). The implicit-function theorem gives a locally unique junction zero.
Moreover, \(u_1\) is the lowest regular-pole/Dirichlet
Sturm--Liouville eigenfunction. It has no interior nodes; small branch
corrections preserve the absence of additional cap zeros.

Multiplication by \(s\) changes scalar and normal orientation, not the zero
set. The sheet label changes \(u_{2,\tau}\) and the endpoint response, not
regularity. The Z2-odd two-cap continuation reverses the scalar across the
common zero junction.

At \(q=0\),

\[
\sigma_0(\rho)=0,\qquad \nabla_A\sigma_0=0
\]

for every point in the cap. Its zero set is the entire cap. It is not a
regular hypersurface.

## Invariant amplitude and blow-up chart

The stored per-cap scalar norm is

\[
Q[\sigma]^2
=\int_0^{\rho_J}a^4\sigma^2\,d\rho
\]

in proper-normal gauge, or equivalently

\[
Q[\sigma]^2
=\int_0^1Na^4\sigma^2\,dt
\]

on the fixed domain. Using

\[
\int_0^{\rho_J}a_0^4u_1^2\,d\rho=1,
\]

the branch expansion gives

\[
Q[\sigma]^2=q^2[1+2\alpha_\tau q+O(q^2)],
\]

\[
Q[\sigma]=q+\alpha_\tau q^2+O(q^3),
\qquad
q=Q-\alpha_\tau Q^2+O(Q^3).
\]

For \(Q>0\), define

\[
\widehat\sigma=\frac{\sigma}{Q[\sigma]}.
\]

Then

\[
\widehat\sigma
=s\left[u_1+q(u_{2,\tau}-\alpha_\tau u_1)+O(q^2)\right]
\longrightarrow s u_1.
\]

Consequently

\[
\Sigma_0=\{u_1=0\}=\{\rho_J\}
\]

is a regular limiting support because \(u_1'(\rho_J)\ne0\).

The norm is a radial-coordinate invariant scalar integral.
\(\widehat\sigma\) and its zero set transform covariantly under radial and
four-dimensional diffeomorphisms. Positive constant rescaling changes the
profile normalization but not its zeros. A two-cap norm adds a fixed
\(\sqrt2\), again leaving the support unchanged.

The blow-up chart is nonlocal but introduces no physical field. It is unique
only along the selected one-dimensional center manifold. At
\(\sigma=0\), general off-center-manifold approaches select different
projective profiles and potentially different zeros.

## Composite endpoint response

For any regular profile \(f\) defining \(f(X(x))=0\), the outward-cap
convention gives

\[
\zeta=-\frac{\delta f}{n^A\partial_Af}\bigg|_\Sigma .
\]

For \(q>0\), this applies to \(f=\sigma\). It must not be evaluated at the
fold because \(\sigma'_\Sigma=O(q)\).

At the fold, the projective profile gives

\[
\zeta_0=-\frac{\delta\widehat\sigma}
{n^A\partial_A\widehat\sigma}\bigg|_{\Sigma_0}.
\]

Differentiating
\(\widehat\sigma(q,\rho_J(q))=0\) yields

\[
\partial_q\widehat\sigma|_J
+s u_1'(\rho_J)\partial_q\rho_J=0.
\]

The exact v6.1.7 cap family has

\[
\partial_q\rho_{J,\tau}=-\tau\frac{\chi_1}{4}.
\]

Hence

\[
\partial_q\widehat\sigma|_J
=s\tau\frac{\chi_1}{4}u_1'(\rho_J),
\]

and

\[
\zeta_0=-\tau\frac{\chi_1}{4}\delta q.
\]

This reproduces the full endpoint coefficient, not merely its sign. The
unknown normalization correction \(\alpha_\tau\) drops out because
\(u_1(\rho_J)=0\).

## Configuration-space and action-equivalence test

The current independent variables remain

\[
(g,\sigma,h,A,\sigma_\partial,\Lambda),
\]

with fixed \(\iota\). The candidate relation

\[
\iota=\iota[\widehat\sigma]
\]

would make the support dependent while leaving \(h,A,\sigma_\partial\) as
independent intrinsic B1 fields. In particular,
\(\sigma\ne\sigma_\partial\).

The relation is not required by the current action and has not been adopted
as a BHSM axiom. Although coefficient-free on the fold center manifold, it is
an additional off-shell domain restriction.

For a fixed regular \(f\),

\[
\int_\Sigma\sqrt{|\gamma|}\,\mathcal L_{\rm B1}
=\int_M\sqrt{|g|}\,\delta(f)|\nabla f|\,
\mathcal L_{\rm B1}.
\]

This distributional expression is only a cross-check. It is orientation and
scalar-sign independent, and the common Z2 junction is counted once.

The two representations cease to be a mere rewriting when \(f\) is varied.
The surface then moves and generates shape, scalar-flux, B1-pullback, and
matching-pullback terms absent from the fixed-\(\iota\) variation. This
introduces no new local density or coefficient, but it does create a
scalar--B1 coupling through an adopted domain restriction.

## Shape and scalar variation

The general moving-support variation has the form

\[
\delta_\iota S
=\int_\Sigma\sqrt{|\gamma|}\,\zeta\,\mathcal E_{\rm shape}
+\text{tangential divergence}
+\text{existing field equations}.
\]

With composite support,

\[
\delta_\iota S
=-\int_\Sigma\sqrt{|\gamma|}
\frac{\delta\widehat\sigma}
{n\cdot\partial\widehat\sigma}\,
\mathcal E_{\rm shape}+\cdots .
\]

For a fully covariant moving-support formulation, the embedding equation is
the normal-diffeomorphism Ward combination of the bulk equations and metric
junction. It must not be counted as an independent new force law. In the
current fixed-\(\iota\) action it is absent. Under the unadopted composite
domain it would be finite only after projection to the center manifold.

On fixed support,

\[
\delta\sigma_\Sigma=0
\]

is independently imposed Dirichlet data. Under composite support it becomes
the linearized defining identity

\[
\delta\widehat\sigma_\Sigma+
(n\cdot\partial\widehat\sigma)\zeta=0.
\]

It cannot simultaneously be imposed as an independent Dirichlet variation.
The scalar integration-by-parts flux, moving-domain term, B1 pullback, and
matcher pullback would combine into the projected transversality expression.
Because the composite domain is not adopted, no new natural flux or wall
pressure condition follows from the current action.

## Endpoint threading and fold limit

The preserved invariant is

\[
\mathcal S_\Sigma
=[B+N_0^2\zeta-a_0^2\partial_\rho E]_\Sigma .
\]

For \(q>0\),

\[
\mathcal S_\Sigma^{\rm comp}
=\left[
B-N_0^2\frac{\delta\sigma}{n\cdot\partial\sigma}
-a_0^2\partial_\rho E
\right]_\Sigma .
\]

At the fold,

\[
\mathcal S_{\Sigma_0}^{\rm comp}
=\left[
B-N_0^2\frac{\delta\widehat\sigma}
{n\cdot\partial\widehat\sigma}
-a_0^2\partial_\rho E
\right]_{\Sigma_0}.
\]

This supplies one relation for \(\zeta\), but no condition on
\(\mathcal S_\Sigma\). Pole regularity remains the only stored radial-domain
condition; B1 supplies zero conditions on the invariant threading trace, so
one endpoint trace remains unresolved. The exact constraint differential
order and kernel are not invented without the missing scalar ADM operator.

Power counting gives

\[
\sigma'_\Sigma=O(q),\qquad
\widehat\sigma'_\Sigma=O(1),
\]

\[
\zeta_{\rm direct}=O(\delta\sigma/q),\qquad
\zeta_{\rm blowup}=O(\delta\widehat\sigma).
\]

Center-manifold tangent variations are finite. Scalar-sign and sheet changes
are discrete rather than infinitesimal. Arbitrary off-branch or orthogonal
fluctuations select approach-dependent projective profiles.

Therefore the blow-up chart cannot yet be used to evaluate \(k_q^E(0)\).
The viable route is to adopt and derive a composite-support
transversality/threading domain—or derive another action-selected endpoint
condition—then calculate at \(q>0\) and take a controlled \(q\to0\) limit.

No new action term, coefficient, primitive, boundary tension, `tau_J`,
radion potential, measured input, neutral work, or physical bulk Dirac law
is introduced.
