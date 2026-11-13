# Integrated magnetic forcing on the exported retained histories

Norman P. Carberry / BHSM continuation — 17 October 2026

## Result and scope

The uploaded `BHSM_RETAINED_HISTORY_INPUTS_20261017.zip` has been consumed. All
47 hashes in its `SHA256SUMS.json` match, and the outer ZIP passes its CRC checks.
There are twelve numerical samples: each chronological arm has two endpoints
and four interior Gauss time nodes; each sample has 192 original radial nodes.
Eight original source-text snapshots are included and hash-checked. The export
records revision `70e82fd4dbe5f53ff27ae17f6aaac7a4727c1fde` and explicitly labels
the histories provisional. No fresh remote-head check is implied by that pin.
The original large repository archives cited by the exporter are not separately
available here and were not rehashed here.

Executed on these actual samples:

1. The full signed Maxwell quadratic field action on the selected n=1 angular
   space and four supplied radial functions, including electric, radial, spatial,
   shift, and background-curvature contacts.
2. Direct magnetic boundary-lift source columns and their source-dependent
   canonical momentum, with the inherited time motion of R4 and the Higgs axis.
3. Finite 64-coordinate algebraic Gauss-block solves at all twelve samples,
   keeping the resulting force, momentum, and action-constant shifts.
4. Exact identification of eight central-gauge null directions in the remaining
   finite kinetic matrix; no pseudoinverse or arbitrary eigenvalue deletion.
5. Full radial magnetic third-variation blocks between n=1 and n=0 field
   variations, including value/rate placements and magnetic-amplitude-rate terms.
6. Temporal weak integrals using the actual exported positive quadrature and
   explicit temporal source conormals at both ends of each arm.

Not executed: the physical collider state, inherited reference, complete matter,
interface/native magnetic response, physical retarded exterior evolution, a
coupled state correction, fresh Maxwell/all226 physical admission, or a muon
magnetic moment. The field quadratic action is NOT the native quantum heat
operator. The n0/n1 calculations below do not replace the full n0,n2/n1,n3
source spaces or a converged localized packet.

## 1. Original scalar action and representation

The actual export carries fields in material order `(At,Ar,A1,A2,A3)` with four
unit-Tr16 gauge coefficients. The density order is
`(electric,radial,angular,electric_radial,shift)`. Denote these by `(e,r,d,k,beta)`;
`e` here is an electric metric weight, not the canonical electric charge.
The source-snapshot scalar density is

    L_Max = 1/2 [ k X.X + e (T-beta Z).(T-beta Z) - r Z.Z - d Bcurv.Bcurv ],
    X = d_t Ar - d_rho At + [At,Ar],
    T_i = d_t Ai - E_i At + [At,Ai],
    Z_i = d_rho Ai - E_i Ar + [Ar,Ai],
    Bcurv_i = 2 Ai + epsilon_ijk E_j Ak + 1/2 epsilon_ijk [Aj,Ak].

The Lie bracket is the supplied SU2 bracket divided by sqrt(2); the fourth
coordinate is central. Total exported connections are used once. The mechanical
reference subtraction has no derivative with respect to independent gauge fields
at fixed geometry; it is not removed from any total geometric derivative here.

Use Cartesian normalized harmonics `Y=(2x0,2x1,2x2,2x3)` and the unchanged radial
basis `beta_j`, j=0,...,3. A variation has coordinates
`q_(radial4,field5,internal4,harmonic4)`, hence 320 values and 320 independent
rates. These are general field variations in this finite space, not just four
transverse photon amplitudes. Temporal/Gauss and radial variables remain.
The homogeneous exported coefficients make the linear n1 block invariant within
this particular Maxwell linearization; this is not assumed for collider fields.

The spatial right-frame derivative matrices intertwine with the existing odd
harmonics by signs `(1,-1,1,-1)`. `existing_odd_coordinate_map.npz` supplies the
exact signed inclusion into radial4 x existing-full400, preserving n3 as an
unpopulated component of this particular source rather than deleting it from
other physical applications.

For `F` the curvature vector, its field Hessian is

    K[u,v] = (DF[u])^T W DF[v] + F^T W D2F[u,v].

