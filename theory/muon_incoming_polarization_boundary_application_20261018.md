# Incoming subspace: defining boundary relation and a conditional application

The new result is a nonstationary, finite original-action **control** of an
explicit incoming boundary selector, followed by actual section synthesis and
exact-pair current consumption. It is not the physical Gaussian collider
realization. The control also exposed and fixes a channel/spin index collision
in the previously unexecuted ordered-current consumer. No completed response,
archive import, calibration or CI repair is repeated.

## 1. What determines a subspace

On an admitted common background/domain y, use the original canonical field
chi=R4^(3/2) psi and its positive Cauchy pairing. The retained lepton action gives

    (i partial_tau-H_y) f = 0,
    H_y = -i alpha^a(E_a+Omega_a)/R4
          +(3/2)gamma5/R4+M_Y(H)-i Omega_tau.

After action-isometric identification with a fixed Hilbert space, the generator
is h_y=T H_y T^-1+i (partial_tau T)T^-1. All moving frame, density and domain
identifications belong to T; their terms cannot be omitted. The homogeneous
control below has a fixed canonical Haar pairing, so T is constant.

If P(tau) is a solution subspace, Dirac evolution requires

    i partial_tau P = [h_y,P],
    P(tau)=U_y(tau,tau0) P0 U_y(tau0,tau).

This is a transport equation with boundary datum P0. The Euler equation and a
Gram condition do not provide that datum. Self-adjointness, charge/family
compatibility, CAR reality and the positive-frequency Hadamard singularity
constrain it. They do not impose an initial spectral boundary condition.
Here this conclusion follows from the explicit general solution of the
equation, not from an absent routine. It does not prove multiple solutions of
the full coupled physical background/preparation problem.

## 2. An explicit candidate boundary prescription, not adopted

The conditional stationary-past construction already appears in section 7 of
[the retained operator/reference derivation](bhsm_operator_reference_construction_20261016.md).
Its formulas alone are not a new milestone. In a physical charged application
it must be stated with its comparison, domain and dressing:

    (i partial_tau-h_y) f_a,s = 0,
    lim_(tau->-infinity)
      || f_a,s(tau)-J(tau) U_as(tau,0) f_as,a,s ||_(Sigma_tau) = 0,
    f_as,a,s in Ran P_as,a .

J identifies the comparison Cauchy spin/gauge/density frames and domains.
U_as is a same-action incoming comparison evolution, including required charge
dressing and long-range terms. It is not assumed to be the free propagator.
If a same-action stationary gapped asymptotic generator h_-^phys is established
in its physical time and gauge lift, the additional spectral boundary rule is

    P_as,+ = 1_(0,infinity)(h_-^phys),
    P_as,- = 1_(-infinity,0)(h_-^phys),
    Omega_- = strong-lim_(tau->-infinity)
                  U_y(0,tau) J(tau) U_as(tau,0),
    P_in,+/- = Omega_- P_as,+/- Omega_-^dagger.

These equations actually identify incoming subspaces. Zero modes need their
own rule. If Omega_- has only a scattering range, its two images do not cover
unidentified bound/reference sectors; I-P_in,+ is not automatically the full
antiparticle projector. Current-unitarity, charge/family/reset compatibility,
domain control and the continuum Hadamard property must be proved at the
physical scope. The full18 point fiber is not a self-dual doubled CAR carrier;
the latter's antiunitary reality constraint must be imposed on its own carrier.

A sufficient packetwise Cook condition is

    integral_(-infinity)^tau0
      ||(h_y J-i Jdot-J h_as) U_as(tau,0) f_as||_Sigma d tau < infinity.

For a fixed finite/bounded comparison with J=I and h_as=h_-, the existing
Duhamel bound is 2 integral_(-infinity)^s ||h_y-h_-|| d tau for the
projector cutoff error. Unbounded moving-domain operators require graph
estimates; Coulomb-type long-range tails need not satisfy this bounded
short-range criterion. A regulator D^dagger D or heat proper time does not
select the sign of the physical Lorentz generator.

