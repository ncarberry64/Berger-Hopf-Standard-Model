# BHSM in plain language

## The one-minute version

The Berger-Hopf Standard Model (BHSM) is a research program asking whether
some of the structure that particle physics currently treats as a list of
separate ingredients could instead arise from one deeper geometric system.

The motivating picture is simple: a musical instrument does not contain a
separate object for every note. Its shape, boundary, and allowed vibrations
select an organized family of notes. BHSM asks whether an internal geometric
space, its boundaries, and its allowed modes could organize particle-like
sectors, charges, mixing patterns, and scales in a similarly unified way.

That is the research question, not a completed result. The repository does
not currently prove the Standard Model, derive all particle masses or gauge
couplings, or establish BHSM as physical reality.

## What the name means

- A **Hopf fibration** is a precise mathematical way of organizing one space
  as linked fibers over another space.
- A **Berger sphere** is a three-sphere whose directions can be stretched or
  compressed relative to one another.
- **Standard Model** names the low-energy particle theory BHSM ultimately
  seeks to recover as an effective limit, rather than assume as its final
  foundation.

These geometries provide harmonics, integer weights, connections, curvatures,
and mode overlaps. BHSM investigates whether those structures can do physical
work that would otherwise be assigned to unrelated constants or field
labels.

## The central physical idea

BHSM explores a candidate transition from geometry to physicality:

1. Energy and geometry form a coupled parent system.
2. A compact geometric configuration constrains which modes can exist.
3. Harmonic compatibility and constructive interference select coherent
   channels rather than arbitrary ones.
4. A boundary, collar, or localization mechanism may turn part of the parent
   geometry into an effectively four-dimensional arena.
5. Fields and interactions on that arena may inherit their organization from
   the parent geometry.

In the current construction, each arrow is treated as a theorem gate. A
suggestive analogy or matching number is not accepted as a derivation.

## Why boundaries matter

An ordinary drum has many mathematically possible disturbances, but its
boundary determines which vibrations persist. BHSM studies an analogous role
for geometric boundaries and collars.

The recent construction has identified an exact Lorentzian equator inside a
round five-dimensional parent geometry. Smooth fields spread through the
whole compact space do not automatically acquire one common
four-dimensional Lorentz normalization. This sharpens the problem: a genuine
boundary or localization action is needed, not merely a change of
coordinates or a declaration that the equator is physical.

## Why harmonics and “octaves” matter

Compact spaces admit discrete vibration patterns. Some combinations reinforce
one another; others cancel or fail representation and conservation rules.
BHSM uses this harmonic structure as a candidate selection mechanism.

“Octave” is useful intuition for repeated scale or frequency relationships,
but the scientific implementation is stricter: the repository requires an
explicit operator, spectrum, action source, allowed representation channel,
and stability test before a harmonic pattern is promoted to physics.

## What has actually been built

The repository contains:

- exact and conditional geometric reductions;
- action and variational calculations;
- spectral and Hessian stability tests;
- explicit ledgers separating derived, conditional, and open statements;
- deterministic computational artifacts and thousands of tests;
- interfaces for checking formulas, provenance, and claim boundaries;
- a high-throughput coordinate engine tested on synthetic and published CMS
  Open Data four-vectors.

The [scientific contribution ledger](bhsm_scientific_contribution_ledger.md)
summarizes the major construction pull requests and states what each one adds
without treating an internal BHSM result as established experimental science.

## What remains open

The largest open tasks include:

- deriving the physical four-dimensional boundary/localization action;
- deriving rather than importing an absolute unit of length, mass, or energy;
- completing a healthy gauge-fixed physical spectrum;
- deriving the physical gauge group and normalized couplings;
- deriving a BHSM-native fermionic action and its chiral spectrum;
- deriving masses, mixings, and generations without fitting them afterward;
- recovering the complete Standard Model as a controlled low-energy limit;
- making new quantitative predictions and passing independent experimental
  tests.

Until those gates close, `FULL_BHSM_NOT_COMPLETE` is the correct project
status.

## What the CERN demonstration means

The CERN/CMS demonstration tests the **BHSM Engine**, not the BHSM physical
theory. It asks whether a geometric coordinate transformation is accurate,
stable, reproducible, and fast on realistic particle-collision four-vectors.
It does not test whether BHSM explains the particles that produced those
four-vectors.

See [the CERN toy-model explanation](cern_toy_model_in_plain_language.md) for
the nontechnical walkthrough.

## How to explore the repository

- Start with [the current status](../STATUS.md).
- Read [the claim boundaries](../CLAIMS.md).
- Browse [the scientific contribution ledger](bhsm_scientific_contribution_ledger.md).
- Reproduce the software checks with [the quickstart](../QUICKSTART.md).
- Use [the artifact index](../ARTIFACT_INDEX.md) to trace claims to
  machine-readable evidence.

## What BHSM does not currently claim

BHSM does not currently claim:

- physical validation or CERN/CMS endorsement;
- a complete first-principles derivation of the Standard Model;
- derived particle masses, gauge couplings, CKM/PMNS matrices, or rare-B
  observables;
- a derived physical Dirac equation or magnetic-monopole sector;
- a generated absolute unit;
- full BHSM completion.

The purpose of this discipline is not to make the program timid. It makes
progress legible: one can see exactly which parts are mathematics, which are
conditional physical constructions, and which still require new work.
