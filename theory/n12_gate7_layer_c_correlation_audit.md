# Interval-13 Layer-C correlation audit — 24 September 2026

The Layer-B checkpoint `baf41b96` remains frozen. Its eight-cell complete
physical-tube cover, unchanged radii, descriptor, positive normalization,
handoffs and maximum self-map bound 0.704104 are reused by receipt. Layer A
remains closed at `452c80a7`. This audit neither reopens either proof nor
evaluates intervals 14–18. No physical budget is debited.

**Result:** known linear incidence/output correlations can be recovered from
the retained operands. The full shared mixed normalization graph cannot be
recovered from the saved final rate balls. The resulting isolated upper
bounds are approximately 8.023631757973573e15 and 1.5483054042660948e18.
These are enclosure diagnostics, not global kappas, physical lower bounds,
or a completed Layer-C certificate. Classification remains
`SIGNED_CORRELATION_LOST_IN_LAYER_C_REMAINDER_ASSEMBLY`.

## First loss and dependency ledger

References below identify the unchanged producers at `baf41b96`.

| Stage | Retained representation | Dependency loss |
|---|---|---|
| Endpoint perturbation directions | Signed 99×75 maps; two endpoint groups | None in the map itself. |
| Endpoint rates and DF imported into incidence | Uniform value/DF interval balls | State dependence on common physical theta was already enclosed upstream. These are not Taylor coefficient models. |
| HS midpoint first incidence | Signed 99×150 matrix `(I/2 ± h DF/8) E_side` | Matrix composition preserves direction coefficients until the next line. Interval DF coefficients already lack their theta dependence. |
| Physical direction | Independent zero-centered component balls | **First explicit destructive support in the current rate producer:** `derive_n12_gate7_inherited_site_rate_jet.py:40–43`, `direction_support` and `direction=[arb(0,direction_support(...)) ...]`. The shared endpoint direction symbols disappear. |
| Primal eigenline, response, state | `eigenpair_box`, `response_box`, `raw_domain` balls | Imported objects have no common theta coefficient namespace. |
| First eigenline/response derivatives | Signed coefficient matrix times direction map, then component supports | Line 72 repeats the destructive support operation. |
| Mixed eigenline and mixed response | Complete signed formulas evaluated on balls | Implicit solves and correction balls lose cross-component and repeated-argument identity; all border terms remain included. |
| Unnormalized physical rate, C/J descriptor | Interval jets on the already boxed inputs | Moving-leg terms are included, but common dependencies cannot cancel exactly. |
| Positive normalization | `physical_ball_rate_jet.py:20–37`: component norm upper, positive reciprocal interval, then combined quotient expression | Numerator/norm identity is relaxed. The code combines the signed five-term expression; it does **not** support five separately saved terms. Earlier boxing still destroys their correlation. |
| Normalized rate serialization | 99 midpoint/radius pairs for each value/u/v/uv jet | `derive_n12_gate7_inherited_site_rate_jet.py:95–100` discards `psi`, `response`, `C`, `J` returned by `complete_rate`. Unnormalized jets and parameter coefficients are not serialized. |
| HS second incidence | `m_uv=h(H0−H1)/8` then `DF_m m_uv` balls | `assemble_n12_gate7_local_tube_remainder.py:65–68` repeats the same endpoint Hessians in incidence and direct terms after enclosure. |
| Booked LL/LT subtraction | Independent zero-centered output row balls | Lines 92–93 erase signed output-row and shared cross-endpoint coefficient dependence. |
| Causal transport and output | `G*source`, then `eᵀ value`, then `value−e longitudinal` | Lines 98–100 box each stage; longitudinal subtraction repeats an already enclosed value. No early scalar causal-map norm is used here. |
| Kappa | Absolute component support, Euclidean norm, maximum over nodes, frozen-map error | Lines 101–107 are scalar suprema after projection. They are isolated interval contributions over all 357 destinations. |

The first explicit directional support is therefore **before normalization**.
There is also earlier inherited state boxing; locating line 43 does not mean
everything upstream remains a shared model.

## Normalization: available identity and missing operands

The improved frozen rate jets use site-specific norm lower bounds, not the
global physical-tube lower bound 3.0478007960959285e-8:

