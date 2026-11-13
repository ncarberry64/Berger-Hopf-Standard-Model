# Daughter-envelope cascade: connection to the muon magnetic response

Norman P. Carberry / BHSM research continuation — 17 October 2026

## Scope and result

The author has adopted **daughter-envelope cascade through boundary rupture and
re-formation** as the BHSM interpretation to investigate. The fluid daughter-bubble
experiment supplies an analogy and terminology, not particle-scale coefficients
or proof of the electromagnetic mechanism [1]. No fluid surface tension,
resistivity, fragmentation law, retention fraction, or reconnection rate is added.

This document applies existing projection, resonance, and event-sensitivity
mathematics to that interpretation. It derives a compact route from an admitted
common-domain daughter response to the spin magnetic matrix. Seven groups of
constructed algebra/finite-system controls were executed. No actual BHSM
formation event, quantum daughter propagator, magnetic insertion, physical pole,
normalized incoming packet, or muon anomaly is evaluated here.

Repository read anchor: PR #465,
`70e82fd4dbe5f53ff27ae17f6aaac7a4727c1fde` [R1]. The inspected publication preserves
all 24 daughter action legs and both spin coherences. Its actual source tensor
is still on retained static backgrounds; its scalar ancestry includes
`lambda_H=G_F*m_h^2/sqrt(2)`. The complete physical outgoing derivative and pole
are not admitted. These qualifications remain unchanged.

This continuation does not rerun that publication, replace its vertices, improve
its already checked frequency precision, or write to GitHub. The new software
operates on explicit supplied blocks and constructed test matrices, not a local
checkout of the full research repository.

## 1. Three roles of a daughter cascade

The adopted interpretation has to distinguish:

1. **Formation:** the initial collision/encapsulation event prepares the actual
   muon state and its inherited field/background data.
2. **Evolution:** the formed muon interacts with the weak magnetic probe while
   it remains in its metastable sector.
3. **Decay/readout:** daughter production gives a spin-sensitive measurement.

Daughter-sector coupling can affect both evolution and the readout, but they are
not the same operator. The published analyzer `D(E,n)` in
`Tr[D(E,n) rho_mu(B,t)]` does not supply the magnetic generator [R1].

The physical response must respect the original field equations, charge/spin
representation, common Cauchy pairing, interfaces, and the fixed adopted
500-MeV-per-beam, 100-fm-width preparation. No ideal radiation-only control may
replace the charged incoming fields. A multi-channel cascade includes envelopes,
radiation, and independently encapsulated daughters where their action modes
exist. The interpretation does not select uncomputed channels or populations.

## 2. Exact chronological elimination retains history

Consider an admitted total quantum Hamiltonian and a Hilbert-space splitting into
retained muon sector and its complementary daughter/environment sector. This is
conditional on the physical carrier and domains actually being supplied. Write,
in units with hbar=1,

    i d_t m = H_mu(t) m + V_L(t) z,
    i d_t z = H_D(t) z + V_R(t) m.

On a real physical self-adjoint realization V_L=V_R^dagger. Independently
continued left leaves must be used on an analytic chart.

If U_D(t,s) solves the actual complementary evolution, the exact solution is

    z(t) = U_D(t,t0) z0 - i integral_t0^t U_D(t,s) V_R(s) m(s) ds,

and therefore

    i d_t m = H_mu m + V_L(t) U_D(t,t0) z0
              - i integral_t0^t K(t,s) m(s) ds,
    K(t,s) = V_L(t) U_D(t,s) V_R(s).

This is an elimination identity, not a numerical realization of the missing
history operator. It retains the initial complementary state and nonlocal
memory. Setting extra incoming radiation to zero relative to an inherited sea
does not set z0 or all sea contractions to zero. For mixed states, the full
state/density correlations must also be retained.

Do not replace K(t,s) by a static inverse or a momentum-independent decay tensor
without an applicable approximation and controlled remainder. A finite closed
Hamiltonian used below is an algebra control; it is not a physical reflecting
cap or a proposed boundary condition on the outgoing BHSM channels.

## 3. Where the magnetic moment is encoded

Only once the formed state admits the required stationary/resonant description,
write its quantum inverse operator in a common fixed-domain representation:

    Gamma(E,B) = [[A(E,B), Bc(E,B)],
                  [Cc(E,B), D(E,B)]].

