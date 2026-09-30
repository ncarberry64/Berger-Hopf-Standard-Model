# Muon magnetic response: derivation from the retained BHSM action pieces

Date: 30 September 2026. Classification: exact conditional readout reduction
and local tree result; no physical quantum anomaly is supplied. This analysis
uses existing completion obligations and adds no gate or action term.

## What the existing equations determine

The current-C2 charged-lepton action supplies the local vertex
`Gamma_Q^mu = Q_l gamma^mu`, with `Q_l = -I`, and an inverse tree operator
`S_l^-1 = slash(p) - M_l`. Since `[M_l,Q_l]=0`, direct subtraction gives

`q_mu Gamma_Q^mu = Q_l S_l^-1(p+q) - S_l^-1(p) Q_l`.

This is the existing three-family Ward identity. The minimal local vertex has
no Pauli tensor; its Pauli coefficient is exactly zero. After factoring out
the electric charge, `F1=1`, `F2_tree=0`, hence `g_tree=2` in the positive
magnitude convention. The source witness instead leaves `Q_l=-1` inside F1;
these charge conventions must not be mixed. This tree statement is not the
physical quantum-corrected muon magnetic moment.

The charge-normalized on-shell vertex is

`Gamma_R^mu = D^mu F1(q^2) + P^mu F2(q^2)`,
`D^mu=gamma^mu`, `P^mu=i sigma^(mu nu) q_nu/(2m_mu)`.

Antisymmetry proves `q_mu P^mu=0`. Therefore adding `c(q^2)P^mu` leaves the
Ward contraction unchanged for every c. This is a mathematical demonstration
that the local charge identity does not select the quantum magnetic
coefficient; it is not a claim that the full BHSM action can never select it.

## Deriving the smallest numerical readout

Take nonzero transfer on a physical on-shell branch with independently
normalized external states, and flatten the two tensors in the same fixed
inner product used by the existing form-factor implementation. Define

`P_perp = P - D <D,P>/<D,D>`

`L_P = P_perp/<P_perp,P_perp>`.

Then `<L_P,D>=0` and `<L_P,P>=1`, so

`F2(q^2) = <L_P, Gamma_R(q)>`.

The existing observable is therefore

`a_mu = lim_(q^2 -> 0) <L_P(q), Gamma_R(q)>`,
`g_mu = 2(1+a_mu)`.

For an already normalized magnetic moment in SI units, use
`mu = g_mu Q e hbar/(4 m_mu)` for spin 1/2. That conversion additionally
requires the physical mass and charge scale; a geometric label does not
supply them.

This linear functional is sufficient for the Pauli *coefficient* once the
on-shell two-tensor decomposition has been justified. It is unnecessary to
retain every finite component of Gamma merely to extract F2. It remains
necessary to control components outside the two-tensor span and verify the
charge normalization. The accompanying implementation returns that remainder
rather than discarding it. At exactly q=0, P vanishes: a rank-deficient
projection is not a zero-momentum result. One needs a controlled limiting
coefficient (or the corresponding derivative at zero), not a direct solve on
the zero tensor.

The needed derivative can itself be reduced. In the charge-normalized,
on-shell two-tensor representative, choose a fixed nonzero transfer direction
u and write `q=t u`, so `P(t)=t P_u` at fixed physical rest mass. Construct
`L_u` from D and P_u by the same orthogonalization. Exactly, at nonzero t,

`<L_u, Gamma_R(t u)> = t F2(t^2 u^2)`.

Consequently the smallest soft-transfer numerical object is the **one scalar
directional derivative**

`a_mu = lim_(t -> 0) <L_u, Gamma_R(t u)-Gamma_R(0)>/t`.

The Dirac/charge contribution cancels before differentiation, so this identity
does not require every component of the full vertex to have a regular Taylor
series. It requires the physical Pauli limit to exist and the stated on-shell
decomposition to hold. A calculation performed on spinor-sandwiched amplitudes
must include their external-state kinematic derivatives, or reduce to this
covariant representative first. Arbitrarily differentiating an off-shell
vertex does not meet these conditions. Agreement between allowed directions,
normalization and control of the omitted tensor remainder belong to the
existing physical readout obligation.

