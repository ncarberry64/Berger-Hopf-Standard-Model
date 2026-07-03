# Gauge Action Attachment Update V4 2 v4.2

Status: `OPEN_MISSING_GAUGE_COUPLING_ACTION_ATTACHMENT`

## Candidate

`S_gauge=k sum_i w_i lambda_gauge Tr(F_i^2)`

## Claim boundary

The gauge skeleton does not attach frame averaging, unit volume, sector weights, and k in one normalized term.

## Required boundaries

- Three artifact-backed Berger frame directions do not by themselves imply equal weighting.
- Equal weighting does not by itself imply average normalization by 1/3.
- Average normalization does not by itself attach to gauge trace densities.
- Berger anisotropy must be checked before equal frame averaging can be promoted.
- The denominator 1/[3 Vol(S³)] remains open unless equal frame averaging, unit-volume normalization, and gauge-trace attachment are supported.
- The gauge coupling quantum remains open unless the denominator is action-attached.
- α_i, g2_BH, CKM coefficient value, and CKM exponent remain open unless downstream action gates close.
- Full BHSM remains not complete.

Run `python -m bhsm.interface gauge-action-attachment-update-v4-2 --format json`.
