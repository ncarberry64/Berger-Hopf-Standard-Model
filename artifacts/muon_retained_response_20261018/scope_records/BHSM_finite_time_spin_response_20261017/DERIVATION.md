# Finite-time magnetic spin response along the retained evolving histories

Norman P. Carberry / BHSM continuation — 17 October 2026

## Result and scope

The calculation evaluates the existing intrinsic lepton Hamiltonian and its **direct
applied-field insertion** on the twelve uploaded time-dependent background samples.
It evolves the complete six-component middle-family block with fourteen spatial
harmonics through n=2. It produces an operator-valued causal spin-response kernel,
without selecting an initial density, a positive-frequency muon pole, a lifetime,
a stationary envelope, a reconnection law, or an inherited vacuum.

The background is the supplied provisional one, not the adopted collider's solved
formation-to-decay history. The retained local operator is a one-particle field
component. Its unitary evolution is NOT the full interacting multi-particle
muon/daughter quantum evolution; it cannot, by itself, produce the physical muon
decay. No loss or exponential lifetime has been fitted into that component.

The direct magnetic derivative holds the supplied background fixed as a function
of its time coordinate while differentiating the measuring field. The background
itself is time-dependent. The induced field/geometry response to the magnetic
probe and the native quantum contribution are **not** represented as zero in a
claim of a complete response; they remain separate required terms.

Source read anchor: PR #465, 70e82fd4dbe5f53ff27ae17f6aaac7a4727c1fde,
verified through the GitHub connector during this continuation. No remote/local
repository mutation was attempted. These formulas are source-derived
reimplementations; the complete production repository was not run.

## 1. A time-dependent response does not require a stationary pole

For an actually defined joint Hamiltonian on a common physical Hilbert domain,
write, with hbar=1,

    i d_t U_0(t,t0) = H_0(t) U_0(t,t0),
    H_B(t) = H_0(t) + sum_a B_a(t) V_a(t) + O(B^2).

This defines a derivative around an evolving history. It does not require H_0 to
be time independent. Linear-response constructions for arbitrary driven
Hamiltonians are established; their application here still needs the physical
BHSM Hamiltonian, domain and state [1]. The explicit variation is

    delta U(t,t0) = -i sum_a integral_t0^t
                      U_0(t,s) V_a(s) U_0(s,t0) delta B_a(s) ds.

For a readout O_b(t), independent of the field in this direct partial, define

    O_b,I(t) = U_0(t,t0)^dagger O_b(t) U_0(t,t0),
    V_a,I(s) = U_0(s,t0)^dagger V_a(s) U_0(s,t0),

    K_ba(t,s) = i Theta(t-s) [V_a,I(s), O_b,I(t)].                 (1)

For any supplied density rho_0,

    delta <O_b(t)> = sum_a integral Tr[rho_0 K_ba(t,s)] delta B_a(s) ds.

Equation (1) is Hermitian and causal in time. The kernel can be computed before
choosing rho_0. That postpones the state choice; it does NOT prove the final
observable independent of the state. Arbitrary initial correlations are allowed
when rho_0 and H are the actual full joint objects, rather than an unproved
factorized system/environment approximation.

A field-dependent preparation adds Tr[(delta rho_0) O_b,I(t)]. A moving readout,
muon-sector projection, spin frame, measuring apparatus or domain has its own
contact. These are not present in the numerical direct-insertion partial merely
because (1) has been written. The field is varied after a fixed preparation in
the computed partial; formation-field variation is a distinct input.

A two-time response is not automatically an instantaneous magnetic moment. Where a
properly normalized two-spin description exists, its measured-field generator can
be decomposed as

    partial_Ba H_spin = c_a I - (q_mu hbar / 4m_mu) sum_b g_ba(t) sigma_b.

Only after physical spin, charge, mass and clock matching can this define a g
matrix. An isotropic constant g requires additional tests. An unstable-particle
pole remains a legitimate limiting description, not a demand for a perfectly
sealed envelope. Conversely, a failed stationary ansatz does not prohibit a
finite-time response calculation.

## 2. Preserve survival/occupation and the daughter signal separately

Let P_mu(t) denote an actually admitted muon-sector projector, and let O_b(t)
be an observable in that sector. Put

    p(t)=Tr[P_mu(t) rho(t)],
    m_b(t)=Tr[O_b(t) rho(t)],  s_b(t)=m_b(t)/p(t).

Then for p>0,

    delta s_b = (delta m_b - s_b delta p)/p.                    (2)

