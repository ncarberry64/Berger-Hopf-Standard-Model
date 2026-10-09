# Calibrated local Pauli applications and the remaining native contraction

The evaluated matched local component is
a_mu,partial = 0.0011655419088320725 and
g_mu,partial = 2.0023310838176642. This contains all local QED terms through
alpha squared and the retained fixed-Y neutral radial Higgs one-loop
diagram. It is not the complete calibrated BHSM prediction: higher local
orders, complete weak matching, and the disjoint native remainder have not
been evaluated or enclosed. No experimental muon anomaly or equivalent
g value was used.

The calibrated local Higgs weak equation was actually solved by Newton
iteration. Its final normalized residual is 4.176605523097395e-14. The
retained incoming and child spatial covariant operators were also applied
to the constant neutral reference shape. Their pairings are nonzero:
16.04197663524236 and 10.595156385737292 per chart Higgs amplitude. Thus a
local broken-vacuum solution does not make the retained interacting birth
configuration stationary.

## Scope and preserved baseline

Baseline commit: 914505d4f4e649be8a62bf066f01b09e01586b04, branch
codex/muon-parent-maxwell-density-review, PR #465. The prior moving-interface,
intrinsic Higgs, frozen predictions and historical local ledgers remain
unchanged. Their totals are not added to this newly calibrated component.

The user's explicit measured-input authorization is recorded in inputs.json.
It supersedes the older blanket measured-input prohibition in AGENTS.md for
this separately labeled calculation. It does not authorize changing the
fixed Yukawa operator, fitting a native discrepancy, or promoting an
uncomputed interacting action state. Every action_selected and Gate7_closed
flag remains false. The current cutoff owner remains
BHSM-AE4-BRANCH-BIRTH-CUTOFF-2026-10-08, child-plus at the common birth surface,
with no finite temporal offset.

## Selected measurements and matching

The reusable configuration is
artifacts/muon_calibrated_pauli_20261009/inputs.json. It records primary
sources, exact SI conversions, editions, extraction assumptions and the
primitive-to-consumer Jacobian.

| Input | Selected value | Published standard uncertainty | Role |
|---|---:|---:|---|
| alpha(0) inverse | 137.035999206 | 0.000000011 | Rb recoil charge calibration |
| optical muon/electron mass ratio | 206.76838 | 0.00017 | optical muonium gross structure |
| R_infinity, m^-1 | 10973731.568076 | 0.000096 | hydrogen spectroscopy |
| positive-muon lifetime, ps | 2196980.3 | 2.2 | provisional G_F matching |
| Higgs mass, GeV | 125.11 | 0.11 | scalar pole matching |
| tau mass, GeV | 1.77709 | 0.00013601470508735444 | pole matching |

