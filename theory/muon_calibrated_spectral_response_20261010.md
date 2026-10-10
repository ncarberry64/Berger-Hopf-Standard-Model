# Evaluated calibrated muon photon-current applications

The incoming measured five-flavor electromagnetic spectrum gives the
on-shell hadronic two-current Pauli contribution

\[
a_{\mu,\mathrm{had\,2pt,LO}}=6.969377657120127\times10^{-8}.
\]

Its source-prescription standard uncertainty is
\(3.9891605964527164\times10^{-10}\). This is an evaluated physical current
sector in the calibrated local on-shell description. It is not a complete
BHSM anomaly or an enclosure of the remaining native response. The prior
\(0.0011655419088320725\) local subtotal and frozen prediction files are
preserved. No measured anomaly, g factor or magnetic moment is an input.

## Action, domain and normalization

The existing localized action supplies the minimal electromagnetic
coupling to its charged matter. For the hadronic current use
\(j^\mu=\sum_f Q_f\bar q_f\gamma^\mu q_f\), with the electric charge
excluded from the definition of j. The physical current correlator in the
matched Minkowski vacuum is transverse; the positive inclusive hadronic
spectral measure defines

\[
R_{\rm bare}(s)=12\pi\operatorname{Im}\Pi_j(s),\qquad
\Delta\alpha_{\rm had}(-Q^2)
=\frac{\alpha(0)Q^2}{3\pi}
  \int\frac{R_{\rm bare}(s)}{s(s+Q^2)}\,ds.
\]