Both numerator and denominator have kernels of the form (1), plus their physical
contacts. Omitting the denominator derivative can turn a change in the selected
population into an apparent spin change.

In a general dynamics with returns, p is **current sector occupancy**, not
necessarily the probability of no previous decay. A true no-decay survival
probability needs its corresponding record/measurement construction or an
established no-return approximation. Nothing here assumes away returns.

The daughter counting/analyzer signal is unnormalized, N_lambda(t)=Tr[D_lambda(t)
rho_mu(t)], with the appropriate rate or effect dimensions of D_lambda. It should
not be divided by survival and then multiplied by a second independently fitted
lifetime law. Different daughter marginals of the same event remain marginals,
not independent decay channels to sum three times.

For a declared two-spin no-return control,

    dot rho = -i[Omega.sigma/2,rho] - {gamma0 I+gamma.sigma,rho}/2,

Pauli multiplication gives the exact conditioned Bloch equation

    dot r = Omega cross r - gamma + (gamma.r) r,
    dot p = -p (gamma0+gamma.r).                               (3)

Scalar decay gamma0 changes population but cancels from dot r. Spin-selective
loss can change the normalized direction without changing Omega. Equation (3)
is symbolically and numerically checked; no coefficients of this constructed
control are supplied to the BHSM histories.

One may sometimes construct a time-local generator from an invertible amplitude
map A by H_eff=i dot A A^-1, or from an admissible reduced density map E by
L=dot E E^-1. These objects can fail or become singular while the underlying
finite-time dynamics remains regular [2]. The implementation refuses a singular
amplitude-map inversion. It does not infer a two-spin amplitude map from the
published daughter analyzer or equate it with a complete density channel.

## 3. Actual source-defined lepton operator used in the numerical application

The repository's canonical field is chi=R4^(3/2) psi, with the source's complete
Haar pairing. The proper-clock operator is

    H_can = -i alpha^a(E_a+Omega_a)/R4
            + (3/2) gamma5/R4 + M_Y(H) - i Omega_tau.

In the exported coordinate clock,

    h_t = N_ind H_can,
    Omega_tau = Omega_t,material/N_ind.

The material temporal trace is used once; an extra radial-advection term would
double count its coordinate conversion. The same source gives the spin connection
3gamma5/(2R4). There is no additional temporal density term after canonical
rescaling. A spatially varying physical metric would require its own operator
extension; this calculation uses only the supplied homogeneous slices [R1].

The full18 representation has L_L[weak,family,spin2], e_R[family,spin2]. All family
projectors commute with the source's fixed Y and the gauge action. Therefore the
middle-family indices

    (2,3,8,9,14,15)

form an exact six-dimensional invariant field block for these homogeneous data.
Its neutral-left, charged-left and charged-right entries are all retained. This
is **not** a projection onto two positive-energy physical muon spin states.

The fixed Yukawa values are reconstructed from the existing definitions:

    Y = (16 sqrt(2pi)/3969) diag(exp[-lambda_f/(4pi)]),
    lambda_f=k_f(k_f+2)+(a^2-1)(k_f-2j_f)^2,
    (k,j)=(0,0),(5,2),(9,3), a=1.157054135733433.

No measured muon anomaly, new independent Yukawa, physical pole mass or fitted
scale is inserted. The frozen constants and calibrated ancestry are preserved.
The resulting heavy/middle/light Yukawas are approximately
(0.0101048255,0.000607042046,0.00000300407433); these are action coefficients,
not physical pole masses [R2-R4].

## 4. Spatial magnetic input and reached harmonics

Scalar coefficient harmonics phi_(n,m,k)=sqrt(n+1) conjugate(D_(mk)^(n/2))
use the exact right-coframe derivatives E_a=2i J_a on the active m index. Scalar
harmonic labels are coordinates for component sections, not physical spinor pole
labels. All fourteen harmonics through n=2 multiply the six-component fiber,
so the computed operator is 84x84 [R5].

The applied magnetic first-jet extension is exactly the existing source,

    delta A_i^c/e_can = -(R4^2/2) epsilon_ijk q_j s_H^c B_k,
    q=(-x3,-x2,-x1),
    s_H=(-sqrt(2) H^dagger sigma H/(H^dagger H), sqrt(10/3)).

The temporal component of this direct magnetic trace is zero. This is not a claim
of zero induced electric/Gauss response. Its local first-jet prescription is not
a globally uniform field or a replacement of angular n by external momentum [R6].

The coordinate-time insertion is

    V_k = (i N_ind R4/2) sum_ij epsilon_ijk
                         M_(q_j) tensor alpha_i G(s_H).         (4)