| Site | Actual norm lower bound used | Retained primal border lower bound |
|---|---:|---:|
| Endpoint 13 | 12001019/34359738368 ≈ 3.4927562228403986e-4 | 3.4899275608485305e-4 |
| Actual HS midpoint 13 | 763672499/2199023255552 ≈ 3.472780458650959e-4 | 3.470028359047165e-4 |
| Endpoint 14 | 189871889/549755813888 ≈ 3.4537495412223507e-4 | 3.4509010143607036e-4 |

The positive border bounds were read from the frozen `response_box` arrays,
with exact outward rational endpoints saved in `inventory_first.json`.
No response was recomputed. Thus common-border cancellation is applicable
algebraically on these same certified site domains.

For `nu r = U`, retain one shared object and use

```
r_u  = (U_u  - nu_u r) / nu
r_v  = (U_v  - nu_v r) / nu
r_uv = (U_uv - nu_uv r - nu_u r_v - nu_v r_u) / nu.
```

These identities are equivalent to the combined quotient formula. Merely
evaluating them on independent balls does not restore the lost identity.
The stronger existing common-border construction is
`shared_complete_rate_jet.coupled_rate`: with `t=s/b`, `k=psi+t h`,
`psi·psi=1`, `psi·h=0`, `b>0` and metric weights `w_i>=1`,

```
Q = 1 + sum_i (w_i²-1) k_i² + t² (h·h+c·c) >= 1,
r = (t c, w k, C+t J) / sqrt(Q).
```

This cancels the positive common `b` before differentiation. Its complete
first/mixed recurrence and all moving-leg assignments already exist and
were not modified or rerun on a physical domain. A new calculation must
keep `psi,h,b,s,c,C,J` and their value/u/v/uv jets on one physical parameter
space, with the normalization/orthogonality identities and their derivatives.
It must not manufacture coefficient identities from final interval balls.
The current first-order Taylor class also puts higher-order products into
remainder bounds; cancellation of those products requires combination before
that truncation, or retained higher-order coefficients/a common expression graph.

## Linear recovery possible without new action evaluations

Write `A=DF_m`, and let `P` already include the frozen inverse/test map,
causal map and longitudinal or transverse output projection. The negative
HS residual derivative, before a Taylor half factor, has the identity

```
P h/6 [H0 + 4(Hm + A h/8 (H0-H1)) + H1]
 = (hP/6 + h²PA/12) H0 + (2hP/3) Hm
   + (hP/6 - h²PA/12) H1.
```

`shared_hs_output_operator.py` combines these coefficients before multiplying
the three retained Hessian balls. Each destination uses `P=eᵀGB` or
`P=(I-eeᵀ)GB`; the projection does not assume a floating-point axis has exact
unit norm. Signed causal matrices are composed before leaf support. Booked
cross-endpoint LL coefficients `Q01+Q10` are combined before support; LT
output matrices are projected before their row/operator bounds.

The final estimate still adds a bound for booked LL/LT to the mixed-rate
bound: those functions' common physical parameters are not available here.
It is explicitly **partial correlation recovery**, not the requested full
shared remainder. It retains all 99 outputs, non-affine second incidence,
357 destinations and the frozen causal-map perturbation lemma.

## Term dominance

Values below are classwise isolated bounds normalized by the unchanged
longitudinal/transverse radii, before the common frozen-map error. Classes
are diagnostic counterfactual enclosures, **not a disjoint decomposition**
of kappa; maxima may occur at different nodes. “New” retains only the known
linear correlations described above, not the missing nonlinear correlations.

| Retained class | Old L | New L | Old T | New T |
|---|---:|---:|---:|---:|
| Direct endpoint rates | 1.7078e9 | 8.7739e8 | 1.6466e12 | 1.8037e11 |
| Midpoint state outputs 0–97 | 2.0178e15 | 3.4664e14 | 2.0392e18 | 1.3787e17 |
| Midpoint descriptor output 98 | 1.1093e16 | 7.6755e15 | 1.0558e19 | 1.4239e18 |
| Non-affine midpoint second incidence | 2.6875e12 | 1.3526e12 | 2.5939e15 | 2.8042e14 |
| Booked LL/LT | 7.6004e-5 | 5.8314e-6 | 7.5066e-2 | 1.1117e-3 |
| Complete bound including map error | 1.3113695368730564e16 | 8.023631757973573e15 | 1.2540364054668333e19 | 1.5483054042660948e18 |

The reductions are approximately 1.63 and 8.10, not many orders of magnitude.
The new map-error additions are 1.0049986530060426e11 and
4.7527942475443555e13. The saved midpoint mixed descriptor ball has absolute
upper bound 12.52895425260067, while its 98-state mixed norm is
24028886.739496663. The descriptor nonetheless dominates after the frozen
test/inverse/causal/output maps. This identifies the dominant **transported
enclosure row**, not an irreducibly large action term.

