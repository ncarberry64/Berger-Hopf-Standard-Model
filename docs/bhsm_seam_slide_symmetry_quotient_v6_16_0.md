# BHSM v6.16: Finite Seam-Slide Symmetry and Interface Quotient Theorem

## Primary theorem

```text
BHSM_SEAM_SLIDE_HAS_NONZERO_HIGHER_ORDER_ACTION_COST
```

The first normal jet of a collar gluing extension is not the threading trace
left unresolved by v6.15. In outward-cap conventions,

\[
 \lambda_{\rm jet}
 =
 {\cal S}^{\rm out}_{\Sigma,+}
 -
 {\cal S}^{\rm out}_{\Sigma,-},
\]

whereas the surviving Z2-compatible trace is

\[
 \overline{\cal S}_\Sigma
 =
 \frac12\left(
 {\cal S}^{\rm out}_{\Sigma,+}
 +
 {\cal S}^{\rm out}_{\Sigma,-}
 \right).
\]

Z2 parity sets \(\lambda_{\rm jet}=0\) while leaving
\(\overline{\cal S}_\Sigma\) arbitrary. A finite collar-extension
automorphism therefore does not slide the unresolved trace.

The minimal Z2-compatible finite field map that does change
\(\overline{\cal S}_\Sigma\) changes the radial shift. For nonconstant seam
potential \(\lambda(x)\), it changes the one-sided extrinsic curvature and
\([Q_{\mu\nu}]\). Its first action variation vanishes after the bulk
constraints and junction equation are imposed, but the P1 action has a
generically nonzero quadratic Hessian contribution. Thus the linear
presymplectic null direction is not an exact finite interface redundancy.

No quotient is adopted, \({\cal S}_\Sigma=0\) is not a valid representative
condition, and

```text
unresolved_interface_trace_count_before = 1
unresolved_interface_trace_count_after  = 1
```

The fold route remains paused.

Subsidiary results are

```text
BHSM_SEAM_THREADING_IS_NOT_THE_FIRST_NORMAL_GLUE_JET
BHSM_CORE_CONTACT_FUNCTIONAL_NOT_PRESENT_IN_FROZEN_ACTION
BHSM_SEAM_SLIDE_HAS_NO_FIRST_CLASS_GENERATOR
BHSM_ZERO_THREADING_SHORTCUT_REMAINS_REJECTED
```

## 1. Provenance and source audit

| Object | Repository status |
| --- | --- |
| P1 Einstein--Hilbert action | Explicit stored action term |
| GHY completion | Explicit stored action term |
| Bulk scalar action | Explicit stored action term |
| Intrinsic B1 action | Adopted BHSM axiom |
| Exact metric matcher | Explicit stored action term in the provisional B1 domain |
| Fixed B1 embedding and Z2 cap exchange | Explicit stored domain declaration |
| Tensor pullback and collar-flow theorems | Adopted from established physics/mathematics |
| Common core is non-spatiotemporal | Adopted BHSM axiom in the v6.2 handoff |
| Core-contact functional | Absent structure |
| Uniform contact independent of threading | Proposed BHSM identification, not adopted |
| Seam-slide group acting on \({\cal S}_\Sigma\) | Absent structure |

The audit inspected the v6.1.4 double cap, v6.1.7 fold, v6.12 radial ADM
constraint, v6.13 endpoint domain, v6.14 composite support, v6.15
presymplectic threading result, v6.1.3 frozen action, v6.2 ontology, and the
v5.12 collar/core-source search.

The repository does not define a core-contact functional on which a
seam-slide invariance test could be performed. The v5.12 core-source audit
also records no action-derived core transfer mechanism.

The only retained core ontology used here is:

```text
the common core is non-spatiotemporal
```

No metric, distance, duration, density, ordinary inside/outside relation, or
bulk stress tensor is assigned to the common core.

## 2. Three variables remain distinct

The wall displacement,

\[
 \zeta(x),
\]

moves the support of B1.

The fold amplitude,

\[
 q(x),
\]