All results are per unit canonical electric charge; its physical value is not
selected. The original lapse and radius enter once. The source H axis is its actual
value at each sample and evolves with the sampled H; this remains a direct probe
partial, not the induced delta_B H or delta_B metric.

Exact Clebsch-Gordan multiplication constructs M_(q_j). One n=1 insertion on
initial harmonics n<=1 reaches n<=2. Thus this **first-order** map from those
initial coefficients retains every reached angular output on the homogeneous
reference. An initial state with n=2 would also reach n=3: the full84 matrices
alone are not an angular completeness certificate for arbitrary initial states.
The saved lowest30 projected kernels state the smaller exact reach explicitly.
Finite nonzero-field reruns are numerical differentiation controls on the same
truncated system, not finite-field convergence claims.

## 5. Time representation, actual execution and error scope

The twelve uploaded samples are used: six per arm, at their original endpoint and
four interior-node coordinates. All 47 original history hashes are verified.
Incoming and outgoing are evolved separately; no identity/reset map joins them.

A degree-five Lagrange interpolant of the **sampled Hamiltonian and direct source
matrices** defines the finite numerical time problem. Coefficients are Hermitian
under this real interpolation. No interpolated physical source equation is
claimed exact. DOP853 integrates the chosen interpolant, with the source-dependent
unitary response checked by independent plus/minus-field reruns. A second degree-
three interpolant using the four interior samples yields almost identical final
propagators at this very short retained interval. Agreement of those representations
is not an enclosure of the uncomputed physical history or higher time derivatives.

The coordinate interval is 1e-5 in action units, NOT seconds and NOT the muon
lifetime. Its proper-clock integral is approximately

    incoming: 1.1084271861566383e-5,
    outgoing: 6.9813967778521315e-6.

They cannot be identified with elapsed laboratory decay time without the physical
clock/scale/formation matching.

The evaluated 6x6 grid kernel has shape (output time,input time,probe3,spin3,84,84).
Entries with input time later than output time are zero by the causal definition.
This is temporal causality of this finite equation, not a relativistic spacelike
microcausality certificate. Kernels on arbitrary intermediate times are available
from the supplied dense propagator.

For a test profile b=1 or b=s over the normalized arm, let

    J_a = integral U(s)^dagger V_a(s) U(s) dt,
    U_Ba(tf) = -i U(tf) J_a,
    O_Ba(tf) = i[J_a,O_I(tf)].                               (5)

These two basis profiles do not select a physical turn-on protocol. The six
integrated input directions, source kernels and base propagators are saved.

On the homogeneous reference, the direct magnetic insertion is angularly odd,
whereas the chosen spatially integrated component-spin readout is even. The
first-order kernel therefore has only odd/even off-diagonal blocks. Its even/even
restriction is exactly zero in this representation despite nonzero full kernel.
This does not imply zero g. Physical localized muon modes/readout must replace
a homogeneous parity restriction. No initial packet or density is selected here.

## 6. Clock and spin-frame changes cannot be mistaken for aging

For d tau=N_ind dt,

    h_t=N_ind h_tau,  V_t=N_ind V_tau,
    K_t(t,s)=N_ind(s) K_tau(tau(t),tau(s))

for an amplitude/effect readout with no additional output-rate density. A detector
rate expressed per coordinate time has its own output Jacobian. Magnetic variation
of the lapse would also contribute delta N times h_tau, and a changed endpoint
clock requires its endpoint terms; those total changes are not calculated here.

The same numerical propagation integrated independently in proper time agrees
with coordinate-time evolution within 1.12e-16. The raw direct-insertion maxima
at the first samples are 0.4359408657 incoming and 0.2745764361 outgoing. Dividing
by their actual lapses gives 0.3932968173 and 0.3932973384. These are unprojected
source coefficients per e_can, not magnetic moments. The two histories have not
been joined; no physical change in g is inferred from either comparison.

For a time-dependent unitary description R(t),

    h'_t=R h_t R^dagger+i dot R R^dagger,
    V'=R V R^dagger,  O'=R O R^dagger.

A representation test on the **actual interpolated operators** applies an explicit
rotation of the component-spin frame. Complete kernels agree within 1.12e-16.
Omitting the frame connection changes the control kernel by about0.0893 incoming
and0.0562 outgoing. Those imposed rotations are coordinate tests, not physical
rotations or claimed bugs in earlier code. A moment defined along an evolving
history must specify its transported laboratory/physical spin frame.

## 7. Verification

Ten scoped categories pass on each arm. Two independent executions yield eight
byte-identical result/array files. Selected results:

