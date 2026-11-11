# Repository organization plan

This plan follows the 10 November 2026 inventory of main, open GitHub work and
focused BHSM/Norman Works context. The [repository guide](REPOSITORY_GUIDE.md)
classifies the whole tree; the [open-work register](OPEN_RESEARCH.md) identifies
the live integration boundaries.

## First review: navigation and preservation

This change adds a compact reader map, a dated branch/PR register, a
[scientific topic map](RESEARCH_TOPICS.md), artifact and theory entry guides,
a reproducible path inventory and a bounded navigation audit. Long
documentation catalogs remain at their existing locations with
their original headings and text. Their historical sections are visually
separated so old campaign verdicts are not mistaken for the latest frontier.

The existing scientific modules, equations, frozen prediction bytes, manuscripts,
Museum assets, generated certificates, CI gates and release bindings are kept
under their existing identities. The cleanup is based on an isolated checkout
of the pinned remote main; active research checkouts are not a migration source.

The later [envelope clarification](BHSM_ENVELOPE_CLARIFICATION_20261110.md)
corrects the Museum's regime wording as attributed author interpretation.
The original October amendment/download remains unchanged. Current display
text and AI navigation follow the correction, while physical prediction
outputs and scientific acceptance gates retain their existing status.

The existing CI job includes bounded Museum playback, navigation, source-copy
and generated-record checks. These checks do not deploy the Museum or replace
a full application build and browser review.

## Subsequent work in dependency order

| Stage | Concrete work | Evidence needed before changing structure |
| --- | --- | --- |
| Reconcile scientific status | Review one workstream at a time against its exact action/domain sources; propose focused scientific PRs | Research-owner review, provenance, bounded reproduction, failures and unresolved gates. A branch date or passing software suite is insufficient. |
| Extend topic catalogs | The first [topic map](RESEARCH_TOPICS.md) covers enclosure/response, mass and flavor, gravity/cosmology, and public products; add narrower routes as sources are reviewed | Explicit source succession; separate frozen, conditional, diagnostic and physical claims. Existing file paths remain valid. |
| Reduce duplicate navigation | Replace genuinely redundant summaries with pointers while preserving historical text and anchors | Link/fragment comparison, source ownership and relevant documentation tests. Do not rewrite old conclusions as if they were never recorded. |
| Plan physical file moves only where useful | Produce an old-to-new path map and inspect code imports, generators, hashes, manifests, notebooks, publication URLs and workflows | Compatibility paths/redirects and reproduction checks must be concrete before any move. Review archive/licensing implications. |
| Review retained generated files | Classify each candidate by generator, inputs, source revision, retention role and exact bytes | A reproducible replacement is not permission to discard a unique failed run or certificate. Large-file migration needs a retrieval plan. |
| Review branches and releases | Distinguish merged, superseded, active and provenance-only refs | Named owner decision and retained immutable references. Never infer deletion permission from inactivity. |

## Rules for new material

- Give every result a claim class, action/domain, source revision, input identities,
  generator or derivation, validation scope and unresolved gates.
- Keep an existing identity when revising an owned source. Add dated evidence
  where history must remain immutable; link the successor explicitly.
- Place scratch output in ignored local directories. Put reviewed reproducible
  evidence in its owned artifact directory with a manifest.
- Preserve the boundary between scientific evidence, Museum explanation,
  historical records and software-product validation.
- Consult focused BHSM/Norman Works references when Git leaves a gap. Export
  reviewed scientific content rather than private correspondence, machine paths
  or internal workflow notes.

## Validation and limits

The navigation audit resolves tracked paths using Git, so a sparse checkout
does not manufacture missing-file errors. It checks available Markdown anchors
and reports unavailable content explicitly. It does not verify external sites,
prove scientific claims or replace the required publication audits.

Run the relevant documentation tests and the status, forbidden-claims,
frozen-integrity, precision and public-readiness audits. Preserve historical
test failures as failures; compare against the pinned baseline before calling
one a regression. A sparse public-readiness scan covers only materialized file
contents. The full research suite and expensive proof campaigns are outside
this navigation change.

Approval of this organizational PR does not approve a scientific release,
merge another research branch, remove a historical file/ref, or publish a held
research packet. Those are separate concrete changes with their own review.
