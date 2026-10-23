# Muon birth: numerical E1/C2 reset and first unavailable fermion trace

The actual retained incoming C1/branch23 and outgoing C2/branch24 pair has been recovered and evaluated with `aether_full_reset_action_jacobian.full_reset_residual`. All 57 residual values, original state vectors, normalization inputs, geometric field samples and raw canonical momenta are materialized. The geometric reset norm is **7.64107108345298e-15**, with largest row **5.628594097932515e-15** on the Decimal60 action path.

The first unavailable numerical operand is **INCOMING_C1_E1_FERMION_TRACE**, `g_F^- = Gamma0,E1^- Psi_C1`. It is the incoming tangential fermion/lepton section in the already-owned carrier/spin/gauge/family frame, not the eta radial inclusion or mechanical normal mode. The concrete immediate consumer is `action_extension_global_spin_reset_ae2.transmit_trace(event_trace=g_F^-, reset_lift=U_R)`. The existing enclosure/family transport then consumes that trace. Therefore the complete nonzero physical muon transfer is not identified, and no physical birth energy/KKT/native result is manufactured from this geometric success.

Starting HEAD: `64b51a2cedb7be410251b3fb3c4f942cc148bcc4`. Branch: `codex/muon-parent-maxwell-density-review`. Scientific reference: `524ed90689bd5923c249bba2e699abf627e703cd`. `BRANCH_REALIZATION_TRANSFER_EVENT` and `Sigma_star^mu=Sigma_(P->mu)`, evaluated on the muon child side, remain frozen. This is a value evaluation, not another semantic or family-selector audit.

## Exact retained pair, chart and common-event scope

The source is `artifacts/flagship_integration/BHSM_N12_C2_REFINED_RESET_ROOT_CENTER.npz`, SHA256 `59dd88661b15cbeec96bc19294f9d9c64f754cccbfbc385c32329fa9c864a8fe`. Its `state` contains 196 binary64 values. The forward interpretation is the retained two-sided swap:

```text
incoming C1 / E1^- / branch23 = state[98:196] = original child C_*,
outgoing C2 / E1^+ / branch24 = state[0:98]   = original event E_*,
joint_state = concatenate(incoming, outgoing).
```

The chronology is `E0 -> C1 -> E1=C_* -> C2=E_*`. This uses the retained swap invariance of the double-event locus and its orientation theorem, not an arbitrary coordinate coincidence or right inverse. Each 98-vector is `q37 + velocity37 + multiplier24`; the last 24 encode 12 even lapse and 12 odd shift coefficients. Full decimal values and binary64 hexadecimal representations are saved; no coordinate is refitted.

The same input provides `state_weights[98]` and `branch_reference[61]`. The original normalization coordinates come from `BHSM_N12_FULL_RESET_ACTION_JACOBIAN.npz` and the ordered scale from `artifacts/n12_direct_checkpoint/BHSM_N12_EXACT_ROOT_RESIDUAL.json`: `3.5097287979490443e-06`. State weights are checked identical across inputs. The source NPZ hash is checked against the retained refined-root certificate before evaluation.

The unchanged producer is called at order12, points96, `high_precision_action=True`. Its action, selected line and momentum blocks use Decimal precision60, while trace/Gram normalization and returned residuals remain binary64. The retained reference actually selects incoming index23 and outgoing index24. Their evaluated eigenvalues are approximately `-3.3977039178701237e-23` and `1.3438631609212246e-22` at the stored proof center. These ordered geometric lines are not substituted for the mechanical muon formation mode.

The common-domain digest binds this actual geometric pair, chart, weights, ordering and quadrature. It is explicitly a **retained N12 reset-point identity**, not a complete interacting physical domain identity. The + and - values have no finite temporal displacement. A numerical absolute muon birth time, full-field pairing, fermionic graph values and actual active regular strata are not inferred. The geometric trace maps and opposite-normal fermion graph prescription are recorded separately from their unevaluated physical matter values.

The applicable outgoing C2 positive-duration local-existence certificate is `BHSM_N12_FINITE_TERMINAL_TWO_SIDED_FORWARD_INTERFACE.json`, with explicit outgoing branch24 chronology. The earlier direct persistent-child checkpoint concerns its original branch23 child; it is retained historical evidence, not promoted to a continuation certificate for this swapped outgoing C2 or interacting muon.

## Actual 57-row evaluation

| Row group, zero-based range | Maximum absolute normalized residual |
|---|---:|
| Incoming multiplier constraints, 0:24 | 5.628594097932515e-15 |
| Incoming canonical energy, 24:25 | 2.1353278838997894e-15 |
| Selected event line, 25:26 | 9.680816135581804e-18 |
| Three geometric traces + attachment, whitened 26:30 | 2.323014163086936e-17 |
| Outgoing multiplier constraints, 30:54 | 3.555844229032068e-15 |
| Outgoing canonical energy, 54:55 | 1.85878447001623e-15 |
| Two canonical momentum rows, 55:57 | 1.6174565727540577e-15 |