changes the scalar-wall and cap solution. It remains a static fold
coordinate, not a certified four-dimensional field.

The threading trace,

\[
 {\cal S}_\Sigma
 =
 [B+N_0^2\zeta-a_0^2\partial_\rho E]_\Sigma,
\]

is a gauge-invariant radial-shift/longitudinal boundary trace.

The v6.14 composite level set can determine \(\zeta\) on one selected center
manifold. It does not determine \({\cal S}_\Sigma\). A candidate seam slide
must therefore change \({\cal S}_\Sigma\) without being a normal wall
translation or a change of \(q\).

The minimal candidate tested below has

\[
 \delta_\lambda\zeta=0,\qquad
 \delta_\lambda q=0,\qquad
 \delta_\lambda\sigma=0,\qquad
 \delta_\lambda{\cal S}_\Sigma=\lambda.
\]

## 3. Full collar gluing data

Let

\[
 U_+=[-\epsilon,0]\times\Sigma,\qquad
 U_-=[0,\epsilon]\times\Sigma,
\]

and extend the interface identification into the collars by

\[
 G:(y,x)_+\sim(-y,\Phi_y(x))_-.
\]

The zeroth jet is

\[
 \Phi_0=\phi_\Sigma.
\]

In the frozen B1 coordinates,

\[
 \phi_\Sigma=\operatorname{id}.
\]

The first normal jet is

\[
 V^\mu
 =
 \left.\partial_y\Phi_y^\mu\right|_{y=0}
 =
 D^\mu\lambda_{\rm jet}+V_T^\mu.
\]

It is an extension of the gluing away from the interface, not part of the
zeroth-jet induced-metric identification.

### Metric pullback

On the minus collar, write

\[
 ds_-^2=N_-^2dy_-^2+
 h^-_{\alpha\beta}
 (dx_-^\alpha+N_-^\alpha dy_-)
 (dx_-^\beta+N_-^\beta dy_-).
\]

At \(y=0\),

\[
 y_-=-y,\qquad
 dx_-^\alpha
 =
 dx^\alpha+V^\alpha dy.
\]

Therefore

\[
 dx_-^\alpha+N_-^\alpha dy_-
 =
 dx^\alpha+(V^\alpha-N_-^\alpha)dy.
\]

Comparing the pulled-back cross metric with the plus collar gives

\[
 V_\mu=N_{+,\mu}+N_{-,\mu}
\]

in signed collar orientations.

For the scalar longitudinal sector, the gauge-completed relation is

\[
 V^\mu
 =
 D^\mu\lambda_{\rm jet},
\qquad
 \lambda_{\rm jet}
 =
 {\cal S}^{\rm common}_{\Sigma,+}
 +
 {\cal S}^{\rm common}_{\Sigma,-}.
\]

Using

\[
 {\cal S}^{\rm common}_{\Sigma,+}
 ={\cal S}^{\rm out}_{\Sigma,+},
\qquad
 {\cal S}^{\rm common}_{\Sigma,-}
 =-{\cal S}^{\rm out}_{\Sigma,-},
\]

this becomes

\[
 \boxed{
 \lambda_{\rm jet}
 =
 {\cal S}^{\rm out}_{\Sigma,+}
 -
 {\cal S}^{\rm out}_{\Sigma,-}.
 }
\]

The normalization contains no guessed numerical factor:
\(V^\mu=D^\mu\lambda_{\rm jet}\).

By contrast, v6.15 leaves

\[
 \boxed{
 \overline{\cal S}_\Sigma
 =
 \frac{
 {\cal S}^{\rm out}_{\Sigma,+}
 +
 {\cal S}^{\rm out}_{\Sigma,-}
 }{2}
 }
\]

unresolved. Z2 compatibility requires

\[
 {\cal S}^{\rm out}_{\Sigma,+}
 =
 {\cal S}^{\rm out}_{\Sigma,-},
\]

so

\[
 \lambda_{\rm jet}=0,\qquad
 \overline{\cal S}_\Sigma
 =
 {\cal S}^{\rm out}_{\Sigma,+}.
\]

