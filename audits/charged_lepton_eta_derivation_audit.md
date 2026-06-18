# Charged-Lepton Eta Derivation

## Problem

The charged-lepton dressing candidate improves precision screens only after fitting `eta_l` from `mu/tau`. This sprint asks whether `eta_l` can be fixed from existing BHSM structure before residual comparison.

## Current eta_l Status

Fitted eta_l: `0.0020443439144236667`
Classification: `ETA_L_STRUCTURALLY_MOTIVATED_NOT_DERIVED`
Lepton precision blocker closed: `False`
Candidate status: `CANDIDATE_NOT_OFFICIAL`

## Candidate Sources Inspected

| Candidate | eta_l | Source | Formula | Rel diff to fitted | mu/tau err | e/tau err | Independent | Derived | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `fine_structure_alpha` | `0.0072973525692838015` | BHSM low-energy fine-structure input | `alpha` | `2.5695327570855624` | `0.025923117134174747` | `0.09349655256944192` | `True` | `False` | Uses a BHSM gauge input, but no lepton-boundary derivation fixes eta_l=alpha. |
| `fine_structure_alpha_over_pi` | `0.002322819465771719` | fine-structure input with one geometric circle factor | `alpha/pi` | `0.13621756563721776` | `0.001391408848579023` | `0.008581814110486348` | `True` | `False` | Independent of lepton residuals and improves both rows in this audit.<br>The repo does not derive the pi denominator from a charged-lepton loop/action. |
| `gauge_alpha_1` | `0.01688686394038963` | geometric gauge screen alpha_1 | `1/(6*pi^2)` | `7.260285278443626` | `0.07152572089544978` | `0.2372093405861738` | `True` | `False` | Uses a supplied gauge screen, not a lepton dressing derivation. |
| `gauge_alpha_2` | `0.03377372788077926` | geometric gauge screen alpha_2 | `2/(6*pi^2)` | `15.520570556887252` | `0.14670241175703894` | `0.4371461079957869` | `True` | `False` | Uses a supplied gauge screen, not a lepton dressing derivation. |
| `gauge_alpha_3` | `0.1182080475827274` | geometric gauge screen alpha_3 | `7/(6*pi^2)` | `56.82199694910538` | `0.4405597330099895` | `0.8768747262354893` | `True` | `False` | QCD-like screen is not structurally scoped to charged leptons. |
| `universal_overlap_width` | `0.07957747154594767` | universal overlap width | `S=1/(4*pi)` | `37.92567732097162` | `0.321360783608164` | `0.7532063181006379` | `True` | `False` | S is already used in bare overlaps; reusing it as eta_l over-suppresses leptons. |
| `overlap_width_per_boundary_sum` | `0.0037894034069498894` | universal width divided by Omega_l+Omega_u+Omega_d | `S/(3+6+12)` | `0.8536036819510298` | `0.008687342524319217` | `0.034411347337609706` | `True` | `False` | Uses boundary targets and S, but no action rule derives this normalization. |
| `alpha_per_lepton_boundary` | `0.002432450856427934` | fine-structure input divided by lepton boundary target | `alpha/Omega_l` | `0.18984425236185407` | `0.0019386530898541747` | `0.010536314984320432` | `True` | `False` | Numerically close to fitted eta_l, but dividing by Omega_l is not derived. |
| `alpha_per_up_boundary` | `0.001216225428213967` | fine-structure input divided by up boundary target | `alpha/Omega_u` | `0.40507787381907295` | `0.004149176527547719` | `0.011363927133818003` | `True` | `False` | Wrong-sector boundary target for charged leptons; diagnostic only. |
| `alpha_per_down_boundary` | `0.0006081127141069835` | fine-structure input divided by down boundary target | `alpha/Omega_d` | `0.7025389369095365` | `0.007207002334149855` | `0.02249515609778464` | `True` | `False` | Wrong-sector boundary target for charged leptons; diagnostic only. |
| `epsilon_alpha` | `0.15705413573343296` | alpha-anchored Higgs/electroweak residual | `alpha^{-1}/(12*pi^2)-1` | `75.82373529490464` | `0.5393187740890936` | `0.9388106756090888` | `True` | `False` | Higgs scale residual is far too large as a lepton dressing eta. |
| `inverse_hopf_gap` | `5.105880692270916e-05` | dimensionless Hopf gap | `1/(64*pi^5)` | `0.9750243554607085` | `0.010016255761995486` | `0.032799257819796514` | `True` | `False` | Gap inverse is independent but too small to repair the warning. |
| `zvirt_log_per_boundary_sum` | `0.033007008598092635` | existing Z_virt^{u,2}=1/2 amplitude and boundary target sum | `log(2)/(3+6+12)` | `15.145526379008418` | `0.14342493493540706` | `0.4293243414688513` | `True` | `False` | Uses existing Z_virt, but Z_virt itself remains not derived and is up-sector scoped. |
| `zvirt_log_per_64pi` | `0.0034474312523851813` | existing Z_virt and Hopf-gap exponent scale | `log(2)/(64*pi)` | `0.6863264679011053` | `0.006990885958747748` | `0.028449336812930916` | `True` | `False` | A geometric coincidence check only; no BHSM rule selects 64*pi here. |

## Rejected Numerical Coincidences

Boundary-normalized or large-scale combinations are reported but not accepted as derivations. In particular, `alpha/Omega_l`, `log(2)/(64*pi)`, and wrong-sector boundary normalizations are rejected unless a BHSM action or boundary rule fixes them independently.

## Best Structural eta_l Candidates

Best independent candidate: `fine_structure_alpha_over_pi`
Best precision-screen candidate: `fine_structure_alpha_over_pi`

`alpha/pi` is independent and structurally motivated by gauge/geometry inputs, and it improves both lepton rows in this audit. It is not derived because the repository does not contain a charged-lepton boundary/action argument that fixes the `1/pi` factor as eta_l.

## eta_l Derivation Status

The fitted eta_l remains fitted from `mu/tau`. The strongest non-fitted candidate is structurally motivated but not derived. No candidate in this inventory closes the lepton precision blocker.

## Consequences For Lepton Precision Blocker

Lepton blocker closed: `False`
Official lepton ratios changed: `False`
Frozen outputs changed: `False`

## Promotion Criteria

- derive eta_l from an action, spectrum, boundary condition, or independently fixed BHSM scale
- pre-register eta_l before lepton residual comparison
- retain improvement for both mu/tau and e/tau
- show charged-lepton scope without altering frozen quark, CKM, gauge, Higgs, or H_T outputs

## Rejection Criteria

- eta_l remains fit from mu/tau
- candidate value is chosen only because it is numerically close to fitted eta_l
- candidate damages the held-out e/tau screen
- candidate requires post-freeze official output changes

## Notes

- The fitted eta_l remains the only value that exactly fits mu/tau by construction.
- alpha/pi is the strongest independent structural candidate in this inventory, but the pi denominator is not derived from the BHSM charged-lepton action.
- Numerically close boundary-normalized candidates are rejected unless a boundary rule independently fixes them.
- The lepton precision blocker stays open until eta_l has an independent pre-residual derivation.
