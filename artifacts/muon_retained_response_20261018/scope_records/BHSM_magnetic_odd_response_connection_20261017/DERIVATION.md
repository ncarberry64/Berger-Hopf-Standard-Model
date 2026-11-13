# Retained magnetic source connected to the existing odd response space

Norman P. Carberry / BHSM continuation — 17 October 2026

## Result and limit

This continuation **reuses** the two saved spatial magnetic insertion arrays from
`BHSM_magnetic_retained_application_20261017`. It does not refine them again.
It constructs their exact representation in the repository's existing full400
odd-angular coefficient space, evaluates their ordinary transverse/gradient
components, identifies a reusable leading radial family, and checks the
magnetic derivative of the spatial action's gauge identity on the actual retained
incoming/outgoing wall fields.

This is **not** the completed compatible retarded contraction. The supplied
magnetic matrices are angularly integrated **bulk spatial densities evaluated at
a wall**, not radially/time-integrated weak operators. The full even response,
odd constrained retarded inverse, physical probe extension, and preparation/state
and interface/native source derivatives are not supplied by these files. No
physical muon magnetic moment or error bar is produced.

Repository anchor, read in this continuation: PR #465 at
`70e82fd4dbe5f53ff27ae17f6aaac7a4727c1fde`. No repository mutation is made.
The retained backgrounds are provisional and carry the previously reported
calibrated scalar ancestry. Norman's electromagnetic-carrier and daughter-envelope
cascade interpretations are not new forces or parameters in this calculation.

## 1. What can actually be reused

The read source `muon_parent_maxwell_full_q_application.py` already defines an
uncompressed angular space

    (one-form5, unit-Tr16 internal4, real odd harmonics20),

where the twenty scalar harmonics have n=1,3. It also provides source-independent
right-coframe derivative/curl structures and a full-field Hessian application
before an eight-column photon compression. Its documentation explicitly says the
eight-column image need not be closed, and that it supplies no physical retarded
solution.

The newer spatial magnetic insertion uses

    Y = (1, 2x0, 2x1, 2x2, 2x3)

and all five one-form/four internal directions: 100 coordinates. The even block
here means only the constant harmonic (20 coordinates); the odd block is n=1
(80 coordinates). The words even/odd refer to the antipodal harmonic convention,
not a physical weak-parity selection or spin-statistics assignment.

Let K_B have the saved shape (3,100,100), per canonical electric charge. Write

    M_a = (K_Ba)[odd80, constant20].

These actual density matrices are retained without changes.

The old `muon_parent_retarded_hypercharge.py` additionally supplies a fixed-trace
radial calculation in a **central hypercharge coexact sector**. Reusing a radial
basis from it is not the same as reusing its scalar Green function for a
noncentral or constraint-coupled source. Its own comments make that restriction
explicit. The complete old full400 representation, not a copied central or
8-source inverse, is the relevant starting layout.

## 2. Exact map between the two angular frames

From the original normalized conjugate-Wigner and real-basis conventions, the
first four real odd functions are exactly

    Y_old,n1 = (2x0, -2x1, 2x2, -2x3).

The n1 signs are thus s=(1,-1,1,-1). For a cartesian-harmonic coefficient c with
shape (harmonic4,field5,internal4), define U of shape (400,80) by

    U[(field*4+internal)*20+harmonic,
      harmonic*20+field*4+internal] = s[harmonic].

All other entries vanish. This is an exact signed permutation and inclusion:

    U^T U = I80.

Both angular charts use the same unit Haar and unit-internal pairing. Therefore
an n1 covector represented in the old chart is U times its new-chart covector.
This is not a claim that an arbitrary physical metric or kinetic pairing can be
replaced by the identity.

The new source columns are

    J_a^(400) = U M_a.                                         (1)

All n3 entries of (1) are exactly zero for this homogeneous comparison. All
new-current/source problems outside this homogeneous finite scope must retain
their actually reached harmonics.

An independent check evaluates the original Wigner functions and compares their
values with the quaternion functions. It also evaluates the original coefficient
derivatives E_a=2iJ_a and checks their intertwining with the quaternion derivatives.
The maximum derivative-map discrepancy is 2.22e-16; the value-map discrepancy is
6.46e-17. Both are representation-roundoff checks, not physical mode accuracy.
The source recovered by U^T is bitwise equal to M_a.

**Important reuse boundary:** the old full400 reference coefficient application
was assembled for its declared background. The current independent gauge fields,
material density, clock and source history cannot be dropped to make that old
numerical operator fit. Reuse the verified ordering and original operator
implementation; reuse numerical arrays only when their input identities match.

## 3. The new source is not wholly transverse

On the unit-S3 n1 vector space, in (spatial3,harmonic4) order, let E_i be the
right-frame scalar derivative matrices. Define the ordinary gradient and curl:

    D0 = stack(E_1,E_2,E_3),
    C0_ik = 2 delta_ik I4 + epsilon_ijk E_j.

