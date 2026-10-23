# Magnetic angular application on the actual retained wall fields

Norman P. Carberry / BHSM continuation — 17 October 2026

## 1. Executed advance and its boundary

The preceding package derived the local magnetic third variation of the
original gauge action and checked it on constructed fields. This continuation
imports **actual incoming and outgoing raw268 arrays** from the published
field-symbol archive at PR #465
`70e82fd4dbe5f53ff27ae17f6aaac7a4727c1fde`.

It reconstructs the original material-wall geometry, Higgs-selected source axis,
and connection, and applies the spatial magnetic third variation to all 100
local gauge-value/low-angular coordinates for three probe directions. The
nonzero even/odd block, its coordinate partials and an off-shell gauge identity
are evaluated on those retained data. The backgrounds are not newly chosen
examples.

They are nevertheless **provisional retained backgrounds, not the adopted
collider's physical solution**. This work does not solve the prepared packets,
chronological/radial response, physical quotient, inherited quantum reference,
complete daughter quantum propagator or magnetic moment. The spatial density
at the material wall is not a surface action or an integrated terminal response.
The complete gauge-Higgs/native magnetic insertion is not claimed.

Norman's daughter-envelope cascade is the physical interpretation being tested,
not an extra term added here. No fitted reconnection rate, retaining force,
magnetic moment, radius, sea budget or reference covariance is introduced.

## 2. Actual source inputs and integrity

Read archive:

`artifacts/muon_coupled_lorentz_field_symbol_20261011/run_1/application.npz`

Git blob `a5ed8225144b0ac4dfb36fbb93b30c6a76854c9c`; source-reported full SHA256
`21838fe6355cb2b151e12194442549526179ed9ea4422ede3a56c39e5e65ae97`.

The container could not directly download the archive. Two small base64 ranges
were read through the GitHub connector, decoded and their complete ZIP local
records decompressed. The records' CRC32 values agree with the NPY bytes:

| Entry | Shape | Decompressed bytes | CRC32 |
| --- | --- | ---: | --- |
| `incoming_raw_fields.npy` | (268,) | 2272 | `9faa54f6` |
| `outgoing_raw_fields.npy` | (268,) | 2272 | `f3ccacbd` |

The exact downloaded ranges, extracted NPYs and their computed SHA256s are
included. **The whole archive was not transferred and its full SHA256 was not
recomputed.** Entry CRC checks are not misrepresented as that whole-file check.
`verify_inputs.py` rechecks both ranges and extracted files without network access.

The actual layout is geometry100, gauge80, gauge-rate80, Hreal4, Hdotreal4.
The original enriched radial frame has material-wall trace (0,0,0,1); its
wall gauge connection is the final radial coefficient block plus the original
mechanical connection, not zero. This applies that trace identity, not a change
to the old radial profiles or their source-complement normalization.

Code is a source-derived implementation of the read original formulas, with the
prior supplied curvature routines reused. It is not an installed complete BHSM
checkout. The appropriate source paths/blob IDs are in `PROVENANCE.json`.

## 3. Original wall and magnetic source construction

For the source's order-12 geometry, reconstruct C*, the moving radial coordinate
and its rate:

    C* = RADIUS0 exp(q0 + sum q_u,k (-1)^k + sum q_w,j (-1)^j),
    chi_wall = pi/4 + s/C*,
    chi_wall_dot = (sdot - (log C*)dot s)/C*.

Use the original trigonometric `_fields` expressions for C,A,B,N and shift.
The quotient radius and mechanical coefficient are

    R4 = A B / sqrt(A^2+B^2),
    lambda = A^2/(A^2+B^2).

The independently reported radius and induced lapse are reproduced to at most
4.5e-16. This is a check of those values, not of every physical field equation.
The owned material density is reconstructed from the same anchored, second-order
normal-response formula used by the original evaluator:

    J = 4 chi_wall/pi,
    common = 2 pi^4 (A^2+B^2)^(5/2) (1-4 sigma^2),
    d_Omega = J common N (C/2)/R4.

The full wall spatial connection used here is

    A_i = a_i,wall + sqrt(8) delta_i^c (lambda-1).

Its noncentral spatial components are approximately -1.43553048 on the three
aligned diagonal directions. The original small off-diagonal, temporal, radial
and hypercharge values are not reset. Only the spatial magnetic part of the
action is differentiated, so temporal/radial components do not affect this
specific density.

For the nonzero actual H use its normalized Bloch direction n and the original
unit-Tr16 charge coefficients

    s_H = (-sqrt(2) n_1,-sqrt(2) n_2,-sqrt(2) n_3,sqrt(10/3)).

