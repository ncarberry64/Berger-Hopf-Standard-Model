# Additive SQLite test resource repair

The broad source compatibility run retained two Windows cleanup failures in the
historical `tests/test_sqlite_audit_v1.py` methods 05/06. Their mutation connections
used `with sqlite3.connect(...)`: that context commits or rolls back a transaction
but does not close the connection. The immutable audit helper already closes its
own verification connections. This was test-owned resource leakage, not a change
to the scientific likelihood, data, durability contract or corruption checks.

The original helper and all **18 original test methods** remain unchanged and
source-pinned. Additive `test_sqlite_audit_v2.py` wraps only those two mutation
connections in `contextlib.closing`, retaining the nested connection context for
commit/rollback. All original assertions remain identical; the other 16 method
ASTs are exact. One new test keeps closed connection objects strongly referenced,
checks committed data through another explicitly closed connection, and renames
and removes its own temporary database without garbage collection or ignored
cleanup errors. The focused suite therefore has **19 tests**.

`tests/conftest.py` excludes only `test_sqlite_audit_v1.py` from automatic pytest
collection, so the additive replacement runs without duplicating the frozen
historical test. No other test is ignored, skipped or softened. The original root
conftest and all 119 protected source/input/history bindings remain unchanged.
The retained broad failure remains historical evidence; a focused resource-test
pass alone is not a broad compatibility or statistical acceptance claim.

The reviewer/project record is the
[formal BHSM repository](https://github.com/ncarberry64/Berger-Hopf-Standard-Model).
