# Provisional D5 bulk response consumed at the event

Continuation of e02747f2. Canonical run_4 and run_5 are byte-identical. The new incoming bulk core was independently evaluated twice, then reused for consumer completion. No completed E1 kernel/native precision calculation was repeated.

The full384 carrier in the retained constant angular sector is propagated by the original unsquared Lorentz D5, with the actual six incoming time nodes and both eta collars on that one history. Separate LR/RL kernels produce nonzero interior coefficient fields: inner norm0.03826078 and event-face norm0.03559047 per channel. Those actual interior fields and source responses enter the original event/Jacobi equations and signed Green returns. All366 homogeneous boundary coordinates pertime node remain unassigned.

This is NOT the completed physical outer/event/child solve. Finite collar/source constraints are within2.23e-16, but propagated original D5 residuals reach1.397e-9 at collocation nodes and6.2777 off-node; source residuals reach9.314e-9 and132.135. Complement-plus-extension source reconstruction reaches5.961e-8. Normal integrals, physical outer/time faces, reset/child data and formation remain held, not zero. The unchanged physical2e-10 guard has not passed.

The child birth normal ray immediately enters pre-birth t<0. The derived admissible normal-coordinate domain is a wedge q>=q_birth(s); q_birth'(0)=0.1687758438749448. No child polynomial is extended across that event. The exact event/corner problem remains necessary.

The computational compact interior extension is explicit and differentiated. It is distinct from the physical normal profiles. The existing Higgs seam is not appended as bulk mass. The whole local Maxwell/Higgs subtraction is not repeated or re-added as a force. Native clock/density contacts are reused without assigning the unresolved transmission or native corner.

See [the derivation](../../theory/muon_d5_complement_bulk_response_20261019.md), REUSE_COMPARISON_v1.json, each run's boundary_validation.json, and validation.json for exact identities, equations, original residuals, source derivatives and error scope. Required audit outputs are in publication_audits.

Reproduce in a fresh output directory:

```powershell
$env:OPENBLAS_NUM_THREADS='1'
$env:OMP_NUM_THREADS='1'
C:\Python314\python.exe scripts/evaluate_muon_d5_complement_bulk_response.py --output-dir <new-directory>
```

`--resume` consumes a previously checkpointed core; `--reuse-core-from <completed-directory>` rematerializes the hash-verified core without solving it again. The separate verification script checks both eta collar constraints and source equations. Development runs1-3 are retained locally, not represented as physical solutions.

NEXT_OPERAND: determine the saved homogeneous/normal-profile data through the actual event-corner and outer equations, including child inherited connection, then the coupled mechanical formation KKT. Retain the new bulk response and all finite nonpasses when advancing this connection.
