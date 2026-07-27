# BHSM v6.15: Z2 Double-Cap Scalar Constraint and Interface Threading Domain

## Result

The primary theorem is

```text
BHSM_Z2_SYMPLECTIC_FLUX_LEAVES_ONE_INTERFACE_TRACE
```

The exact double-cap reflection relates the two one-sided threading traces,
but neither reflection parity, the linearized B1 junction equation, nor
vanishing total interface symplectic flux fixes their common amplitude.
Using each cap's outward orientation,

\[
 {\cal S}^{\rm out}_{\Sigma,-}
 =
 {\cal S}^{\rm out}_{\Sigma,+}.
\]

Using one common normal across the double,

\[
 {\cal S}^{\rm common}_{\Sigma,-}
 =
 -{\cal S}^{\rm common}_{\Sigma,+}.
\]

These are the same relation in two orientation conventions. They do not
imply \({\cal S}_\Sigma=0\). Exactly one gauge-invariant interface trace
remains unresolved.

The subsidiary results are

```text
BHSM_Z2_SHIFT_PARITY_DERIVED
BHSM_TWO_CAP_SHIFT_SOURCE_PARITY_DERIVED
BHSM_Z2_INTERFACE_SYMPLECTIC_FORM_DERIVED
BHSM_ADAPTED_REFLECTION_ZERO_THREADING_SHORTCUT_REJECTED
BHSM_MOVING_Z2_REFLECTION_REQUIRES_DOMAIN_EXTENSION
```

The fold-route decision is Case C: pause the fold kinetic route. No
convenient threading condition is selected.

## Status and provenance

| Item | Status | Scope |
| --- | --- | --- |
| Tensor pullback, oriented GHY variation, and Green boundary form | Adopted from established physics/mathematics | Standard geometry used with the repository's signs |
| Provisional B1 and exact metric matching | Adopted BHSM axiom | Frozen action domain |
| Signed-coordinate orientation ledger | BHSM identification | A convention derived from the stored pole-to-junction coordinates |
| Z2 threading and source parity | Derived consequence | No remembered orbifold table used |
| One surviving presymplectic-null trace | Derived consequence | Current action only |
| Adapted-reflection zero-threading shortcut | Rejected by calculation | Requires absent regularity and domain assumptions |
| Constraint Green operator | Active construction target | Blocked until an interface-domain axiom is supplied |

This report preserves

```text
BHSM_EXISTING_B1_VARIATION_DOES_NOT_SUPPLY_SHIFT_BOUNDARY_DATA
BHSM_COMPOSITE_B1_SUPPORT_LEAVES_ENDPOINT_THREADING_OPEN
```

and does not adopt the optional v6.14 composite support.

## 1. Exact double-cap orientation ledger

Both stored one-cap coordinates increase from a regular pole to the
junction:

\[
 \rho_+,\rho_-\in[0,\rho_J].
\]

Define a signed coordinate only after keeping that fact explicit:

\[
 y=
 \begin{cases}
   \rho_+-\rho_J,&M_+,\quad -\rho_J\le y\le0,\\
   \rho_J-\rho_-,&M_-,\quad 0\le y\le\rho_J.
 \end{cases}
\]

The cap exchange is

\[
 R:(y,x^\mu)\longmapsto(-y,x^\mu),
 \qquad \rho_+\longleftrightarrow\rho_-.
\]

Therefore

\[
 \partial_{\rho,+}=\partial_y,\qquad
 \partial_{\rho,-}=-\partial_y.
\]

Choose

\[
 n_{\rm common}=N^{-1}\partial_y.
\]

The cap outward normals are

\[
 n_+=N^{-1}\partial_{\rho,+}=n_{\rm common},
 \qquad
 n_-=N^{-1}\partial_{\rho,-}=-n_{\rm common}.
\]

Thus \(n_-=-n_+\) under the common interface identification.

For

\[
 K_{\mu\nu}=\frac12{\cal L}_n\gamma_{\mu\nu},\qquad
 Q_{\mu\nu}=K_{\mu\nu}-K\gamma_{\mu\nu},
\]

normal reversal changes the sign of \(K_{\mu\nu}\), \(K\), and
\(Q_{\mu\nu}\). Reflection-copied cap values obey