| Requested attribution | What can be established from saved data |
|---|---|
| Normalization denominator relaxation | Actual lower bounds above are known; internal numerator/norm jets are missing, so no separate numerical attribution or fully correlated replacement is justified. |
| Mixed eigenline | Included in the saved final balls; its mixed model was discarded. No separate contribution is identifiable. |
| Mixed response | Same limitation. |
| Descriptor | Dominant final midpoint output row as quantified above; its C/J moving-leg and normalization subterms cannot be separated from that ball. |
| Projected output | Old/new table measures composition before projection/support, together with other known linear recovery. It is not an additive physical source. |
| Causal-map norm | The original uses signed matrix products, not a scalar map norm at every step. The frozen map-error gain is about 8.89577e-6. |
| Cellwise absolute summation | Absent in the old HS remainder. Both old and new use the three HS evaluation sites, not eight independently summed residuals. |

The eight cells cover one time domain; they are not eight additive HS
residuals. For a separately derived dense-time integral, local contributions
must have disjoint integration pieces or a partition of unity and use the
same endpoint parameters. Shared boundaries have measure zero. No such
integral is substituted for the frozen discrete HS ledger in this audit.

## Retained data boundary and exact next calculation

`inventory_first.json` records the inspected files and hashes. The endpoint-19
mixed response and complete-rate certificates contain shared models, but
have endpoint-19 authority only. The September-19 endpoint-14/midpoint-13
archives contain first-order covector residual proposals; their own `missing`
field names the absent complete output correction and endpoint-to-midpoint
joint graph. Their midpoint uses an additional 99-coordinate box group.
They do not supply the required full mixed interval-13 model.

The interval-13 evaluator's action cache exists only in memory
(`derive_n12_gate7_local_ball_rate_jet.Evaluator.cache`). Final rate receipts
retain counts and final balls, not the cache, mixed implicit jets, C/J jets,
unnormalized jets or shared coefficient graph. Many different functions have
the same final interval enclosure; inversion of this serialization cannot
identify the missing correlations.

A full certificate therefore needs a supplied same-domain retained graph,
or permission for a narrowly scoped new calculation of the missing shared
models. The concrete scope is endpoint 13, actual HS midpoint 13 and endpoint
14 only, using the frozen radii, inverses, domains, identities, first-jet
authorities and reusable action receipts. Preserve a common endpoint-state
parameter map and both physical direction groups; serialize complete implicit
jets, C/J jets, common-border normalization and output models before support.
Only missing action operands/implicit mixed models would be newly evaluated,
with explicit receipts and independent reproduction. Do not rerun Layer A,
the eight-cell cover or endpoint 19; do not extend to intervals 14–18.

This scope requires an exception to the user's explicit prohibition on
rerunning mixed eigenline, mixed response and frozen action calculations.
No such exception is inferred here. The normalization-correlation viability
question and the source of any irreducible action inflation remain open.

## Reproduction

Run the following from the repository, with fresh output paths:

```
python scripts/audit_n12_gate7_layer_c_correlation.py --evidence-root <historical-evidence-root> --out <first.json>
python scripts/audit_n12_gate7_layer_c_correlation.py --evidence-root <historical-evidence-root> --out <repeat.json>
python scripts/inventory_n12_gate7_layer_c_models.py --out <inventory_first.json>
python scripts/inventory_n12_gate7_layer_c_models.py --out <inventory_repeat.json>
```

Both programs only read frozen operands; neither imports or invokes an action
producer. Exact rational outward bounds and source hashes are saved under
`artifacts/flagship_integration/gate7_layer_c_correlation_20260924/`.
Focused algebra tests exercise incidence cancellation, output cancellation,
the complete HS chain rule, shape rejection and non-promotion of the receipt.

Both diagnostic pairs reproduced byte-for-byte in separate processes; every
consumed source hash matched. Nine focused tests passed. Status, forbidden
claims, frozen-prediction integrity and precision audits passed. Full public
readiness remains blocked by five pre-existing oversized artifacts (the
causal-center, endpoint-first-error and stored-covariance NPZ files, history
variation action-block ZIP, and mixed-response JSON). Hygiene for this
change's 13 files passed. `validation.json` records their exact paths and
sizes; none was modified to bypass the audit.
