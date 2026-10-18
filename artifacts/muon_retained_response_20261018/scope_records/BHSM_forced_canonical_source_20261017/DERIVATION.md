# Forced Gauss source, moving-lift response, and the magnetic turn-on constraint

Norman P. Carberry / BHSM mathematical continuation — 17 October 2026

## Scope

Repository read anchor: PR #465, `70e82fd4dbe5f53ff27ae17f6aaac7a4727c1fde`.
The inherited calibrated backgrounds and adopted 500-MeV/100-fm collider design
are unchanged. No new magnetic charge, turn-on duration, vacuum, native cutoff,
boundary loss law or physical state is selected. No Git or Windows changes occur.

This continuation advances the **source assembly** of the constrained response:

* It evaluates the nonzero coefficient of the applied magnetic trace's time
  derivative in the original Gauss rows on the two saved wall backgrounds.
* It extends the existing homogeneous Gauss elimination to a fully forced scalar
  action, including its force, momentum and action-constant shifts.
* It gives the exact canonical evolution under a moving zero-trace inclusion and
  an arbitrary compatible boundary lift, and its parameter derivative.
* It verifies two different lift choices against independently integrated original
  finite differential/algebraic equations. Those ODE inputs are declared controls.

The full physical radial/history-integrated forcing and compatible retarded solve
have NOT been executed. The exact mode/state/domain correspondence still needs its
actual physical realization. No magnetic moment or physical uncertainty is given.

## 1. Read source constraints, not a new chosen theory

`muon_parent_maxwell_full_retarded.py` uses the scalar convention

    L = 1/2 zdot^T M zdot + z^T B zdot + 1/2 z^T K z.

Its `constrained_gauss_schur` derives a homogeneous algebraic elimination. Its
reference forms have their explicit finite radial/gauge-slice and affine-history
scope; they do not assert an admitted physical quotient. This work does not claim
that the existing helper is wrong on that homogeneous scope or that every caller
omits source terms. It supplies the forced extension required when new sources
are assembled with that convention.

`muon_electromagnetic_soft_magnetic_source.py` supplies the right-coframe local
magnetic trace and its future-clock/Higgs-axis jets. It also has a finite C2 ramp
and a numerical ramp consumer; that is not an actual source value chosen here.
The local trace extension is not a demonstrated global uniform measuring field.

`muon_profile_preserving_phase_sample.py` explicitly requires saved stage states,
a phase coordinate lift and, on the child arm, parent/reference data for the
inherited profile. A raw wall sample is not those complete radial/time inputs.
`muon_birth_trace_enriched_action.py` also requires the original frozen reference
pair, two interior projection coefficients, wall coefficient and source-complement
normalization to reconstruct its four radial functions. They are not inferred
from the two wall vectors in the supplied mathematical package.

## 2. Actual turn-on coefficient in the Gauss equation

The original full field action has electric density

    L_e = epsilon_t/2 * sum_i (T_i-beta Z_i)^2,
    T_i = partial_t A_i - E_i A_t + [A_t,A_i].

Here epsilon_t is the electric coefficient, NOT the canonical electric charge.
The existing magnetic trace, per applied amplitude b(t), is

    A_i^probe = b(t) a_i,
    a_i = -(e_can R4^2/2) epsilon_ijk q_j s_H,
    q=(-x3,-x2,-x1).

Its time derivative is bdot*a + b*adot. Isolating the bdot coefficient sets the
probe's value to zero and its time derivative to a. This isolates one derivative
slot; it does not set the actual background time/radial derivatives to zero.
For a temporal-field test eta, the exact action Hessian coefficient is

    j_Gauss[eta] / bdot = -epsilon_t integral a_i (E_i eta+[A_i,eta]) dHaar.   (1)

The term F*F_uv vanishes in this isolated slot because the probe's field VALUE is
zero. No unknown background radial/time derivatives enter (1). Other b*adot,
value, radial, shift, geometry, interface, matter and native terms remain.

