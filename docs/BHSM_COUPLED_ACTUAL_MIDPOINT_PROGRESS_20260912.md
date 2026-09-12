# Coupled normalization and actual midpoint progress — 12 September 2026

**Scope:** enclosures for the retained action on selected, fixed physical trial
neighborhoods. These are not Standard Model observable predictions.
`Gate7_closed=false` and `FULL_BHSM_COMPLETE=false`.

## Reproduced numerical results

Uniform endpoint fields for endpoints 13–18 have each been recomputed in
separate invocations with byte-identical output. Coupled normalization uses
the same proved normalized eigenpair and bordered response. The identities
`psi^T psi=1` and `psi^T hard=0` permit common-scale cancellation in the original
physical field without changing the action, physical trial radii or descriptor
terms. No empirical measurement enters these calculations.

For endpoint 13, the maximum state-field interval radius decreases from about
`2.255361e-5` to `4.409813e-7`. The descriptor-rate radius remains below
`1.363088e-11`. These displayed bounds are rounded upward.

The resulting actual Hermite–Simpson midpoint outer domain for interval 13 is
also independently paired. It retains two independent longitudinal directions,
two complete 74-dimensional transverse balls, and all 99 rate-remainder box
directions. Its maximum raw state rate-remainder is below `2.652815e-8`, versus
`1.364366e-6` for the previous construction. The physical endpoint domains have
not been shrunk.

On that complete midpoint domain, the normalized, oriented index-24 eigenpair
passes and reproduces byte for byte. The weighted contraction bound is below
`0.174810`; the image-to-radius bound is below `0.674810`. Both strict tests pass
on the first proposal. The earlier midpoint attempt remains preserved: all four
proposals failed, with the final contraction bound approximately `3.364034`.
That failure did not establish a physical singularity.

Exact artifact digests, paired-recomputation checks and endpoint interval radii
are recorded in
`artifacts/flagship_integration/BHSM_N12_GATE7_COUPLED_MIDPOINT_PROGRESS_20260912.json`.
Full numerical arrays remain in the corresponding execution-workspace folders:

- `.coupled_normalized_physical_value_work/endpoint_013` through `endpoint_018`;
- `.coupled_hs_midpoint_domain_work/interval_013`;
- `.coupled_midpoint_eigenpair_pilot_work/interval_013`.

## Physical-field and derivative implementation

The actual midpoint field producer consumes the paired midpoint eigenpair,
retains all 249 signed response-derivative columns, and uses the raw midpoint
anchor and hull for the point and uniform descriptors respectively. It retains
the configuration-source derivative and recomputes both complete third-action
descriptor terms. The first numerical field run for interval 13 passed; its
independent repeat and neighboring-domain runs are in progress at this report's
cutoff. The first run alone is not accepted as reproduced evidence.

The uniform first-derivative producer reuses the original complete rate
variation, including fourth-action terms and the descriptor basis direction.
It applies the proved coupled inverse bound to subsequent bordered solves.
It covers all 99 weighted augmented basis directions. Its numerical campaign
depends on successfully paired midpoint fields; implementation tests are not
a numerical derivative certificate.

The next dependencies remain uniform physical derivatives, uniform higher
derivatives/remainders, the physical quotient and the full integration proof.
The full curvature campaign remains necessary. None of these selected-domain
results supplies missing observable data to Museum engines or closes the
flagship manuscript's physical dependencies.

## Runtime recovery and validation

A Windows `PermissionError` while replacing the Hessian progress JSON stopped
an independent repeat after 27 rows. The new execution wrappers retry only the
specified progress-file writes for Windows access/sharing errors, using the
same original writer and bytes. Scientific artifact writes and the original
Hessian producer are unchanged. The interrupted midpoint-15 Hessian repeat
subsequently completed under this wrapper.

The focused suite passes **29 tests**, covering complete affine groups,
reproduction and failure retention, private-module routing, coupled
normalization, midpoint descriptors, all derivative columns, coupled inverse
bounds and status-only retries. An initial syntax error in the newly added
derivative producer was corrected before any numerical invocation.

The runtime uses at most six numerical workers with immediate dependent
pipelines, followed by continuation of the full curvature campaign. No scheduled
task is created. Native process identities and owned suspension counts are
recorded in execution-workspace state files.
