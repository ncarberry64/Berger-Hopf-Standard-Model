# Retained nonfermion boundary variation and graph-jet adjudication

## Result

The retained GFHS bulk variation does **not** uniquely determine

\[
D_{\Phi_{SM}}\Theta_{\rm GFHS}[B;0].
\]

It determines the Maxwell and FP Green pairings and constrains an already
supplied graph to be compatible with those pairings. It does not generate the
horizontal field derivative of that graph. The retained coefficient-free
Einstein--Cartan/HS action is algebraic, so its normal Legendre map has rank
zero and it supplies no HS boundary pairing at all.

The first missing variational datum is

`ACTION_OWNED_BRST_COMPATIBLE_MIXED_RESET_BOUNDARY_VARIATION_D_PhiSM_D_GAMMA0_SQUARED_S_RESET_GFHS[B;0,0]`.

Equivalently, an action-owned BRST-compatible reset boundary generating
functional must be supplied by the attachment/trace-incidence physics. Its
mixed derivative is precisely the graph first jet and is the first datum that
distinguishes the old `Theta_0` and `Theta_1` witnesses.

## Boundary Green forms

For the gauge sector the parent radial Maxwell energy produces

\[
q_A=\Gamma_0 A,\qquad
\pi_A=\Gamma_1^A A,
\qquad
\mathcal G_A(x,y)=\langle q_x,\pi_y\rangle-
\langle\pi_x,q_y\rangle .
\]

`Gamma1^A` is the outward weighted radial Maxwell conormal. The executable
witness assembles the same weighted finite-element radial form used by the
local GFHS germ and verifies its discrete Green identity before any radial
elimination. No stored DtN or response table enters.

The FP action is bilinear in independent antighost and ghost variables. Its
cross-Green form is

\[
\mathcal G_{\rm FP}(\bar c,c)=
\langle q_{\bar c},\pi_c\rangle-
\langle\pi_{\bar c},q_c\rangle .
\]

BRST therefore requires the ghost graph to be the restriction of the gauge
graph to the longitudinal BRST image. The antighost graph is the adjoint of
the ghost graph; it is not an independently selectable jet.

For every retained HS channel,

\[
\pi_H=\frac{\partial L_{\rm EC/HS}}
{\partial(\nabla_n H)}=0,
\qquad \mathcal G_H=0.
\]

Both the local EC/HS action and the gauge-composite HS rewrite explicitly lack
a bare derivative kinetic term. A later heat-derived HS response is not a
generating action and cannot be used to manufacture `pi_H`.

## Why variation does not select the jet

The authorized zero-background reset data identify traces by the returned
reset lift and give the zero relative-conormal graph coordinate
`Theta_GFHS[B;0]=0`. At fixed field, any supplied Hermitian graph coordinate
has a unitary Cayley transmission lift. Transporting the child momentum by
the opposite cotangent lift cancels the two-sided vertical boundary variation.
Thus the bulk Green form verifies such a graph but does not generate it.

The executable test applies this to

\[
\Theta_0(\phi)=0,
\qquad
\Theta_1(\phi)=\phi P_{\rm nonfermion}.
\]

Both remain Hermitian, gauge central, projector preserving, maximal isotropic,
and compatible with the fixed-field two-sided variation. BRST accepts both
when the same jet is used on the gauge longitudinal image and ghost sector.
The HS bulk variation is blind to both. Genuine variation of the Maxwell bulk
coefficient at two backgrounds changes none of these facts.

Field motion of the domain introduces the horizontal term involving
`D_Phi Theta`. Defining that horizontal lift is exactly the missing reset
boundary variation. Two hypothetical boundary functionals with Hessians
`Theta_0` and `Theta_1` both pass direct moving-domain Hessian differentiation
but produce different mixed Hessians. Since neither functional occurs in the
retained action, second variation confirms the nonuniqueness instead of
selecting a candidate.

## AE4, child inheritance, and balance

The zero-field reset match, AE2 fermion graph, nine frozen family/mode fibers,
retarded child rule, and AE4 algebraic assembler are unchanged. None supplies
the missing mixed reset boundary variation. Consequently first-order
nonfermion AE4 gluing and nonzero-field child inheritance are not unique.

The event balance is recorded without hiding the failure:

- bulk local/algebraic residual: zero;
- boundary/reset residual: unavailable;
- retained fermion history/seam residual: zero;
- nonfermion event-child residual: unavailable;
- physical total: unavailable.

The owning missing term is the mixed derivative of `S_reset_GFHS`; no
empirical counterterm is inserted.

## Higher moving-domain derivatives

One boundary variation is differentiated `k-1` times in the `k`th action
variation. Therefore global derivative authority requires:

| action derivative | graph data |
|---|---|
| `S1` | `Theta[B;0]` |
| `S2` | `D_Phi Theta[B;0]` |
| `S3` | `D_Phi^2 Theta[B;0]` |
| `S4` | `D_Phi^3 Theta[B;0]` |

No retained action proves that the graph is affine, so the first jet alone
would not complete global `S1`--`S4`. Repeated mixed variations of the same
missing `S_reset_GFHS` owner must generate the second and third graph jets.

## Claim boundary

The maximal regular-current-C2 GFHS germ remains derived. The global
stratified family is not promoted. All of the following remain false:

- `physical_background_bound`
- `physical_HS_direction_derived`
- `physical_yukawas_derived`
- `physical_spectrum_derived`
- `FULL_FIELD_ACTION_ATTACHMENT_READY_FOR_GATE7_BACKGROUND`
- `FULL_BHSM_COMPLETE`
