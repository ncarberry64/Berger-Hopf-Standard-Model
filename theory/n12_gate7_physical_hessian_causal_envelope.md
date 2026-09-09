# Physical center Hessian error in the causal transverse bound

This consumer joins the physical midpoint Hessian errors and exact normalized
endpoint-projector Hessian errors with the existing complete physical DF
incidence envelope. It introduces no action term or empirical calibration.

For interval i and a common endpoint block-sup input radius r, let m_i be the
certified midpoint pair coefficient and e_(n,i) the certified single-endpoint
coefficient for node n in interval i. Then the additional local response obeys

    ||delta_i|| <= (m_i + e_(i,i) + e_(i+1,i)) r^2.

Node zero is fixed and has no endpoint input. The midpoint coefficient already
contains its factor two for the concatenated pair norm. Single-endpoint
coefficients are not doubled. Interior endpoints contribute once to each of
their two incident intervals; terminal node 370 contributes only to interval
369. Each endpoint output includes physical midpoint DF incidence and output
construction errors. Midpoint input coordinates include physical endpoint DF
and exact normalized projector construction. These are frozen stored frames;
identification with an intrinsic physical quotient is a separate requirement.

The new local errors concern H_physical minus H_stored. The preceding incidence
envelope concerns the stored tensor and its coordinate, storage, and output
errors. Adding them includes the remaining physical-Hessian cross terms
without adding the earlier coordinate/output bounds twice. Each local bound
retains the signed output-map contraction before taking a norm.

The existing 512-bit signed-block causal transport bounds the new source
through the same 370 stored maps. With map perturbation gain k < 1 and source
coefficient E, its additional frozen response bound is E/(1-k). The complete
consumer recomposes all raw source errors with the reconstructed covariance
coefficients, applying the map perturbation formula once to their total.

Default execution requires all 370 midpoint and 370 noninitial endpoint
certificates. It fails on absent points, missing endpoint incidences, source
conflicts, changed data, or incompatible maps. Original and factored midpoint
backends are allowed through their existing source-bound certificates;
original is selected first if both exist, independently of numerical values.

An explicit `--selected-only --midpoints ... --nodes ...` run instead bounds
only the indicated additive component. Outside that component the transport
vector is zero by definition of the selection, not by an assertion about the
unknown physical error. Its artifact lists every missing point, supplies no
combined global coefficient or self-map adjudication, and cannot close Gate 7.
It must never be interpreted as an upper bound on all physical Hessian errors.

Even complete center coverage does not recertify Y, Z1, the central/mixed
coefficients, neighborhood remainders, or the physical quotient chart. A
stored polynomial self-map witness is not a physical contraction proof.
