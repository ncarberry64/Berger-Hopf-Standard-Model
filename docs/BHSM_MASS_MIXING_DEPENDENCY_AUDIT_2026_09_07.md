# BHSM mass and mixing dependency audit — 7 September 2026

## Scientific result

The retained charged-lepton construction yields a conditional, scale-free
tree relation. It does not yet evaluate the corresponding physical pole
relation. The current quark response supplies neither absolute Yukawa
normalizations nor physical mixing. The stationary Einstein–Cartan candidate
cannot fill those gaps on the retained nonzero spin-source mode: that mode is
outside its action domain. These are separate dependencies, not quantities
that additional transverse-response shards can determine by themselves.

This audit uses the existing AE3.1 action attachments and mode ledger. It
does not change an action, choose a regulator, or infer a physical state from
experimental masses. `FULL_BHSM_COMPLETE = FALSE`.

## Exact tree statement and its physical test

In the supplied heavy, middle, light charged-lepton slots, the retained
`(K,q^2)` values are `(0,0)`, `(35,1)`, and `(99,9)`. From

```text
m_f = M_common exp[-(K_f+(a^2-1)q_f^2)/(4 pi)]
```

the combination eliminates both `M_common` and `a`:

```text
R_tree = log(m_e/m_tau)-9 log(m_mu/m_tau)-54/pi = 0.
```

This cancellation is exact for the admitted ledger. It does not independently
select that ledger or establish the global interpretation of each state.
For positive dressed masses `M_f=Z_f m_f`, direct substitution gives

```text
R_pole = log(Z_e)-9 log(Z_mu)+8 log(Z_tau),
D = exp(R_pole) = Z_e Z_tau^8/Z_mu^9.
```

Here `Z_f` describes an effective mass shift, not necessarily a wavefunction
renormalization. The frozen post-derivation comparison requires
`R_reference=0.05880357568422312`, or `D_reference=1.0605668991516508`.
Those values are a later test of a calculated operator, never its fit inputs.
A common multiplicative rescaling cancels. An additive or nondiagonal
self-energy is not excluded by this restricted cancellation theorem.

The physical-promotion test is to derive the state, two-point operator,
renormalization prescription, and mass readout from the same declared action
and domain; calculate or bound `D` without using its reference target; then
compare with the frozen data, propagating theory and reference uncertainties.
The existing identities alone give no finite physical error bound on `D`.

Sources: [tree theorem](../theory/ae31_charged_lepton_scale_free_sum_rule.md),
[dressing invariant](../theory/ae31_charged_lepton_pole_dressing_invariant.md).

## Dependency table

| Quantity | Present result | Missing action-owned operand | Promotion criterion |
|---|---|---|---|
| Charged-lepton tree ratios | Exact conditional sum rule; common scale and squashing cancel | Independent physical mode identification and global readout | Demonstrate that the action-selected states realize the admitted slots |
| Physical charged-lepton masses | Required dressing combination is specified | Global state, dressed two-point function, self-energy or equivalent pole mechanism, and renormalization prescription | Calculate the physical mass readout and `D` with controlled uncertainty before comparison |
| Up/down Yukawa normalizations | Within-sector ratios have normalization nullity two | Domain- and trace-fixed up/down parent third variations | Evaluate both vertices and their canonical residues without copied historical coefficients |
| Relative quark-channel direction | A kinetic normalization alone leaves a direction ambiguity | Same-domain channel Hessian and physical Higgs identification, or a proved equivalent source | Select a physical direction from the action rather than an assumed angle |
| Charged-current mixing | Common family response basis gives `V_response=I3`, `J_response=0` | Family-noncentral dressing of the left-handed up/down embeddings or an equivalent mixed second variation | Derive mass-basis embeddings and their charged-current matrix element with fixed normalization and state conventions |
| Einstein–Cartan LR contribution | Exact local interior kernel; global stationary-domain obstruction on the retained source | No admissible repair established within the fixed candidate and mode | A finite stationary solution must follow from the declared action and preserve the required state content |
| Photon-dependent radiative observables | Isolated frozen trace has no zero on the reference Maxwell shell | Physical propagator, global state, and compatible gauge/vertex identities | Derive the physical electromagnetic two-point and vertex objects before a radiative prediction |

The missing quark vertex owners are explicitly

```text
P_u delta^3 S_parent/(delta bar(Q_L) delta H_tilde delta u_R) P_u,
P_d delta^3 S_parent/(delta bar(Q_L) delta H       delta d_R) P_d.
```

Gauge permission for these terms does not determine their coefficients.
Likewise, a noncentral response is not by itself a physical CKM matrix: the
action-selected states, kinetic normalization, and current readout must agree.

Sources: [quark normalization](../theory/ae31_c2_quark_yukawa_normalization_no_go.md),
[channel direction](../theory/ae31_c2_quark_hs_direction_no_go.md),
[charged current](../theory/ae31_c2_coexact_su2l_charged_current.md),
[EC domain](../theory/ae32_c2_einstein_cartan_lr_action.md),
[photon audit](../theory/ae3_c2_photon_symbol_audit.md).