| Check | Incoming | Outgoing |
|---|---:|---:|
| Original point action vs assembled H application | 6.10e-16 | 3.36e-16 |
| Original point magnetic insertion vs assembled map | 9.05e-17 | 7.76e-17 |
| Unitarity of finite one-particle evolution | 5.56e-16 | 6.67e-16 |
| Complete spin-frame kernel consistency | 1.12e-16 | 8.37e-17 |
| Proper/coordinate-time evolution | 1.12e-16 | 1.12e-16 |
| Kernel quadrature: 12 vs24 nodes | 1.70e-21 | 8.48e-22 |
| Independent finite-field spin derivative at step0.25 | 2.05e-18 | 5.12e-19 |

The last checks compare very small response matrices over a very short interval.
Their tiny absolute discrepancies are not physical uncertainty or a new2e-10
outgoing certificate. The independent right-frame finite difference is about
7.78e-12; its complete values are retained.

The separately labeled two-spin controls verify (2)/(3) exactly/symbolically and
numerically. Scalar loss cancels from conditioned spin; deleting a magnetic
survival-denominator derivative causes0.12504 error in the constructed example.
No control's decay rate, density or frequency is imported as a physical operand.

## 8. Exact next connection, without changing the target back to static closure

The direct local V in (4) is one term. The total local contribution also needs

    delta_B h(t) = V_direct(t) delta B(t)
                  + (D_Phi h)(t) delta_B Phi(t),

including the clock, frame, constraints, mode normalization, and field components.
The previously evaluated Maxwell/Higgs/normal input-response maps can supply
parts of delta_B Phi only when their input and domain identifications match.
Their open wall/normal variables still need their action-defined physical coupling.
Do not double count a source already included through a boundary lift.

Native memory cannot in general be represented by one instantaneous h(t): the
full equation requires its kernel variation delta_B Sigma(t,s), together with
its state/noise/correlation structure. The daughter tensor is not already that
self-energy or a classical Maxwell source. A complete detector calculation must
retain the actual preparation and physical daughter measurement map.

This finite-time formulation removes a requirement to first construct an eternally
static or perfectly sealed muon. It does NOT remove the requirement for an admitted
evolving physical field/domain solution, physical muon/charge/spin projection,
inherited-reference construction or bound, total source derivative, and controlled
native/overlap accounting. The current code has no physical Fock daughter decay
kernel, so it makes no claim to simulate the whole lifetime.

No physical a_mu, g_mu, lifetime, total uncertainty, coupled background correction,
fresh Maxwell/all226 admission or Git write is produced. The2e-10 physical guard
is unchanged. Background time variation, scalar decay, a changing spin frame and
an evolving magnetic moment remain separate quantities to be distinguished.

## Primary sources and recorded code provenance

[R1] muon_native_dirac_hamiltonian.py, blob7afd78d8ee94a9e0ceafbbd947270349c0820489.
[R2] ae31_c2_intrinsic_m4_lepton_action.py, blobff8a33eb4fd3ff7fcbb9303d497eebe43df67dd8.
[R3] ae3_c2_hopf_semigroup_transport.py, blob5a56cf1580afbf6f0115a852a8b18609a6a8715c,
and ae3_family_harmonic_energy_pullback.py, blobdf8a461d37406469710bbca128cceb5cc0ab3dde.
[R4] master_action/topographic_profile_component_selection.py,
blob3a9946be248df63c55af83758222bb59a98b6d3e.
[R5] muon_intrinsic_scalar_discretization.py, blob47868a252ca79325f71d1c7c6608dd54788d2fa5.
[R6] muon_electromagnetic_soft_magnetic_source.py,
blob8ece11042beeac44208778f23905992d8c8428a3.
All read through the GitHub connector at revision70e82fd4dbe5f53ff27ae17f6aaac7a4727c1fde.

[1] I. Safi, Time-dependent theory of non-linear response and current fluctuations,
arXiv:0908.4382 (2009). https://arxiv.org/abs/0908.4382
[2] D. Chruscinski and A. Kossakowski, Non-Markovian quantum dynamics: local versus
non-local, Phys.Rev.Lett.104,070406(2010), arXiv:0912.1259.
https://arxiv.org/abs/0912.1259

The general response/clock/conditioning mathematics is not claimed as an original
BHSM discovery. The new evaluated application is to the supplied action-derived
component operators on the actual exported coefficient histories, at the precise
partial scope above. Reusable harmonic and wall reconstructions are unchanged
copies from the preceding supplied packages, with hashes preserved.