The labels Bc and Cc denote coupling blocks; B denotes the external magnetic
field. D includes the actual daughter-sector operator and its domain/completion.
Where its outgoing inverse is defined,

    Gamma_eff = A - Bc D^(-1)_out Cc.                         (1)

This is the Feshbach-Schur reduction [2]. It organizes a coupled quantum
response; it does NOT identify the classical Maxwell retarded inverse with a
quantum propagator. The existing 24-leg field Green inside the daughter tensor
is not automatically the multi-particle daughter resolvent in (1).

At an admitted two-spin pole E=z_mu and B=0, let R contain right null columns
and L the independently normalized left null rows of Gamma_eff. Define

    Z = L (partial_E Gamma_eff) R,
    M_a = -Z^(-1) L (partial_Ba Gamma_eff) R.                 (2)

The eigenvalues of M_a are the first pole-energy responses to the corresponding
weak magnetic field. In an unstable-particle construction use the physical
complex pole/residue convention; taking an off-shell Dirac tensor coefficient
or a local free-rest spinor does not perform that extraction [3,R1]. Keep real
and absorptive responses separate instead of dropping imaginary parts early.

In the real, charge-normalized isotropic Zeeman limit, with s=+1/-1 labelling
spin along B and hbar restored,

    E_s(B) = E0 - s g_mu q_mu hbar B/(4 m_mu) + O(B^2),
    g_mu = -(2 m_mu/(q_mu hbar)) Re[zeta_+ - zeta_-],
    a_mu = g_mu/2 - 1,

where zeta_s is dE_s/dB and q_mu is the signed matched muon charge. All masses,
field units, charge normalization and spin labels must be those of the admitted
physical solution. In a nonisotropic prepared environment, first retain the
full three-axis response rather than force it into one universal scalar g.
The connection to the charge-normalized soft Pauli form factor F2(0) remains
an actual matching check, not a convention that erases other terms.

Equation (2) is already the structural magnetic consumer in the repository [R1].
The point of this calculation is to connect the proposed cascade to its actual
quantum source blocks, not introduce another independent magnetic formula.

## 4. Only contracted daughter applications are needed for each first derivative

For fixed base pole leaves, solve

    D u = Cc R,
    D^T p = (L Bc)^T.

Then for any source s, including E or one magnetic component,

    L Gamma_eff,s R = L A_s R - L Bc_s u - p^T Cc_s R
                     + p^T D_s u.                          (3)

No explicit inverse matrix is needed. For a two-spin retained pair, this uses
two right-hand sides on each side, reused for the different source contractions.
The continuum application must still solve the true outgoing problem. Matrix
size alone does not establish compatibility with historical stored maps.

Every block derivative in (3) must contain its complete field, normalization,
measure, constraint, state, interface, event, and native-domain dependence along
the selected preparation. At a genuine pole the outer null-leaf derivative terms
vanish in the first pole sensitivity because Gamma_eff R=L Gamma_eff=0. This
fact must not be used to discard motion of injections INSIDE the block map, or
moving tests at an unmatched off-shell candidate.

**Sign check.** In Hamiltonian notation,

    Sigma(E,B)=V_L(E-H_D+i0)^(-1)V_R,
    Gamma_eff=E-H_mu-Sigma.

For energy-independent H_D and V, partial_E(E-H_D)^(-1)=-(E-H_D)^(-2),
not the positive sign. Hence the residue contains I-partial_E Sigma. Magnetic
variation includes both vertices and the intermediate propagation. If a source
moves D, the final +p^T D_s u term in (3) is indispensable.

The two-spin finite control checks (2) against the original full Hamiltonian's
normalized degenerate eigenvectors and independently against finite-field
splittings. Dropping Z changes the answer in that control.

## 5. Decay probabilities do not determine the real magnetic correction

For a stationary self-adjoint complementary Hamiltonian, introduce the spectral
measure

    W(omega,B) = V_L delta(omega-H_D) V_R,
    Sigma^R(E,B)=integral W(omega,B)/(E-omega+i0) d omega
                + required local/renormalization completion.

At a real boundary value, the anti-Hermitian part contains

    -2 Im Sigma^R(E,B)=2 pi W(E,B),

