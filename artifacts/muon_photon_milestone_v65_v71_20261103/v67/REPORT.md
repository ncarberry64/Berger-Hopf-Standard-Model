# v67: propagated photon charge, entering flux and boundary work

2026-11-03. The new calculation applies v66's radial photon dual to the
original temporal D5 current operator. It reduces the required local matter
insertion to the diagonal normal-pair sum, evaluates its coefficients and
189 local derivatives, and proves why a covariantly constant Ward-test
shortcut cannot eliminate the remaining angular/source work. It does not
evaluate a physical current, reconnection event, or magnetic anomaly.

The v66 checkpoint is unchanged. The numerical background remains the saved
t=2^-9 initializer, not a common physical Cauchy solution. Its admitted
temporal20 residual is 2.962944017741165e-13. The later wall-coordinate
diagnostic remains conditional. The physical guard remains 2e-10 and the
method checks remain 2e-11. No native-factor zero was crossed.

## 1. Action insertion and the quantity actually consumed

The original first-order operator has

    delta_A_t,c D_L = i Gamma0 G_c / N.

The original material volume is N C_rho R^3. Put w=C_rho R^3,
Phi=sqrt(w) Psi, ell=sqrt(w) barPsi Gamma0, with ell an independent analytic
left row. Then the local canonical temporal insertion is exactly

    rho_c,D5 = ell (i G_c) Phi.

The lapse cancels here. Its field dependence is still present in the
solutions, density/frame identification and independent left response.
No Maxwell kappa, extra self-dual multiplicity or fabricated cap-volume
conversion is appended. The physical action/pairing/relative normalization
must agree before this insertion becomes the complete Maxwell load.

For the owned normal pair [W,JW] and its dual, the recovered 36-dimensional
generators have diag(G18,G18), commute with J, and have zero cross blocks.
These statements are checked against the archived full-carrier restriction,
not inferred from the sign of the spatial-current operator. Consequently,
for C_ab=Phi_a ell_b, a,b in {s,n},

    ell i G(phi) Phi = Tr18[V_phi (C_ss+C_nn)],
    V_phi = i sum_c phi_c G18_c.

There is no C_sn or C_ns insertion in THIS temporal charge. Both diagonal
terms and their independent left/normal-partner data are required. The
previous spatial-current and evolution equations still couple normal
channels; this local reduction is not a closed diagonal-only evolution.

At the wall, phi=s_H and the original Higgs alignment gives

    V_wall=Q_H=diag(-P_H tensor I6,-I6),
    P_H=H H^dagger/(H^dagger H).

Q_H has eigenvalue -1 twelve times and 0 six times. These are charge
eigenvalues of a carrier operator, not selected occupations. For an exact
real compact gauge connection, radial parallel transport conjugates Q_H
unitarily: V_phi remains a negative projector with operator norm one.
This is a regular-chart operator identity, not a complete physical state.

## 2. Propagated covector and its new evaluated application

v66 owns U(b,a), with d_b U=-ad(A_rho)U. The source dual is

    phi(rho)=U(W,rho)^T s_H,
    (partial_rho+ad A_rho)phi=0, phi(W)=s_H.

The existing first-order return U1=I-J, J=integral_rho^W ad A_rho, is
consumed directly. No prior source integration or heat calculation is
repeated. For the saved fractional-polynomial connection the inherited
covector at rho=0 is approximately

    (-1.93369166891819e-14, 2.95372407208292e-14,
      1.414213562373095, 1.825741858350554).

Its change from s_H has norm 3.367560208697191e-14. This evaluates the
readout, not the entering normal flux on which it acts. The coordinate
rho=0 is v66's reference endpoint; an actual entering port needs its
actual trace/domain. No zero pole flux or extra admissible trace is chosen.

The 49-node V_phi, 189x49x4 covector derivative, inherited derivative,
angular derivative and its 189-coordinate response are saved explicitly.
The eight-source/four-profile symmetry-reduced return is recovered by

    -sum_q w_q (phi_q-s_H)^T K_q,