Consequently a collar-extension seam jet is orthogonal to the remaining
threading datum.

## 4. Collar-flow automorphism

For a smooth vector field \(V\) on \(\Sigma\), a finite collar extension may
be written locally as

\[
 \Phi_y=\operatorname{Flow}_y(V).
\]

On compact spatial \(S^3\), every smooth \(V\) is complete as a tangential
flow. For a sufficiently small collar this gives a regular, invertible
extension with no topology change, caustic, pole obstruction, or
normal-bundle holonomy.

This is a noncanonical collar-extension choice. It changes
\(\lambda_{\rm jet}\), not \(\overline{\cal S}_\Sigma\).

The purely longitudinal family \(V=D\lambda\) is also not closed under
arbitrary finite compositions:

\[
 [D\lambda_1,D\lambda_2]
\]

is not generally a gradient. The full collar-extension group is a
diffeomorphism group and develops transverse components through the
Baker--Campbell--Hausdorff series.

This genuine coordinate/collar redundancy therefore cannot be used as the
desired quotient group.

## 5. Infinitesimal threading-slide candidate

The minimal Z2-compatible transformation of the free average is

\[
 \delta_\lambda
 {\cal S}^{\rm out}_{\Sigma,+}
 =
 \delta_\lambda
 {\cal S}^{\rm out}_{\Sigma,-}
 =
 \lambda.
\]

In one common orientation,

\[
 \delta_\lambda
 {\cal S}^{\rm common}_{\Sigma,+}
 =
 \lambda,
\qquad
 \delta_\lambda
 {\cal S}^{\rm common}_{\Sigma,-}
 =
 -\lambda.
\]

Choose a smooth reflected collar profile \(c_\pm(\rho)\) equal to one at the
junction and vanishing near each pole. A minimal extension is

\[
 \delta_\lambda B^{\rm common}_+
 =
 c_+(\rho) \lambda(x),
\qquad
 \delta_\lambda B^{\rm common}_-
 =
 -c_-(\rho) \lambda(x),
\]

with

\[
 \delta_\lambda E=
 \delta_\lambda\zeta=
 \delta_\lambda N=
 \delta_\lambda h_{\mu\nu}|_\Sigma=
 \delta_\lambda\sigma=0.
\]

The induced metric, scalar pullback, B1 fields, and intrinsic B1 stress are
unchanged at fixed support. The tangential shift changes by

\[
 \delta_\lambda N_\mu=D_\mu\lambda
\]

in each outward-cap convention.

Using the stored ADM formula,

\[
 K_{\mu\nu}
 =
 \frac{1}{2N}
 \left(
 \partial_\rho h_{\mu\nu}
 -D_\mu N_\nu-D_\nu N_\mu
 \right),
\]

gives

\[
 \boxed{
 \delta_\lambda K_{\mu\nu}
 =
 -\frac1N D_\mu D_\nu\lambda.
 }
\]

Therefore

\[
 \delta_\lambda Q_{\mu\nu}
 =
 -\frac1N
 \left(
 D_\mu D_\nu\lambda
 -h_{\mu\nu}D^2\lambda
 \right),
\]

up to the displayed index convention. It is nonzero for a generic
nonconstant \(\lambda\). The doubled \([Q]\) changes rather than cancelling.

The candidate thus fails the requested simultaneous conditions

\[
 \delta_\lambda\gamma_{\mu\nu}=0,\qquad
 \delta_\lambda\sigma_\Sigma=0,\qquad
 \delta_\lambda[Q_{\mu\nu}]=0.
\]

Compensating \(\partial_\rho h_{\mu\nu}\) to restore \(Q\) changes the bulk
normal metric jet and curvature. If the compensation is completed to an
ordinary bulk diffeomorphism, the v6.13 gauge law instead leaves
\({\cal S}_\Sigma\) invariant. No stored transformation changes
\({\cal S}_\Sigma\) while preserving all these data.

## 6. Finite threading field map

The minimal infinitesimal candidate integrates algebraically to

