# Source-defined magnetic insertion in the original BHSM field-action Hessian

Norman P. Carberry / BHSM continuation — 17 October 2026

## Scope and result

The latest inspected PR #465 head is `70e82fd4dbe5f53ff27ae17f6aaac7a4727c1fde`.
The preceding photon-projection package supplied conditional quantum Schur and
Ward formulas but not their physical operator or magnetic insertion. This work
moves to an explicit insertion in the **existing local field action**, rather
than another arbitrary inverse-matrix example.

Results: (1) the three terms of the gauge-action Hessian's magnetic derivative;
(2) an exact local contact in the original 20 gauge-value coordinates, embedded
in the 24 gauge/Higgs value-leg order; (3) a source-defined nonzero even/odd angular
matrix element and a vanishing even/even one; (4) a total local derivative with
explicit density, measure and test motion; (5) a qualified Higgs fixed-generator
versus moving-frame comparison.

These are local action formulas and exact coefficient evaluations. No physical
collider sections, inherited state, prepared background history, outgoing
quantum domain, native effective action, physical pole or muon magnetic moment
has been evaluated. No new NPZ physical inputs were imported. The current GitHub
source text was read, not executed as an installed repository checkout. The local
code is a source-derived implementation with independent matrix-action checks.
The nonzero numerical field jets in those checks are declared constructed inputs.
No GitHub/Windows-worktree file or frozen result was changed.

## 1. The magnetic probe already has an action-defined local source

`muon_electromagnetic_soft_magnetic_source.py` supplies a local magnetic first jet
in the reached right Maurer frame. In its chart

    g = w I - i q_a sigma_a,  X_a = R4 q_a,

at the observation point g=I the applied probe potential vanishes and its spatial
curvature is fixed. With nonzero H, define

    n_c = (H^dag sigma_c H)/(H^dag H),
    s_H = (-sqrt(2) n_1,-sqrt(2) n_2,-sqrt(2) n_3,sqrt(10/3)).

The source coefficients for magnetic axis k are

    (a_Bk)_i = -(e_can R4^2/2) epsilon_ijk q_j s_H.

They give at the anchor

    a_Bk = 0,
    (delta_Bk magnetic_curvature)_i = e_can R4^2 delta_ik s_H.

This is the existing local applied-source convention, not a newly chosen global
uniform field. It is not the total induced field response. e_can is already
included once in that source, so it must not be added again at the field vertex.
H=0 is outside this H-selected regular chart. A physical continuation through a
vanishing H needs its actual gauge/domain construction rather than division by
H^dag H. Field and source motion at a moving event remain unsolved here.

## 2. Differentiate the actual original gauge density

The independent original evaluator uses five connection components
(At,Ar,A1,A2,A3), four unit-Tr16 internal coordinates, and the bracket

    [u,v]_c = epsilon_abc u_a v_b/sqrt(2), c=1,2,3,
    [u,v]_Y = 0.

Let the component curvatures be

    X = d_t A_r-d_r A_t+[A_t,A_r],
    T_i = d_t A_i-E_i A_t+[A_t,A_i],
    Z_i = d_r A_i-E_i A_r+[A_r,A_i],
    B_i = 2 A_i+epsilon_ijk E_j A_k+(1/2)epsilon_ijk[A_j,A_k].

All inherited connections, when supplied, belong in A once. The source-owned
local Lorentzian density is

    L = 1/2 [k X.X + e_d (T-beta Z).(T-beta Z) - r_d Z.Z - d_Omega B.B].

Here e_d is the electric metric density, NOT e_can. Dot products on the analytic
chart are bilinear: no complex source coefficient is conjugated. The same density
and signs are used by `muon_baton_zoo_original_validation.py`.

Collect F=(X,T,Z,B) and write this as L=1/2 F^T W F. At a fixed coframe F is
quadratic in A, so F_uvw=0. For field variations u,v,

    K(u,v) = F_u^T W F_v + F^T W F_uv.

For a probe variation b, the direct fixed-geometry derivative is EXACTLY

    K_b(u,v) = F_bu^T W F_v + F_u^T W F_bv + F_b^T W F_uv.       (1)

All three placements are required. The last term is the probe applied to the
curvature contact already present in the original Hessian. A source derivative
of only the two covariant-derivative factors does not supply (1).

This is a derivative of the specified local Yang-Mills/Maxwell action. It is not
a new interaction, a fluctuation-Hessian square, or identification of this
bosonic Hessian with the entire microscopic induced operator. It is one input to
gauging the existing field Green and the subsequent daughter coupling. The general
principle of attaching the photon throughout coupled equations and preserving
subtractions is standard; it is not claimed as a new physical law [E1].

## 3. Exact direct contact at the magnetic anchor

