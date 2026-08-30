# Universal physical release reconciliation

The release reconciler is the final internal proof gate, not a prediction
engine.  It consumes outputs that have already passed their own action-owned
promotion gates and refuses a release unless all of the following hold on one
candidate:

- Gate 7 is closed on one identified physical background.
- Every physical-completeness row other than the reconciliation row is
  `IMPLEMENTED_PROMOTABLE`, has left `OPEN_INTERNAL_BLOCKER`, and has a
  materialized physical output.
- Every required benchmark pair has one physically promoted frozen prediction.
- All predictions share the declared action version and physical background.
- Every dimensional prediction uses the one declared scale map.
- The release artifact manifest is byte-exact under SHA-256.
- A clean deterministic reproduction has passed and the release commit is
  recorded.

The reconciliation row is deliberately excluded from its own prerequisite
set, avoiding a circular `FULL_BHSM_COMPLETE` assertion.  Measured values
cannot select a prediction or retune a sector-specific scale.

The current repository fails this validator by construction: Gate 7 is open,
the physical matrix rows remain internal blockers, no complete promoted
benchmark prediction set exists, and no full clean release reproduction has
been declared.  The implementation therefore improves release engineering
without changing the scientific classification.
