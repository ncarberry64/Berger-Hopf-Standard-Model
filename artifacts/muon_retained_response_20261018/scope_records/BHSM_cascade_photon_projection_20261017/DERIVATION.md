# Coherent cascade source and the electromagnetic insertion of its reduced operator

Norman P. Carberry / BHSM continuation — 17 October 2026

## Result and boundary

This extends the attached `BHSM_daughter_cascade_magnetic_connection_20261017`
package. It supplies (i) a two-parent-spin, all-leg coherent daughter-source
projection and its first derivative, (ii) the finite-transfer electromagnetic
vertex of a Schur-reduced operator, (iii) its Ward identity, (iv) a pure moving-frame
cancellation test, and (v) a two-energy spectral test exposing magnetic mixing
that is absent from zero-field decay data.

Six groups of constructed finite/algebraic checks were executed twice. These
are NOT physical BHSM source or pole values. The numerical arrays in those tests
are explicitly constructed; no published 64-entry physical tensor was
reconstructed from reported means or fitted to the anomaly. No collider packet,
inherited reference, quantum daughter domain, magnetic insertion, coupled
correction, or physical a_mu/g_mu was supplied or solved by this continuation.

The connected PR #465 head was read at
`70e82fd4dbe5f53ff27ae17f6aaac7a4727c1fde`. The latest publication still labels
its daughter tensor as a calibrated, static-background application and its
frequency derivative as a fixed-domain partial. No newer physical source,
quantum domain or pole was recovered. Source text was inspected via GitHub;
its NPZ archives were not imported or executed. The network download attempts
did not supply those bytes. No remote or Windows-worktree write was performed.

The daughter-envelope cascade remains Norman's interpretation to investigate.
Neither a bubble-fragmentation rate nor a plasma reconnection coefficient is
introduced. The adopted beam design and all prior physical guards are unchanged.

## 1. A coherent daughter source, not a classical Maxwell current

The current source code defines

    C_abcd = R_A,ab G_AB L_B,cd

with 24 retained gauge/Higgs legs, R shape (24,2,4), L shape (24,4,2), and the
literal left placement. For a joint daughter configuration lambda, keep the
parent spin s and electron spin r explicit:

    j_mu(lambda,A,s) = nu_left(lambda,a) R_A,ab mu(lambda,b,s),
    j_e(lambda,B,r)  = e_left(lambda,r,c) L_B,cd anti_nu(lambda,d),
    A(lambda,r,s)    = sum_AB j_mu(lambda,A,s) G_AB(lambda) j_e(lambda,B,r).

The electron antineutrino is the outgoing v section of the electron-neutrino
field, not an additional particle representation. The code does not manufacture
these sections. On real physical parameters the left sections have their
physical adjoint meanings; on an analytic source chart their independently
continued leaves must be supplied. Complex transition amplitudes must not be
inserted as real classical field-source expectations.

Let w_lambda be the actual joint-channel quadrature/measure, including whatever
state and normalization factors the admitted construction requires. Define

    V_(lambda,r;s) = sqrt(w_lambda) A(lambda,r,s).

This maps TWO parent spin columns into the coherent joint daughter space.
For this finite on-shell source projection its rate Gram is V^dagger V. Turning
it into a Hamiltonian coupling or an off-shell spectral density still needs the
corresponding energy-shell measure and normalization; the rate Gram alone does
not establish that identification.

No separate sum over three daughter marginal total rates is performed. Every
exclusive joint channel is included once. Alternative histories of the same
indistinguishable final state must be combined coherently unless orthogonality
or decoherence is actually demonstrated.

The implemented derivative is

    V_s = sqrt(w) A_s + (w_s/(2 sqrt(w))) A.

A_s contains all seven placements: nu_left, R, mu, e_left, L, anti_nu, and G.
Derivatives of trace, domain, inherited-state, scale and preparation maps belong
inside these supplied total operands and measure. They are not zero by default.
The code tests the full product against an independent route that first builds
all 64 tensor entries. It retains all24 legs and both parent/electron spins.

This construction allows momentum-dependent source values per joint node. It
does not replace an uncomputed nonlocal spacetime source by a diagonal-node
ansatz. Any required nonlocal spatial/history convolution must first supply the
actual projected values, or be represented in an enlarged source space.

## 2. Insert the measuring photon into the equations before eliminating daughters

The previous package established the first-derivative contraction at one base
point. The present extension works at the TWO momentum arguments needed for a
current vertex and supplies a conservation identity.

For an admitted common fixed-domain quantum inverse operator, write

    Gamma(p) = [[A(p), B(p)], [C(p), D(p)]],
    S(p) = A(p) - B(p) D(p)^-1 C(p).

D^-1 must have the actual physical outgoing/analytic realization. The elementary
finite matrix solve in the code is not a substitute for its continuum history,
initial state, retarded/quantum distinction, or ultraviolet/domain completion.

