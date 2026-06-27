# Prediction gallery

The gallery combines registry entries, deterministic report outputs, theorem
blockers, and runtime gates. Speculative templates appear only when explicitly
requested. Gallery entries are status summaries, not empirical validation claims.

```powershell
python -m bhsm.interface gallery --format markdown
python -m bhsm.interface gallery --format json
```

Gallery status remains distinct from artifact provenance. Use
`python -m bhsm.interface artifact-report --format json` for source fields and
claim-use booleans. Artifact-backed outputs are local BHSM outputs with
provenance, not empirical validation claims.