\[
 T_\lambda:
 \left(
 {\cal S}^{\rm out}_{\Sigma,+},
 {\cal S}^{\rm out}_{\Sigma,-}
 \right)
 \mapsto
 \left(
 {\cal S}^{\rm out}_{\Sigma,+}+\lambda,
 {\cal S}^{\rm out}_{\Sigma,-}+\lambda
 \right).
\]

It satisfies

\[
 T_0=\operatorname{id},
\]

\[
 T_{\lambda_1}T_{\lambda_2}
 =
 T_{\lambda_1+\lambda_2},
\]

\[
 T_\lambda^{-1}=T_{-\lambda}.
\]

With a smooth reflected extension, it maps the broad off-shell fixed-Z2
multiplier domain to itself and preserves the ADM determinant because that
determinant is independent of the shift. It produces no topology change or
collar caustic.

It is not uniquely determined by its boundary parameter: infinitely many
regular bulk profiles have the same boundary value. More importantly, it is
not an action symmetry and does not map a general solution to another
solution while the other fields are held fixed.

A spacetime-constant \(\lambda\) has \(D_\mu\lambda=0\). It changes only the
additive convention for the scalar shift potential and is a trivial
stabilizer. It cannot remove the local threading function. A
time-independent spatial \(S^3\) harmonic with \(\ell\ge1\) has a nonzero
Hessian. A spatially uniform but time-dependent parameter is also
nontrivial through \(D_t\lambda\).

## 7. Off-shell action test

### P1 plus GHY

At fixed \(h\) and \(N\), the radial ADM kinetic combination changes through

\[
 K_{\mu\nu}K^{\mu\nu}-K^2.
\]

Its linear term is

\[
 2Q^{\mu\nu}\delta_\lambda K_{\mu\nu}
 =
 -\frac2N Q^{\mu\nu}D_\mu D_\nu\lambda.
\]

After integration by parts, this is the bulk momentum-constraint
contraction plus the corresponding tangential and radial endpoint
divergences. It is generically nonzero fully off shell.

The quadratic term is

\[
 \boxed{
 \delta_\lambda^{(2)}
 (K_{\mu\nu}K^{\mu\nu}-K^2)
 =
 \frac1{N^2}
 \left[
 (D_\mu D_\nu\lambda)^2
 -(D^2\lambda)^2
 \right].
 }
\]

Thus the P1+GHY action is not invariant after the linear constraint term
vanishes.

For a time-independent scalar harmonic on round \(S^3\),

\[
 -D^2\lambda_\ell
 =
 \frac{\ell(\ell+2)}{a^2}\lambda_\ell.
\]

The Bochner identity gives

\[
 \int_{S^3}
 \left[
 (D_iD_j\lambda_\ell)^2
 -(\Delta\lambda_\ell)^2
 \right]
 =
 -\int_{S^3}
 {\rm Ric}(D\lambda_\ell,D\lambda_\ell)
\]

and hence

\[
 =
 -\frac{2\ell(\ell+2)}{a^4}
 \int_{S^3}\lambda_\ell^2.
\]

It is nonzero for every \(\ell\ge1\). This is an analytic non-invariance
test, not a numerical kinetic evaluation.

### GHY separately

The trace changes by

\[
 \delta_\lambda K=-N^{-1}D^2\lambda.
\]

Its integral is a closed-slice divergence only under the corresponding
homogeneous coefficient assumptions. The combined P1+GHY conclusion above
does not depend on treating GHY as a new interface energy.

### Bulk scalar

The normal derivative contains the shift:

\[
 n\sigma
 =
 N^{-1}(\partial_\rho\sigma-N^\mu D_\mu\sigma).
\]

Therefore

\[
 \delta_\lambda(n\sigma)
 =
 -N^{-1}D^\mu\lambda D_\mu\sigma.
\]

The scalar action is not invariant for a general off-shell scalar. It is
unchanged on the homogeneous static fold, where \(D_\mu\sigma=0\).

### Intrinsic B1 and matcher

