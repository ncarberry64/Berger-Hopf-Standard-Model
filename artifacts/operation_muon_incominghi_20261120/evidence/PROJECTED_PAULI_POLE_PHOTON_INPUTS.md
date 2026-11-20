# Projected Pauli route: pole and photon inputs
2026-11-19 focused reuse audit. No orbit/formation rerun.
Pinned main551ce2c8e4e672538e520629b0d4a8962cbba968; muon branch4a650a61a6e0e4cd3674650c399b435c106d66c3.

## Already reusable
- theory/muon_minimum_pauli_readout_20260930.md: one charge-orthogonal derivative <L_u,[Gamma(tu)−Gamma(0)]>/t, not a full vertex reconstruction.
- src/bhsm/interface/ae31_c2_neutral_connection_hessian.py: exact Q_em=T3+Y Higgs-null connection and same-C2 current rotation A_Q=(W3_hat+B_hat)/sqrt2, J_Q=(J3+JY)/sqrt2. This preserves interaction pairing; it is explicitly NOT canonical photon normalization/Weinberg rotation.
- src/bhsm/interface/ae31_c2_local_em_ward_identity.py: local charged Dirac vertex Q_l gamma^mu, family-central charge and exact Ward identity. No canonical photon residue is used.
- src/bhsm/interface/universal_lsz.py: inverse-free unit descriptor residue algorithm for an admitted simple pole; physical action selection is required separately.
- Incoming finite n0 near-charged spin pair and source derivative are available candidate inputs, not admitted physical muon legs.

Primary prefix:
https://github.com/ncarberry64/Berger-Hopf-Standard-Model/blob/551ce2c8e4e672538e520629b0d4a8962cbba968/

## Exact remaining pipeline
1. Same-domain physical charged two-point branch: Gamma2(E*)r=0,l†Gamma2(E*)=0, nonzero l†partial_E Gamma2 r; normalized mode must be action-selected and isolated at the required scope. Source input flag action_selected=True is not a constructor.
2. Same-domain photon direction and physical kinetic response. The neutral-Hessian source explicitly identifies an unrenormalized temporal/spatial residue mismatch and calls for one common Lorentzian Maxwell residue on the Q_em null connection. AE4 supplies a common induced-action OWNER, not numerical current-C2 residue.
3. Project the complete renormalized electromagnetic source derivative onto those legs, including their changes, moving Higgs direction/domain contacts and overlap subtraction once. Apply the already-owned L_u. Control out-of-two-tensor-span remainder and soft-direction agreement.

## Two misleading 'pole' candidates already resolved
source_muon_d5_pole_admissibility.py derives geometric cap Frobenius exponents+1/−2 and regular-range compatibility. This selects admissible radial behavior, NOT a particle energy pole.
pole_germ_reference.json evaluates an actual finite declared radial action E derivative, but stage0 full null rows≈8.86e−7 and candidate residue null rows≈4.09e−4 fail the stored null guard. Source-envelope energy contacts cancel in represented physical Cauchy trace and are not a spectral residue. This does not prove current spin splitting is arithmetic or require a degenerate pair in a background; it only prevents recycling that saved candidate as an admitted pole.

native_photon_transverse_normalization.json is n1 geometric transverse/gradient decomposition at a different saved radius, expressly not LSZ. It cannot normalize the present n0 curl2 source by relabeling.

## Potential shorter normalization check, strictly conditional
If the SAME physical projected vertex factorizes into a common scalar normalization Z times the two on-shell tensors,
Gamma_raw=Z[D f1+P f2],
then charge normalization gives F2=f2/f1, and the common scalar external factors cancel. Equivalently divide the raw Pauli derivative by the raw Dirac coefficient at zero transfer, after factoring the known signed charge. Thus absolute external-factor values need not each be known independently if common factorization is established.
This does NOT cancel unknown mode shapes, tensor-valued residue mixing, moving external-state derivatives, non-Lorentzian temporal/spatial mismatch, or uncomputed quantum vertex. It is a testable simplification, not permission to set the photon residue to1. The source's current mismatch is precisely why scalar factorization cannot yet be assumed.

## Minimum completion request
Seek the actual physical two-point branch and the Q_em-projected kinetic/source jet needed for common scalar normalization or its failure. Then compute the single normalized Pauli derivative. No full formation history or orbital calibration is logically required by this route. No physical F2 was evaluated in this audit.