Using the same normalized n1 functions (2x0,2x1,2x2,2x3), and the central source
coefficient s_Y=sqrt(10/3), exact right-frame differentiation gives

    div(a_Y)/(e_can R4^2) = s_Y q_axis.

Thus, for magnetic axes1,2,3 and harmonic indices0,1,2,3, respectively,

    j_Y / (epsilon_t e_can R4^2 bdot)
      = [[0,0,0,-sqrt(30)/6],
         [0,0,-sqrt(30)/6,0],
         [0,-sqrt(30)/6,0,0]].                               (2)

The temporal-source and spatial-momentum coefficient arrays are also mapped into
the EXISTING full400 layout using the saved signed isometry. Both back-maps
recover the arrays exactly; no new angular basis is selected. The source has only
n1 entries in this homogeneous comparison.

The zero-based field tests are the temporal one-form. This is an exact coefficient
matrix, with magnitude sqrt(30)/6 = 0.9128709291752769. It is not a magnetic moment
or a physical constraint residual. The noncentral terms in (1) retain the actual
saved connection and are stored as complete three-by-sixteen arrays.

The electric density is reconstructed from the source-defined material weights:

    epsilon_t = d_Omega R4^2 / N_ambient^2.

N_ambient is the lapse in the material bulk density, NOT the induced moving-wall
proper lapse. On the saved inputs this gives:

| Quantity | Incoming | Outgoing |
|---|---:|---:|
| electric density epsilon_t | 4198.456226361781 | 6633.697222936036 |
| largest Gauss bdot coefficient per e_can | 3557.068852072180 | 5620.284336328863 |

These are angular integrals of bulk densities **sampled at the wall**, before
radial integration and the source-owned overall action conversion. They are not
new surface actions and cannot simply be appended to a radially integrated Green.
The independent direct divergence and Hessian applications agree; two angular
rules differ by at most9.10e-13.

The previously evaluated static spatial cubic insertion had zero central-Y rows.
Equation (2) is a DIFFERENT, electric/time-derivative term; there is no contradiction.
It demonstrates that the whole driven problem cannot be restricted to those
spatial rows. Conversely, this particular bdot term vanishes on a plateau of b.
Background/source-frame motion may still contribute b*adot. No nonzero static
muon anomaly is inferred from a turn-on transient. This is the measuring-field
switching problem, not a solved formation/rupture event.

## 3. Full forced Gauss elimination

Let y be the algebraic temporal-field coordinates and z the remaining variables.
In a fixed common real/analytic-bilinear chart, write the integrated quadratic
ACTION as

    L = 1/2 zdot^T M zdot + z^T B zdot + 1/2 z^T K z
        + y^T C z + y^T D zdot + 1/2 y^T A y
        + j_y^T y + j_z^T z + h^T zdot + c.                 (3)

The linear coefficients are those of the original first variation or source
functional with its actual sign. They are NOT guessed from a residual's label.
All radial/time integrals, source normalizations and requisite second-map
contacts must first be assembled consistently. If the algebraic block has an
unresolved kernel, keep a valid bordered constrained system: do not pseudoinvert
it by choosing a positive geometric reference pairing.

Where the original A is invertible,

    y = -A^-1(C z + D zdot + j_y).

Let Y=A^-1 C, Z=A^-1 D, a=A^-1 j_y. The reduced action is

    Lred = 1/2 zdot^T Mbar zdot + z^T Bbar zdot + 1/2 z^T Kbar z
           + fbar^T z + hbar^T zdot + cbar,

    Mbar = M-D^T Z,
    Bbar = B-C^T Z,
    Kbar = K-C^T Y,
    fbar = j_z-C^T a,
    hbar = h-D^T a,
    cbar = c-1/2 j_y^T a.                                  (4)

This is exact completion of the quadratic square. The last three terms are
essential when j_y is nonzero. The source changes both force AND canonical
momentum. The constant also matters if background/source variations or action
values are consumed; it is not dropped merely because it has no z derivative.