The intrinsic B1 action is unchanged because its metric and fields are held
fixed. At fixed support the induced bulk metric is \(h_{\mu\nu}\), so the
algebraic matching constraint is also unchanged. These facts do not cancel
the bulk P1 or scalar changes.

### Invariance hierarchy

The result is:

| Test level | Invariant? |
| --- | --- |
| Fully off shell | No; the linear constraint contraction is present |
| After metric matching only | No |
| After bulk constraints, at first order | Yes |
| After junction equation, at first order | Yes |
| Static fold family, at first order | Yes |
| Static fold family, at quadratic order | No for nonconstant \(\lambda\) |

Thus

\[
 \Delta_\lambda S
 =
 A_1[\lambda]+A_2[\lambda,\lambda]+\cdots,
\]

with \(A_1\ne0\) generically off shell, \(A_1=0\) on the constrained
solution, and \(A_2\ne0\) for nonconstant spatial harmonics. The first
possible nonzero cost on the solution family is second order.

No anchoring potential or coefficient was added to obtain this result.

## 8. Uniform core-contact proposal

Because no core-contact functional is stored, the strongest conditional
statement is the abstract proposal

\[
 {\cal C}_{\rm core}
 =
 {\cal C}_{\rm core}
 [
 \gamma,\text{ topology},\text{ orientation class},
 \text{ conserved charges},\text{ scalar-wall support},
 \text{ allowed interface invariants}
 ],
\]

with

\[
 \frac{\partial{\cal C}_{\rm core}}
 {\partial{\cal S}_\Sigma}=0.
\]

This is an admissible coefficient-free BHSM identification and does not
conflict with a non-spatiotemporal core. It is not derived from the absence
of an \(S_\Sigma\) term in the action, is not inserted into the action, and
is not adopted here.

Even if adopted, it would state only that an otherwise undefined
core-contact label is insensitive to threading. It would not remove the
changes in \(K_{\mu\nu}\), \([Q_{\mu\nu}]\), bulk curvature, or the P1 action.
It is therefore insufficient to construct an exact \(T_\lambda\)
equivalence.

The distinction is:

```text
the stored core/contact sector does not see S_Sigma
```

does not imply

```text
the complete physical state identifies all values of S_Sigma.
```

## 9. Observable audit

For the minimal finite candidate:

| Object | Result |
| --- | --- |
| Induced metric and intrinsic curvature | Exactly invariant |
| Intrinsic B1 fields, stress, currents, and relevant holonomies | Exactly invariant |
| Scalar pullback, wall zero set, \(\zeta\), \(q\), \(\tau\), and \(s\) | Exactly invariant |
| One-sided extrinsic curvature | Changed for nonconstant \(\lambda\) |
| \(Q\) jump | Changed for nonconstant \(\lambda\) |
| Bulk curvature invariants | Changed generically |
| Scalar normal derivative | Changed off shell; invariant on the homogeneous fold |
| Topology and orientation | Exactly invariant |
| Causal/geodesic relations confined to declared \(M_4\) | Invariant because \(h\) is fixed |
| Bulk causal relations | Changed generically |
| Matching multiplier after elimination | Not a physical observable |
| Bulk gravitational charge change | Not evaluated |
| Stored core-contact label | Undefined |
| Conditional uniform-contact label | Invariant by the proposed definition only |
| Frozen predictions | Exactly invariant |

The changes in \([Q]\), bulk curvature, and the action already fail the
observable-invariance requirement for a quotient.

## 10. Noether and nonlinear presymplectic test

v6.15 derived

\[
 \iota_{\partial/\partial{\cal S}_\Sigma}
 \Omega_\Sigma=0.
\]

The shift has no radial canonical momentum, so a pure multiplier variation
remains a null direction of the extended ADM presymplectic form at nonlinear
order:

\[
 \iota_{\delta_\lambda^{\rm multiplier}}\Omega_{\rm ADM}=0.
\]

One may write the trivial extended-space relation

\[
 G_{\rm multiplier}[\lambda]=0.
\]