All individual rows are in the packet; rounded table values are summaries. The norm is `7.64107108345298e-15`. The 4x4 boundary whitening mixes the three original geometric trace coordinates and the attachment coordinate, so raw and normalized values are both preserved. Raw geometric trace maximum is approximately `3.1496e-17`; the raw attachment difference is approximately `-3.4694e-18`.

Raw canonical momenta are

```text
incoming = [-0.4789487515413658,  -0.19295498262193034],
outgoing = [-0.47894875154136635, -0.19295498262193034],
child-minus-event = [-5.551115123125783e-16, 0].
```

The exact retained momentum normalization matrix and normalized two-vector are supplied. These are geometric-action Legendre outputs, not full interacting fermion/gauge/HS canonical momenta.

A binary64-only action path on the same inputs differs from the Decimal60-return path by up to **3.6823765508674276e-11**. This measures arithmetic sensitivity, not a rigorous error enclosure; binary64-only evaluation would obscure the small residual. The retained refined-root action-norm distance upper bound `4.3223310537263596e-15` remains a root-distance certificate and is not relabelled as a component residual bound. No new root, trajectory or continuum convergence campaign was run. Quadrature96, finite retained-order truncation, original-center representation and binary64 normalization remain the explicit numerical scope.

## Concrete fields, attached objects and muon projector

Both sides have same-event Gauss96 samples of `C,A,B,N,beta`, ADM rates, the eta invariant, the response/localization profile and the mechanical connection coefficient. The retained q representation is

```text
u=sum_(k=1..12) q[k] cos(4k chi),
w=sin^2(2chi) sum_(j=0..11) q[13+j] cos(4j chi),
b=sin^2(2chi) sum_(j=0..11) q[25+j] cos(4j chi),
R=R0 exp(q0), C=R exp(u+w),
A=R exp(u+b)cos(chi), B=R exp(u-b)sin(chi),
N=exp(sum m[k-1]cos(4k chi)),
beta=sin(4chi)sum m[12+j]cos(4j chi),
f_eta=chi=rho/2,
sigma=-1/2+2chi/pi-sin(4chi)/(2pi), L_sigma=1-4sigma^2.
```

These are evaluated geometric-action quantities, not independent interacting matter amplitudes. At the retained cap boundary, `A=1.4164337797583075`, `B=1.397800698020681`, quotient base radius `R4=0.9949167164637878`, incoming lapse `1.1185575823583358` and outgoing lapse `0.7006542298207211`. The different lapse values are recorded without asserting a completed physical clock/metric pullback. No exterior spatial M5 parent-bulk packet at step1222 is extrapolated into E1.

The existing muon projector is reused numerically: `Pi_mu=diag(0,1,0)`, charged-lepton slot1, frozen label `(5,2)`, rank1 and idempotence residual0. No family projector is rederived. Actual E1 reset/projector compatibility on a supplied matter state and actual nonzero transported-state norm remain null. A representative 2x2 reset used by an older algebraic certificate is not inserted as the E1 physical lift.

The bound eta zero mode supplies `Psi5=u_eta Psi4` with `u_eta=J^(-1/2)sin(f_eta)/sqrt(I_eta)`. It determines the radial inclusion acting on a supplied tangential section; it does not supply `Psi4_C1(E1^-)`. The fixed family ray and odd-FR rotor ground ray likewise do not evaluate the local carrier/spin/gauge coefficient function at E1. The mechanical normal mode is a third, distinct object.

The numerical inventory explicitly examines the refined reset, muon geometry, radial inclusion, eta collar, source/contact, common-A/operator and finite fermion-body arrays. It records every key, shape, dtype and file hash. The fermion-body cache contains kinetic/current operators and geometry jets but no incoming C1 spinor coefficient vector. Eight retained current derivatives have nonzero Frobenius norms approximately `2 sqrt(2)`; consequently their quadratic values depend on a state and cannot be recovered from the operators alone. No trial spinor is chosen to demonstrate this dependence.

The historical reconstructed N3 zero-classical-field/Weyl amplitudes are documented at their original selected-background scope. They are not an inactivity proof for this interacting branch23/24 E1 transfer. For a valid linear transport, a genuinely zero trace would transport to zero, which cannot pass the requested actual nonzero muon-state check. Zero sector-amplitude records are not promoted to a full spinor vector. Gauge/ghost/HS sectors are not declared inactive just because the 98-coordinate adapter omits their amplitudes.

## Exact missing value and consumer chain

```text
actual incoming fermion solution on C1
  -> g_F^- = Gamma0,E1^- Psi_C1
  -> transmit_trace(event_trace=g_F^-, reset_lift=U_R)
  -> (P_D L_sigma tensor I)(U_R tensor I_F)(I tensor Pi_mu) g_F^-
  -> actual nonzero muon trace and quadratic current/Green/traction values.
```

`g_F^-` is **not present in the examined retained numerical packets or emitted by their attached field reconstructions**. The immediate producer/consumer failure is a missing numerical incoming trace, not an undefined map or generic statement that I_phys is unevaluated. The retained Dirac propagation body requires supplied Cauchy coefficients; the geometry/reset/eta reconstructions emit geometric fields and operators, not those coefficients.