## Review and resource decision

The first three critique-sprint items now have an explicit adjudication:
the photon inference is corrected while its isolated route remains rejected;
the EC stationary-domain rejection is independently checked; and the mass
and mixing gaps are stated as identifiable operators. None is a physical repair.
The bounded next research target is the regular AE3.1 non-EC fermion/Higgs
two-point owner. The [chiral Green-domain theorem](../theory/ae31_c2_chiral_green_domain.md)
already assembles the first-order lepton operator on the reset-glued domain
and establishes advanced/retarded Green existence on each finite-core history.
The operator and that seam must not be rebuilt. The outstanding operands are
selection or maximal continuation of the physical history, selection of a
compatible state covariance, and an evaluated dressed kernel. A causal
existence theorem does not select that quantum state or define a global
frequency pole on a time-dependent history. Record the missing specification
before evaluating a self-energy; do not choose one using `D_reference`.

The [Hadamard-state class](../theory/ae31_c2_fermion_hadamard_state_class.md)
is already proved nonempty member by member, and
[reset transport](../theory/ae31_c2_reset_hadamard_transport.md) already maps
admissible covariances bijectively. Moreover, the retained
[fixed-history nonuniqueness result](../theory/ae31_c2_fixed_history_state_nonuniqueness.md)
exhibits distinct compatible pure covariances even after a history is fixed.
The remaining datum is one action-selected Cauchy covariance `C`, satisfying
`0<=C<=I`, self-dual CAR reality, the Hadamard condition, and reset/family
compatibility. Closing the history alone does not select it. No adiabatic
order, temperature, or Bogoliubov angle is supplied by this audit.

The [lepton/composite mixing calculation](../theory/ae31_c2_lepton_composite_mixing_structure.md)
also already fixes the singular Hadamard family direction proportional to
`Y_l`. Its finite family coefficients remain covariance dependent. That
singular local result cannot supply the missing finite physical normalization.
For the quark branch, the same source identifies a common parent odd
endomorphism or an independently derived nonzero gap as the missing link;
the scoped vector-gauge chirality obstruction must be respected.

An academic review can assess the conditional tree identity, the photon
scope correction, and the domain obstruction from their explicit hypotheses.
This is an internal audit packet, not evidence of independent review or
novelty. A literature comparison and external technical review remain open
before a journal novelty claim. The flagship manuscript must retain these
counterresults alongside any later positive result.

The existing six-worker signed-response campaign continues under its existing
budget. Its certificates address their own numerical operators; they cannot
replace missing mass, state, or action maps. Only compatible validated outputs
should enter the existing Museum engines. No photon mass, physical CKM matrix,
or fitted dressing is published to those engines by this audit.

## Initial literature comparison

The available causal Green theorem uses established mathematics rather than
a new BHSM existence principle. Christian Bär's
[Green-hyperbolic operators on globally hyperbolic spacetimes](https://arxiv.org/abs/1310.0738)
studies advanced and retarded operators, including Dirac-type examples.
The BHSM burden is to verify the specific geometry and operator hypotheses
and then evaluate the required state-dependent physical object.

State selection also has substantive prior constraints. Fewster and Verch's
[Dynamical locality and covariance](https://arxiv.org/abs/1106.4785)
proves a no-go for covariantly preferred states across all spacetimes under
dynamical locality and additional assumptions. Those hypotheses have not
been established for BHSM here; the theorem is not applied as a BHSM no-go.
It does show why a preferred state cannot simply be treated as a generic
consequence of covariance. A specific state prescription needs its own
scope and justification.

Our algebraic assessment of the lepton identity is likewise limited:
eliminating two common directions from three log masses is elementary linear
algebra. The potentially substantive BHSM content is the action provenance
and independent selection of its discrete ledger, and any subsequent physical
dressing prediction. This initial comparison establishes context, not priority
or a completed literature review of geometric flavor models.

## Reproduction

The EC materializer accepts an optional output path so checks can preserve
the retained report:

```sh
python scripts/materialize_ae32_c2_einstein_cartan_lr_action.py --output tmp/ec-audit.json
python -m pytest -q tests/test_ae32_c2_einstein_cartan_lr_action.py
python -m pytest -q tests/test_ae31_charged_lepton_scale_free_sum_rule.py tests/test_ae31_charged_lepton_pole_dressing_invariant.py tests/test_ae31_c2_coexact_su2l_charged_current.py -k 'not materialized'
```

The second command includes twice-materialization and unchanged-source-report
checks. The third runs the scientific assertions while excluding the three
legacy materialization tests that write into tracked artifact destinations.
The combined audit run passes 42 tests with those three deselected. The EC
power thresholds and leading geometric coefficient are checked symbolically;
the historical cutoff rows remain numerical diagnostics.