The preparation slice tau=0 and its local tetrad are already specified. They
are not new knobs. The candidate requires a same-action incoming reference
history and comparison-state boundary rule, not another choice of beam energy
or spin polarization. Naively diagonalizing H_can on an arbitrary slice is
also gauge-dependent: a time-dependent gauge frame adds i Vdot V^dagger to
the generator. The spatial/mass operator H_can+i Omega_tau transforms
covariantly in the stated gauge frame, but its instantaneous sign remains an
extra selector and generally fails the transport equation. A physical
stationary generator includes the specified time/gauge lift.

## 3. What the action and adopted preparation already supply

The original action implements the local full18 Hamiltonian, fixed Yukawas,
Higgs-selected charged fiber, original current vertices, complete represented
Haar Gram and time jets. The current consumer implements the finite exact
pair mean and all ordered products; the change here repairs its independent
channel indices. The two cap histories are not beam labels.

The adopted JSON fixes the 500 MeV central energy, 100 fm scalar probability
RMS widths, centers at +/-1000 fm, phases/chirp, incoming directions, tau=0
preparation slice, and independent unpolarized exact pair. Those amplitudes
are to be expanded in the comparison's actual action spectral resolution,
with its mass shell, measure conversion and charge-conjugate antiparticle
convention. They do not define that resolution. The adopted no-extra
occupation/radiation condition is explicitly relative to the inherited
same-action reference. It neither specifies a stationary incoming end nor
sets that reference, its constraint fields or homogeneous correlations to zero.

The packet and background must then jointly satisfy the original Dirac,
gauge/Higgs/metric constraints and boundary equations, with the existing
physical-unit equation G_F exp(2e)-c_F[y,modes,domain]=0. In particular the
lepton contribution to a material Gauss row is

    j_c = (1/2) sum_s [U_s^dagger(i G_c)U_s-V_s^dagger(i G_c)V_s],
    delta S_gauge/dA_t + delta S_H/dA_t + density*j_c
      + surviving native/reference/interface terms = 0.

The finite relative j_c needs no separately supplied complementary sea once
actual U,V exist. This is not a proof that reference-sensitive terms cancel
from the completed physical construction. A smooth CAR-compatible rotation
in the complement of four fixed packet modes can preserve those modes and
their exact preparation while changing the complementary reference. That
limited witness neither proves ambiguity of the packet images nor proves
two self-consistent BHSM backgrounds. An additional selector must be derived
or adjudicated; physical nonuniqueness is not inferred here.

## 4. The equation actually executed

The reproducible implementation is
`scripts/evaluate_muon_incoming_polarization_candidate.py`. It uses a declared
manufactured homogeneous S3 path:

    R4=N=1; Omega_mu=0 only on this control;
    H=(0,m(tau)/Y_e), m=.75+.75 S(tau),
    S=0 (tau<=0), S=1 (tau>=1),
    S=exp(-1/tau)/[exp(-1/tau)+exp(-1/(1-tau))] inside (0,1).

The unchanged frozen electron Y_e supplies the mass map. Its Higgs amplitude
is a numerical test input, not a fitted or calibrated physical background.
The full18 constant-angular charged electron image is invariant on this
homogeneous path. Its two equal spin blocks have W=[[-a,m],[m,a]], a=1.5,
up to the existing unitary Dirac/LR frame change. The represented spatial
section is constant/sqrt(2 pi^2), with the complete constant-sector Haar
integral 2 pi^2. No point Gram is substituted for that integral.

The selected past is exactly stationary for tau<=0 **by control definition**.
We execute P0=1_(0,infinity)(W(0)) and i Udot=W(tau)U, U(0)=I, then synthesize
the two positive and two negative columns of U in the original full18 frame.
The past Cook tail is exactly zero on that control; cutoff conjugations
starting at -1 and -2 differ by 4.48e-16 in finite arithmetic. No claim of a
physical asymptotic end follows from this control.

For an independent five-point time difference (epsilon=1e-4) at nine
interior points, the original full18 Dirac residual max is 1.557e-11 in the
complete constant-sector canonical Haar norm (point norm times sqrt(2 pi^2));
the coefficient projector transport residual is 2.465e-11. Invariant-carrier
leakage is 5.31e-16; evolution unitarity defect is 1.43e-13. These are finite
floating point diagnostics, not outward or continuum bounds or physical
derivative admission. Final run_3 and run_4 materialized byte-identically.