Define the right and left lifts

    T(p)       = [I; -D(p)^-1 C(p)],
    Ttilde(p') = [I, -B(p') D(p')^-1].

They obey

    Gamma(p) T(p) = [S(p);0],
    Ttilde(p') Gamma(p') = [S(p'),0].

Let J^mu(p',p) be the COMPLETE measuring-photon insertion of the unreduced
quantum inverse operator, including its coupling, source, domain and completion
contacts. The reduced insertion is

    J_eff^mu(p',p) = Ttilde(p') J^mu(p',p) T(p).              (1)

Expanded into blocks, this is

    J_A - J_B D^-1 C - B' D'^-1 J_C
        + B' D'^-1 J_D D^-1 C.                              (2)

Primes in (2) denote p', not derivatives. Both momentum arguments matter.
A photon coupled only to a daughter propagator omits the interaction/source
terms J_B and J_C. A photon coupled only to the retained parent omits all three
other terms. Gauging the complete equations rather than selecting only some
attachments is the established few-body current-construction principle [E1].
It is reused here, not claimed as a new physical law.

The microscopic BHSM generating operator is not reconstructed by this algebra.
An electromagnetic vertex of a chosen finite field symbol is not automatically
the complete quantum J^mu in (1).

## 3. Exact charge-conservation test on the reduced vertex

Fix the Ward convention

    q_mu J^mu = Gamma(p') Q - Q Gamma(p),  q=p'-p,

and require the charge to respect the retained/complement split:

    Q = diag(Q_P,Q_D).

In the actual fixed-charge muon/daughter sector this has the appropriate equal
total charge; the code's more general block-diagonal charge is an algebra test,
not a selected physical charge assignment.

Using the two lift identities gives exactly

    q_mu J_eff^mu = S(p') Q_P - Q_P S(p).                    (3)

Proof: multiply the full Ward identity by Ttilde(p') on the left and T(p) on the
right. Its first product becomes [S',0] Q T = S' Q_P and its second becomes
Ttilde Q [S;0] = Q_P S. No summation over omitted modes or numerical fitting
is involved in the identity.

The finite test constructs a noncommuting, complex full operator and a vertex
satisfying the stated Ward equation. Its reduced residual is 1.01e-16. Removing
the daughter photon block gives a reduced residual 0.0186151 in the same
constructed example. This diagnoses that omission in the example, NOT in the
published physical BHSM code.

Moving projectors/pairings and interaction-dependent boundary maps must first
be included in the common-domain operator and J. The identity is not permission
to treat them as fixed in the physical source derivative.

## 4. A moving daughter basis cannot create a physical magnetic moment

Let U(s) be a unitary change of daughter frame alone. With F=diag(I,U),

    Gamma_new = F^dagger Gamma F.

Its Schur complement equals S for all s. At s=0, with X=F_s,

    Gamma_new,s = Gamma X - X Gamma

for anti-Hermitian X. Therefore

    Ttilde (Gamma X-X Gamma) T = 0.                          (4)

Changes in D are canceled by the corresponding changes in B and C. Retaining
D_s while freezing the coupling/source maps can create a fictitious response.
This is relevant when a Higgs-selected frame or mode normalization is moving,
but does not prove that an existing implementation has made that mistake.

The finite test gives complete derivative 6.29e-18 and a 0.0124421 false
response if the coupling motions are deleted. An independently evaluated
finite frame change leaves S unchanged within 5.55e-17.

## 5. The magnetic source needs off-diagonal daughter transitions

On a stationary self-adjoint daughter spectral chart, at an appropriate complex
resolvent point z,

    Sigma(z) = V_L (z-H_D)^-1 V_R.

For a real magnetic parameter a, its intermediate insertion contains

    V_L (z-H_D)^-1 H_D,a (z-H_D)^-1 V_R.                    (5)

If H_D has spectral projection-valued measure dP(omega), (5) is

    integral integral
        V_L dP(omega) H_D,a dP(omega') V_R
        /[(z-omega)(z-omega')].                             (6)

In addition there are V_L,a and V_R,a terms and all domain/completion terms.
A diagonal spectral density V_L dP(omega) V_R is not the two-energy object in
(6). Discarding omega!=omega' is justified only under actual commutation or
selection rules, not because the zero-field energy derivatives vanish.

### Exact constructed example

Take two parent and two daughter coordinates, with

    H_D=diag(2,4), V_L=V_R=I2, H_mu=diag(1/2,1/4).

For the full Hamiltonian [[H_mu,I],[I,H_D]], the Schur inverse has a two-fold
zero at E=0 and

    Z=diag(5/4,17/16).

Compare two different supplied magnetic insertions, H_D,B=0 and H_D,B=sigma_x.
Their complete B=0 operators, poles, residues and daughter spectral weights are
IDENTICAL. Their daughter eigenvalue first derivatives also both vanish at B=0.
But the second case has

    Sigma_B(0)=sigma_x/8,
    eigenvalues(Z^-1 Sigma_B) = +/-1/sqrt(85).

The first case has zero response. Direct calculation in the full normalized
zero eigenspace confirms those slopes. This is an exact finite counterexample
to inferring magnetic response from zero-field decay/spectral data alone.
It is NOT two constructed self-consistent BHSM theories, a freedom to fit a
magnetic term, or a proposed physical daughter Hamiltonian.

## 6. Ward conservation is necessary, not sufficient to select a_mu

For antisymmetric sigma^(mu nu),

    q_mu sigma^(mu nu) q_nu = 0.

Thus an additional transverse Pauli vertex can leave the Ward equation
unchanged. The code checks the Clifford identity exactly. This does not add
such a term to BHSM. It prevents (3), by itself, being used as a magnetic-moment
prediction. The full transverse vertex must be obtained from the retained
quantum action, regulator/relative completion and overlap prescription.

Similarly, a B=0 decay spectrum does not determine its field derivative; the
example in section 5 makes this explicit even with full B=0 inverse data.
The ordinary daughter-bubble analogy selects neither that transverse vertex nor
its finite completion.

## 7. Physical pole consumer and what actually remains

At an admitted two-spin physical resonance use the same-domain left and right
null leaves L,R and total energy/magnetic derivatives:

    Z = L S_E R,
    M_a = -Z^-1 L S_Ba R.

These are the existing structural formulas. For an unstable particle, physical
quantities require the appropriate complex-pole residue definition [E2]. No
local free-rest columns or off-shell Clifford coefficient supply that admission.
Use the adopted field, charge, mass and spin normalization before translating
energy slopes into g_mu or F2(0).

The newly identified concrete input is the full measuring-photon insertion
J_full^mu (or equivalently its appropriate total weak-B application), together
with the actual quantum daughter operator and physical sources. The published
frequency-first routine is not that input. Its dQ/dT/H/R/N dependencies must be
completed along the actual physical branch, not replaced by zeros.

The coupling constructor in section 1 can consume physical sections once
available. Section 2 then gives a charge-consistent reduction, section 4 tests
basis artifacts, and section 5 ensures magnetic intermediate transitions are
not lost. These checks target the observable rather than refinements of already
adequate static coefficients. They do not themselves solve formation, choose the
inherited reference, repair the physical outgoing derivative, or pass Maxwell
and all226 original matching rows.

No physical g_mu, a_mu or total uncertainty is evaluated. No measured anomaly,
new field strength, damping rate, sea budget, surface tension or retention
fraction was used. Calibrated G_F/Higgs-mass ancestry and non-V-A discrepancies
of the static background remain explicit. No historical result is overwritten.

## 8. Execution and provenance

Six constructed check groups pass in two byte-identical result files:
- coherent all24 source and its total first derivative;
- finite-transfer Ward identity after Schur elimination;
- complete moving-daughter-frame cancellation;
- exact off-diagonal magnetic spectral counterexample;
- exact transversality of a Pauli tensor;
- exact scalar Schur derivative signs and contacts.

Independent source first differences improve from 3.35e-12 at h=.02 to
1.75e-14 at h=.005; the h=.0025 value is 2.50e-14, retaining observed roundoff.
All values describe constructed finite controls, not physical error enclosures.
No pointwise static inverse has been declared to be a chronological retarded or
quantum operator. No source code/binary archive from the repository was rerun.

[R1] Connected GitHub PR #465, head 70e82fd4dbe5f53ff27ae17f6aaac7a4727c1fde.
https://github.com/ncarberry64/Berger-Hopf-Standard-Model/pull/465

[R2] `src/bhsm/interface/muon_daughter_action_source.py`, blob
49b67487005230d83b94b5af61e628ad18f61e94; complete text inspected through GitHub.
The source defines C=R G L, its supplied-domain firsts and open complex currents.

[R3] `scripts/evaluate_muon_daughter_source_20261016.py`, blob
2e402c92376e2d979bff40e1577f7f0df6f880c5; inspected through GitHub. It states the
static calibrated context and absence of physical modes and outgoing admission.

[R4] Attached `BHSM_daughter_cascade_magnetic_connection_20261017/DERIVATION.md`.
Its Schur/pole/event constructions remain conditional controls, not physical
inputs. The present work extends rather than promotes that package.

[E1] A. N. Kvinikhidze and B. Blankleider, Gauging of equations method. I.
Electromagnetic currents of three distinguishable particles, Phys. Rev. C 60,
044003 (1999), arXiv:nucl-th/9901001.
https://arxiv.org/abs/nucl-th/9901001

[E2] J. Gegelia and S. Scherer, How to define physical properties of unstable
particles, Eur. Phys. J. A 44, 425–430 (2010), arXiv:0910.4280.
https://arxiv.org/abs/0910.4280