Primary measurements:
[Rb recoil](https://www.nature.com/articles/s41586-020-2964-7),
[optical muonium](https://arxiv.org/abs/hep-ex/9907013),
[hydrogen spectroscopy](https://doi.org/10.1126/science.aah6677),
[MuLan](https://arxiv.org/abs/1211.0960),
[ATLAS](https://arxiv.org/abs/2308.04775),
[Belle II](https://arxiv.org/abs/2305.19116).
These are calibrated inputs, not predicted observables.

Electron mass is derived from m_e = 2 h c R_infinity alpha_inverse^2,
with the stated exact SI-to-GeV conversion; m_mu = r_mu/e m_e. They give
m_e = 0.000510998950905377 GeV and
m_mu = 0.10565842526040435 GeV. The optical ratio is deliberately selected
instead of the CODATA magnetic muonium adjustment: its Eq. (185) contains
the jointly adjusted muon anomaly. The optical extraction still uses bound
state QED, charge universality and the documented hyperfine/Doppler
corrections. Recoil alpha uses bound-electron QED and shared mass/Rydberg
metrology, rather than a muon-anomaly target. These dependencies are
recorded, not assumed absent.
[Adjustment dependency source](https://physics.nist.gov/cuu/pdf/RevModPhys.97.025002.pdf)

The configuration derives provisional G_F by

    G_F^2 = 192 pi^3 hbar / (tau_mu m_mu^5 R_decay),
    R_decay = F(x) - 4233.7e-6 + 36.3e-6,
    F(x) = 1 - 8x + 8x^3 - x^4 - 12x^2 log(x),
    x = (m_e/m_mu)^2.

The rounded reference-QED terms give
G_F = 1.1663772930435853e-5 GeV^-2. This is not an exact precision extraction
for the newly selected parameters or a complete BHSM decay calculation.
The independent-primitive illustrative covariance retains the induced
G_F/m_mu correlation, approximately -0.971594. The actual cross-source
covariance is not established and is never silently assigned zero.

A new explicit decay application evaluates the finite-mass tree phase
space and the massless inclusive one-loop term at the selected alpha(0):

    delta_q1,massless = alpha(0)/(2 pi) (25/4 - pi^2)
                     = -0.004203843776879088,
    F(x) = 0.9998129493472899,
    F(x) + delta_q1,massless = 0.9956091055704108.

This differs from the provisional factor by -6.443776879194729e-6.
MuLan's -4233.7 ppm uses its effective running charge and finite electron
mass terms, and +36.3 ppm contains the reference two-loop contributions.
The comparison is not a rounding-only discrepancy. Finite-mass one-loop,
consistent order-two running/scheme reorganization, and any native decay
correction must be included before replacing the provisional G_F.
[Inclusive decay equations](https://arxiv.org/abs/hep-ph/9904240),
[MuLan extraction](https://arxiv.org/abs/1211.0960).

The retained potential is V = lambda_H (H^dagger H - nu^2)^2. Candidate
canonical tree matching gives

    v^2 = 1/(sqrt(2) G_F),
    nu^2 = v^2/2,
    lambda_H = G_F m_h^2/sqrt(2).

Numerically v = 246.21979929677656 GeV,
nu^2 = 30312.094782872464 GeV^2 and lambda_H = 0.12909460903411638.
Radiative Higgs/pole normalization and BHSM matching corrections remain
uncomputed. Lambda is not identified with 64 pi^5; measured alpha is not
identified with the interface stiffness.

The actual retained Y eigenvalues and common relation M_l = v Y_l/sqrt(2)
are unchanged.

| Family | Fixed-Y tree mass, GeV | Selected pole, GeV | Required pole/tree minus one |
|---|---:|---:|---:|
| tau | 1.7592874031050838 | 1.77709 | +0.010119208983986994 |
| muon | 0.10568825995994285 | 0.10565842526040435 | -0.0002822896275310738 |
| electron | 0.0005230204249447711 | 0.000510998950905377 | -0.02298471238606692 |

One common rescaling cannot match all three central ratios. The action
must produce the family-dependent pole corrections through

    m_f^2 A_L(m_f^2) A_R(m_f^2) = B_L(m_f^2) B_R(m_f^2).

These numbers quantify required corrections; they are not fitted
independent Yukawas or evaluated self energies. The derivative of this
equation and the matrix adjugate are needed for interacting residues.
Matching pole positions alone does not fix them.

## Executed scalar and moving action applications

The local reference Newton solve uses the existing literal nonlinear
Higgs weak residual and its realified Jacobian, H=(0,h/sqrt(2)) in a flat
unit M4 cell, on the positive broken branch. The classical fermionic body
source vanishes by the retained Grassmann-body ownership; the quantum
determinant and induced source are retained in the quantum ledger. An
external LSZ muon is not substituted as a commuting classical source.

| Iteration | Accepted radial correction, GeV | Updated weak residual, GeV^3 |
|---|---:|---:|
| 0 | +77.07750238855614 | -512322.11128608265 |
| 1 | -24.09704419596018 | -59823.63818406567 |
| 2 | -3.6543514520007423 | -1286.4486033176313 |
| 3 | -0.08210580293703344 | -0.6429787933066499 |
| 4 | -0.000041078292569468085 | -1.6096463888074067e-7 |

Initial h is 0.8 v. Final h is 246.21979929678685 GeV; the positive
potential curvature is 15652.512100001957 GeV^2. The Lorentzian weak-action
Jacobian has the opposite sign. This solves the stated local matching
reference, not the interacting E1 Cauchy problem.

The common-vector primal implementation contains unknown H and p_H, one
geometry and multiplier vector, normal-chart coefficients, and real u(2)
connection coefficients. All temporal and angular derivatives are computed
from that same vector. The Peter-Weyl basis is unit-Haar normalized; the
physical volume 2 pi^2 is inserted once. Complex Higgs variations are
realified with the real 2 Re pairing. Real gauge harmonics use the unitary
conjugation transform; imaginary coefficients of a real scalar harmonic
are no longer redundant Newton variables. The child connection uses the
actual pointwise Ad_g in the same coframe, rather than a constant matrix.

The first-order scalar equations are

    p_H = wT D_t H,
    D_t p_H + D_i^dagger(wS D_i H)
      + wV[2 lambda_H (H^dagger H - nu^2)H + J_H] = 0,

in the homogeneous time chart. The graph application retains
p_H=G^{t nu}D_nu H including normal first-order contacts. The weak
contraction has 2 Re; the complex canonical momentum equation has no
extra factor two. Future/interior collocation rows leave the past Cauchy
unknowns to the event equations.

The producer evaluates the retained incoming/child geometric action,
surface-per-gamma and Higgs-potential-per-lambda-nu^4 Euler rows and temporal
weak Hessians. Its q(t)=q_birth+t qdot_birth, constant-m, H=p_H=gauge=0
coefficient vector is an explicitly off-shell starting iterate, not a
solution or a physical zero background. For that iterate the geometry
F_q norms are 1150.5100608929988 (parent) and 1114.1364568938416 (child).
The available scalar, conormal, endpoint and normal contacts are retained.
A zero scalar row at this iterate is not evidence that the coupled
interacting base is stationary.

Calibration supplies lambda and physical nu^2, but the geometric chart
uses its common action unit E_kappa. The correct conversion remains

    H_chart = H_GeV/E_kappa,
    nu_chart^2 = 30312.094782872464/E_kappa^2,
    lambda nu_chart^4 = 118615107.59131451/E_kappa^4,
    lambda nu_chart^2 = 3913.1280249999995/E_kappa^2.

No measured lepton mass, Planck energy or lifetime is silently used as this
unit. This is a reached common-unit matching application, not an assertion
of a new independent measurement or a theory-definition gap. The
pre-calibration lambda-unbound diagnostic is superseded; it is not the
current stopping result.

Existing calibration maps make the next common-unit calculation concrete:
UniversalGFScaleMap gives G_F=c_F/Lambda^2 and Lambda=sqrt(c_F/G_F);
master_action.observable_transport gives ell_star=v_hat/v_F. Applying these
to E_kappa requires the dimensionless weak coefficient c_F or v_hat in the
current ell_kappa chart and its explicit common-action identification. The
selected G_F is already available. A test c_F or a historical independent
lambda5 cannot supply the current coefficient. The alternative G_N route
requires the current four-dimensional coefficient
c_G E_kappa^2=(8pi G_N)^-1. The retained K_G5=kappa1 Vol(S3_RF) is a
five-dimensional normalization; directly equating kappa1 with inverse
G_N is dimensionally wrong because kappa1 has length^-6 units. Neither
route was numerically closed by the reached owners. The conditional
Planck-calibrated Higgs saddle and old fold coefficient pi/2 do not establish
their identification with the current common action.

Applying the actual finite spatial covariant pencil to the constant
neutral shape gives

    parent: <e0, K_spatial e0> = 16.04197663524236,
    child:  <e0, K_spatial e0> = 10.595156385737292.

The amplitude is sqrt(nu_GeV^2)/E_kappa. The local potential derivative
vanishes on the broken reference with explicit provenance, but the spatial
row does not. Temporal canonical momentum and the event cotangent remain
in the full equation. These applications prevent promotion of the local
vacuum to an E1 stationary base.

The retained E0 load is an equation for the unknown primal fields:

    -2 Re <phi_i,p_H,E0>
      + delta_H(S_event+S_boundary+S_constraints)[phi_i] = 0.

With N=1 and three time coefficients, the represented linearized scalar
problem has 120 complex H/p_H unknowns, 80 complex interior equations,
20 common-birth trace/flux equations, and 20 past Cauchy equations to be
supplied by this event application. This count is a representation check,
not a proof of full nonlinear uniqueness or a requirement for a complete
history in every Pauli reduction. No H=0 or p_H=0 physical condition is
imposed by omission of the past equations.

Worldvolume scalar transport now integrates the actual induced tangential
flow, bundle transport and measure Jacobian, including coefficient
variations, from the same metric/connection representation. It distinguishes
the temporal Cauchy normal from the spatial material normal. Its paired
dual is G_parent^-1 T^dagger G_child (real transpose for a real pairing).
This implements the producer; the current physical worldvolume/bundle
initial conditions and coupled base have not yet been solved.

## Executed local quantum Pauli contraction

With on-shell charge and canonically matched local poles, the retained
minimal local lepton/photon symbol gives the ordinary local QED diagrams.
The finite spacelike one-loop form factor is evaluated as

    F2(-Q^2) = alpha/(2 pi) integral_0^1
               du/[1+(Q^2/m_mu^2)u(1-u)].

This is the local four-dimensional on-shell limit of the vertex tensor
reduction. Charge/residue counterterms multiply its Dirac tensor; the
Pauli projection removes that local contribution.
[One-loop original](https://doi.org/10.1103/PhysRev.73.416),
[finite-transfer integral, Eqs. 33-34](https://doi.org/10.1103/PhysRevD.108.096036).

For signed t, q=t m_mu u, the actual retained gamma matrices construct
P=i sigma q/(2m_mu), and L_u annihilates D while pairing to one with P_u.
The computed quantity is <L_u,Gamma(tu)-Gamma(0)>/t.
Both signs, three spatial axes, and |t|=1e-3,1e-4,1e-5 are evaluated.
The exact local one-loop limit is alpha/(2pi). The analytic soft-bias bound
is alpha t^2 |u|^2/(12pi), reaching 1.9356828864198055e-14 at |t|=1e-5.
This is not a soft-limit bound for an unevaluated native vertex.

The local spin-sector quadratic pencil is actually solved at p=0 and
p=m_mu/10, for each spin. Its normalized pole residual is at most
4.14981833813801e-18 and descriptor pairing residual at most
2.220446049250313e-16. The full Dirac spin degeneracy is two; no false
simple full-symbol pole claim is made. Interacting self-energy/native
external-mode normalization remains uncomputed.

The complete mass-independent two-loop coefficient is

    A1^(4)=197/144+pi^2/12+3 zeta(3)/4-(pi^2/2)log(2).

Electron and tau VP terms use the subtracted two-parameter integral

    A2^(4)(r)=2 integral dx(1-x) integral dy y(1-y)
                log[1+r^2 x^2 y(1-y)/(1-x)].

The inner integral is evaluated analytically with a stable beta series
near zero; one adaptive outer integral is then performed. Its derivative
with respect to log(r) is differentiated analytically. Independent 60- and
90-digit integrations agree for the requested test ratios; the high
precision agreement is a convergence check, not a rigorous enclosure.
The same-muon VP is already in A1 and is not added a second time.
[Mass-independent source](https://doi.org/10.1103/PhysRev.107.328),
[VP integral](https://arxiv.org/abs/2210.11071),
[diagram ledger](https://arxiv.org/abs/1205.5370).

The neutral radial Higgs loop uses g_hmu=Y_mu/sqrt(2), preserving the fixed
Y operator, rather than independently fitting g_hmu=m_mu/v:

    a_H = g_hmu^2/(8pi^2) integral_0^1
          dx x^2(2-x)/[x^2+(1-x)(m_h/m_mu)^2].

This is one matched local diagram approximation. It does not claim the
required full fixed-Y self-energy, Higgs wavefunction, Yukawa vertex or
interacting LSZ corrections were computed.
[Scalar loop, Eqs. 35 and 64](https://arxiv.org/abs/1403.2309).

| Evaluated term | Contribution to a_mu |
|---|---:|
| Local QED one loop | +0.001161409731851883 |
| Local QED two-loop mass independent | -1.7723050597130995e-6 |
| Local QED two-loop electron VP | +5.904060869095057e-6 |
| Local QED two-loop tau VP | +4.2114919292546455e-10 |
| Fixed-Y local radial Higgs one loop | +2.1614509207310445e-14 |
| Evaluated subtotal | 0.0011655419088320725 |

Higher local QED, remaining weak matching and the disjoint native remainder
are not included. Strong terms are reserved to the unevaluated
native/overlap ledger; no separate strong total is added.

## Smallest remaining native calculation

The minimum readout is the projected, renormalized, charge-normalized scalar

    Delta a_native =
      partial_t <L_u,[Gamma_AE4-Gamma_local,owned]_R(tu)> at t=0.

A common multiplicative LSZ factor cancels in a=A2(0)/A1(0); physical
on-shell injections and their motion, internal response, source motion,
contacts, quotient/domain and relative completion do not thereby cancel.
Since q_mu P^mu=0, Ward and Thomson charge matching constrain the Dirac
normalization rather than the transverse Pauli coefficient.

The induced form is already action-owned:

    R_ind(v,j) = delta_v delta_j Gamma_AE4 - H_local,owned(v,j).

On a common physical quotient define A=A0+R_ind, Au=J_gamma and
A0^dagger p=L_gamma. The exact resolvent identity is

    L_gamma^dagger(u-u0) = -p^dagger R_ind u.

Consequently the response part can be calculated from the application
R_ind u paired with one downstream adjoint, and its soft/source/domain
jets. A full R_ind matrix, complete CAR verdict and complete reconstructed
birth history are not proved prerequisites for this contraction.

The immediate reached operator equation is

    (K0,Q + zeta M0,Q) u_zeta = bar_gamma B_tilde r_in,

on the positive physical photon quotient, with the paired electron-muon
fermion insertions, same regulator and owned overlap. The response must
retain contact and double-insertion terms, moving length/domain/Gram terms,
relative zeta/eta completion, and physical-source/external-state motion.

The saved negative Lorentzian angular density is not the completed positive
proper-time photon operator. Its old C2 source returns were independently
recontracted:

| Conditioning shift zeta/ kappa1 | Tr(J^dagger u_hat) |
|---|---:|
| 93420.48007025628 | 3.5391356579032634e-6 |
| 149472.76811241003 | 2.1894811648609800e-6 |
| 298945.53622482007 | 1.0855589761340900e-6 |

These agree exactly with the saved binary64 returns but retain their old
angular-component, symbolic 1/kappa1 scope. Conditioning shifts are not
soft momentum transfers. The component stiffness trace is
-803192.2451015242, and its existing certificate excludes native, domain,
source and continuum errors. Neither a sign flip nor a selected finite
harmonic block turns these numbers into a calibrated Pauli contribution.

Raw heat dependence also survives the charge algebra. For
Q_c(x)=exp(-cx)/(2x),

    partial_c [(Q_c(x)-Q_c(y))/(x-y)]
       = [exp(-cy)-exp(-cx)]/[2(x-y)],

with diagonal c exp(-cx)/2. This does not prove that the full completion
and subtraction cannot cancel cutoff dependence. That cancellation has
not been evaluated. Where it survives, the cutoff is the owned
c_mu=i_mu_plus/r_mu_plus on the physical birth section; pole mass and
lifetime alone do not specify it.

The narrow unresolved scalar is therefore the Pauli-directed derivative
of this completed source/adjoint contraction after the owned local
subtraction. Its first unexecuted physical application is the positive
completed photon form/remainder on the matched current. Existing angular
component returns, local pole matching and the local Higgs vacuum do not
supply that application. Its inputs depend on calibrated charge and poles
through their physical current/injections; the internal heat, source,
domain and mechanical response must still be computed from their owners.
This is an uncomputed action application, not a missing measurement or an
OWNER_DEFINITION_GAP. No native value or bound is inferred from the muon
anomaly, a small intermediate norm or passing software checks.

## Error budget and verification

The illustrative independent-primitive input standard uncertainty of the
evaluated subtotal is 1.4343531283933382e-12. The linear upper bound over all
primitive correlations is 1.5878928059341156e-12. These are standard
uncertainties of a partial calculation, not observable enclosures. Exact
mass/G_F dependency and mass-ratio motion are retained. Missing actual
cross-source covariance is not treated as zero.

The summed quadrature estimate for the evaluated diagrams is
9.61687641927906e-19. VP beta-series truncation is bounded in exact
arithmetic and scaled to the observable; adaptive quadrature and binary64
roundoff are not certified enclosures. Higher local-order, scalar/radiative
matching, native/overlap, continuum/response and complete soft-limit errors
remain unbounded. The cap 96-to-128 refinement is a diagnostic and does not
supply the missing physical-base error.

The deterministic producers and focused verification commands are:

    C:\Python314\python.exe scripts/evaluate_muon_intrinsic_coupled_primal.py --output artifacts/muon_intrinsic_coupled_primal_20261009/run_1
    C:\Python314\python.exe scripts/evaluate_muon_intrinsic_coupled_primal.py --output artifacts/muon_intrinsic_coupled_primal_20261009/run_2
    C:\Python314\python.exe scripts/evaluate_muon_calibrated_pauli.py --output artifacts/muon_calibrated_pauli_20261009/run_1
    C:\Python314\python.exe scripts/evaluate_muon_calibrated_pauli.py --output artifacts/muon_calibrated_pauli_20261009/run_2

Both producer pairs are byte-compared after LF normalization. Exact test
commands, stdout/stderr, exit status, publication-audit output, input/output
SHA-256 hashes and replay comparison are recorded in
artifacts/muon_calibrated_pauli_20261009/verification.json. That file is the
command/output/hash part of this report. It also records development
failures: corrected numerical tolerance assertions and the replacement of
nested VP quadrature that emitted roundoff warnings. None was hidden or
reinterpreted as physical uncertainty. Prior unchanged producers are reused.

Final focused checks passed 102 tests; existing action, native-consumer,
quadratic pole, LSZ and form-factor checks passed 191 tests. All five required
publication audits passed: status, forbidden claims, frozen integrity,
precision and public readiness. These checks establish implementation and
provenance at the stated scope, not a full physical anomaly enclosure.

| Replayed file, identical in run_1 and run_2 | SHA-256 |
|---|---|
| calibrated_pauli.json | 20a4b5a169439f2db2ff8d37c9746bb7a43c6887a266d6c3e5262d8500fad419 |
| primal result.json | 77d63c5fcb37df313513e35583bdbd4b2fb0cb46375b959701945a694c1e75fe |
| primal_action_applications.json | 24135ae4e3121b89deb90cb8ee9fa863d7e15496d810f790cd0051cabaee8ebf |

| Class | Result |
|---|---|
| DERIVED | Local tensor/readout reduction, real normalized representation, canonical/paired equations, exact source-adjoint native reduction and input dependency gradients |
| EVALUATED | Local Higgs Newton solve, retained off-shell temporal/spatial actions, local spin poles/residue checks, signed one-loop Pauli limit, local QED through alpha^2, fixed-Y scalar loop, decay component and fixed-Y matching discrepancy |
| CONTROL_ONLY | Mesh choices, software fixtures and numerical initial guesses; they select no physical birth/Cauchy state |
| UNEVALUATED | Interacting pole/vertex matching, common-unit/event application, full stationary birth base and formation section where consumed, positive native sourced response/completion/overlap, complete a_mu/g_mu and uncertainty |
| OWNER_DEFINITION_GAP | None established |

The published advance is the evaluated calibrated component and its
reproducible residuals/contractions. Completion of the requested full
observable is not claimed.