The initial local run_1/run_2, retained as untracked evidence, used looser
finite ODE tolerances and reported the pointwise Dirac norm 1.345e-10.
Review identified that its complete Haar norm is about 5.98e-10, exceeding
2e-10 even at this finite control scope. The final producer reports both
norms explicitly and uses rtol=3e-14, atol=3e-16 for this small four-coefficient
integration. This numerical correction changes no physical guard, state,
calibration or completed response. The initial nonpass is recorded in the
checkpoint; it is not relabeled as a physical pass.

The instantaneous sign has a nonzero independently checked defect:

    ||i Pdot_inst-[W,P_inst]||
       = |a mdot-m adot|/[2(a^2+m^2)] = .32 at tau=.5.

At that point its distance from the transported projector is .0854391.
Thus the action distinguishes transport of an identified past subspace from
continual instantaneous reselection. This is more than a normalization test.

The sections were consumed by `construct_action_packet_sections`,
`apply_incoming_packet_current` and `original_material_Gauss_source`, using
the retained exact pair with trace 1 and purity .25. The ordered 24-by-24
original-vertex products agree with direct 16-by-16 Fock traces to 1.09e-19.
The consumer's old einsum reused one label for a 24-channel axis and a
four-mode spin axis; it could not execute this application. Distinct labels
fix that defect without changing the pair density or current definition.

At tau=.5 the transported material source density in channel order
unitTr16 H1,H2,H3,HY is

    [0,0, .015712101499192534, -.012170541488058656].

Its constant-test Haar loads are
[0,0,.31014445221358666,-.24023685966836866]. The mean original-current
difference from instantaneous reselection is .00138312. In the declared
trial the classical gauge curvature is zero, and a spatially homogeneous
real Higgs amplitude has zero temporal Higgs charge. The nonzero finite
lepton load is therefore an explicit Gauss **subtotal nonpass**, not a solved
constraint. Unknown native/reference/interface terms of the physical problem
are not set to zero or absorbed into a fitted force.

## 5. Exact limit and adjudication

The homogeneous constant-angular control does not represent the adopted
Gaussian energy, widths or centers. Its physical MeV/fm moment and projection
residuals are unexecuted/null with reasons in the receipt, never passes.
It is not an initial physical collision solution, an incoming Fock transition,
a 900-coordinate occupation, a corrected wall, or a magnetic readout.

The precise outstanding selection question is whether the inherited
incoming reference is defined by the dressed incoming boundary condition in
section 2, on an action-derived constrained past, or by a different explicit
action-owned finite-boundary/Euclidean state functional that fixes its
polarization. The Gaussian design and relative no-extra-radiation condition
do not choose between those prescriptions. Current sources do not establish
the past/domain/comparison hypotheses of section 2. This candidate remains
unadopted; no new vacuum, asymptotic geometry or spectral rule is assigned to
the physical branch by this publication.

NEXT_OPERAND: derive or adjudicate that incoming boundary-state relation and
its same-action constrained reference/domain, then solve the adopted packet
and background constraints jointly and evaluate actual preparation moments
and original residuals. The physical 2e-10 guard, calibration, prior gauge
reconstruction/membrane finite-step nonpasses and continuum/time-error limits
remain unchanged. No coupled correction or final moment/uncertainty is claimed.

Reproduce the finite control in two new output directories (existing outputs
are checkpoints and are not overwritten):

```text
python scripts/evaluate_muon_incoming_polarization_candidate.py --output artifacts/muon_incoming_polarization_candidate_20261018/replay_A
python scripts/evaluate_muon_incoming_polarization_candidate.py --output artifacts/muon_incoming_polarization_candidate_20261018/replay_B
python -m pytest -q tests/test_muon_incoming_polarization_candidate.py tests/test_muon_native_dirac_hamiltonian.py tests/test_muon_magnetic_open_lepton_vertex.py
```

The recorded final result hash is
`f379bb41e6a636b7ce20f37ab3d91dfd778737c69a48780362914db71046e4e4`.
Byte identity is the observed repeat result in the recorded Python/NumPy/SciPy
environment, not a guarantee of identical last bits on other numerical stacks.