Canonical evolution is

    p = Mbar zdot+Bbar^T z+hbar,
    zdot = solve(Mbar,p-Bbar^T z-hbar),
    pdot = Bbar zdot+Kbar z+fbar.                           (5)

In a second-order form the force contains fbar-partial_t hbar. Equation (5)
handles that source without taking an unstable numerical derivative of hbar.
**Count each source once.** The probe-driven term in section2 can arise from
C*w+D*wdot when the boundary lift is substituted in the unreduced equations.
It is then already included by the moving-lift composition of the same Schur
form, not an extra j_y to add again. In (3), j_y denotes only the remaining
independent linear action terms in that chosen assembly. Derive the combined
forcing from the one scalar action rather than adding both representations.

Natural temporal conormals use this complete p. This does not identify a temporal
conormal with the spatial material-wall traction.

## 4. Exact source derivative

For any complete source/domain parameter s on the common chart,

    Y_s = A^-1(C_s-A_s Y),
    Z_s = A^-1(D_s-A_s Z),
    a_s = A^-1((j_y)_s-A_s a).                              (6)

Differentiating every expression in (4) gives the full forced coefficient jet.
`forced_gauss_schur_first` implements all terms, including cbar_s.

Given form jets, the canonical sensitivity is

    zdot_s = Mbar^-1[p_s-(Bbar_s)^T z-Bbar^T z_s
                       -hbar_s-Mbar_s zdot],
    pdot_s = Bbar_s zdot+Bbar zdot_s+Kbar_s z+Kbar z_s+fbar_s. (7)

No derivative of a missing physical field, state or domain is invented here.
The construction preserves independently continued left leaves and does not add
moving-adjoint terms to a different contraction whose adjoint was fixed.

## 5. A boundary lift is a representation, not another physical field choice

Assume the complete boundary data are already specified, and z=E(t)x+w(t)
parametrizes their affine space. E spans zero-trace variations; w is any admissible
extension with the correct prescribed trace. Set Ed=partial_t E, wd=partial_t w.
For the reduced form (drop bars in this section), define

    p_w=M wd+B^T w+h,
    Mx=E^T M E,
    Bx=Ed^T M E+E^T B E,
    Kx=Ed^T M Ed+E^T B Ed+Ed^T B^T E+E^T K E,
    hx=E^T p_w,
    fx=E^T(K w+B wd+f)+Ed^T p_w,
    cx=L(w,wd).                                             (8)

Substitution proves that (8) gives the EXACT action in x,xdot. In particular

    p_x=E^T p_full.

Freezing the moving inclusion deletes Ed terms. Keeping only -K w as the source
deletes the lift's velocity and momentum terms. Either can change the original
boundary response.

Two admissible lifts w2=w1+E a give the same field if x2=x1-a. Initial x and its
velocity representation must change accordingly; canonical p_x remains the same
when E is common. A full solution on the same span and physical conditions is
therefore independent of this purely computational lift change. No special
chosen internal extension of a boundary drive is required for that equivalence.

This statement is conditional on specified *complete* boundary/initial data and
a complete compatible response space. It does not select the quantum reference,
fix a merely local magnetic first jet globally, eliminate continuum truncation
error, or turn the old central-Y return into a full noncentral inverse.
An external prescribed volume current is physical data, not a lifting freedom.

## 6. Independent executed evolution controls

The finite trajectory tests use a declared constructed action with two algebraic
and four dynamical coordinates, nonzero j_y, time-dependent M/B/K, and one
prescribed boundary coordinate. They are NOT the original BHSM field histories.

One integrator solves the literal original momentum and Gauss equations by a
bordered solve at every time. It does not call the Schur or lift routines. Two
other integrators use (4)/(8) with different moving lifts and consistent initial
physical data. They agree on the complete reconstructed fields, algebraic y,
velocities, momenta, and original boundary-action reaction.

