# The permanent BHSM science collection

The public Museum retains dedicated exhibits for particle decays/collisions,
the full magnetic-moment inventory, SM predictions, SM equivalence, force
unification, the common action and spectral forecasts. Sandbox comparisons
are additions. They must never displace the science prototypes. Computation
and research achievements remain a separate exhibit; other-work cosmology
comes after the author.

## Current data and simulation boundaries

`tools/materialize_museum_science.py` reads the existing 34-entry prediction
ledger, retained SM-bundle artifact, current system map and reviewed output
registry. It does not call a solver or modify scientific inputs. The catalog
tracks 17 SM particle-family labels plus proton/neutron composite benchmarks.
The collision workbench also offers explicitly selected conjugate channels;
this does not derive neutral-state conjugacy or a complete physical spectrum.

The default collider returns an elastic prototype for the two selected incoming
species; the visitor can also inspect a separately selected outgoing channel.
It calculates relativistic two-body phase space for user-selected
incoming and outgoing states in arbitrary demonstration units. Charge balance
and thresholds reject incompatible choices. Four-vectors and their conservation
residual are genuine calculations of that illustrative setup, not BHSM event
predictions. A kinematically open channel does not establish an amplitude,
cross-section, branching fraction or decay. Input masses are clearly labeled
demonstration parameters. No random branching probabilities are invented.

The magnetic tracker separates charged-lepton g/a/mu from neutral, confined,
composite, boson-specific and spin-zero definitions. It does not export a lepton
formula to every particle. Pending values are never displayed as zero.

SM equivalence displays the retained bundle's representation/anomaly checks
without promoting them to full interacting physical equivalence. The force
animation illustrates a proposed common origin, not measured running curves,
a meeting energy or an established quantum-gravity result.

## Updating these same exhibits with derived data

1. Complete and review the source-owned physical result in `artifacts/`.
   The Museum does not determine whether the physics is proved.
2. Add a record to `data/museum/approved_science_outputs.json`. Each record
   has `id`, `exhibit` (`decays`, `magnetic`, `predictions` or `forces`),
   `label`, applicable `particle` and `observable`, `source_path`,
   `source_pointer`, LF-normalized `source_sha256`, `reviewed_by`, and
   `review_record`. The review record must name the real academic review;
   an empty placeholder is not a review.
3. The pointed-to source object must itself contain `classification`
   (`DERIVED_POINT_PREDICTION` or `DERIVED_INTERVAL_PREDICTION`), `value`,
   `units`, `uncertainty_note`, `action_version`, `domain`, `source_revision`,
   `physical_promotion_ready: true`, `experimental_target_used: false`, and
   explicit `gates`. A point is finite; an interval is ordered and finite.
   Decay and magnetic records must also own the same `particle` and
   `observable` identifiers as their publication entry; relabeling is rejected.
   Required gates are `gate7_closed`, `action_selected_external_state` and
   `physical_units_fixed`; magnetic records additionally require
   `ward_identity_closed`, `renormalization_fixed`, `moment_definition_fixed`;
   decay records require `amplitude_action_derived` and
   `channel_inventory_complete`. All must be true in the source, not merely
   asserted in the Museum registry. A record may be scoped without asserting
   `FULL_BHSM_COMPLETE` for the entire program.
4. Run `python tools/materialize_museum_science.py` twice; compare the generated
   bytes. Commit the canonical catalog and identical application/download
   copies. `--check` rejects stale catalog/source copies. Approved magnetic
   `g`, `a`, and `mu` entries populate the corresponding tracker cells; all
   reviewed outputs appear in their science exhibit with source provenance.
5. Run the Museum tests/build, scientific integrity and publication audits.
   Merge the reviewed change to `main`; the Pages workflow publishes updates
   to these existing exhibits. Publish the same source to the Sites mirror.

The registry is initially empty because no qualifying physical outputs were
identified for this publication pass. Existing structural results and
historical screens remain useful and visible under their original status.
No forecast date or invented percentage implies that a missing gate is closed.

## Other work

The cosmic enclosure cycle is a separate author-described conceptual model.
Its animation has no connection to the numeric promotion registry and cannot
change BHSM's physical status. See the [cycle context](museum/norman_cosmic_enclosure_cycle.md).
