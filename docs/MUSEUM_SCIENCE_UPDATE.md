# The permanent BHSM science collection

The public Museum leads with collision theatre, the Blackhole Tracker research
product, magnetic moments in motion,
combined SM predictions/equivalence, force unification, common action and
spectral forecasts. Five numbered comparison exhibits follow. CMS animation
and numerical research remain in a separate data exhibit; cosmology follows
the author. Publication copy addresses visitors, not the implementation brief.

## Blackhole Tracker research-product exhibit

The `blackhole-tracker` exhibit provides an animated synthetic compact-lens
example, the reviewed local Python app, and links to the manuscript and
reproducibility record. Its mass, center and motion use one BHSM-interpreted
exterior optical potential. The ordinary fit and a conditional R1 response
are distinct; neither the animation nor a supported track establishes a
horizon, microscopic core modes, a physical core-transfer law, or a new
observed black hole. A declared enclosing radius is not a measured hard
boundary. This is a research-product exhibit, not a promoted physical
prediction in `approved_science_outputs.json`.

The 0.2.0rc3 correction adds a separate, explicitly labelled real-observation
panel: all 100 historical OGLE-III events and 76,344 native measurements were
processed without fabricated resolved-image data. Eighty-nine baseline
PSPL/diagonal-noise screens were inadequate; eleven passed the declared
chi-square screen and two met conservative archival follow-up criteria.
OGLE3-ULENS-0585 and OGLE3-ULENS-3092 remain `MASS_UNRESOLVED`; duration is
not a measured black-hole mass, and no new black-hole interpretation is
established. The known-system HST precision fit remains blocked by unresolved
timing/frame provenance. Neither a successful ordinary light curve nor a
failed simple model establishes a BHSM-specific core/envelope mechanism.

The public panel links all 100 annotated results, the frozen protocol,
qualified ranking and derived residual plots. Native raw observations remain
external, with hashes/acquisition/citation metadata in the paper's pilot
record. The animated resolved-image example is still synthetic and retains
its original independent source pin. Current versioned downloads and their
receipt are distinct from the unchanged historical 0.2.0rc2 bytes.

The Museum is static. It offers direct downloads and instructions for local
inference; it does not run the Python fit on GitHub Pages. Distribute the
reviewed product ZIP and wheel without rebuilding them, preserve their exact
SHA-256 bindings and canonical research-license notices, and use immutable
formal code/manuscript links while the integration is under review. Never
make a visitor's app access depend on the author's local server or checkout.

For setup and the complete run/export/replay path, see the
[researcher start](BLACKHOLE_TRACKER_RESEARCH_START.md). For Museum development
and publication, see the [Museum source guide](../museum/README.md).

## Current data and simulation boundaries

The collision theatre cycles between three deterministic two-body examples
and real CMS dimuon records. Visitors pause the animation to read the selected
event, or browse all 64 CMS events. Demonstrations use CODATA 2022 reference
masses and selected energies/angles in GeV; they calculate phase space, not
BHSM amplitudes or rates. Measured CMS subsystem invariant mass is not called
the full pp collision energy. Curved track shapes are normalized illustrations,
not propagated helices in a calibrated detector or reconstructed hit tracks.
The decay/stability ledger and its old tracker UI were removed at the author's
request; approved decay results can still be published in the same exhibit.

Magnetic moments in motion uses four explicitly sourced CODATA 2022 moments:
electron, negative muon, proton and neutron. All are spin-1/2 benchmarks.
The numerical Larmor frequency is 2|mu|B/h; the field-distance profile, cone
and logarithmically compressed playback are illustrative. This supersedes the
empty all-state tracker. Approved magnetic results remain connected to the
exhibit, without inventing a BHSM counterpart to the external reference.

The combined SM exhibit retains all 34 ledger entries and the conditional
representation/anomaly evidence. Force branching follows the author's
conceptual topology: gravity from electromagnetic, electromagnetic from weak,
through strong into the aether core. Its infinity symbol is a conceptual limit,
not a derived physical energy or observed coupling merger. Reference energies
have distinct physical definitions and do not form a monotonic energy axis.

`data/museum/experimental_references_20260907.json` contains external comparison
references from CODATA 2022, PDG 2025 and NuFIT 6.0 (2024), with URLs, conventions
and uncertainties. They are comparisons only, never upstream BHSM inputs.
NuFIT values use normal ordering, IC24 with SK atmospheric data. The neutrino
gap ratio uses central values without inventing an uncertainty from an unknown
covariance. CKM experimental/theory errors remain separate. The original
September 2 sandbox snapshot is unchanged and accessible. `sync:assets`
mirrors the external references into the app and public downloads.

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
   copies. `--check` rejects stale catalog/source copies. All reviewed
   outputs appear in their science exhibit with source provenance.
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