The spectrum is the public June 17, 2026 alphaQEDc26 standard-ee release,
IUNMIX=0, with its separate omega/phi domains, resonance prescription,
undressing and pQCD tail. Its FSR convention is retained. A measured
hadronic cross section is used to compute the current contraction;
the release's nominal integrated anomaly is a comparison only. The
independent integral is not shifted to agree with that number. The raw
archive and restricted rhad code remain outside the repository; the
consumed numerical samples and extraction/provenance receipts are retained.
See the [primary data provider](https://people.physik.hu-berlin.de/~fjeger/software.html)
and the [spacelike dispersion kernels](https://arxiv.org/abs/2112.05704).

For a unit transverse polarization, divide out the physical charge and
external current normalization. Then

\[
A_0=Q^2,\quad R_{\rm ind}=-Q^2\Delta\alpha_{\rm had},\quad
A=Q^2(1-\Delta\alpha_{\rm had}).
\]

The implementation actually solves \(Au=J\), \(A_0^\dagger p=L\) and
\(A^\dagger z=L\). It evaluates both
\(L^\dagger(u-u_0)=-p^\dagger R_{\rm ind}u\) and the full adjoint derivative
\(\dot L^\dagger u+z^\dagger(\dot J-\dot A u)\).
The recorded Q² derivatives use the same spectral rows, not a conditioning
shift. The leading Pauli consumer takes exactly one VP insertion; the
unexpanded resummed response is not added as an all-orders result.

## Actual Pauli projection and soft limit

On the calibrated mass shell, the massive-photon spectral vertex reduces
to the Pauli kernel

\[
K(s,\rho)=\int_0^1dx\,x^2(1-x)\int_0^1du\,
\frac{1}{x^2+(1-x)s/m_\mu^2+\rho x^2u(1-u)},
\quad \rho=Q_{\rm ext}^2/m_\mu^2.
\]

Here beta+gamma=x and gamma=xu are the two charged-line Feynman parameters.
The minimal vertex's on-shell Pauli numerator is x²(1−x). The massless
photon limit independently reproduces the previously evaluated QED vertex.
At zero transfer this gives the standard physical dispersion contraction

\[
F_2(0)=\frac{\alpha(0)^2}{3\pi^2}
       \int\frac{ds}{s}R_{\rm bare}(s)K(s,0).
\]

The code computes finite-transfer K, multiplies the existing tensor
\(i\sigma^{\mu\nu}q_\nu/(2m_\mu)\), and applies the existing signed
Pauli covector at t=−.01,+.01,+.003 with q=tm_mu(0,u).
Breit external momenta remain on shell. The covariant representative
contains their motion once. Charge and LSZ counterterms of this matched
local sector are Dirac tensors annihilated by the Pauli covector.

For positive R and rho≥0 the denominator gives the **derived soft bound**

\[
0\le F_2(0)-F_2(\rho)\le\frac{\rho}{6}F_2(0).
\]

It bounds finite-transfer bias for this sector; it is not an enclosure of
the spectral data or of other native contributions. Photon-mass endpoint
layers are resolved in the x quadrature. The full primitive heat-source
receipt, its nonzero contacts and their scope are preserved. The dispersion
route evaluates the hadronic-current sector without identifying that
contact coefficient with the complete native value.

The same bare current has also been contracted on the electron mass shell:
\(a_{e,\mathrm{had\,2pt,LO}}=1.8720490520471017\times10^{-12}\).
Both contractions retain the same statistical and systematic spectral
rows. Their difference uses the difference of those rows before taking
norms. This is a paired current calculation; the muon consumer takes its
own value, not the electron-subtracted diagnostic.

## Contribution accounting

The measured current sector is disjoint from the preserved leptonic VP
and one-loop radial Higgs diagrams. Its overlap with that local subtotal
is exactly zero by flavor and diagram content. It belongs to the native
strong ledger once. It must not subsequently be added on top of a native
ledger that already includes the same hadronic current.

The new local QED orders three through five give
\(3.052798240740239\times10^{-7}\). Separate leading weak and literal
fixed-Y charged-lepton Higgs/photon and Higgs/Z terms are evaluated. The
fixed Yukawa operator is unchanged. Higher hadronic kernels and the decay
and weak matching have their own producers and reports; the consumer
must bind their final packets before a completed contribution sum.

The additive component ledger now consumes the final packets. The newly
extracted operational Fermi coefficient is
\(G_F=1.1663774240217167\times10^{-5}\,\mathrm{GeV}^{-2}\).
Its weak subtotal replaces the earlier provisional leading-weak and
lepton Hgamma/HZ rows; those rows are not added twice. The evaluated
finite-order components are:

| Component | Contribution to a_mu |
|---|---:|
| Preserved QED orders one/two and fixed-Y H1 | 0.0011655419088320725 |
| Leptonic QED orders three through five | 3.052798240740239e-7 |
| Evaluated rematched weak sectors | 1.7592934564604527e-9 |
| Hadronic VP LO | 6.969377657120127e-8 |
| Hadronic VP NLO | -9.847382256422242e-10 |
| Hadronic VP NNLO | 1.2370043161834343e-10 |
| Published connected hadronic four-current projection | 1.019e-9 |
| Lowest electromagnetic top VP | 6.096275717098775e-14 |

The top loop uses the retained vector current and color-charge factor
Nc*Q_top^2=4/3 with the independently measured pole mass. Its exact
one-loop VP insertion is evaluated, not just its leading heavy-mass term.
The latter is a one-loop upper bound by log(1+z)<=z. No top Yukawa is
assigned. Higher top interactions remain an explicitly separate size
estimate. The five-flavor data do not include this sixth-flavor sector.

The three HVP orders use one measured spectrum and common statistical and
systematic rows. Adding those rows before taking norms gives
\(a_{\mu,\mathrm{HVP}}=6.883273877717739\times10^{-8}\) with source
standard uncertainty \(3.9322964803041445\times10^{-10}\).
The [published four-current projection](https://arxiv.org/abs/2412.00190v2)
is retained at its source convention with standard uncertainty
\(7.9\times10^{-11}\). Its uncomputed exact mass derivative is not declared
zero: the nearby-mass approximation has a separate 4.2405338922142075e-13
modeling allowance, not a derivative bound. The HVP mass derivatives are
evaluated on the same kernels at two steps and two quadrature resolutions.

These components sum to **0.0011659187997493429**. This is an evaluated
subtotal, not the completed BHSM a_mu. Its arithmetic gives
g_subtotal=2.0023318375994985 and
mu_z_subtotal=+4.4904461719636446e-26 J/T for mu+ with Sz=+hbar/2;
mu- reverses that sign. The common primitive derivatives are added before
covariance propagation, including the shared optical mass in the SI
magneton. The illustrative independent-input uncertainties are
1.6810514628694008e-12 in the subtotal and 3.6919299285619244e-32 J/T
in its moment. They exclude spectral, matching, truncation and uncomputed
native terms and do not define a total observable uncertainty.

Hadron-only R is not the total photon propagator's spectral measure.
The retained parent functional has
\(K_A=K_F^{(5)}N_{\rm DtN}+\Pi_{AA}\).
Thomson matching fixes the local residue, not the momentum-dependent
charge-subtracted parent DtN remainder. No new free Pauli coefficient is
introduced. Neither a heavy-state screen nor an assumed equality of the
interface primitive alpha_FSC with measured alpha_EM removes that term.

## Scientific status

| Status | Result |
|---|---|
| DERIVED | Current normalization, source/adjoint identities, on-shell spectral Pauli kernel, positive-spectrum soft bound, disjoint local overlap |
| EVALUATED | Actual five-flavor spectral form and Q² jets; primal/adjoint applications; finite-transfer signed Pauli projection; local higher QED and fixed-Y lepton Higgs terms |
| CONTROL_ONLY | Polynomial algebra test of moving J and L; compact test source of the separate frozen parent component; transport fixture used to test boundary rows |
| UNEVALUATED | Remaining full common-action parent/native application and any contribution not closed by the final contribution ledger |
| OWNER_DEFINITION_GAP | None established by these calculations |

The newly implemented scalar birth rows produce the canonical event
cotangent from the parent unknowns, instead of requesting an independent
incoming Higgs packet. They retain the moving transport image complement,
reference quadrature, Gram, bundle and orientation derivatives. Passing
their tests does not make the retained geometric reset center a stationary
interacting base.

## Actual predecessor action and singular-birth applications

The central hypercharge part of the actual eight saved photon lifts is
an invariant coexact sector: its mechanical SU2 commutator and curvature
contact vanish, its curl squared is nine, and its saved source Gram is
(10/3)I8. The radial/time action on a normalized channel is

\[
S/\kappa=\tfrac12\int d\tau\,d\rho\,
 [e(a_\tau-\beta a_\rho)^2-r a_\rho^2-9d a^2].
\]

All four coefficients come from the retained E1+ geometry. The common
kappa/embedding index is factored consistently and has not been assigned
a physical value. The original one-form coordinate is used. A prescribed
wall trace is the input to this DtN component; its reaction is an output,
not a new physical interface condition. The pole's positive finite-energy
root satisfies alpha(alpha+3)=9. Jacobi orthogonalization improves the
mass conditioning without changing this form or its trial space.

The actual snapshot has max|C_rho*beta/nu| about 2.97564. Its coordinate
energy is indefinite; the Lorentz determinant remains -e*r and the
normal-frame spatial energy is positive. No coefficient/sign is changed.
The represented normalized trace pairing is 146.76163334208331; attaching
the actual central Gram gives the diagonal eight-source pairing
489.20544447361107. Spatial48/64/80 and time256/512/1024 refinements are
recorded. The strong conormal pairing still differs by 0.520584898 and its
L2 discrepancy grows. This does not establish continuum conormal
convergence or an error bound on a physical Pauli response.

The advanced boundary test reverses the gyro sign and uses zero terminal
perturbation on the source-support interval. The independent retarded
and advanced finite boundary pairings agree to 2.7284841053187847e-12.
Both compact trace probes are CONTROL_ONLY; neither selects a particle
mode, heat cutoff, formation time or physical soft transfer.

The continuum residual calculation uses the same Lorentzian action and
an independent advanced boundary adjoint. Its strong Euler residual is
e a_tt - 2e beta a_trho - (e beta)' a_t - (r-e beta^2) a_rhorho
- (r-e beta^2)' a_rho + 9d a. The positive normal energy uses
pi=e(a_t-beta a_rho) and E=1/2 integral(pi^2/e+r a_rho^2+9d a^2).
The shifted energy identity includes the exact beta/metric derivative
rates and boundary terms; Friedrichs pole and homogeneous error trace
remove those boundary terms on the error domain.

At radial quadrature1280 and time quadrature4, the primal/advanced
weighted residual norms are 1376.2656782042 and1.81689468942.
The advanced residual contraction is -0.5205848801228211, reconciling
the direct conormal pairing147.2822181993774 with the weak pairing.
The goal-corrected finite weak pairing is146.76163332109908. The
same-space weak correction of order1.6e-9 is Galerkin orthogonality,
not an action cancellation. The estimated continuum remainder is
83.89722499776684 (57.17% of the pairing). Its sampled growth constants,
potential minimum, residual norms and integration are not certified
supremum/infimum enclosures. Consequently this calculation supplies an
EVALUATED residual and loose estimate, not a precise native response.
Spatial/time refinement changes are recorded separately from that
continuum estimate in the energy-residual replay and verification.

The noncentral full-Q application additionally retains the actual
mechanical first derivatives. In the same unit-Tr16 basis its connection
generators have Gram8I3, hence the background action is

\[
L_{\rm bg}=12e(D\lambda)^2-12r\lambda_\rho^2
             -48d\lambda^2(\lambda-1)^2.
\]

Its temporal/radial momenta are 24eDlambda and
-24(e beta Dlambda+r lambda_rho). The derivative-form weak Euler covector
contains the action's oriented contacts already; adding them again would
double count. It uses the actual lambda_tau from the owned velocity,
including its nonzero boundary value about0.40324526.

For all eight saved Q lifts the full off-shell identity
S''[a,D_A eta]+S'[[a,eta]]=0 is evaluated. Its two nonzero Hessian
pairings are approximately -13291.1103172 and -7673.62611946;
the background Euler-commutator pairings cancel them. The curvature
contacts are nonzero and retained. The largest integrated Ward defect is
about2.65e-13. Dropping the background term and solving only an unforced
Gauss row would change this action application.

The complete velocity Hessian at the saved birth center has condition
about2.93e17. A direct inverse produced order1e12 accelerations and was
rejected; its small residual did not justify those values. The weak
first-jet covector supplies the coupled history calculation without
inventing a finite point acceleration at a singular birth.

The current E0 source owner fixes the external BRST-quotiented birth trace
through differentiation, then sets it zero. This selects M_f=M11; it does
not erase internal responses or create an integrated pre-E0 seam. The
remaining coupled background variations use this fixed-trace domain.
No independent incoming Higgs profile or physical underdetermination has
been proved by the present applications.

The common material-chart spatial weak application now evaluates all100
columns (q,qdot,lapse/shift,s,sdot) of the geometric Jacobian, including
measure, metric, shift, normalized sigma response and induced connection
motion. The physical coordinate is rho_phys=2rho*chi_wall/(pi/2).
Writing its Jacobian as J, the pulled coefficients are e_ref=Je,
r_ref=r/J,d_ref=Jd and beta_ref=(beta+rho_phys_dot)/J.
The connection derivative is lambda_tau_ref=lambda_tau+
rho_phys_dot*lambda_rho and lambda_rho_ref=Jlambda_rho. That
advection appears once; independent gauge coefficients remain fixed
in the material chart while geometric columns are differentiated.
The unit-Tr16 non-Abelian curvature polynomial and its contacts,
temporal and radial momentum cotangents, and clock Jacobian are retained.
The evaluated weak Jacobian norm is5.116887230525563e7; both normal
value and normal-rate mixed columns are nonzero. These are derivatives
of the retained reference, not a stationary coupled base. This spatial
block expressly leaves temporal/radial Gauss to their actual action
rows, rather than asserting those rows zero or replacing them.

## Verification and error scope

The current-response driver is
`C:\Python314\python.exe scripts/evaluate_muon_calibrated_current_response.py --output <directory>`.
The paired final outputs retain source and input hashes. Its independent
spacelike source-return orders 32,64,128 converge to the timelike result;
the final difference is 6.311871425190018×10⁻¹⁵. At t=.003 the actual soft
difference is 9.38119529915842×10⁻¹⁵, below the derived
1.0454066485680194×10⁻¹³ soft bound. The local tensor projection residual
is at binary64 rounding scale. Dimensionless return residuals are used
near Q²=0; subtracting two large unscaled inverse propagators has a
separately reported rounding residual.

The combined focused command passed145 tests in23.99s; all five required
publication audits returned exit0. These checks
are recorded verbatim, with stdout, stderr, exit status, source/input
hashes and thirteen byte-identical replay pairs, in
`artifacts/muon_calibrated_current_response_20261010/verification.json`.
The collector is
`C:\Python314\python.exe scripts/verify_muon_calibrated_spectral_response.py --tests`
and, after staging the reviewed files, the same command with `--audits`.
The test count and audit outputs in that receipt are authoritative.
Two earlier new-test failures exposed
an unresolved uniform-Gauss endpoint layer and an incorrect expected SI
magneton range. The endpoint partition and the test's unit expectation
were corrected; neither change alters the physical input selection.
Data covariance follows the source point/range prescription with common
alpha_s dependence. Undressing, interpolation/tail, numerical quadrature,
input and omitted-order errors remain distinct. The published local
QED-coefficient errors and alpha⁶ estimate are not a whole-observable
enclosure. Shared primitive gradients must be combined before applying
covariance; the old subtotal and new QED terms are not independent.

No completed a_mu, g_mu or magnetic-moment uncertainty is asserted while
the full native ledger remains unevaluated. The arithmetic uses
mu_vector=g*q*S/(2m), so the moment for spin +hbar/2 is positive for mu+
and negative for mu−. Intermediate subtotal arithmetic is explicitly
identified as such in the consumer artifact. Promotion flags retain their
existing meanings and remain false.