This does not prove gauge symmetry. The multiplier-only vector is not
tangent to the nonlinear solution space when the canonical fields are held
fixed, and it is not an action symmetry.

The actual first-class momentum generator is

\[
 G_{\rm diff}[\xi]
 =
 \int_C \xi^\mu{\cal C}_\mu
 +\text{allowed boundary term}.
\]

It generates the already declared boundary-preserving diffeomorphisms.
Those transformations leave \({\cal S}_\Sigma\) invariant. No new Noether
identity, first-class constraint, boundary charge, or reducibility identity
acts as the proposed seam slide.

The correct canonical interpretation is therefore:

```text
auxiliary multiplier presymplectic null
+ nonlinear action lifting
!= first-class interface redundancy.
```

## 11. Classification

The candidate is not:

- an exact interface redundancy;
- a global on-shell solution degeneracy;
- a physical flat modulus;
- an old bulk or boundary-preserving diffeomorphism.

The finite field map exists, but it is not an action symmetry and changes
junction data. The v6.15 null direction is consequently classified as an
auxiliary/domain direction whose apparent linear degeneracy is lifted by a
quadratic action cost for nonconstant \(\lambda\).

This yields the single primary classification

```text
BHSM_SEAM_SLIDE_HAS_NONZERO_HIGHER_ORDER_ACTION_COST
```

The threading value remains a domain label until an action-derived boundary
condition or a stronger explicitly adopted equivalence theorem is supplied.
No family of physically distinguishable equal-action solutions has been
constructed, so it is not promoted to a physical flat modulus or radion.

## 12. Quotient test

Because \(T_\lambda\) is not an action symmetry, no physical equivalence
relation

\[
 {\cal C}_{\rm admissible}/{\cal G}_{\rm seam}
\]

is defined.

The set

\[
 \left\{
 ({\cal S}^{\rm out}_++\lambda,
  {\cal S}^{\rm out}_-+\lambda)
 \right\}
\]

is a family of off-shell field maps, not an equivalence orbit.

Its spacetime-constant parameters with \(D_\mu\lambda=0\) are trivial
stabilizers of the shift-potential representation. There is no local slice,
residual seam group, or quotient Jacobian to compute.

In particular,

\[
 {\cal S}_\Sigma=0
\]

is not a valid quotient representative. Imposing it would remain an
arbitrary interface condition.

## 13. Threading and fold consequence

The count remains

\[
 \boxed{
 \texttt{unresolved_interface_trace_count_before}=1,
 }
\]

\[
 \boxed{
 \texttt{unresolved_interface_trace_count_after}=1.
 }
\]

No representative condition, adjoint domain, kernel count, or unique Green
operator follows.

The uniform core-contact proposal is not required to reach this verdict.
Adopting it would not remove the bulk action obstruction by itself.

The fold decision remains:

```text
keep the fold route paused.
```

The exact next input is either:

1. an action-derived interface boundary condition for
   \({\cal S}_\Sigma\); or
2. an explicitly adopted BHSM equivalence theorem with transformation laws
   that also remove the \(Q\), bulk-curvature, and action distinctions.

Until then, \(q(x)\) is not reconsidered as a certified four-dimensional
field. This sprint does not calculate

\[
 k_q^E,\quad B_{\rm ext}^E,\quad B_{\rm core}^E,\quad
 m_{\rm ext}^2,\quad m_{\rm core}^2.
\]

The preserved fold data are

\[
 F_0=M_4^2=\frac{\pi}{2},\qquad
 K_{\rm scalar}\ge2>0,
\]

\[
 K_{\rm Weyl}
 =
 \frac{3\chi_1^2(4-\pi)^2}{16\pi}>0.
\]

## Integrity boundary

No action term, anchoring potential, anchoring coefficient, numerical or
dimensionful primitive, arbitrary threading condition, boundary tension,
`tau_J`, radion potential, measured input, neutral work, or physical bulk
Dirac law is introduced. No Green operator or fold kinetic coefficient is
constructed. Frozen predictions and official prediction logic remain
unchanged.