For PEI06, the complete six-sector restriction/dependency ledger is bound, with actual geometry/eta/sigma values and unknown interacting amplitudes explicitly distinguished. For PEI07, both geometric canonical-energy rows and geometric momentum matching have been evaluated. Full parent/event/child conormal stress, dynamic flux, Noether/current balance and active contacts need the same physical state operands; no missing term is filled with zero. The existing sector assembly and graph definitions remain closed. Other later active-field/mixed-block values must still be checked when the first missing trace is available; supplying that trace alone is not claimed sufficient for complete physical transfer.

The opposite-normal Green consumer uses the supplied trace and variations; the full Noether consumer contracts an actual event trace and tractions as `2 Re <Tq,Pi_parent+Pi_child_return+J+C^dagger lambda>`. Knowing the cancellation identity does not evaluate those state-dependent terms at E1. The owned absence of an independent fermion seam density does not set bulk fermion current or all contact jets to zero.

## Energy, KKT and downstream status

The birth event is retained unchanged. `F_E_mu` and `Delta_imp_bulk=<psi_mu^+,(H_impedance-H_bulk,constrained)psi_mu^+>` are null because a complete actual muon state/domain and mechanical formation mode have not been identified from the missing trace. The geometric `E_can` rows are not substituted for this energy condition. No nonzero discrepancy is discarded and no surface is moved.

Physical kinetic normalization, xi_psi, seven-port values, one stationary full-field KKT base, the six derivatives, h_psi, delta_psi, z_psi, r/i jets, cutoff, AE4 heat, relative zeta/eta, R_ind, photon response, paired electron–muon heat and Pauli readout remain unevaluated. This stop is before the physical transfer passes and is not an intentional stop at an available I_phys, h_psi or z_psi.

## Claim and verification scope

| Label | Scope |
|---|---|
| EVALUATED | Actual retained incoming/outgoing vectors, all57 geometric reset rows, field samples, raw/normalized traces/momenta, existing projector idempotence and input/operator inventories. |
| DERIVED | Existing field reconstruction, action and transport relations reused without new semantics or family proof. |
| RETAINED_CERTIFIED | Local orientation/noncontinuation, reset-root and positive-duration child results at their original scope. |
| CONTROL_ONLY | Prior finite demonstrations excluded; no control state replaces the incoming fermion trace. |
| UNEVALUATED | Incoming C1/E1 fermion trace, actual nonzero muon transport, full interacting balance and mechanical/native values. |
| OWNER_DEFINITION_GAP | None reopened. The first unavailable object is a numerical trace value. |

The retained numerical pair evaluates the geometric reset, lapse/shift/eta fields and canonical momenta, and the existing projector is available, but **the incoming C1 fermion trace `Gamma0,E1^- Psi_C1` required by `transmit_trace` is unavailable in the examined operands**. Therefore the physical nonzero muon birth transfer and xi_psi cannot yet be evaluated.

Replay commands are `python scripts/replay_muon_birth_transfer_value.py --out artifacts/muon_birth_transfer_value_20261008/run_1` and the same command with `run_2`. The packet, source manifest and hash receipt are materialized twice. Input identities include all loaded BHSM numerical dependencies. Detailed commands, outputs, hashes, focused checks, publication checks and exact error scope are in [verification.json](../artifacts/muon_birth_transfer_value_20261008/verification.json). The independently retained reset and sector receipts also record their deterministic repeated evaluations.

Focused command: `python -m pytest --noconftest -q tests/test_muon_birth_transfer_value.py`. Output: **33 passed in 1.14s**, exit0. Tests compare actual vectors with original NPZ bytes/hex, all57 rows and raw normalization, actual branch23/24, existing projector, scientific identity and unavailable-trace guards; they do not rerun the high-precision producer or numerical controls. The final replay runs execute that producer separately.

The transfer packet is 494,980 bytes, SHA256 `c351215d0218f1acfc74b0c6d818975e460d694fd1ca5234aad6f3c1f0b24a09`. The manifest covers 241 source/input files and 43 checked retained identities, plus external operator/metadata receipts, and verifies 25 Python citations. Final manifest/product comparison hashes are recorded in verification.json rather than introducing a circular theory/manifest hash dependency.

Publication commands: `python tools/audit_bhsm_status.py --format json`, `python tools/audit_forbidden_claims.py --format json`, `python tools/audit_frozen_prediction_integrity.py --format json`, `python tools/verify_precision.py` and `python tools/audit_public_readiness.py --format json`. Status, forbidden-claim and frozen-integrity checks returned `passed:true`. Repository precision returned `PASS: precision gate verified (1.066e-14 <= 1.000e-13)`; that pre-existing gate does not certify a physical muon prediction or the new reset's continuum error. Public-readiness completion is recorded in verification.json. No retention entry, frozen prediction, historical array, support/cutoff definition, family projector, common-A/eta identity, QED calculation or seam proposal is changed.