with norm 5.622569530130817e-14, agreeing with v66 to 9.47e-30. The raw
affine contraction is also checked against v66. The earlier raw symmetry
drift is not removed or reclassified as physical accuracy.

The v66 omitted-order bound gives a V_phi operator remainder bound
2.642541186309388e-23 for the frozen polynomial transport only. Floating
carrier/input errors, source representation drift, radial quadrature,
domain errors and physical uncertainty are excluded. The saved local
derivatives are derivatives of U1; they are not certified derivatives of
the omitted exact transport orders or total physical photon responses.

## 3. Complete projected Gauss and surface balance

Use canonical flux densities, the invariant gauge pairing and a common
regular material chart. On a patch with fixed material angular domain,
let lambda_h=chi_h phi. The nonlinear Gauss equation gives

    Q_h(W) = Q_h(in)
             + integral_rho,Omega <D_i lambda_h, Pi^i>
             - integral_rho,Omega <lambda_h, rho_bulk>
             - integral_rho,edge <lambda_h, Pi_edge>,
    Q_h(rho)=integral_Omega <lambda_h,Pi^rho>.

Here D_rho lambda_h=0. On a moving/partial graph this identity is used in
the common pulled-back energy domain, with its conormal and Reynolds work;
it does not license a sharp-indicator split of a weak flux. Any face or
test motion remains part of the corresponding total derivative.

The original outward-parent wall equation is

    -Pi^rho_wall + B(H)^T p_H + rho_Gamma,rest + ports = 0.

Its photon projection has no direct intrinsic Higgs momentum, because
B(H)s_H(H)=0. The full derivative of that identity is also zero:
B_Y s_H+B s_H,Y=0. A fixed-readout variation of B^T p_H alone is not zero;
the readout motion is necessary. This removes only the demonstrated
classical Higgs range term, not native Higgs/connection responses or
released-port work. Substituting the Gauss identity gives the exact
projected compatibility condition

    0 = -Q_h(in) - integral <D_i lambda_h,Pi^i>
        + integral <lambda_h,rho_bulk> + integral_edge <lambda_h,Pi_edge>
        + integral_wall chi_h <s_H,rho_Gamma,rest+ports>.

Every term is on the same physical domain and action normalization. This
is the reduced physical residual to evaluate; its value is still null in
the result receipt because its prescribed physical sections are absent.

The matched source ledger remains
Gamma_attached - Gamma_old_reference + Gamma_native_replacement - Gamma_overlap.
Use its full derivative, with overlap subtraction once, native/relative
domain and cutoff contacts, inherited correlations and released sources.
The local D5 insertion above is not added again as a second native loop.
The stationary18 wall load is not an interior causal bulk current.

## 4. Why conservation alone does not supply the missing contractions

The original eight photon sources feed the saved twenty scalar harmonics
n=1 (four modes) and n=3 (sixteen). Radial transport keeps the central
hypercharge coefficient phi_Y=sqrt(10/3). Thus the central component of
D_i(chi phi) is sqrt(10/3) E_i chi. On the original complete unit S3 Haar
domain, the scalar Laplacian eigenvalues are 3 and 15. Hence

    sum_i ||D_i(chi phi)||^2 >= (10/3) sum_i ||E_i chi||^2
                            >= 10 ||chi||^2.

This nonconstancy is exact in the owned harmonic sector. It prevents
replacing these tests by a covariantly constant conserved-charge test.
The full initializer angular Gram at the wall has eigenvalues
20.11338044476971 (four times) and 84.1133804447697 (sixteen times).
The central-only Gram has eigenvalues 10 (four) and 50 (sixteen).
Direct coefficient application checks the Gram at all 49 saved nodes.

The numerical Gram assumes the saved angular-constant coefficient chart.
The complete-S3 inequality is not a coercivity theorem for an unknown
retained/released partial graph, nor a bound on its trace/edge work. No
claim of complete matched cancellation, noncancellation, physical density
dependence or state nonuniqueness follows from this partial Ward test.

