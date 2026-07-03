# CKM-Relative Current Normalization Kill Screen v4.8

Verdict: `CKM_RELATIVE_CURRENT_NORMALIZATION_BLOCKED`

Status: `WEAK_LAMBDA_TO_ALPHA2_BRIDGE_BLOCKED`

## Kill-screen doctrine

BHSM v4.8 blocks the CKM-relative weak-coupling bridge at the current-normalization gate. The CKM artifacts may encode relative mixing geometry, but they do not currently derive c_rel²=4π or attach a 4π relative angular measure to the charged-current inner product. Therefore λ_2 remains a conditional spectral covariance candidate and is not derived as physical α_2. The v4.7 `ACTION_ATTACHMENT_BLOCKED` result remains in force.

## Weak bridge

The proposed weak-only bridge is

`Amplitude_ab = sqrt(λ_2) c_rel V_ab`,

`α_2 = [c_rel²/(4π)] λ_2`,

with `λ_2=2/(6π²)`. It closes only if an action-backed current normalization proves `c_rel²=4π`. The artifact-backed charged-current coefficient form remains `C_CC=g2_BH V_ab/sqrt(2)`; the `1/sqrt(2)` convention is tracked separately and is not absorbed into `c_rel`.

## Proposition audit

| Proposition | Result | Reason |
|---|---|---|
| A: CKM is relative charged-current geometry | Conditional | A bounded cross-sector transport target exists, but the transport space and identification theorem remain open. |
| B: transition space is `S²`, `CP¹`, or `SU(2)/U(1)` | Unsupported | No CKM artifact defines this pairwise geometry. |
| C: relative measure has volume `4π` | Unsupported | The boundary measure is symbolic and its absolute normalization remains open. |
| D: current inner product fixes `c_rel²=4π` | Unsupported | No same-term measure/coefficient attachment exists. |
| E: `α_2=[c_rel²/(4π)]λ_2` | Conditional identity | It localizes the required normalization but is not action-derived. |
| F: `α_2=λ_2` | Blocked | `c_rel²=4π` is not derived. |
| G: action-derived `g2_BH` | Open | `OPEN_MISSING_G2_BH_ACTION_SOURCE`. |
| H: CKM coefficient value | Open | The form `g2_BH/sqrt(2)` does not derive its value. |
| I: CKM exponent | Not derived | `CKM_EXPONENT_NOT_DERIVED`. |

## Route audit

1. **Existing CKM relative geometry:** conditional transport candidate only; no absolute current norm.
2. **Pairwise SU(2) transition:** unsupported analogy; no derived `CP¹/S²` transition space.
3. **Global CKM manifold:** no action-selected manifold or volume; a unitary matrix is not a `4π` measure.
4. **Charged-current coefficient convention:** `g2_BH/sqrt(2)` is artifact-backed as a target form; its factor is not `c_rel`.
5. **Inner-product normalization:** CKM overlap/unitarity is dimensionless and does not provide an absolute `4π` current norm.
6. **Kill screen:** blocked; v4.7 remains in force.

## Minimal unadopted principle

The CKM Relative S² Current Normalization Principle would assert that each physical charged-current transition is evaluated on an `S²/CP¹` relative angular space whose current norm satisfies `c_rel²=4π`. With this principle, the weak bridge is coherent. The repository does not contain, adopt, or derive this principle.

## Hindsight

**Validated:**

- The bridge equation `α_2=[c_rel²/(4π)]λ_2` is localized.
- CKM-relative current normalization is the exact proposed blocker.
- The bounded CKM term is a cross-sector charged-current target.
- The independent `1/sqrt(2)` charged-current convention is preserved.

**Invalidated / downgraded:**

- CKM matrix entries or unitarity do not fix absolute weak-current normalization.
- A normalized overlap `V_ab` does not supply `c_rel²=4π`.
- The area of a formal `S²` analogy is not a current-normalization derivation.
- Arithmetic from `λ_2` cannot derive `g2_BH` or the CKM coefficient value.

**Still open:**

- action-derived CKM-relative current measure;
- `c_rel²=4π`;
- `α_2` action derivation;
- `g2_BH` action source;
- CKM coefficient value and exponent;
- physical running and full BHSM completion.

## No-go protection

- The numerical value of `λ_2` does not imply `α_2=λ_2`.
- `4π=Vol(S²)` does not establish that CKM current geometry is `S²` or uses its unnormalized area measure.
- The CKM matrix does not supply an absolute current normalization.
- The charged-current `1/sqrt(2)` convention is not double-counted.
- `g2_BH`, CKM value/exponent, running, and full completion remain open.
