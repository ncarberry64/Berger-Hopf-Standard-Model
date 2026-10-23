# Canonical operator current consumed by the open field system

This milestone evaluates a missing lepton matter-source component on both retained
histories, propagates its Higgs forcing through the saved classical operator, and
consumes the returned current in the actual common wall rows. It also evaluates
one restricted causal current derivative. No physical density/reference, collider
trajectory, wall closure, magnetic moment or total uncertainty is selected.
Phase A was published first at de0dcc748bec0a097d599c984369257be0298aa8, with remote
and PR465 heads verified. Its saved Maxwell/Higgs maps are unchanged.

## Action normalization and new source

Let V=2*pi^2. The original common intrinsic action is S4_raw/V^2, with
chi_hat=R4^(3/2)*psi/V and physical angular carrier phi_Haar/sqrt(V).
Thus psi=sqrt(V)*R4^(-3/2)*phi_Haar*a gives the unit coefficient action
S_lepton=integral dt a_dagger*(i partial_t-h_t)*a. No additional cap or charge
factor multiplies the current. The classical response uses S_hat=T*S, dt=T*d tau.
Consequently the original conditioned scalar-value forcing is

    j_H=-T^2*N_lapse*J_H^T*(E^dagger U^dagger V_scalar U E).

The operators use all84 intermediate modes and initial30 columns. They are
Hermitian current coefficients, before any state contraction. Occupation need
not be a trace-one density. At's coordinate conversion1/T is already in the
Hamiltonian map, and the six direct magnetic columns are included once.

Only the new forcing is solved: z_current'=F*z_current+(0,j_H), at held arbitrary
scalar initial data. Zero initial *correction* is the specified derivative
convention, without choosing a zero physical state. The128-stage system uses900
operator-entry right sides. A separately assembled192-row original system in
(h,v,p) enforces p=Mv+B^T h and p'=Bv+Kh+j_H, independently checking the result.
Its worst residual is5.05e-29 and canonical-stage discrepancy7.58e-29, in the
stated conditioned/time-scaled component norms. Original H and p are restored
and saved; these checks are not the complete physical226-row norms.

## Causal wall return and indispensable endpoints