while its Hermitian part involves a principal-value energy integral and the
specified completion. The decay calculation samples on-shell spectral weight;
the magnetic response also needs the field derivative, energy derivative, and
proper subtractions. On-shell energy means and a total rate do not determine all
those quantities. This does not prove multiple complete BHSM models; it limits
what can be inferred from the published static diagnostic.

The existing C_abcd=R_A G_AB L_B is a four-fermion amplitude tensor, not the
muon self-energy itself and not a classical Maxwell current [R1]. Its physical
mode projections can provide vertices in the daughter contraction; all momenta,
spin labels and connected-channel propagation still have to be supplied. In
particular, the momentum-dependent C cannot be pulled outside the local
phase-space moments, as the current report already notes.

**No double counting:** the cascade is an interpretation of existing action
channels. Any contribution already present in the native action or frozen
local ledger must not be added a second time as a 'bubble correction'. Matching
requires the owned overlap subtraction. The inherited G_F/Higgs calibration
remains explicit; no parameter is adjusted to reproduce measured a_mu.

## 6. Daughter marginal rates are not independent decay rates

For an exclusive joint final state lambda, let A_lambda map parent spin into
that complete daughter channel. The inclusive decay-rate/analyzer structure
uses A_lambda^dagger A_lambda integrated over that joint channel. Partial
observations of the electron, muon neutrino or electron antineutrino are
marginals of the SAME event.

The publication finds the three integrated parent-spin matrices equal and their
energy-weighted sums balanced [R1]. Thus summing the three total rates would
triple-count the event. Multiple exclusive physical channels may be summed once;
three observations of one channel may not. Indistinguishable cascade histories
must be combined coherently before squaring unless an actual decoherence or
orthogonality argument permits an incoherent sum.

For coupled successive daughter sectors, joint elimination and nested Schur
elimination agree. Independently deleting their cross couplings does not. The
finite control explicitly verifies both statements.

## 7. A stationary daughter analyzer changes visibility, not the precession frequency

Assume solely for this exact conditional identity that the formed spin evolves
with H=omega sigma_z/2, scalar loss gamma I, and a time-independent Hermitian
positive analyzer D=d0 I+d dot sigma. For
rho0=(I+P dot sigma)/2,

    N(t)=exp(-gamma t) [d0+dz Pz
          +(dx Px+dy Py) cos(omega t)
          +(dy Px-dx Py) sin(omega t)].                      (4)

This follows directly by exponentiating the 2x2 spin Hamiltonian. Changes in D
can reverse the asymmetry or change its phase/amplitude while leaving omega
unchanged. The published non-V-A static analyzer differences therefore cannot,
by themselves, be interpreted as a magnetic-moment shift. They remain important
weak-decay diagnostics.

For P=0 there is no mean spin-precession modulation in this specialized signal,
even though the Hamiltonian has a nonzero splitting. One can retain the two-spin
operator and joint-spin correlations; the adopted unpolarized incoming beams
need not be changed just to define the theoretical magnetic response. Do not
assume that the actually produced muon is unpolarized or has scalar loss without
calculating its density and decay operator.

If spin-selective loss, time-dependent sources/analyzers, entanglement with the
environment, or nonlocal memory are relevant, (4) must be replaced by the full
evolution/readout. No such simplification is adopted for the actual BHSM branch.

## 8. A popping event may require event-time derivatives

Where a derived continuum transition has a valid reduced hybrid representation,
write the before/after vector fields f^-, f^+, event condition g(x,t,s)=0, and
reset R(x,t,s). This notation does not choose a formation condition, a reset, or
a deterministic rule for quantum decay. It applies only after they have been
obtained from the physical dynamics and a transverse event has been established.

At the event define v_g=g_t+g_x f^-. Then

    delta t_event=-(g_x delta x^-+g_s delta s)/v_g.

Comparing the perturbed after-state at a common time gives

    delta x^+ = Xi delta x^- + eta_s delta s,
    Xi = R_x + (f^+-R_x f^- - R_t) g_x/v_g,
    eta_s = R_s + (f^+-R_x f^- - R_t) g_s/v_g.                (5)