The source's right-frame magnetic extension is

    b_(k),i(x) = -(e_can R4^2/2) epsilon_ijk q_j(x) s_H,
    q=(-x3,-x2,-x1).

Canonical e remains an external multiplicative factor. Arrays are per e_can;
setting the numerical normalization factor to one in the output does not select
an electric charge or apply a second coupling. This is the source's local-field
first-jet extension, not a globally uniform magnetic field or a computed induced
response.

## 4. All three placements, integrated on the retained angular slice

The spatial magnetic curvature and signed density are

    B_i = 2 A_i + epsilon_ijk E_j A_k + [A_j,A_k] (cyclic j,k),
    L_mag = -d_Omega sum_i B_i.B_i/2.

For affine independent gauge variations u,v, the magnetic Hessian derivative is

    K_b[u,v] = -d_Omega [B_bu.B_v + B_u.B_bv + B_b.B_uv].

This uses all three terms from the preceding derivation. It does not replace the
integrated expression by the observation-point contact alone. The background
connection is the reconstructed actual field, and all right-angular derivatives
of source and test sections are retained.

The finite angular basis is

    Y=(1,2x0,2x1,2x2,2x3),

orthonormal under unit Haar measure on S3. Combining it with five gauge components
and four internal generators produces 100 coordinates in harmonic-major order.
Every stored matrix has shape (3,100,100). Purely scalar legs are not included or
silently identified with gauge legs.

The integrands are polynomials of degree at most three: the background is angular
constant, the magnetic source is degree one and each test has degree at most one.
Therefore the normalized eight signed coordinate-axis points give the exact Haar
integral algebraically. The 24-point rule checks the entire arrays independently;
its degree-five exactness is more than sufficient at this scope. This does NOT
undo the previous degree-six source-product counterexample. No use of these rules
for a localized nonpolynomial collider packet is justified by this certificate.

Numerical results (per e_can, before radial integration or the separate overall
Maxwell-to-cap conversion):

| Quantity | Incoming | Outgoing |
| --- | ---: | ---: |
| R4 | 0.9633777962755173 | 0.9633777962755175 |
| induced lapse | 1.108427234091954 | 0.6981395735679910 |
| d_Omega | 5581.932384918571 | 3532.797575885532 |
| d_Omega R4^2 | 5180.573463447701 | 3278.7780487656237 |
| largest matrix entry magnitude per e_can | 6475.7168293096265 | 4098.472560957030 |
| largest entry after division by d_Omega R4^2 | 1.25 | 1.25 |

These are coordinate/density coefficients. They are not forces, physical
residual norms, muon energies, g factors, or errors on a_mu.

## 5. Why a constant-angular magnetic projection still gives zero

Antipodal parity is exact for this homogeneous angular comparison. The first
magnetic insertion is odd, so the matrix has the form

    K_B = [[0, K_even,odd], [K_odd,even, 0]],

where the constant sector has dimension20 and n=1 has dimension80. The actual
mixed blocks are nonzero. The diagonal blocks vanish algebraically; floating
summation leaves an incoming constant-block entry of 1.14e-13 before normalizing
by its common factor. This roundoff is preserved, not changed into a nonzero
physical effect. An initial test that demanded literal floating-point zero failed;
the corrected test checks roundoff while retaining the exact parity argument.

Under the additional conditions that the full *reference* zero-field operator,
its domain and trace/source maps preserve these parities, G0 is block diagonal,
so its fixed-map derivative is

    (G_B)_odd,even = -G_odd K_B,odd,even G_even,
    (G_B)_even,even = 0.

This is a conditional inverse identity. It does not supply either returned Green
and cannot be imposed on a nonhomogeneous physical state without testing its
actual support. The old constant-angular 24-leg tensor cannot receive the mixed
term by simply projecting it into its existing diagonal block. Nor does its
zero diagonal response prove a physical zero magnetic moment.

The finite even/odd magnetic block is now an evaluated input. The compatible
radial/temporal/constraint return and actual physical external-mode injections
remain required. Any already computed compatible odd-sector operators should be
reused; this work does not assert that no such operators exist elsewhere.

## 6. Off-shell gauge Hessians require the residual contact

This is an additional check on the actual retained field, not a new force.
For a constant internal gauge parameter alpha, the spatial gauge generator is

    t_alpha(A) = [A,alpha].

Gauge invariance of the original spatial action gives DS[t_alpha]=0. Differentiate
in an arbitrary field direction v:

    K[t_alpha,v] + DS[[v,alpha]] = 0.

At an unmatched background DS need not vanish. Therefore K times the gauge tangent
is not generally zero. Omitting the second term is not a legitimate gauge-null
test there. A gauge-fixed off-shell calculation remains possible; this identity
does not prohibit it. It forbids identifying that incomplete null test with an
admitted physical quotient.