The scalar response returns the original gauge value/rate covectors
ell_g=K_gh*h+B_gh*v and p_g=B_hg^T*h+M_gh*v. Their actual wall test contraction is
W_return=sum b_i*(G_i^T ell_g+G_i'^T p_g). The temporal gauge endpoint [G^T p_g]
and its Euler complement are saved separately. Scalar reciprocity requires

    W_return,c = sum_i b_i*h_c,i^T*j_H,i
                   +[h_current^T*p_c-h_c^T*p_current]_lo^hi.

A forward-test pullback -T*J_total alone therefore misses the scalar symplectic
endpoint in the causal wall load. Omitting it changes the incoming/outgoing
wall operator by1.7967e-14/1.1316e-14; including it leaves discrepancies
1.2913e-22/5.1224e-23 (maximum absolute entry). The scalar Green identity itself
has residual1.90e-29/1.11e-29. These are finite component comparisons, not physical
before/after Maxwell or226-row residuals.

The quantum Cauchy endpoint +T*J is retained separately from the bulk current
-T*J. Their cancellation along a propagated on-shell fermion section does not
remove the independent bosonic source equation. A moving initial section or
Cauchy Gram requires both endpoints and normalization derivatives.

## Actual common-row consumption

The evaluated current is converted to trace-dual columns on an orthonormal
Hermitian basis of the initial30 occupation operand, with900 real coordinates n.
The numerical common row is now

    known_wall = [W_classical, C_current] * (eta574,n900).

The134x1474 wall map,440x1474 final-state map, separate temporal endpoint,
scalar-initial covectors and scalar symplectic contacts are materialized.
Independent signed Hermitian algebra probes verify the trace composition within
4.17e-17. These probes are software controls, not physical occupations. No
unknown reference or exterior is set to zero, and this known contribution is
not imposed as a homogeneous wall law. The actual interface/normal/source/native/
exterior/reference terms still belong to the common equation. Maxwell influence
through future wall feedback is preserved. No arbitrary inverse or arm gluing
is used.

## Restricted current derivative and numerical scope

Coordinate166[160], or eta574[568], is the existing magnetic profile. On the
explicit affine control h_epsilon=h0+epsilon*V_d, with the classical F/test maps
and vertices fixed for this partial only, integrate the84x30 tangent

    delta(UE)'=-i*T*(h0*delta(UE)+V_d*UE).

Differentiate the current as delta(UE)^dagger V UE+UE^dagger V delta(UE), then
consume that new forcing through the same scalar/wall maps and endpoint law.
Independent finite-field isometries at eight signed epsilon values check
fourth-order differences at h=.5,.25,.125. The finest wall absolute difference
is1.13e-21 on both arms; relative differences are1.80e-10/2.85e-10 for derivative
amplitudes6.29e-12/3.96e-12. Errors increase as h decreases, consistently with
roundoff, so no convergence-order or physical error enclosure is asserted.
All steps and norms remain in the checkpoint.

Physical source-chart contacts V_cd, the classical-map derivative, geometry,
normal, trace, clock/measure, state, reference and domain motion remain required.
They are held fixed only in this declared affine control and are not set to zero
in the complete physical derivative. The separate normal-graph branch, its
symbolic membrane gamma and its finite-step nonpass remain untouched.

Two processes produced byte-identical current arrays,28 derivative files and
three common-system files. The second-run arrays are retained in the local restart handoff; their exact
hashes are published without a duplicate Git copy. Every analytic, finite-field and difference application
was checkpointed before continuing. Resume verifies input/code and output hashes
and reuses completed arms and epsilon applications.

## Physical correspondence and remaining admission

Existing records were recovered, including pre-existing untracked event-domain
evidence. They already supply the adopted beam controls, exact pair density,
all256 ordered current products and finite regional CAR/Gauss extensions. Their
quasifree replacement nonpass0.25 is retained. Older statements that these user
choices or finite extensions were missing are superseded.

The value-level collision incidence Phi_coll and physical packet embedding are
still unevaluated. The actual source-normalized particle/antiparticle sections,
complete Cauchy Gram, constrained dressing and common event domain must give

    g_coll=D Phi_coll^T*g_original,
    H_coll=D Phi_coll^T*H_original*D Phi_coll
             +sum_a g_original,a*D2 Phi_coll,a.

Then the signed trace/source/domain maps and interacting two-collar law must be
consumed, with their complete jets. The two saved cap arms are successive branch
histories and cannot be identified with the electron and positron by dimension.
The needed reduced muon occupation is obtained from the same interacting Fock
collision map and prepared pair state, not by treating the one-particle field
Green or the classical Hessian as that quantum map.

Whether reference moments survive must be decided by the complete oriented
K_event+U_geo^dagger*K_child,oriented*U_geo+K_return/source/constraint/domain
and its admissible CAR/charge/family quotient, including solved-background and
ordered higher-correlation dependence. Neither cancellation nor its failure is
established here. Physical no-extra-radiation data do not erase sourced fields.
PHYSICAL_CORRESPONDENCE.json pins the recovered evidence and exact missing maps.

The unchanged physical2e-10 guard in original norms is unadmitted. No physical
coupled correction or fresh physical Maxwell/all226 after-state is computed.
Prior gauge-reconstruction nonpasses, inherited G_F/Higgs-mass calibration,
membrane error, and unenclosed radial/time/continuum error remain. Formation,
causal spin response, survival and daughter measurement are distinct. Local/
native overlap subtraction and the strong-sector ledger remain to be consumed
in a complete readout, with no guessed remainder or fitted anomaly.
