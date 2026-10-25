BHSM Blackhole Tracker candidate localization inventory, 23 October 2026

This metadata deliverable maps 155 distinct historical source/event directions:
the complete frozen100-event pilot and all59 Wyrzykowski2016 parallax events,
with four independently rechecked shared identities counted once. Every pilot
fit outcome, including89 inadequate simple fits, is retained. A separate
benchmarks array contains the literature-positive OGLE-2011-BLG-0462 system.
It is not part of the155-event count. The optional benchmark adds one marker.

Three entries are investigation targets for different reasons. OGLE3-ULENS-0585
and3092 passed the existing frozen photometric followup screen. This screen
does not distinguish a BH from other lenses; duration alone is not a mass.
PAR-13 retains a specifically disputed BH-scale, population-conditional
literature possibility: unreliable Gaia source astrometry and an alternative
lower-mass inference are explicit. This is not a newly identified BH candidate.
No new numerical ranking is claimed, and no atlas event has an accepted engine
BH interpretation or measured lens mass, distance or absolute motion.

The13 historical dark-remnant-consistent entries include white dwarfs and
neutron stars; they are not13 BHs. The later2021 primary reanalysis is retained
alongside the2016 interpretation. In particular, the old strong-BH interpretation
of PAR-02 must not be treated as current evidence: the later population model
favors a roughly0.9 solar-mass bulge star. These are prior-dependent literature
interpretations, not observations imported into the tracker likelihood.
https://arxiv.org/html/1509.04899v2
https://arxiv.org/html/2107.13701v1
https://ogle.astrouw.edu.pl/cont/4_main/len/oiii-bhs/

The benchmark's strong-BH classification is explicitly from the literature,
using angular microlensing, parallax and lens-light evidence. The current
tracker recovery remains NOT_ESTABLISHED_NUMERICAL_STAGE_UNRESOLVED. Published
mass values were not used as optimizer targets or promoted to engine results.
https://doi.org/10.3847/1538-4357/adbe6e
https://arxiv.org/html/2503.07820v2

Sky markers identify printed catalog source/event directions. J2000 is the
catalog equinox, not a supplied observing epoch. All inferred lens positions,
position uncertainties, distances, masses, absolute proper motions and radial
velocities remain null. No three-dimensional or propagated lens position is
available here. An empty map region does not establish absence of black holes.

Offline metadata rebuild, with Python3.11 or later and no third-party packages:

    python build_inventory_v3.py --freeze INPUT_FREEZE_v3.json --out replay.json
    python test_inventory_v3.py

Choose an output filename that does not already exist; the builder uses an
exclusive write. The output must match inventory_v3.json byte for byte:
SHA256 4a76300f0e0e3883a0c9c343e1e0c5fbead595c9b4f333aaa01ec05c9ec9debc

All classification and exact-identity association rules rerun from16 factual
metadata snapshots. They include100 selected original catalog lines, all100
derived pilot outcomes, all59 declarations and142 degenerate published model
summaries, printed2021 Table1 cells,26 native-table availability records, and
compact benchmark metadata/outcome. These are not resolved images, manufactured
observations or new likelihood inputs. Full article HTML, the complete2015
catalog, native photometric rows and the complete2025 observed input are absent.
The original42 source files were independently hash-checked before and after
snapshot preparation. Original source paths survive only as provenance traces;
offline rebuilding does not read them. Tests also rebuild from a relocated
snapshot while forbidding all reads of the original source paths.

The raw photometry availability audit records23 older ClassA and3 ClassB tables,
19068 original rows, and33 unavailable exact-ID matches. It does not claim that
these older2015 files equal the dedicated2016 reduction, outlier masks or
calibration. Offline rebuilding verifies the availability-audit metadata, not
the unbundled original observations again. Clock scale and covariance stay null.
No error rescaling or clipping is applied to observations by this inventory.

Researchers who independently obtain original files can additionally provide
a JSON role-to-local-file map to --source-map. Paths may be relative to that map.
Every supplied original is checked against its original byte count and SHA256.
Original URLs, source hashes, snapshot hashes and extraction rules appear in
INPUT_FREEZE_v3.json. Some original inputs are earlier derived metadata artifacts;
their primary URL is a citation, not a promise of an identical derivative file.
The metadata snapshots suffice for the complete offline atlas assembly.

Rights and attribution: this pack contains BHSM-generated analyses and factual
catalog/model metadata with source attribution. It does not redistribute OGLE
native light curves or assign them the BHSM software license. Access to public
data and a citation request do not grant a blanket raw-observation license.
The source papers, CDS metadata and OGLE source-specific terms remain separate.

BHSM interpretation: one ordinary compact-lens Einstein/GHY exterior optical
response is counted once. No additional core/envelope potential is introduced.
The optical data here do not uniquely identify a membrane, core state or horizon.
Formal software, reviewer repository and metadata citation:
https://github.com/ncarberry64/Berger-Hopf-Standard-Model

Earlier inventory/builder drafts are preserved outside the portable v3 package.
No existing raw observations, frozen analysis, repository or release was changed.