Actual retained results:

| Quantity | Incoming | Outgoing |
| --- | ---: | ---: |
| max naive K times gauge tangent | 168.2384978033224 | 106.4779213048237 |
| max complete identity discrepancy | 3.55e-12 | 2.07e-12 |
| discrepancy divided by d_Omega | 6.36e-16 | 5.87e-16 |

This check uses the spatial gauge action only and constant internal transformations.
It is neither the full quantum photon Ward identity nor a certificate of the full
BRST quotient. It does not establish that the repository omitted this contact,
that it caused the prior matching errors, or that the complete physical theory
cannot satisfy its equations.

## 7. Independent action and partial derivative tests

An independent 2x2 matrix representation evaluates the original spatial scalar
action, using matrix commutators rather than the component-curvature routines.
A three-direction signed polarization extracts its third variation. Since the
action is quartic in the affine field variables, this polarization has no
finite-step truncation error; arithmetic error remains.

For 24 indexed entries per side at each of two steps (0.5,1.0), the largest
absolute discrepancy is 7.28e-12. The worst common-factor-normalized discrepancy
is 1.67e-15. Entire-array eight-point versus 24-point agreement is at most
1.37e-12 absolute. Matrix symmetry is exact in the retained output arithmetic.

Four raw-coordinate partials are also implemented: log_R(index0), normal
value(index98), H1 real(index260), and H2 real(index261). They move the connection,
geometry, density, source R4 factor and normalized H axis according to the same
retained formulas. Analytic continuation treats H as its four real coordinates;
it does not conjugate a complex source parameter.

Complex-step partials are compared to independent real four-point finite
differences of the reconstructed matrix at h=0.002,0.001,0.0005. The non-negligible
partials converge strongly. Some absolute differences remain above2e-10: the last
log_R differences are2.37e-7/1.43e-7; normal-value differences are7.26e-8/9.40e-8.
These correspond to small relative errors of these large coordinate derivatives,
not to a passed physical absolute guard. The almost-null H2 partial exhibits
roundoff growth as the step decreases; all comparisons are retained.

There is **no claim of a complete outgoing derivative**. No packet, interface,
state, native or event-time derivative is generated by these four partials.
They do not include source-induced changes of the solution and are not physical
beam-preserving sensitivities of a solved collider history.

## 8. Reproduction and exact current limit

Two completed executions give 15 corresponding byte-identical numerical/JSON
files, including the arrays, four derivative arrays per side, side results and
joint result. The failed exact-floating-zero assertion and the timed-out partial
run are retained separately and not counted as completed checks. No cache cleanup,
historical rerun, GitHub mutation or Windows-worktree change was made.

The physical application still needs the actual prepared state, complete
moving-domain current projection and compatible field/quantum returned response.
The current static backgrounds retain their calibrated G_F/Higgs ancestry.
No state, pole, charge or magnetic anomaly was fitted or substituted.

The next useful operation is to integrate this spatial term with the electric,
radial, Higgs, geometry, native and source/domain terms through their existing
common-action maps, then apply the physical mode injections. The spatial
coefficient at the wall must not be added as a new boundary interaction.

The unchanged2e-10 physical criterion and fresh Maxwell/all226 checks remain.
Coupled corrections:0. Physical a_mu, g_mu and total uncertainty:null.

## Source references

All are at the pinned commit above under
`https://github.com/ncarberry64/Berger-Hopf-Standard-Model/blob/70e82fd4dbe5f53ff27ae17f6aaac7a4727c1fde/`.

- `artifacts/muon_coupled_lorentz_field_symbol_20261011/run_1/result.json`:
  source archive identity, provisional-domain scope, independent radius/lapse.
- `src/bhsm/interface/muon_birth_trace_enriched_action.py`:
  original radial/field ordering and material wall trace.
- `src/bhsm/interface/muon_moving_geometric_action.py`:
  `_fields`, moving wall and represented anchored normal response.
- `src/bhsm/interface/muon_intrinsic_m4_normal_pullback.py`:
  intrinsic radius/lapse and induced weights.
- `src/bhsm/interface/muon_parent_maxwell_geometry_weak.py`:
  actual material density and mechanical connection.
- `src/bhsm/interface/muon_electromagnetic_soft_magnetic_source.py`:
  source-owned right-frame magnetic extension and normalization.
- `src/bhsm/interface/aether_post_cut_nonround_lorentzian_cap_v15_48.py`:
  RADIUS0, not a newly selected radius.
- The preceding attached `BHSM_action_magnetic_insertion_20261017` package:
  original curvature/third-variation formulas and independent matrix action.

The mathematical parity, inverse and gauge identities above are derived here
from those specified formulas. They are not additional empirical assumptions.
