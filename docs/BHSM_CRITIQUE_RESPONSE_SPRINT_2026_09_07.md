# BHSM critique-response sprint — 7 September 2026

## Objective and evidence baseline

Translate the proposed physical picture into explicit, independently checkable
academic claims, and address the substantive weaknesses identified by the
viability critique. Author confidence motivates the work; the scientific
conclusions depend on stated assumptions, derivations, and reproducible results.
An unsuccessful route is a useful sprint result and must remain visible.

Baseline: Git revision `c6d6a81caf2687002a77e20f5df6abee0c0e288f`.
`FULL_BHSM_COMPLETE = FALSE`. This sprint does not promote a physical result.
Existing six-worker signed recovery continues with unchanged scientific inputs,
fingerprints, precision, and compute ceilings. Its completion is one numerical
milestone, not a percentage of physical BHSM completion.

## Work order and acceptance criteria

### 1. Audit the photon-sector inference, then adjudicate the retained route

Reproduce the current continuous-frequency DtN energy identity and the exact
two-sided reflection argument. Preserve the recorded lowest-mode ratio
`Z_t/Z_s = 0.590609601652908` and its source assumptions.

The first source inspection identifies an interpretation to audit explicitly:
`lowest_transverse_residue_witness()` calculates `n^2*(-dN/dq^2)/N(0)` at
`n=2`, and `current_c2_transverse_frequency_symbol()` defines its spatial
coefficient using `R4*N(0)/n^2`. Explain the conditions under which this
complete static-mode ratio is the relevant Maxwell normalization test.
Distinguish a fixed-mode obstruction from a statement about the full local
principal symbol or an effective derivative expansion. Check curvature terms,
radial-gradient energy, frequency regime, and the common physical metric.
This audit question is not a refutation of the existing theorem and does not
authorize fitting the two coefficients to equality.

Deliverable: a short derivation of the precise necessary condition, a
reproduction of its operands, and one of:

- the existing no-go holds at its claimed scope;
- a documented error or missing hypothesis narrows that scope;
- a repair follows from an already specified action/domain term, with all
  coefficients and boundary conditions traced to their sources.

If no retained repair exists, report that fact. A new boundary/collar term,
nonreflection exterior, or independent boundary field is a new model proposal
requiring explicit motivation and a versioned assumption ledger. Do not silently
count it as a translation of the unchanged action.

Sources: [frequency Hessian](../theory/ae3_c2_lorentzian_gauge_ghost_hessian.md),
[route screen](../theory/ae3_c2_gauge_mismatch_resolution.md), and
[two-sided no-go](../theory/ae3_c2_two_sided_calderon_reflection_no_go.md).

### 2. Resolve the Einstein–Cartan domain question at its actual scope

Audit the original stationary first-order action as well as the eliminated
quartic form. Retain the documented collapse-endpoint scalings and the
nonintegrable `chi^-2` stationary density for the retained zero mode.

Deliverable: either an action-derived admissible domain/solution with finite
stationary action and unchanged required state content, or a clear rejection of
this completion on that domain. No arbitrary cutoff, mode deletion, compensating
counterterm, or nonstationary field choice counts as a solution. A radial endpoint
and a historical event-control endpoint must not be identified without proof.

Authority: the AE3.2 candidate discussion in
[current status](current_bhsm_status.md).

### 3. Separate family response, physical masses, and mixing

Preserve the current family-central charged-current result and the common
diagonal response basis. Identify the exact missing action-owned term required
for nontrivial left-handed up/down misalignment. A supplied flavor matrix or an
observable-selected ordering cannot be counted as a derived mixing matrix.

Use the latest main-branch charged-lepton result as a bounded candidate:

```text
R_tree = log(m_e/m_tau) - 9 log(m_mu/m_tau) - 54/pi = 0.
R_pole = log(Z_e) - 9 log(Z_mu) + 8 log(Z_tau).
```

Reproduce the tree identity and its cancellation of common scale and squashing.
Keep its mode-ledger assumptions explicit. The stored post-derivation target
`exp(R_reference) = 1.0605668991516508` is a comparison quantity; it is not an
allowed input for choosing a self-energy. Determine whether the specified action
can calculate or constrain that dressing combination. If it cannot yet do so,
report the missing operands and retain the result as a conditional tree theorem.

Deliverable: a mass/mixing dependency table and a concise sum-rule result with
an explicit physical-promotion test. Do not call a local tree mass shell a
globally dressed particle pole.

Sources: [charged current](../theory/ae31_c2_coexact_su2l_charged_current.md),
[tree sum rule](../theory/ae31_charged_lepton_scale_free_sum_rule.md), and
[dressing invariant](../theory/ae31_charged_lepton_pole_dressing_invariant.md).

### 4. Assemble the academic case around the strongest checked result

Prepare a compact review packet containing the action and domain, admitted
inputs, strongest nontrivial result, strongest counterevidence, reproduction
commands, and unresolved dependencies. Compare the result with relevant prior
literature before claiming novelty. Independent technical review is a priority;
no external correspondence is sent by this sprint document.

The flagship manuscript must follow the demonstrated scope. Museum updates
continue to feed compatible validated outputs into the existing exhibit engines.
Neither presentation work nor an implemented API is evidence that a physical
observable has been derived.

## Sprint decision rule

At the review point, assess what changed scientifically: a central obstruction
was resolved, a claim was corrected, a physical consequence became evaluable, or
a route was rejected. Counts of tests, artifacts, shards, and manuscript pages
are execution metrics, not the acceptance criteria. Do not expand the numerical
budget or start an expensive successor solely because the previous batch passed.

The critique is a testable work program. Strengthening BHSM can mean improving
its explanatory reach or identifying more accurately where a particular
construction does not work.

## Initial verification

The focused frequency-Hessian, charged-lepton sum-rule, and pole-dressing
invariant suites pass: 31 tests. The gauge materializer now accepts `--output`
so its subprocess reproducibility test writes twice to a temporary file and
checks that the tracked certificate is unchanged. The scientific calculation
and default materialization destination are preserved. Passing these tests
establishes the internal baseline, not the remaining physical interpretation.