The second term uses the actual exported background time/radial derivatives.
It is not dropped on these unmatched backgrounds. Exact angular contraction
uses `<Y_h Y_k>=delta_hk`. Radial integration uses the 192 exported nodes and
`MAXWELL_TO_CAP=0.0003208119454588855` exactly once. A second angular volume or a
new scalar/current normalization is not added.

The resulting finite quadratic Lagrangian is

    L2(q,qdot) = 1/2 qdot^T M qdot + q^T B qdot + 1/2 q^T K q.

M, B, and K are 320x320 at each of the twelve samples. M has zero At rows and
columns, and B has zero At-rate columns. No action sign is changed to create a
positive kinetic or native operator.

## 2. Actual magnetic trace and the integrated source

Use the source-defined local magnetic trace, per unit canonical charge:

    a_i = -(R4^2/2) epsilon_ijk q_j s_H,    q=(-x3,-x2,-x1).

It is a local magnetic first-jet extension, not a global uniform collider field.
Its radial lift is the original independent wall function beta_3, whose wall
value is one. This is a computational lift of specified trace coefficients, not
an added volume current. A different compatible lift can be used only with the
correspondingly transformed interior solution and source. Physical completeness
of the boundary prescription has not been inferred from this choice.

Let `W(t)` be the 320x3 lift and `b(t)` the three measuring-field amplitudes.
The variation is `w=W b`, with

    wdot = Wdot b + W bdot.

The source uses the exact exported `H_selected_charge_coordinate_rate` and the
R4 time derivative obtained along the exported raw-coordinate rate. No Higgs
axis, background time rate, or radius is frozen to zero. The real-coordinate
radius expression is analytically continued solely to evaluate its directional
rate; it is not a physical Wick continuation. Its agreement with the supplied
H-axis rate is recorded independently.

Substituting q=x+w into L2 gives the cross functional

    Lcross = x^T(F_b b + F_bdot bdot) + xdot^T(H_b b + H_bdot bdot),
    F_b    = K W + B Wdot,
    F_bdot = B W,
    H_b    = B^T W + M Wdot,
    H_bdot = M W.

All four source matrices are evaluated, including At tests in F. These are
coefficients of the action cross term. The response equation must use their
correct action sign; they are not automatically the right-hand side of an
arbitrarily signed Euler residual.

A direct independent check of the integrated central Gauss turn-on coefficient is

    (F_bdot)_(j,At,Y,h,k)
      = -(s_Y R4^2/2) delta_(h,3-k)
         integral d rho MAXWELL_TO_CAP * e * beta_j * beta_3.

It agrees with the full assembled coefficient at the tested endpoints within
2.23e-16. Zero direct central rows in a different spatial cubic term do not
remove this electric term. Source value and source rate are kept as independent
columns: no magnetic field strength, switching duration, or physical ramp is
selected in this calculation.

## 3. Finite Gauss solve and source-dependent momentum

Partition the field values into y=At (64 coordinates) and z=(Ar,Ai) (256).
For this finite algebraic operation,

    A = K_yy,  C=K_yz,  D=B_yz,
    y = -A^-1(C z + D zdot + j_y).

The original A is nonsingular at all sampled points. This is a finite matrix
property, not a proof that all its test rows form the completed physical
boundary/constraint domain. In particular, future interface sources can change
which traces are retained as ports rather than eliminated.

The reduced action contains

    Mbar=Mzz-D^T A^-1 D,
    Bbar=Bzz-C^T A^-1 D,
    Kbar=Kzz-C^T A^-1 C,
    fbar=j_z-C^T A^-1 j_y,
    hbar=h_z-D^T A^-1 j_y,
    cbar=c-1/2 j_y^T A^-1 j_y.

The code evaluates both the b and bdot columns of these source terms. Maximum
original Gauss solve residual is 2.842170943040401e-14; maximum scaled backward
error is 1.5209163889588806e-17. No matrix is inverted explicitly.

The canonical momentum is `p=Mbar zdot+Bbar^T z+hbar`, not the source-free one.
The additional momentum term is nonzero on these actual fields. It is included
in the endpoint records. It is NOT added a second time as an independent charge
source: the Gauss load here arose from the same boundary-lift substitution.