\[
 K^{\rm out}_-=K^{\rm out}_+,
 \qquad
 K^{\rm common}_-=-K^{\rm common}_+,
\]

and similarly for \(Q\). Hence

\[
 [Q_{\mu\nu}]
 =Q^{\rm common}_{\mu\nu,+}
  -Q^{\rm common}_{\mu\nu,-}
 =2Q^{\rm common}_{\mu\nu,+}.
\]

This is the v6.1.4 convention. It permits nonzero one-sided extrinsic
curvature and an intentional junction cusp.

For the odd wall,

\[
 \sigma_-(\rho)=-\sigma_+(\rho).
\]

It follows that \(\partial_y\sigma\) is even. Consequently

\[
 (n_{\rm common}\sigma)_-=(n_{\rm common}\sigma)_+,
 \qquad
 (n_-\sigma)_-=-(n_+\sigma)_+.
\]

Statements about common-normal and outward-normal scalar flux therefore
also cannot be interchanged.

## 2. Three distinct Z2 statements

The repository contains:

1. Background cap exchange: two identical static regular caps are exchanged.
2. Fixed-support orbifold parity: the declared gluing has fixed set
   \(\Sigma=\{y=0\}\).

It does not contain:

3. A varied moving reflection
   \[
   R_\zeta:y-\zeta(x)\mapsto-[y-\zeta(x)].
   \]

The homogeneous family \(\rho_J(q)\) consists of separately solved doubled
backgrounds. Its derivative

\[
 \partial_q\rho_{J,\tau}=-\tau\frac{\chi_1}{4}
\]

does not by itself define an \(x\)-dependent reflection map in one frozen
double.

The v6.14 composite level set could make the moving center dependent on
\(\widehat\sigma\), but only after the additional identification

\[
 \iota=\iota[\widehat\sigma]
\]

is adopted off shell. It is not current-action derived.

## 3. Tensor parity from the gluing pullback

The radial ADM metric is

\[
 ds_5^2=N^2dy^2+
 h_{\mu\nu}(dx^\mu+N^\mu dy)(dx^\nu+N^\nu dy).
\]

The Jacobian of \(R\) is
\(\operatorname{diag}(-1,1,1,1,1)\). A covariant component receives one
minus sign for every \(y\) index. Directly applying \(R^*g=g\) gives

| Quantity in signed \(y\) | Parity |
| --- | --- |
| \(g_{yy}\) | even |
| \(g_{y\mu}\) | odd |
| \(g_{\mu\nu}\) | even |
| positive lapse \(N\) | even |
| \(N_\mu\) | odd |
| scalar shift potential \(B\) | odd |
| \(\psi\) | even |
| \(E\) | even |
| odd-wall background \(\sigma\) | odd |
| fixed-sheet fold perturbation \(\delta\sigma\) | odd |
| \(\widehat\sigma\) | odd |
| fixed-gluing radial gauge parameter \(\xi^y\) | odd |
| tangential scalar gauge parameter \(\xi\) | even |

An arbitrary perturbation on the unrestricted cover can be decomposed into
even and odd scalar sectors. Background oddness alone is not a license to
add the even sector to the frozen orbifold domain. In the stored odd-wall
sector, arbitrary admissible scalar perturbations are odd and obey the
Dirichlet trace. The fold-amplitude tangent is in this sector.

