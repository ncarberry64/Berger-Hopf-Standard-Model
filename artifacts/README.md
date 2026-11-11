# Scientific artifacts

This directory retains machine-readable evidence, numerical results,
certificates, diagnostics and provenance. Generated does not mean disposable:
failed checks and superseded runs can be essential parts of the scientific record.

Start with the [artifact catalog](../ARTIFACT_INDEX.md),
[repository guide](../docs/REPOSITORY_GUIDE.md) or
[open research register](../docs/OPEN_RESEARCH.md). The catalog preserves
campaign headings; "current" inside an older entry refers to that campaign.

Before using a result, follow its manifest to the exact source revision, inputs,
generator, precision, domain, hypotheses and validation receipt. A JSON status,
plot or small residual alone is not a physical prediction. Frozen predictions
retain the separate [integrity policy](../docs/frozen_predictions.md).

For new reviewed evidence, keep a named owner directory and record deterministic
reproduction where applicable. Put scratch/caches in ignored local locations.
Do not overwrite a historical result just because a newer calculation exists.
Follow the [organization plan](../docs/REPOSITORY_CLEANUP_PLAN.md) before moving
files or changing a retention policy.

`repository_organization/` contains metadata about the repository structure and
public research refs. It contains no new scientific result.