At the anchor a_B=0, F_bu=F_bv=0 for independent local field variations. Equation
(1) reduces to the last curvature term. Let I=(i,a),J=(j,b) label spatial
connection and SU(2) generator coordinates. Define

    c_B = d_Omega e_can R4^2.

Then the direct applied-probe gauge contact is

    (K_Bk)_(i,a;j,b) = c_B epsilon_kij epsilon_abc n_c.          (2)

Time/radial, hypercharge, and Higgs-value entries vanish for THIS term. This is
not a statement that those fields have no other response. Coefficient ordering
is gauge20=(At,Ar,A1,A2,A3) x generator4, followed by Hreal4; the actual source/
trace/quotient map must still carry these local coordinates into its 24 legs.

Choosing n=(0,0,-1) is an internal frame representative for a nonzero H, not
selection of a Higgs magnitude, vacuum, packet or physical trajectory. Each
normalized 24x24 matrix K_Bk/c_B then has rank four and spectrum

    -1 (multiplicity 2), 0 (multiplicity 20), +1 (multiplicity 2).

For example,

    K_B3(delta A1^H1,delta A2^H2) = -d_Omega e_can R4^2.

This value is verified by exact differentiation of the original magnetic energy
and by every 3x20x20 entry in the local curvature calculation. The spectrum is a
local Hessian-insertion spectrum, NOT spin states, daughters, masses or g factors.
A purely neutral Q_H variation is annihilated by this local contact. Charged
adjoint variations are therefore necessary to retain this component of the
magnetic response; an exclusively neutral field model removes it.

Nonzero background fields need not be assumed zero for the anchor identity:
a_B=0 makes F_bu=F_bv=0 at that point even on an arbitrary background A. The global
source has nonzero potential away from that point, where all terms of (1) return.
Thus (2) cannot be substituted for the full integrated magnetic insertion.

## 4. The actual odd magnetic source connects angular sectors

The source-owned magnetic extension is n=1 in the right frame. The previous
carrier test space is even, n=0,2. On a homogeneous background and homogeneous
measure, the original first angular derivatives preserve antipodal harmonic
parity. The third variation with one odd magnetic source and two even test
sections has an odd integrand. Therefore

    K_B[even,even] = 0

for that fixed-background integrated sector. This is **antipodal harmonic
parity on S3**, not identification with a laboratory parity transformation.
It does not imply zero local magnetic curvature or zero physical muon moment.
Nonhomogeneous fields, actual localized packet/mode products and moving-domain
terms must be evaluated before applying the selection rule to physical sources.

A nonzero even/odd coefficient can be evaluated exactly without picking any
physical field strength, radius or mode occupation. In source conventions let

    x=(x0,x1,x2,x3) in S3,
    q=(-x3,-x2,-x1),
    u = delta A1^H1 = 1,
    v = delta A2^H2 = 2 x0.

Both 1 and 2x0 are unit-normalized in Haar measure. At the homogeneous zero
connection used as a coefficient comparison, the B3 third-variation integrand,
after factoring d_Omega e_can R4^2, is

    -2 x0^2-x3^2.

Using exact Haar moments <xi^2>=1/4 gives

    integral K_B3[u,v] = -(3/4) d_Omega e_can R4^2.             (3)

Replacing v by the constant even test produces integrand -x0, whose integral
vanishes. The code obtains both polynomials by differentiating the original
magnetic energy, not by imposing the parity answer.

Equation (3) is a specific local action/finite angular coefficient. It does not
claim that the homogeneous zero-connection comparison is the actual BHSM base.
The original static 84-component restriction does not thereby become a physical
magnetic kernel. It instead shows explicitly which off-diagonal angular block
must be available when constructing that kernel. Original code that already
retains it is to be reused, not duplicated.

## 5. Total local derivatives and the Higgs-frame distinction

For changing density W, integration weight w, and moving test sections u,v,

    delta [w K(u,v)] = w K_b(u,v)
        + w [F_u^T W_delta F_v + F^T W_delta F_uv]
        + w K(u_delta,v) + w K(u,v_delta) + w_delta K(u,v).     (4)

The code differentiates the original five densities, including beta-dependent
electric/radial cross terms. Each supplied local field jet has value, temporal,
radial and angular derivatives. All total source/test/measure derivatives are
explicit arguments; there is no fallback to an unspecified zero derivative.
Coframe, source, trace, time-boundary, reset, native and inherited-state contacts
must first produce their actual jets. Equation (4) does not generate these data.

The Higgs conclusion from the existing report is preserved: the pulled scalar
action along A -> A+a Q_H(H) is independent of a because rho_H(Q_H(H))H=0.
It must not be assigned a fabricated photon-amplitude restoring force.

