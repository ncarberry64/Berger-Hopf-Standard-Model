# Required CI integration

At79c374d the numerical job failed collection because bhtracker was not installed. Four product test modules raised ModuleNotFoundError. The workflow now installs `pip install -e ./product` before the unchanged repository-wide pytest command. No tests are excluded and no import shim conceals package errors. Dedicated tracker manuscript and Linux/Windows clean-wheel jobs retain the older manuscript job and both existing figure commands.

The first corrected runs passed wheel and both manuscript jobs; the full numerical job remained busy. Investigation found historical timing evidence: artifacts/submission_pytest.xml records three luminosity-distance tests taking 2246.474,2242.469 and 2183.266 seconds, and the documented full run took 6699.65 seconds. This is evidence of repeated slow work, not a newly introduced failure.

The three tests called exactly the same no-argument deterministic `dl.diagnostics()`, with no parameter/global changes and no mutation of its report. A module-scoped pytest fixture now evaluates it once and all three original test identities/assertions read that report. The separate duality calculation, all tolerances and production numerical code remain unchanged. An independent read-only reviewer verified these conditions and root/vendor source identity. This removes two duplicate expensive integrations without replacing the calculation with a stored answer. Final CI must still execute the actual calculation, all assertions and both figure programs.

The final actual-head run IDs/outcomes and downloadable artifact hashes are recorded in the external release receipt after the Git commit is known. Superseded, canceled or earlier successful runs are labeled separately. They are not evidence for final-head completion.