## 4. Eight null directions are identified, not regularized away

The remaining 256-coordinate Mbar has eight eigenvalues at roundoff scale.
They are represented by explicit central U1 gauge transformations. Put

    alpha=(sqrt(45)-3)/2,
    chi_1=(rho/WALL)^(alpha+1),
    chi_2=(rho/WALL)^(alpha+2).

Both chi_j and their radial derivatives are exactly in the polynomial part of
the original four-function frame. Combining either chi with any of the four n1
harmonics gives a gauge parameter. Its spatial field direction is

    delta Ar = partial_rho(chi Y_h),
    delta Ai = E_i(chi Y_h),

in the central gauge coordinate. For a static gauge parameter its curvature
variation vanishes pointwise. For a time-dependent parameter, the At variation
is `chi Y_h * parameter_rate`. The central commutators are zero.

The original stiffness and B^T annihilate these static field directions. The
Gauss electric identity and reduced kinetic null identity hold numerically within
1.78e-14 across the twelve samples. The source and reduced momentum annihilate
the corresponding gauge directions within recorded roundoff. No small positive
physical mode is discarded, no mass regularizer is added, and no positive
geometric Gram is substituted for the Maxwell kinetic operator.

The next positive finite kinetic eigenvalue is about 4.14e-8 incoming and
5.20e-8 outgoing. A raw eigenvector-based nullspace comparison is only accurate
at about 1.4e-8 in the worst sampled coordinate test; that diagnostic is preserved,
not described as a 2e-10 physical certificate. The algebraic gauge construction,
not a threshold-selected eigenspace, supplies the eight directions. This does
not establish the complete nonabelian, matter, metric or boundary gauge quotient.
No canonical evolution was attempted by inverting the singular Mbar.

## 5. The integrated magnetic derivative of the field Hessian

The boundary-drive source of section 2 is a second action variation. It is NOT
the third variation needed when differentiating a fluctuation operator already
acting on another response. Both are now supplied separately.

For a fixed-background probe a and two field variations u,v,

    D_a K[u,v] = (D2F[a,u])^T W DF[v]
                + DF[u]^T W D2F[a,v]
                + DF[a]^T W D2F[u,v].

All three terms are retained, including the electric, radial, spatial and shift
weights. Source a has the prescribed W/Wdot and radial derivative of beta_3.
The separately supplied bdot slot has zero probe value and nonzero probe time
jet; it is not a claim of zero actual background field derivatives.

The evaluated blocks are 3x320x80 for magnetic axes, odd n1 field coordinates,
and even n0 field coordinates. Their value/value, value/rate, rate/value, and
bdot value/value contributions are saved. The rate/rate third variation vanishes
for this fixed-geometry quadratic curvature action. This does not assert that
other action sectors or moving metric derivatives have zero rate/rate terms.
The n0 input is a declared component of the full response, not the whole even
n0,n2 space. Physical packets and nonhomogeneous fields require the channels
they actually reach.

Largest radially integrated b value/value entry at incoming lo is 4.4008397576;
at outgoing lo it is 5.5402641803, per canonical charge. Those are integrated
operator coefficients, not magnetic moments or improvements in old residuals.
The existing quantum daughter and pole normalizations have not been applied.

## 6. Chronological integrals and endpoint source conormals

Each arm uses its four positive exported time weights, summing to 1e-5, in the
source's original coordinate-time units. Incoming chronology is [-1e-5,0],
outgoing [0,1e-5]. Negative saved incoming span is not used as negative quadrature.
The endpoint derivatives are the exported one-sided inside-cell derivatives.

For a constant coefficient test and a unit constant b column, the separation is

    original weak cross action = integral F_b dt,
    integrated Euler coefficient = integral F_b dt - [H_b]_lo^hi.

The two are not the same object. Endpoint source conormals must accompany any
integration-by-parts conversion. These coefficient columns do not select a
physical plateau or nonzero initial excitation. General weak integrals are saved
on temporal test/drive basis (1,tau), tau=(t-lo)/(hi-lo), with the correct physical
coordinate derivatives 1/(hi-lo). This is a finite basis for a linear functional,
not a chosen magnetic switching protocol.