The matrices satisfy the exact identities

    D0^T D0 = 3 I4,
    C0 D0 = 0,
    C0^2 = 3 C0,
    tr C0 = 24.

Thus the ordinary curl spectrum is 0 with multiplicity4 and +3 with
multiplicity8, per internal generator. The exact projectors are

    P_grad = D0 D0^T / 3,
    P_coex = C0 / 3,
    P_grad + P_coex = I12.

The saved magnetic output in each spatial/internal channel can be contracted
with these projectors. BOTH contractions are nonzero on the actual retained
incoming and outgoing arrays.

After factoring out the common d_Omega R4^2, the joint Frobenius norms over
three magnetic axes and the constant-field input columns are:

| Norm in this stated coordinate pairing | Incoming | Outgoing |
|---|---:|---:|
| Full spatial magnetic source | 7.0016687256 | 7.0016687256 |
| Ordinary coexact component | 6.3365502770 | 6.3365502770 |
| Ordinary gradient component | 2.9785055868 | 2.9785055868 |

The ordinary-gradient norm divided by the full norm is about 0.4253994. This is
NOT a fraction of magnetic moment, force, energy or physically propagating
longitudinal radiation. It is a diagnostic of a particular unreduced angular
covector in a stated pairing. The physical Gauss quotient uses the actual
background-covariant derivative, temporal/radial fields, Higgs/current response
and boundary data, not just D0.

Nevertheless, dropping P_grad J before implementing those constraints would
change the original weak forcing. The source does not justify a transverse-only
scalar inversion by itself. Each magnetic-axis block has numerical rank9 at
threshold1e-10 after common-factor normalization; its singular values are saved.
No global rank or physical mode-count theorem is inferred from this numerical
rank.

For this spatial cubic Maxwell term the source's central hypercharge rows are
exactly zero. Its nonzero outputs lie in the SU2 components. It therefore cannot
be supplied by the old *central hypercharge-only* DtN return. Coupling in the full
system may subsequently create other components; this zero does not remove
hypercharge, Higgs, or electromagnetic fields from the physical problem.

## 4. The coexact leading radial family already exists

