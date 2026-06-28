# Python CLI

Entrypoint:

```powershell
python -m bhsm.interface --help
```

Commands:

```powershell
python -m bhsm.interface registry
python -m bhsm.interface registry --format json
python -m bhsm.interface status electron_neutrino
python -m bhsm.interface predict --particle W_boson --mode calibration
python -m bhsm.interface predict --particle electron_neutrino --anchor W_boson
python -m bhsm.interface report --anchor W_boson --particles W_boson,electron_neutrino --format json
python -m bhsm.interface report --anchor W_boson --include-open-theorem --format text
```

`registry` lists source and claim metadata. `status` returns one entry and reports
unknown keys as `UNKNOWN_OR_UNREGISTERED`. `predict` runs only the deterministic
placeholder interface examples. `report` combines solved values, comparisons,
statuses, warnings, and claim boundaries.

The CLI requires neither network access nor optional PDG, Wolfram, FeynRules,
UFO, or MadGraph tooling.

See `docs/bhsm_v1_2_0_cli_command_table.md` for the release command matrix.

Additional offline commands cover `gallery`, `plot-gallery`, `notebook-pack`,
`pdg-status`, `pdg-fetch`, `speculative`, `theorem-blockers`, and
`theorem-attempt`.