## 5. Total source response and exact remaining physical obligation

For fixed material endpoints the exact dual tangent is

    D_rho phi_Y = -ad(A_rho,Y) phi,  phi_Y(W)=s_H,Y,
    D_rho phi_XY = -ad(A_rho,XY)phi
                  -ad(A_rho,X)phi_Y-ad(A_rho,Y)phi_X.

Moving endpoints, clock/normal and trace graph must be included by the
owned pullback or endpoint terms. At fixed carrier frame V_Y=i G(phi_Y).
In a moving frame its connection/identification terms are additionally
required; they cannot be dropped by selecting a new left adjoint.

The D5 first variation is ell_Y V Phi+ell V_Y Phi+ell V Phi_Y.
The mixed variation retains all nine placements:

    ell_XY V Phi + ell_X V_Y Phi + ell_X V Phi_Y
    + ell_Y V_X Phi + ell V_XY Phi + ell V_X Phi_Y
    + ell_Y V Phi_X + ell V_Y Phi_X + ell V Phi_XY.

Differentiate the matched relative/source ledger, domain measures, moving
readout, inherited normal flux and surface/edge terms as well. The new
189-coordinate arrays supply local coefficient derivatives only.

The adopted stationary-past condition already specifies the preparation
route, using J U_as P_as G g_as and action-owned dressing: 500 MeV beams,
100 fm widths, +/-1000 fm centres, exact unpolarized pair, no extra incoming
radiation relative to the inherited reference. It does not supply saved
physical values of the dressed independent-left/right columns on this
common constrained domain. Bare |g_as|^2 is not their charge density.

The next indispensable evaluation is now precisely the charged diagonal
normal-pair moments against chi_h V_phi, together with Q_h(in) and the
matched retained/released load in section 3. At the temporal insertion no
cross-normal covariance is needed, but their coupled propagation still
needs the existing angular/normal equations and entering trace. The
physical native/relative causal-domain correspondence and the common
constrained background remain unconstructed, not replaced by this
initializer. No author decision or new occupation choice is inferred.

A conditional norm estimate follows from the exact charge operator:
|integral ell chi V_phi Phi| <= ||chi||_infinity ||ell||_2 ||Phi||_2
on a compatible domain. It does not bound the complete matched native
current without its actual left/right norms, relative completion and
released/domain terms. The bound alone supplies no 2e-10 physical test.

The smallest substantive successor is to apply this reduced charge
insertion to the prescribed incoming-column/normal-partner construction
on the same constrained slice, retaining its native/relative residual;
the coefficients and covectors need no further recalculation. A numerical
value cannot be obtained merely by another kernel derivative. This turn
does not launch a coupled history or background solve, choose resolution,
or claim its cost is established. Such a solve needs the domain/source
construction above first.

## 6. Reproduction and scope

`prepare_evidence.py` freezes twelve hashed source records, v66's return
and the recovered carrier. `propagated_photon_charge.py` computes only the
new application. `test_propagated_photon_charge.py` has seven focused tests.
Use the included isolated runner with C:\Python314\python.exe -I -S;
the invocation receipts identify inspected roots and code hashes. No
uninspected startup/import paths, site/.pth execution or plugin autoload
are used. This is invocation isolation, not a host security certification.

Final algebra checks: 25, maximum defect 2.842170943040401e-14.
Ten independent fourth-order derivative checks: maximum 4.39648317751562e-13.
Both are below 2e-11. The initial two-point derivative check and its wider
verification threshold are preserved as superseded run_1; the final
fourth-order check meets the original method threshold without changing
any operator, state or physical tolerance. Final deterministic outputs are
run_2/run_3; extraction replay and verification are recorded separately.

The process command using CIM was unavailable; the fallback Get-Process
check showed no Python job. No duplicate job was launched. No push occurs.
All new calculations are one-worker, local, subsecond applications using
the previous representation. Physical a_mu, total uncertainty, complete
residual and actual reconnection remain uncomputed.