The new ordinary n1 coexact component has curl squared9. Where the previously
derived regular cap leading equation applies,

    -(rho^4 a')' + 9 rho^2 a = 0,

its homogeneous exponents solve alpha(alpha+3)=9. The finite-energy branch is

    alpha = (sqrt(45)-3)/2 = 1.8541019662496845.                (2)

This is exactly `ALPHA` in the pre-existing `regular_radial_basis` factory. Its
Jacobi family and separate wall lift may therefore be reused for this particular
leading coexact component, without inventing another exponent or normalization.

Equation (2) is NOT a complete sourced solution, a boundary condition for At/Ar,
an assignment to the gradient sector, or a proof of a physical outgoing domain.
An inhomogeneous source may have different particular asymptotics. The current
noncentral couplings, full radial coefficients, geometry, and outer traces remain
part of the full equation.

## 5. Magnetic differentiation moves the gauge direction too

The previous work tested a second-variation spatial gauge identity on the actual
off-shell fields. The next identity differentiates that relation in the magnetic
probe direction itself.

For the original spatial action, define the gauge direction

    t_alpha(A)=d alpha+[A,alpha].

Gauge invariance and its first variation imply

    S''[t_alpha,v] + S'[[v,alpha]]=0.

Differentiate along b with v and alpha held as independent test coordinates:

    S'''[b,t_alpha,v]
       + S''[[b,alpha],v]
       + S''[b,[v,alpha]] = 0.                              (3)

Writing K=S'' and K_b=S'''[b,.,.], the two required contacts in (3) describe motion
of the gauge direction and of its action pairing. Testing K_b t_alpha alone is
not the complete identity. No on-shell assumption was used to delete terms.

The implementation uses the SAVED actual K_b arrays, evaluates the lower-order
spatial Hessian K from the original curvature action on the same fields, and
checks all16 n1 gauge parameters, all20 constant one-form/internal tests, and
all3 actual magnetic directions. The n0 part of [b,alpha] is sufficient in its
pairing against the constant test through the homogeneous K. Its n2 part is not
claimed absent; it is orthogonal in this specific comparison only.

| Check, in retained spatial density units | Incoming | Outgoing |
|---|---:|---:|
| Maximum K_b[t_alpha,v] without contacts | 7770.8601952 | 4918.1670731 |
| Complete identity, 8-point exact-at-this-degree rule | <=2.73e-12 | <=1.82e-12 |
| Complete identity, independent 24-point rule | <=8.19e-12 | <=4.55e-12 |

The two lower-order Hessian evaluations differ by at most2.19e-11 absolute, at
coefficient scales of thousands. These are algebra/roundoff tests of the original
spatial action at the two retained walls. They do not certify the full quantum
Ward identity, moving Gauss quotient, chronological solve or physical2e-10 gate.
They also do not establish that a repository implementation omitted the contacts.

During development, one check initially failed because the newly constructed
gauge-parameter probe had its spatial/internal axes interchanged. The failed
source and its explicit correction are retained under `development_checks/`.
This was a bug in this new check, not a defect assigned to the historical BHSM
calculation. The final checks use independent ordering/intertwining tests.

## 6. What the actual response equation must consume

After the complete fields and moving domain are pulled to a common weak chart,
a source derivative satisfies

    K delta u = delta f - (delta K)u.                       (4)

Only under the appropriate zero-field angular block conditions can (4) be written
for the odd response alone as

    K_odd^R delta u_odd = f_B,odd - K_B,odd,even u_even
                         + domain/trace source terms.      (5)

The right side of (5) needs the FULL integrated insertion and the actual even
response, not a wall sample and an arbitrary vector. Source, test, clock, frame,
normal and measure motions must occur once. On a nonhomogeneous collider state
use the complete coupled equation rather than imposing the reference parity.

The At/Ar and constraint channels of K_odd must remain. If a legitimate quotient
makes an algebraic block invertible, its Schur elimination changes both operator
and source. If it does not, retain the original bordered constraint equations;
do not use a pseudoinverse of a positive geometric Gram as a Maxwell inverse.

The output (1) provides an exact **angular** interface to the old full400 layout.
It still multiplies the unknown actual radial/time lift. The wall matrices are
bulk density values. Treating them as a delta-function surface term or directly
multiplying them by an integrated 24-leg wall Green would be an unproved change
of domain and normalization, so neither operation was performed.

The old central hypercharge Green, eight-column returned photon matrix, and
constant-angular24-leg daughter tensor are not interchangeable with K_odd^R.
The original full400 spatial operator construction is reusable infrastructure,
not already the required global quantum daughter propagator.

## 7. What is and is not complete

Executed:
- exact angular source inclusion and derivative convention check;
- original n1 curl/gradient decomposition and leading radial identity;
- both actual retained magnetic source images and their nonzero gradient parts;
- magnetic derivative of the original spatial gauge identity, all listed axes;
- two independent runs, 46 byte-identical result files.

Not executed:
- the full radial/history weak magnetic forcing for the adopted preparation;
- a compatible physical odd/even retarded field solve or terminal return;
- physical muon/daughter mode and inherited-state projection;
- the full outgoing derivative, coupled correction or fresh Maxwell/all226 checks;
- the native quantum magnetic contraction, final a_mu/g_mu or total uncertainty.

The supplied input archive's magnetic-array hashes are checked. Raw-field NPYs
are checked against the preceding supplied manifest. Their provenance still rests
on the previously CRC-verified partial extraction; the full original repository
archive has not been transferred/rehashed here.

The next calculation is the actual integrated common-domain forcing and odd
constrained response in (4)/(5), using the now-verified angular connection and
the pre-existing radial machinery only at its proved scope. Further refinement
of the saved spatial K_b alone does not perform it.

## Sources read and preserved

At repository revision `70e82fd4dbe5f53ff27ae17f6aaac7a4727c1fde`:

- `src/bhsm/interface/muon_parent_maxwell_full_q_application.py`: full400 odd
  angular layout, original derivative/curl structures and unclosed eight-source
  restriction; no physical retarded solution asserted.
- `src/bhsm/interface/muon_intrinsic_scalar_discretization.py`, blob
  `47868a252ca79325f71d1c7c6608dd54788d2fa5`: normalized Wigner sections, real
  transforms and right-frame derivative matrices.
- `src/bhsm/interface/muon_parent_retarded_hypercharge.py`, blob
  `a9dfca45aa654066ed84b9b72cbe8e6489b027b0`: central source restriction and
  existing lambda9 leading radial factory.
- `src/bhsm/interface/muon_coupled_lorentz_field_symbol.py`: local frozen
  polynomial scope and four computational radial reactions, not a physical quotient.
- `src/bhsm/interface/muon_coupled_lorentz_radial_green.py`: signed source/trace
  return in its stated finite restriction, not a global causal quantum propagator.
- `src/bhsm/interface/muon_profile_preserving_phase_sample.py`: midpoint/affine
  reconstructed history scope; not a continuous prepared collider solution.

Local inputs: the attached `BHSM_magnetic_retained_application_20261017.zip` and
`BHSM_compatible_source_application_20261016.zip`. Their code implements formulas
read from the repository; this run is not a checkout/replay of the complete BHSM
production pipeline. All new numerical claims refer to the computations included
in this package, not the unexecuted physical solution.