That statement is not interchangeable with taking derivatives at a fixed
laboratory generator. In a local fixed generator example, H=(x+i y,h0), a charged
spatial mode has density -(kappa-q s A)^2(x^2+y^2). Its photon variation vanishes
at x=y=0, while its x-Hessian derivative equals 4 kappa q A. This exact comparison
is included only to mark the derivative convention. If Q_H(H) is moved with H,
the additional field-map contacts cancel the corresponding pulled scalar terms;
the field/gauge description changes elsewhere as well. No nonzero fixed-Q term
may be added by itself to the comoving-Q physical calculation.

## 6. Use the insertion in the existing return without replacing operators

The existing daughter routine already supplies the correct derivative structure:

    Ared = Q^T K_field Q,  Ptrace=T Q,
    G_field=Ptrace solve(Ared,Ptrace^T),
    C=R G_field L,
    C_B=R_B G_field L+R (G_field)_B L+R G_field L_B.

The present calculation supplies a LOCAL contribution to (K_field)_B; Q_B,T_B,
other action sectors, and boundary/source jets must be included as prescribed by
`quotient_trace_return_first`. At fixed maps the inverse term has the minus sign
-deltaG = G deltaK G in its uncompressed inverse representation. It must not be
frozen just because the frequency derivative has already passed.

Three distinct objects must remain separate:

1. Local field-action Hessian and its magnetic variation (partly constructed here).
2. The returned 24-leg field Green used inside C (still needs its physical domain).
3. The complete multiparticle daughter quantum response entering the muon
   self-energy and its pole/residue magnetic readout (not equal to item 2).

The previous finite-transfer photon projection applies only when item 3 and its
actual physical insertions exist. This continuation does not manufacture that
quantum operator, physical external sections, inherited sea or renormalized
transverse vertex. No Schur inverse is heated or declared a native propagator.
The inherited G_F/Higgs calibration and the non-V-A static differences remain.

## 7. Executed checks and limits

Two independent executions write identical JSON and 3x24x24 contact arrays. Six
scoped check groups are recorded. Independent matrix representations of the
unit-Tr16 gauge algebra evaluate the original scalar action, separately from the
component-curvature derivative. Because the action is quartic in affine field
variables, a three-direction centered polarization extracts its third variation
without finite-step truncation; only arithmetic error remains for that control.

Selected results:
- Matrix-versus-component action: difference 6.66e-16 on constructed field jets.
- Triple action polarization: differences 2.22e-16, 7.77e-16, 7.72e-14 over the
  recorded steps (the smallest step amplifies arithmetic cancellation).
- Anchor contact: exact integer normalized matrices and exact eigenvalues; all
  tested gauge entries agree with the original-curvature derivative.
- Total local moving-input derivative: independent differences decrease from
  2.07e-9 to 1.43e-12 over the stored step sequence; the failed coarse comparison
  is preserved rather than promoted to an admission.
- Haar even/odd and even/even integrals: exactly -3/4 and 0.

These checks are not a physical outgoing derivative certificate. No actual
collider trajectory, all-226 correction, physical magnetic response or uncertainty
was calculated. The 2e-10 physical guard is unchanged.

The immediate physical task remains to instantiate the correct physical
mode/history/source/domain construction and consume this local insertion and the
other completed blocks in it. If those constructions still lack an action-defined
operand, report that operand explicitly instead of producing additional static
coefficient refinements or inferring a magnetic moment from the local contact.

## Source provenance

All repository reads below are pinned to the source revision above.

[R1] src/bhsm/interface/muon_baton_zoo_original_validation.py,
Git blob 59efca62b185207a88cd3d93bd298d1c40da22b9; literal original gauge action,
component curvatures, analytic pairings and independent derivative scopes.

[R2] src/bhsm/interface/muon_electromagnetic_soft_magnetic_source.py;
local right-frame magnetic wavefunctions, e_can R4^2/2, source and point-curvature
conventions, no global uniform-field or Fourier identification.

[R3] src/bhsm/interface/muon_magnetic_open_lepton_vertex.py;
20 gauge plus four scalar value-leg convention and distinction between a local
positive-band matching diagnostic and a physical quantum muon pole.

[R4] src/bhsm/interface/muon_intrinsic_higgs_gauge_action.py,
Git blob c41e7dca1bcff9b67f5f6d7afb6777890580b69c; retained unit-Tr16 representation
and original scalar action. The quantum/native determinant is separate.

[R5] src/bhsm/interface/muon_daughter_action_source.py,
Git blob 49b67487005230d83b94b5af61e628ad18f61e94; supplied-domain return derivative
and C=R G L. Code/source text was read; no runtime repository import is asserted.

[E1] A. N. Kvinikhidze and B. Blankleider, Gauging of equations method. I.
Electromagnetic currents of three distinguishable particles, Phys. Rev. C 60,
044003 (1999), arXiv:nucl-th/9901001.
https://arxiv.org/abs/nucl-th/9901001

The exact local calculations here are derived from the cited action conventions.
They neither prove the general electromagnetic-carrier/cascade hypothesis nor
reject it because a local coefficient is insufficient for a physical muon.
