# Existing dressed-pole engine to charged-lepton invariant

The whole-system integration adds one concrete consumer: three compatible
`universal_dressed_pole.DressedPole` outputs now feed the already-derived
AE3.1 charged-lepton pole invariant, including their complete correlated
covariance. This connects existing mathematical pieces without adding an
action term, coefficient, self-energy, particle assignment, or physical pole.

The implementation is
[`charged_lepton_pole_observable.py`](../src/bhsm/interface/charged_lepton_pole_observable.py).
Its entry point is `charged_lepton_pole_observable(inputs, covariance=...,
covariance_coordinates="log_mass" or "mass")`.
`ChargedLeptonPoleInput` supplies the explicit family role, existing pole,
common variational-domain ID, and common scale-map ID. The fixed spectral
convention is that of the existing universal engine:
`z=m_p^2-i*m_p*Gamma_p`.

## Exact fit and uncertainty coordinates

The existing invariant theorem supplies the heavy/middle/light coefficient
vector `c=(8,-9,1)` and the roles `tau_slot`, `mu_slot`, `electron_slot`.
The consumer evaluates

```text
R = 8 log M_tau - 9 log M_mu + log M_e - 54/pi,
D = exp(R).
```

It forms the two log-mass differences before contraction. Both poles and
the covariance are reordered together by the declared family roles; sorting
by measured masses or assigning a family from a pole magnitude is absent.

For a supplied full log-mass covariance `C_log`, the affine residual has
exact variance `Var(R)=c^T C_log c`. This statement concerns the declared
log-mass random variables, not an approximation to the mean of nonlinear
mass ratios. For a supplied full mass covariance `C_M`, its first-order
delta-method variance is `g^T C_M g` with `g_i=c_i/M_i`. The variance of
`D` is separately labelled first order: `D^2 Var(R)`.

Cross-family covariance entries are retained. They are not replaced with
independent error bars. Because `c^T(1,1,1)=0`, a common multiplicative unit
conversion cannot alter `R`. A covariance component
`sigma_scale^2 (1,1,1)(1,1,1)^T` cancels from `Var(R)` exactly in log-mass
coordinates. The implementation contracts through the two difference rows
before taking scalar variance, preserving that exact common-scale null
direction even for a singular covariance.

The covariance must be finite, real, explicitly symmetric, and positive
semidefinite within a declared machine-roundoff allowance. Zero-variance
rows must vanish. A propagated negative variance within the exported
roundoff allowance is clamped to zero with an explicit output flag. The
standard deviation is a covariance readout, not an outward numerical error
bound or a replacement for action/solver error control.

## Provenance and promotion boundary

Every pole retains the existing engine's admission checks: closed Gate 7,
complete same-action self-energy ledger, convergence, simple isolated pole,
and causal width. Empty producer provenance, malformed numerical records,
incompatible action/background/domain/scale IDs, missing or repeated family
roles, and a different spectral convention are rejected. The wrapper adds
metadata that `DressedPole` does not carry; attaching identifiers here does
not authenticate or select the action, domain, state, or scale producer.

The result is always
`CONDITIONAL_ALGEBRAIC_READOUT_FROM_SUPPLIED_DRESSED_POLES`, with
`current_bhsm_physical_prediction_promoted=False`. No current physical
electron, muon, or tau pole has been supplied. Passing synthetic records
through this consumer exercises the algebra and does not establish physical
pole ownership or full BHSM completion.

This bridge does not reuse the active muon branch's unsquared energy
`Gamma2(E)=B_i+B_f U(E)` as a squared spectral symbol. Its rank-two
Keldysh residue, temporal exterior domain, charge normalization, and
same-clock mass/lifetime conditions have their own owners. Likewise the
current-C2 radial product-Dirac spectrum is not inserted as a physical mass
pole. Compatibility between those operators requires its own proved map.

## Verification and remaining dependencies

Focused tests in
[`test_charged_lepton_pole_observable.py`](../tests/test_charged_lepton_pole_observable.py)
compare the new consumer with the existing invariant witness, preserve full
correlated covariance under family permutation and common unit conversion,
verify the exact shared-log-scale null direction, exercise every inherited
pole gate, reject malformed covariance and mixed provenance, and reproduce
the serialized conditional result byte-for-byte.

The current action-selected global two-point functions, same-domain
self-energies, physical poles, and controlled errors remain upstream. The
quark normalizations and noncentral charged-current embeddings, neutral
rank-three projector and propagation operator, and physical photon/Pauli
normalization remain separate unfinished owners. This executable consumer
removes a downstream integration gap and changes none of those statuses.

Sources:
[existing pole-dressing invariant](ae31_charged_lepton_pole_dressing_invariant.md),
[intrinsic-M4 local lepton action and global pole boundary](ae31_c2_intrinsic_m4_lepton_action.md),
[quark normalization no-go](ae31_c2_quark_yukawa_normalization_no_go.md),
[current charged-current identity/no-mixing theorem](ae31_c2_coexact_su2l_charged_current.md),
[neutral propagation gate](ae31_c2_capture_neutrino_propagation_gate.md).

`FULL_BHSM_COMPLETE = FALSE`.