The latter is computed as L_z(boundary)-partial_t p_boundary, with the complete
p_boundary time derivative. Hence equality is not tested solely on an internal
coordinate vector or on a copied reduced output.

Results:

* Independent original DAE versus reconstructed solutions: at most8.33e-17.
* Difference between the two lifts' complete solutions:7.63e-17.
* Difference between original boundary-action reactions:5.55e-17.
* Original Gauss equations: at most1.11e-16.
* Complete parameter derivative versus independently rerun original DAE:
  2.79e-15,2.56e-15,6.27e-15 at steps .02,.01,.005. The small-step
  nonmonotonicity is roundoff, not a claim of indefinitely improving precision.
* Omitting the source momentum shift changes that control by about.03230;
  omitting its force shift changes it by.05700. Dropping inclusion motion changes
  a stiffness entry by.08399. These are control errors, not physical muon errors.
* Exact symbolic action identities verify (4) and (8) independently.
* An unresolved singular algebraic block raises an error, not a pseudoinverse.

The local retained-source coefficients and these independently constructed
response tests are separate provenance classes. No numerical ODE input was
manufactured by relabeling a wall density as a full cap operator.

## 7. Precise next application and remaining inputs

On the actual compatible representation, assemble the original weak M/B/K and
linear sources (including original background residuals) from the admitted or
explicitly provisional history, with all radial derivatives and normalized
source/trace functions. Use the existing implementations; do not rerun adequate
local coefficient precision tests simply to fill the same slots.

The data needed include the complete original frozen radial frame, phase coordinate
lift/stage states, incoming/child/reference clock contributions, and the true
source/current, interface/native and inherited-state applications and their jets.
The supplied two raw wall arrays and magnetic odd400 map do not instantiate them.
None is replaced here by the central source-free condition q(0)=0.

Then use the forced reduction only on a legitimate invertible algebraic block,
or retain the original border; compose the actual source/lift jets and integrate
the constrained history. Verify the original constraints and terminal pullback,
including the natural momentum shift. A lift-invariance comparison and independent
original-equation derivative are useful checks on that actual run.

The full2e-10 physical outgoing admission, coupled correction, fresh adopted-
preparation Maxwell/all226 checks, muon pole/residue and soft magnetic contraction
remain unperformed. No final a_mu, g_mu or total uncertainty is asserted.

## Sources and input provenance

At the pinned revision:

* `src/bhsm/interface/muon_parent_maxwell_full_retarded.py` — homogeneous scalar
  convention, Gauss elimination, original finite temporal solver and its scope.
* `src/bhsm/interface/muon_electromagnetic_soft_magnetic_source.py` — local magnetic
  source, eR4^2 factor, source time jets and ramp distinction.
* `src/bhsm/interface/muon_parent_maxwell_geometry_weak.py` — the common material
  density formulas, including electric=J common Crho R4/N and angular=J common N Crho/R4.
* `src/bhsm/interface/muon_profile_preserving_phase_sample.py` — actual saved-stage
  interpolation, coordinate lift and inherited source-clock dependence.
* `src/bhsm/interface/muon_birth_trace_enriched_action.py` — the original frozen
  four-function radial representation and coefficient sources.
* `scripts/evaluate_em_carrier_original_maxwell_20261016.py` and
  `scripts/bhsm_real_full_d5_combined_eta_open_form_20261016.py` — composition and
  integration requirements for those saved histories.

All were read through the connected repository. This package is a focused
source-derived implementation, not a production checkout/replay. Source-derived
formulas must be compared with current owner functions when integrated locally.

The two raw268 NPYs and the wall reconstruction/action code are unchanged copies
from the supplied magnetic-retained package. Their original archive provenance
is the preceding CRC-verified partial extraction, not a new full-archive hash check.
The full400 signed isometry is an unchanged input from the immediately preceding
odd-response connection package. All local input and output hashes are included
in VERIFICATION.json.