Because \(\sigma_0'\) is even and a fixed-gluing \(\xi^y\) is odd, the pure
gauge perturbation

\[
 -\sigma_0'\xi^y
\]

is also odd.

For the gauge-invariant pullbacks, the resulting parities are

| Invariant | Parity |
| --- | --- |
| \(\Psi_\Sigma\) | even |
| \(\delta\sigma_\Sigma\) | odd and zero in the stored Dirichlet domain |
| \(\delta X_\Sigma\) | even |
| \({\cal S}_\Sigma\), common-normal form | odd one-sided trace |
| \({\cal S}_\Sigma\), outward-cap form | equal copied-cap traces |

The last line is derived for the full invariant, not by guessing the parity
of its terms.

## 4. Interface regularity is not smooth-junction regularity

The double is piecewise smooth and contains an intentional B1 junction.
The minimum stored regularity is:

- the induced metric has a common continuous trace;
- \(h_{\mu\nu}\), \(N\), \(\psi\), \(E\), and \(\sigma\) are piecewise
  regular on each cap;
- first normal derivatives may have finite one-sided jumps;
- \(K_{\mu\nu}\), \(Q_{\mu\nu}\), and scalar normal flux have finite
  one-sided traces governed by reflection and junction data;
- the odd scalar itself is continuous and has
  \(\sigma_\Sigma=0\).

Exact induced-metric matching does not independently match the radial shift
multiplier. It also does not require continuity of \(\partial_yE\).
Therefore parity supplies

\[
 B(0+)=-B(0-),\qquad
 \partial_yE(0+)=-\partial_yE(0-)
\]

as one-sided relations, but does not supply

\[
 B|_\Sigma=0,\qquad \partial_yE|_\Sigma=0.
\]

An odd function has a zero fixed-set value only after continuity of that
field is established. Imposing ordinary \(C^1\) evenness on the whole metric
would incorrectly force \(K=0\) and contradict the retained v6.1.4
background.

## 5. Allowed diffeomorphisms

A continuous diffeomorphism preserving the fixed gluing has

\[
 \xi^y(-y,x)=-\xi^y(y,x),\qquad
 \xi(-y,x)=\xi(y,x).
\]

Thus \(\xi^y|_\Sigma=0\). Such maps preserve both caps, pole regularity, and
the fixed interface. Composing with \(R\) exchanges the caps. Even
tangential \(\xi\) generates an intrinsic B1 reparameterization.

A transformation with \(\xi^y|_\Sigma\ne0\) moves the fixed set. It is not a
gauge transformation of the frozen double unless an embedding or moving
reflection map is added to the domain.

The v6.13 invariant is

\[
 {\cal S}_\Sigma
 =
 [B+N_0^2\zeta-a_0^2\partial_\rho E]_\Sigma.
\]

One may use allowed gauges to set \(E=0\), and Case I already has
\(\zeta=0\). A local Gaussian-normal chart may also set a shift component
to zero while moving information into the other variables. None of these
operations changes \({\cal S}_\Sigma\). The three conditions
\(\zeta=E=B=0\) are simultaneously possible only if
\({\cal S}_\Sigma\) was already zero or if a new domain restriction is
imposed.

The global quotient therefore does not remove the homogeneous
\({\cal S}_\Sigma\) trace as gauge.

## 6. Two-cap scalar momentum-constraint source

The stored one-cap source in its pole-to-junction orientation is

\[
 J_\tau(t)
 =
 -\frac{3\tau\chi_1t}
 {4\sin^2(\pi t/4)}.
\]

The two copied cap geometries give

\[
 (J^{\rm out}_+,J^{\rm out}_-)=(J_\tau,J_\tau).
\]

Converting the minus cap to the common normal contributes the derived
orientation sign:

\[
 (J^{\rm common}_+,J^{\rm common}_-)=(J_\tau,-J_\tau).
\]

The signed-interval source is therefore odd. The sheet label \(\tau\)
reverses both entries. The scalar sign \(s\) does not enter because the
fold source is geometric and the critical scalar flux vanishes.

For an even measure, the odd source has zero integral on the symmetric
double and is automatically orthogonal to an even constant test mode. This
is only a partial compatibility check. The exact coupled radial operator
and all adjoint kernels are not stored, so full Fredholm compatibility is
not certified.

## 7. Exact interface canonical pairing

For each oriented cap, P1 plus GHY gives the metric pair

\[
 \left(
 \gamma_{\mu\nu},
 \pi_{\rm out}^{\mu\nu}
 =\frac{\kappa_1}{2}Q_{\rm out}^{\mu\nu}
 \right).
\]

The scalar pair is

\[
 \left(
 \sigma_\Sigma,
 -Z_5 n_{\rm out}\sigma
 \right).
\]

Before imposing parity, the total interface potential is schematically

\[
 \Theta_{\Sigma,\rm total}
 =
 \Theta^{\rm out}_+
 +\Theta^{\rm out}_-
 +\Theta_{\rm B1}
 +\Theta_{\rm match}.
\]

In a common orientation, its metric coefficient is one half of

\[
 {\cal J}_{\mu\nu}
 =
 \kappa_1[Q_{\mu\nu}]
 +2C_\partial G_{\mu\nu}^{(4)}
 -T_{\partial,\mu\nu}.
\]

The exact matcher is algebraic. Imposing
\(h=\iota^*g\) and eliminating \(\Lambda\) removes the multiplier from the
combined junction equation.

The endpoint displacement is not an independent configuration variable in
the fixed-\(\iota\) action. The radial shift is an ADM multiplier, and its
radial canonical momentum vanishes. The invariant
\({\cal S}_\Sigma\) is consequently a gauge-invariant
radial-shift/longitudinal multiplier trace. It is absent from the interface
symplectic form. Its Euler--Lagrange partner is the bulk longitudinal
momentum constraint, not an independent interface momentum
\(\Pi_{\cal S}\).

## 8. Linearized scalar junction projections

The scalar decomposition of \(\delta{\cal J}_{\mu\nu}=0\) contains four raw
projections:

1. Hamiltonian scalar;
2. longitudinal momentum scalar;
3. spatial trace scalar;
4. traceless-longitudinal scalar.

There are two scalar Ward relations from

\[
 D^\mu{\cal J}_{\mu\nu}
 =
 -[T_{{\rm bulk},n\nu}],
\]

after the bulk Hamiltonian and momentum constraints and intrinsic
stress-conservation identity are used. Thus two scalar combinations are
independent. The longitudinal divergence is the Codazzi/Bianchi Ward
identity and is not counted as a second momentum condition.

Raw scalar projections can contain shift-dependent representatives through
\(K_{\mu\nu}\), but after the bulk constraint and Ward identity are imposed
they supply no independent endpoint equation for \({\cal S}_\Sigma\).

## 9. Symplectic-flux test

For two perturbations,

\[
 \Omega_\Sigma(\delta_1,\delta_2)
 =
 \delta_1\Theta_{\Sigma,\rm total}(\delta_2)
 -\delta_2\Theta_{\Sigma,\rm total}(\delta_1).
\]

The metric part can be written

\[
 \frac12\int_\Sigma\sqrt{|\gamma|}
 \left[
   \delta_1{\cal J}_{\mu\nu}\delta_2\gamma^{\mu\nu}
  -\delta_2{\cal J}_{\mu\nu}\delta_1\gamma^{\mu\nu}
 \right].
\]

The scalar part is

\[
 -Z_5\sum_{c=\pm}\int_\Sigma\sqrt{|\gamma|}
 \left[
  \delta_1(n_c\sigma)\delta_2\sigma
 -\delta_2(n_c\sigma)\delta_1\sigma
 \right].
\]

After cap parity, induced-metric matching, the intrinsic B1 equations, the
linearized junction equation, and odd scalar Dirichlet matching are applied,
both displayed contributions vanish. Matcher terms vanish after constraint
imposition and multiplier elimination.

There is no term

\[
 \delta\Pi_{\cal S}\wedge\delta{\cal S}_\Sigma
\]

because no independent \(\Pi_{\cal S}\) exists in the stored interface
symplectic form. Thus vanishing flux requires none of:

\[
 {\cal S}_\Sigma=0,\qquad
 \Pi_{{\cal S},+}=\Pi_{{\cal S},-},\qquad
 \alpha{\cal S}_\Sigma+\beta\Pi_{\cal S}=0.
\]

Reflection supplies only the orientation relation between cap traces.
The allowed trace line has one functional dimension per scalar harmonic.
\({\cal S}_\Sigma\) is a null direction of the interface presymplectic form,
so a maximal-isotropic test cannot select a Lagrangian slope or a value on
that line. No Robin-family parameter is present because there is no
canonical \(({\cal S},\Pi_{\cal S})\) plane.

## 10. Fixed and composite support

### Case I: frozen fixed-\(\iota\) B1

Here \(\zeta=0\) and is not an action variable. Reflection gives

\[
 {\cal S}^{\rm out}_-={\cal S}^{\rm out}_+,
 \qquad
 {\cal S}^{\rm common}_-=-{\cal S}^{\rm common}_+.
\]

Flux gives no further restriction. One trace remains.

### Case II: conditional v6.14 composite support

On a fixed \((\tau,s)\) center-manifold sheet,

\[
 \zeta
 =
 -\frac{\delta\widehat\sigma}
 {n^\mu\partial_\mu\widehat\sigma},
\qquad
 \zeta_0=-\tau\frac{\chi_1}{4}\delta q.
\]

This fixes the displacement representative but leaves the same threading
relations and the same one free trace. Composite support therefore does not
close the domain even conditionally. Adopting it would still require the
off-shell BHSM identification

```text
identify iota with the regular center-manifold level set of sigma_hat
and vary all induced pullbacks in that restricted domain
```

but that axiom alone does not select \({\cal S}_\Sigma\).

## 11. Moving reflection center and the rejected shortcut

Introduce

\[
 \widetilde y=y-\zeta(x).
\]

The map \(\widetilde y\mapsto-\widetilde y\) is an \(x\)-dependent change of
the reflection/gluing map. For arbitrary \(\zeta\), it is an additional
orbifold datum. If \(\zeta\) is tied to \(\widehat\sigma\), it is a dependent
datum under the unadopted v6.14 domain axiom. It is not a permitted
fixed-gluing diffeomorphism of the current double.

In adapted variables,

\[
 {\cal S}_\Sigma
 =
 [\widetilde B-a_0^2\partial_{\widetilde y}E]_\Sigma
\]

when the adapted support has \(\widetilde\zeta=0\). This is the same
gauge-invariant trace.

The shortcut

```text
parity -> B=0
parity -> partial_y E=0
adapted support -> zeta=0
therefore S_Sigma=0
```

fails because:

- the moving reflection is absent from the frozen action domain;
- induced-metric matching does not establish continuity of \(B\);
- the junction permits a one-sided jump in \(\partial_yE\);
- the allowed gauge transformation cannot change
  \({\cal S}_\Sigma\);
- imposing zero deletes the unresolved trace instead of deriving its
  boundary equation.

## 12. Interface-domain count

The stored scalar ADM list contains four bulk scalar metric functions:

\[
 A,\quad B,\quad\psi,\quad E,
\]

plus the endpoint representative \(\zeta\) and the scalar source/tangent.
In Case I, \(\zeta\) is diagnostic and not an action variable.

Each cap has regular-pole data. At the interface the stored domain supplies:

- induced-metric continuity;
- reflection parity;
- odd scalar Dirichlet matching;
- the linearized metric junction modulo its two scalar Ward identities.

Fixed-gluing gauge kernels consist of continuous odd \(\xi^y\) and even
tangential scalar \(\xi\). Their quotient does not remove
\({\cal S}_\Sigma\).

The exact coupled reduced radial operator and its differential orders were
not derived in v6.12--v6.14 and are not invented here. The physical
homogeneous-kernel dimension likewise remains uncomputed. Nevertheless,
reflection reduces the two cap threading values to one invariant trace:

\[
 \boxed{\texttt{unresolved_interface_trace_count}=1.}
\]

No pseudoinverse is used. Because the count is nonzero, this sprint records
no invented Green boundary operator, adjoint operator, or kernel dimension.

## 13. Fold-route decision

The global Z2 source has the required odd integral parity and does not show
a compatibility violation. But that partial check does not close the
operator domain.

The decision is:

```text
C. One invariant trace remains.
Pause the fold kinetic route. Do not select a convenient condition.
```

Therefore

\[
 k_q^E(0)
 =
 K_{\rm scalar}
 +K_{\rm shift+endpoint}^{\rm red}
 +K_{\rm Weyl}
\]

cannot be certified. The preserved pieces are

\[
 F_0=M_4^2=\frac{\pi}{2},\qquad
 K_{\rm scalar}\ge2>0,
\]

\[
 K_{\rm Weyl}
 =
 \frac{3\chi_1^2(4-\pi)^2}{16\pi}>0.
\]

The exact remaining input is an action-derived or explicitly adopted BHSM
interface-domain axiom fixing the single gauge-invariant threading trace.
Only after that input exists may a later sprint derive the coupled operator,
adjoint domain, kernels, solvability condition, and Green operator.

## Integrity boundary

This sprint introduces no new action term, coefficient, numerical or
dimensionful primitive, arbitrary threading condition, boundary tension,
`tau_J`, radion potential, measured input, neutral construction, or
physical bulk Dirac law. It does not change frozen predictions or official
prediction logic. It constructs no pseudoinverse, Green function, complete
fold kinetic coefficient, or mixed spectrum.