This refines the target from a full vertex function or full tensor jet to one
projected soft-transfer derivative, plus its physical-domain and error
justification. The supplied local tree vertex is independent of q and gives
zero for this derivative. Its quantum value requires evaluation of the same
projection of the quantum action's vertex; no status flag is used to set it.

Linearity permits summing the projected contributions from the existing
action-owned diagram ledger, preserving their shared regulator and signed
cancellations. It does not permit omitting diagrams, inventing their finite
coefficients, or selecting a subtraction by agreement with experiment.

## Existing obligation map and mathematical necessity

| Existing obligation / implementation | Quantity needed here | Why necessary |
| --- | --- | --- |
| Physical muon mode and LSZ external states (`universal_lsz.py`) | pole, residue, normalized mode, rest-frame mass | Defines the on-shell state and P tensor |
| Normalized photon and charge identity (`ae31_c2_local_em_ward_identity.py`) | physical photon coupling and F1(0)=1 after factoring charge | Fixes the normalization of the magnetic response |
| Same-action loops and renormalization (`universal_loop_renormalization.py`) | projected finite vertex, canceled poles, complete contribution ledger | Selects the coefficient invisible to the Ward contraction |
| Existing precision form-factor readout (`universal_precision_form_factor.py`) | controlled q²→0 Pauli coefficient and decomposition remainder | Defines a_mu rather than a finite-transfer proxy |

No full incoming-history reconstruction is required by this algebra alone.
If a state/vertex operand depends on incoming history, its action-sufficient
projection must be derived or bounded through that dependence. The Pauli
reduction does not prove state independence. It also does not automatically
remove the separate force/root/Hessian/persistence obligations already in
the completion definition.

## Operand search and outcome

Inspected the current action's local Ward/Pauli witness, the universal
form-factor and renormalization implementations and their tests, the recovered
full-corpus muon dependency, and the historical action-owned G2/C3 packet.
Here G2/C3 denotes geometric/group structure, not a muon g−2 calculation.
The reference muon moment in the museum is CODATA input. Values such as
`0.00123`, `0.002`, and `0.25` in the precision tests are synthetic supplied
coefficients; the tests recover them rather than derive them from BHSM.
The corresponding local files in the main scientific, engine-integration,
full-field, canonical-recovery and cross-resolution workspaces supplied no
new numerical renormalized muon vertex.

Thus the established action supplies the local tree result and the exact
readout above, but the inspected work does not supply the projected finite
quantum vertex on normalized physical states. No numerical physical a_mu is
derived in this audit. This is an unresolved computation, not a failed
comparison with experiment, and not a declaration that BHSM is incapable of
predicting it. Inserting the QED Schwinger term or a measured anomaly without
deriving the required BHSM photon/lepton limit would not complete this task.

## Reproduction and sources

Run `python -m pytest -q tests/test_muon_pauli_sufficient_readout.py
tests/test_universal_precision_form_factor.py` from the repository environment.
The tests compare the reduced functional with the existing complex
least-squares readout, retain out-of-basis remainders, reject a vanishing
Pauli basis, and re-evaluate the local action identity.
An additional algebraic control checks the soft-transfer scalar derivative
while varying an arbitrary Dirac term; these synthetic coefficients test the
reduction only and are never treated as BHSM predictions.

- [Local action derivation](ae31_c2_local_em_ward_identity.md)
- [Recovered muon dependency](../docs/BHSM_NORMAN_SCHOOL_FULL_CORPUS_RECONSTRUCTION.md#muon-f20-dependency)
- [Existing definition of done](../docs/BHSM_1_0_DEFINITION_OF_DONE.md)
- [Existing form-factor implementation](../src/bhsm/interface/universal_precision_form_factor.py)
- [Reduced numerical readout](../audits/muon_pauli_sufficient_readout.py)
