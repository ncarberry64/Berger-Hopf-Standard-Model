# Gate 7: 66D tangent reconciliation checkpoint — 2026-09-26

Checkpoint base: `efd26896a13b592d3631c50e103bed18d5d3f03c`.
Branch: `theory/gate7-66d-reduced-adjoint-integration`.
This is preservation of validated numerical findings, not a nonlinear closure proof.
`Gate7_closed = False`; `FULL_BHSM_COMPLETE = False`.

## Validated state and corrected binding

Stage B remains **numerically resolved: 73 = 66 intrinsic child + 7
boundary/interface**. The original final numerical adjudication and rank-refinement
arrays are preserved in `artifacts/flagship_integration/gate7_66d_checkpoint_20260926/`.
Its historical next-stage text is superseded by the explicit blocker below.

The tangent-authority comparison is **Case B**, not evidence of a distinct physical
child. The frames use the same constraint construction at nearby Newton centers;
they are not exactly equal subspaces. Projector differences at nodes 13 and 14 are
approximately `6.70e-8` and `7.21e-8`. The Stage-B child through the alternate tangent
has relative residuals `4.62e-9` and `4.90e-9`. Stored residual matrices and Arb512
outward Frobenius allowances are retained in `binding/report.json` and `binding/arrays.npz`.

All three frozen interval-13 midpoint scientific source hashes match:

| Source in the sibling `BHSM-ae32-crossing-correction` checkout | SHA256 |
| --- | --- |
| `artifacts/flagship_integration/.coupled_midpoint_eigenpair_pilot_work/interval_013/eigenpair.npz` | `60CABA68D3C017B5C6F1A605A7474A970EEB914F5A4F49789FD31B7A51032489` |
| `artifacts/flagship_integration/.primal_mean_value_component_centered_midpoint_uniform_df_work/interval_013/derivative.npz` | `D58D440D259FEEC2AE1FBA518F21508C2716233E772EA8F0F0E0A79A552355B1` |
| `tmp/bhsm_midpoint_center_mean_value_right_pair_20260913/value/first/column.npz` | `8D9F46D9D7C958FD6D367264C72FA3A02DBA2DF5CB277DC27BA942A4D68BBC8D` |

Two historical Layer-C wiring errors are corrected in the replay:

- Descriptor **trial scale is `1e-7`; test scale is `1e6`**. A physical descriptor
  rate must be divided by `1e-7` before entering trial coefficient coordinates.
- The recovered midpoint `input_map` is the **interval-13 right-endpoint-14
  Hermite–Simpson partial input frame**, not a node-13 frame. It is not the complete
  two-endpoint physical-history derivative.

The corrected first-order binding is valid subject to the explicit tangent
reprojection allowances. Its midpoint allowance is approximately `5.23494e-8`.
The retained 66D descriptor row and fixed adjoint are center proposals, not a
certified uniform nonlinear child map. The prior tiny midpoint/point differences
(`4.31e-16` for the line and `3.35e-10` for response) compare coefficient centers.
They are **not full interval certificates**. Restoring coefficient radii gives
coarse difference bounds about `2.19416` and `1.38315e6`; this is not physical failure.

## Existing center operator M_13

`newton/M_13.npz` stores only the 74×74 center matrix and an inverse proposal.
The source is the existing
`BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_BLOCK_NEWTON_PREDICTOR.npz`, key
`reduced_right_Newton_blocks[13]`, under `artifacts/flagship_integration/`.
`newton/report.json` records source hashes, coordinate conventions, replay errors,
and outward inverse residuals. The center condition number is approximately
`49.3624034113`; the left inverse residual Frobenius bound is `1.97642e-15`.
This verifies invertibility of the exact stored binary64 matrix, not a uniform
physical-tube operator or an eight-reaction subblock.

In the existing 99D action coordinates, indices 0:98 are weighted state and index
98 is physical descriptor. At endpoint 14, `E_trial` has the physical 98×73 tangent
in its first 73 columns and descriptor entry `1e-7` in column 73; `E_test` instead
has descriptor entry `1e6`. With `h = 1/4`,

```
R_13 = I - h/6 [4 J_mid (I/2 - h J_14/8) + J_14]
M_13 = E_test(14)^T R_13 E_trial(14).
```

Partitioning this as **66 child + 7 boundary + 1 descriptor** still requires seven
owner-bound Stage-B complement columns, their normalization/conditioning, and
matching residual rows or dual test transformation. The 66 columns must be carried
into this tangent frame with their explicit residuals. A numerical nullspace alone
does not specify nonlinear boundary equations. The existing 99D→74D construction
records normal residuals; this checkpoint adds no nonlinear authority for them.

## Exact blocker and next allocation

The 66D child has **no certified nonlinear slaving map for the seven
boundary/interface reactions plus descriptor response**. The recovered
124-variable eigenline/response fixed adjoint does not eliminate these eight
reaction variables. The 25 constraint-normal directions belong to the prior
99D→74D construction; they are not being counted as 25 new reaction unknowns here.

The first mathematical task is to bind the seven Stage-B boundary-complement
columns and their residual rows to the same endpoint-14 trial/test convention,
then form the eight-reaction center block `M_qq` with the descriptor coordinate.
After that, certify the owner-bound nonlinear equation `F_q(p,q(p)) = 0`, uniform
invertibility and mixed reaction jets on the unchanged physical tube. Only those
objects authorize reduced nonlinear curvature and subsequent adjoint support.
No nonlinear `M_qq(p)` variation proof was attempted in this checkpoint.

## Reproduction and limits

Run `scripts/checkpoint_n12_gate7_66d_tangent_binding.py --out <new-directory>` and
`scripts/checkpoint_n12_gate7_interval13_newton_center.py --out <new-directory>`.
The binding replay uses the explicitly hashed local Downloads evidence, sibling
science archives, and primary checkout caches; these large inputs are not bundled.
The preserved Stage-B files provide a repository copy of that part of the evidence.
Both replays were run in independent processes twice with byte-identical outputs;
`reproduction.json` contains hashes. No scientific action/Hessian producer ran.

Validation: `python -m pytest --noconftest tests/test_gate7_66d_tangent_binding.py -q`
passed **7 tests**. The initial fixture-enabled run had one byte-hash failure from
the global JSON line-ending normalization (six tests passed); the capsule test now
reads raw bytes directly. The focused rerun avoids the unrelated repository-wide
snapshot fixture. Both replay pairs passed byte-for-byte comparison.

Focused tests are in `tests/test_gate7_66d_tangent_binding.py`. No physical budget
debit, intervals 14–18 extension, decay/instability inference, or revision of the
inherited interval-13 local closure is made. This is a research checkpoint, not a
public release; the broad publication audits were deliberately not rerun under the
user's checkpoint-only instruction. Pre-existing untracked scientific evidence is
left in place.