| coefficient maximum, per e_can | Incoming | Outgoing |
| --- | ---: | ---: |
| integral F_b dt | 4.10946658236e-5 | 5.20323536635e-5 |
| endpoint difference [H_b] | 2.47384746992e-5 | 2.67139185035e-5 |
| integral F_b dt - [H_b] | 3.13132742103e-5 | 3.60229588194e-5 |

These are maxima of different vectors; one must subtract the vectors, not the
three displayed maxima. None is a physical field-equation residual or an a_mu
error. The endpoint terms are materially nonzero in the actual exported data.
Incoming and outgoing endpoint vectors are retained separately. Their physical
interface pullback has not been supplied and is not replaced with an identity.

The magnetic third-variation blocks are likewise integrated with all value/rate
placements; the resulting finite time weak operators are supplied for applying
the actual even response, not to invent that response.

## 7. Independent checks and error boundary

An independent original-action evaluator uses explicit 2x2 anti-Hermitian
generator matrices and literal matrix commutators. It evaluates the full scalar
action on the actual exported backgrounds. Quartic polynomial differentiation
isolates its quadratic and cubic variations without calling the assembled
matrix derivative routines.

Checks include full-coordinate directions, all three source axes, amplitude and
amplitude-rate terms at both chronological endpoints of both arms. Twelve finite
Gauss solves and all twelve explicit gauge-null tests are also recorded.

Maximum discrepancies across the listed samples and steps:

* Original quadratic action: 4.97379915032e-14.
* Direct source amplitude: 2.03170813506e-14.
* Direct source amplitude rate: 2.18158824339e-14.
* Independent angular 24-point / 50-point full scalar-action rules: 4.45e-16.
* Magnetic third variation: 5.15143483426e-14.
* Magnetic-rate third variation: 8.23230372760e-14.

The angular linear/quadratic contractions are exact at their declared degree on
the homogeneous reference; this is not a Gaussian-packet convergence theorem.
There is only one exported radial quadrature and one exported temporal rule.
No continuum radial tail or time-quadrature error enclosure is claimed. Replays
check determinism, not physical accuracy. The twelve scoped check groups pass;
33 numerical/result files from the two separate executions are byte-identical.

Development evidence preserves an initial array-broadcast error (caught before
any coefficient output), its correction, and two interrupted check processes.
A curvature/harmonic slice layout was corrected before the first successful
assembly. These are implementation-development records, not failures assigned
to the original BHSM source. No provisional failed output is used in the results.

## 8. Next operation, without another input-export loop

The supplied data transfer is complete for this finite Maxwell assembly. The
new source and field-operator blocks can now be integrated into the repository
with the completed source/current and geometric work. They should not be replaced
with the old wall-only matrices or the central-hypercharge-only retarded inverse.

A physical retarded calculation still requires the compatible spatial/interface
ports, matter/native and inherited-reference response, and physical mode/source
projection. The archive explicitly does not contain those constructions. Use
actual constraints or an established bordered formulation rather than inverting
the singular kinetic matrix; retain all original-equation checks. The provisional
n0 background defects are not corrected by solving an n1 magnetic variation.
The physical preparation and original Maxwell/all226 after-state must be checked
on their own coupled solution, with the unchanged 2e-10 guard.

No physical retarded solution, total magnetic derivative, state correction,
physical pole/residue, a_mu/g_mu, uncertainty or Git write was produced. The work
here supplies evaluated finite radial/time Maxwell source and magnetic-response
blocks rather than another wrapper awaiting the exported histories.

## Sources

Primary numerical basis: the user-uploaded `BHSM_RETAINED_HISTORY_INPUTS_20261017.zip`,
its MANIFEST, SHA256SUMS, sample arrays and eight `source_snapshot/` files.
Source conventions: the supplied `muon_parent_maxwell_full_weak.py`,
`muon_electromagnetic_soft_magnetic_source.py`,
`muon_profile_preserving_phase_sample.py`,
`muon_birth_trace_enriched_action.py`, and original sampler scripts.
Supporting constructions: the preceding attached forced-canonical-source,
magnetic-retained, and odd-response packages. No external literature or new
physical model parameters were introduced in this continuation.