This is the saltation/event-sensitivity formula [4]. It can have different
before/after state dimensions. The fixed-time reset Jacobian R_x alone is not
generally sufficient. A continuum evolution with a fully differentiated moving
event already contains this effect; adding (5) again would double count it.
At grazing/degenerate events with v_g=0 the formula is not admitted. Returning
to the regular field problem or another validated chart is required.

This is a concrete audit target for the earlier derivative discrepancy, NOT a
claim that the current code omitted it or that it explains the 1.05-6.21% error.
The exact event control recomputes a changing transition time independently and
shows a nonzero failure when that time is frozen.

## 9. Executed evidence

Seven check groups pass in two byte-identical executions:

- exact symbolic scalar Schur product rule;
- independent analytic-left contracted derivative versus the original full inverse;
- a coupled, degenerate two-spin pole including its energy-residue normalization;
- coherent nested/joint cascade elimination and a deleted-cross-coupling control;
- chronological elimination with the nonzero initial complementary term;
- event-time sensitivity against a separately solved event trajectory;
- the stationary analyzer identity against explicit 2x2 density evolution.

Selected final numbers are in `replay_A/result.json` and identically in replay_B.
The contracted derivative error is 5.06e-15 at the last stated finite-difference
step. The pole magnetic matrix agrees with the full normalized eigenspace at
5.56e-17. The independent field-difference slopes show second-order convergence;
the recorded last error at step 0.00025 is 3.61e-10. This is a finite control,
not a physical 2e-10 outgoing admission. The event derivative matches its direct
trajectory difference within 4.81e-14. Freezing the event time produces 0.0648
error in that constructed example.

No test matrix or example frequency is promoted to a BHSM field, charge, pole,
daughter population, lifetime, or magnetic moment. Physical a_mu/g_mu and total
uncertainty remain null. No coupled correction was applied.

## 10. The actual next application

Use the published daughter tensor and compatible source machinery only after
the physical mode/domain relation is established. Construct the true
preparation-to-cascade current projection, retain the full nonlocal outgoing
response, and obtain the total E and three B derivatives in a common chart.
Where a reduced popping event is used, verify whether its time sensitivity is
already present. Apply (3) to the physical source directions and evaluate (2)
on the admitted pole. This is more targeted than producing further static
daughter energy spectra or further precision on already checked local arrays.

The current package supplies this reduction and its controls. It does not supply
the missing physical source or domain. If those objects remain undefined, the
next task is their particular action correspondence, not declaring the bubble
analogy to have fixed them. Maintain the 2e-10 physical guard and the existing
fresh Maxwell/all-226 validation before physical promotion. Preserve all static
non-V-A discrepancies and the calibrated input ancestry.

## Sources

[R1] Norman Carberry, Berger-Hopf-Standard-Model, pinned revision above:
`artifacts/muon_daughter_source_spin_20261016/DERIVATION_AND_SCOPE.txt`,
`SOURCE_MAP.json`, and `scripts/evaluate_muon_daughter_source_20261016.py`.
Read through the connected GitHub tool in this continuation. Code and binary
arrays were not imported or replayed locally. PR head was verified at this SHA.
https://github.com/ncarberry64/Berger-Hopf-Standard-Model/pull/465

[1] J. C. Bird et al., Daughter bubble cascades produced by folding of ruptured
thin films, Nature 465, 759-762 (2010), doi:10.1038/nature09069.
https://www.nature.com/articles/nature09069

[2] Y. Pavlyukh, M. Schuler and J. Berakdar, Single- or double-electron emission
within the Keldysh nonequilibrium Green's function and Feshbach projection
operator techniques, Phys. Rev. B 91, 155116 (2015), arXiv:1504.05450.
The projection mathematics is reused, not claimed as a new discovery or as an
already established BHSM physical realization.
https://arxiv.org/abs/1504.05450

[3] J. Gegelia and S. Scherer, How to define physical properties of unstable
particles, Eur. Phys. J. A 44, 425-430 (2010), arXiv:0910.4280.
https://arxiv.org/abs/0910.4280

[4] N. J. Kong et al., Saltation Matrices: The Essential Tool for Linearizing Hybrid
Dynamical Systems, arXiv:2306.06862; Proceedings of the IEEE (2024).
https://arxiv.org/abs/2306.06862
