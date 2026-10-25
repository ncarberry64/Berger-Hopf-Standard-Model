"""Select the additive SQLite test repair; retain the frozen v1 source intact."""

# Only this historical test filename is omitted from automatic pytest collection.
# Its helper and all 18 methods remain immutable provenance. test_sqlite_audit_v2
# preserves every assertion and fixes two test-owned connection lifetimes; no
# scientific helper, corruption check, skip or failure criterion is weakened.
# See docs/SQLITE_TEST_RESOURCE_REPAIR_20261025_V2.md for source/audit scope.
collect_ignore = ["test_sqlite_audit_v1.py"]
