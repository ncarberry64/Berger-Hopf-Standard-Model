# Museum content update — 24 September 2026

## Claims, calculations and open scientific review — 30 September 2026

Applied the accepted editorial approach throughout the twelve science/record
exhibits: attributed BHSM statements lead, animations and existing numerical
results remain central, and expandable review sections collect source links,
scoped limitations and a concrete reproduction or critique question. The R1
statement surfaces its retained rank-two result at all eight audited post-anchor
epochs; the local-certificate heading names the eight interval-13 cells.
Historical comparisons remain historical screens, with their numerical values
and reference editions unchanged. No numerical match is promoted to an
independently selected physical prediction.

The welcome slide invites visitors to explore claims, inspect calculations and
help test what follows. Sources & links introduces the museum as a living, open
scientific review forum and distinguishes public scrutiny from journal review.
Each review section opens a prefilled GitHub issue draft for the visitor to review
and submit; nothing is submitted automatically. The AI-readable catalog and guide
carry the same statements and review questions.

Validation: 35 Node tests, 13 museum Python tests, TypeScript, focused lint,
production export and all five publication audits passed.
Browser checks confirmed all twelve review sections, correctly scoped issue-draft
links, source links and 390px readability. Existing scientific classifications,
frozen predictions and numerical source files are preserved. Two presentation
tests were updated to verify relocated scope statements in the review sections
instead of requiring the former headline wording.

## Scrollable panels, matter explanation and AI search fallback — 30 September 2026

All three Children of BHSM panels now have matching viewport-relative heights,
independent vertical scrolling, visible scrollbars, sticky headings and keyboard
focus. Structure cards use natural-height columns, removing the molecule card's
stretch to the much taller atom card. The phone layout keeps one structure column.

Exhibit 4 identifies the repeating charged-lepton/neutrino/up-quark/down-quark
family pattern and explains the projected Hopf-fiber animation and family selector.

The AI handoff now supplies ordinary GitHub file pages alongside raw URLs and a
capability-aware BHSM search plan. It directs assistants to use available search,
browsing, connectors or local sources before asking for excerpts, without claiming
access to unread material or changing completion obligations. Clipboard failure
reveals a selectable JSON field and download link immediately beside the button.

Validation: TypeScript, focused lint, 34 Node tests, 13 museum Python tests and
production export and all five publication audits passed. Repeated guide generation
was byte-identical. Desktop
and 390px browser checks covered independent keyboard scrolling, natural molecule
height, example selection and the Exhibit 4 text. Successful-copy feedback was
verified; a controlled denial fixture verified valid, fully selectable fallback
JSON. The automation's virtual clipboard did not expose the browser's successful
clipboard write, so end-to-end paste was not asserted in this run.

## AI handoff and animated particle families — 28 September 2026

Added a “Copy BHSM for AI” button to the welcome slide and Sources & links.
It copies a provider-neutral JSON packet pointing to the public GitHub repository,
current status, claim boundaries, existing definition of done and gate ledger.
The packet asks assistants to read and cite sources, preserve their scope and
report inaccessible material. It creates no new scientific completion criteria.
A manual-copy field and JSON download provide alternatives to clipboard access.
The museum does not host a language model or transmit visitors’ questions.

Added deterministic, public `llms.txt`, `ai/index.json` and `ai/handoff.json`
assets, with all 13 exhibits mapped to scoped summaries and source links.
Generation runs with asset synchronization and static export validates the map.
The guide distinguishes mutable repository sources from dated museum snapshots.

Removed Helium from the atom selector while retaining the Helium-4 nucleus.
Hydrogen and Carbon use explicit identities so their seven- and three-orbital
sets remain correct. Animated family halos now surround all 18 Standard Model
labels; the labels stay fixed and the existing motion/visibility controls govern
the animation. Halos and labels scale to narrow phone cards.

Validation: 34 Node tests, 13 museum Python tests, TypeScript, focused lint,
production build/static export, byte-identical repeated guide generation and all
five publication audits passed. Browser checks verified actual copy/paste of
valid JSON, the manual-copy panel, Hydrogen/Carbon choices, motion/pause and
390px/desktop layouts without page overflow or console errors.

## Orbital densities, matter cycle and large-scale structures — 28 September 2026

Replaced the atom waveform sketches with code-rendered, glowing hydrogenic
probability-density sections inspired by the supplied reference. Hydrogen has
seven selectable orbital views (1s, 2s, 2p, 3s, 3p, 3d and 4f); helium and carbon
offer illustrative occupied-orbital shapes. The view rotates, while the underlying
density stays fixed. Each image has its own brightness and spatial scaling;
many-electron examples are explicitly illustrations rather than full solutions.
The center marker and the two nucleus illustrations have circular outlines.

Matter now cycles solid, liquid, gas and plasma every six seconds on the existing
visibility-aware museum clock. Manual selection holds a state; a cycle control
resumes the sequence. Automatic cycling suppresses live-region announcements.

Removed Earth and Sun from astronomical structures. Added BAO, Laniakea,
the Great Attractor and Shapley alongside the Milky Way and cosmic web.
The BAO scene represents a statistical separation preference, and the attraction
scenes are qualitative rather than survey reconstructions. Source links point to
ESA, ESO and the original Laniakea research paper.

Validation includes exact radial/angular-node checks, symmetric finite density
sections, byte-identical repeated raster generation, and cycle order/hold tests.
TypeScript, focused lint, static export, 31 Node tests, 13 museum Python tests
and all five publication audits passed. Browser checks covered all seven
hydrogen orbitals, the carbon orbital subset, all six cosmic choices, visible
nucleus outlines, automatic cycling/manual hold, global pause, and desktop,
tablet and phone layouts. The rotating image uses a soft aperture to avoid
exposing the square raster edges.

## Selectable structures and quantum illustrations — 28 September 2026

All six structures-across-scales cards now offer independent selections: 18
examples spanning hadrons, nuclei, atoms, molecules, matter and cosmic structures.
Selecting an example changes its SVG, accessible description, explanation and
pressed state. Keyboard activation uses native buttons and selections survive
exhibit navigation.

Proton and neutron views show their distinct valence-quark content with animated,
labeled gluon exchanges. Hydrogen, helium and carbon show waveform packets
inside stationary probability envelopes, including directional p lobes for
carbon. Captions distinguish illustrative phase motion from stationary density
and from classical trajectories. DOE and OpenStax references are linked locally
to those cards. The molecular choices show bent H2O, linear double-bonded CO2,
and a DNA double helix. Each remaining choice also has a distinct scene.

Validation: TypeScript, focused lint, static production export, 28 Node tests,
13 museum Python tests, and all five publication audits passed. The initial
Python invocation from the museum subdirectory failed to import the root tools
package; rerunning from the repository root passed. Browser checks exercised
all 18 selections, unique scenes, matching accessible descriptions, keyboard
activation, pause/resume, and desktop/tablet/phone layouts without page overflow.

## Children of BHSM example showcase — 28 September 2026

Expanded all three welcome-map panels with named examples and explanations.
The foundation cards show a rotating projection of S³ in R⁴, three standing-wave
harmonics, and overlapping hexagonal patterns that produce a changing moiré
pattern. The supplied hypersphere-only statement is explicitly a BHSM proposition.
The six structures cards show a proton, helium-4 nucleus, hydrogen cloud,
vibrating water molecule, four states of matter, and spiral galaxy, with further
examples listed in each card. Standard Model families also have short explanations.

All nine scenes share the existing visibility-aware scene clock and global motion
preference. Animations remain schematic rather than new numerical predictions.
Responsive cards retain the museum palette, slide navigation and soundtrack.

Validation: TypeScript, focused lint, production build/static export, 28 existing
Node tests, 13 museum Python tests, and all five repository publication audits
passed. Browser checks covered 1440px desktop, 768px tablet and 390px phone
layouts, absence of horizontal overflow, pause/resume, and no console errors.

The existing museum now presents the September cosmology results in context,
the ready interval-13 BHSM numerical certificates in the numerical-research
exhibit, and the previously verified museum authenticity corrections.
Exhibit order, styling, motion controls, soundtrack, CMS data and historical
screen values are retained. No new physical particle observable was promoted.

Source inventory, exact snapshots, hashes and exhibit-by-exhibit disposition:
`public/research/museum-update-record.json`.

The R1 environment-to-topography transfer has numerical rank two at eight
audited post-anchor epochs. Spatial-profile selection and microscopic
normalization remain open. The manuscript integration is explicitly labeled
pending full-suite validation at the retained snapshot. Eleven focused
upstream checks passed; this museum update does not claim a completed upstream
full suite.

The Pantheon and DES held-out comparisons are conditional results, not an
established coherent residual. Prospective Gate A/B tests remain separate.
The January animation stays labeled as a historical schematic.

BHSM interval 13 has an eight-cell physical-tube certificate. The subsequent
signed-remainder upper bounds do not certify the sufficient targets; they are
not global kappas or evidence of physical instability. Gate 7 remains open.

## Validation

- TypeScript check and production build passed.
- Six existing interaction/numerical demonstration tests passed.
- Seven unchanged museum regression checks passed against this checkout.
  The old January-only label assertion was superseded by checks for the new
  September/historical-animation labels; its motion, fallback and asset
  requirements were retained and checked.
- All 15 research snapshot hashes verified. The eight saved environmental
  matrices independently reproduce rank two and nonzero matter-only minors.
- All 34 historical ledger entries are retained. CMS, scalar-monitor and
  sandbox JSON values equal the previous Site source. Conventional reference
  values and uncertainties are unchanged; four quantity labels were corrected.
- Local HTTP preview returned 200 with the new content. Browser inspection
  confirmed the cosmology layout and preserved museum navigation.
- BHSM source status, forbidden-claim, frozen-integrity and precision audits
  passed. Its public-readiness audit passed all categories except hygiene:
  five existing oversized research files lack approved size exceptions.
  Those files are not included in this Site or its deployment archive.

The standalone science collection was built twice identically with the
canonical exporter. Frozen scientific code and manuscripts were not modified.

## Animation replacement

The current cosmology exhibit now leads with an interactive four-map R1
realization: specified matter-density and velocity-potential patterns drive
the two topographic components through the retained physical-basis matrices.
Nine discrete frames cover the anchor and eight audited later epochs. Playback
stops at the present reference epoch and can be replayed or stepped manually.
Aligned, independent and zero environmental presets change both the visible
fields and the nine-coefficient output rows. Radiation and initial topography
are zero; all environmental coefficients are chosen illustrative inputs.

Globe colors are normalized per panel to reveal shape. Euclidean coefficient
norms and signed coefficients retain amplitude information. View rotation does
not rotate the physical axis. The fixed S3 slice and explicit quadratic basis
are documented in the exhibit. No observed sky, continuous-interval rank
theorem, physical axis selection or early-Universe realization is claimed.

Four new numerical tests cover source equality, temporal/spatial rank, linear
transfer and the illustrative harmonic basis. Browser controls produce ranks
2, 1 and 0 for independent, aligned and zero inputs; the anchor is rank zero.
The 390px viewport has no page-width overflow. Historical visualizations and
the detailed science text are now disclosures below the new animation.

## Original cosmology exhibit restored — 26 September 2026

Restored the January proposal and full cosmic-cycle animation as a separate, visible cosmology exhibit alongside the R1 realization. Both exhibits have direct links to each other. Original animation controls and scientific context are preserved.

## Force exhibit animation — 26 September 2026

Replaced the force-tree visualization with five coordinated parametric mesh animations inspired by the supplied reference. Selectable strong, electromagnetic, weak, gravitational and common-origin studies retain the museum console and explanatory references. Playback, restart and timeline controls honor reduced motion and offscreen visibility. The animations are explicitly conceptual; the reference image’s electromagnetic-frequency claim for gravity is not promoted as physics. Both cosmology exhibits remain intact.

## GitHub Pages publication — 26 September 2026

Synchronized the public GitHub Pages museum with the reviewed Sites exhibits, including both cosmology sections and the animated Force studies. Updated the static exporter to verify the current exhibit labels and the original cosmology section. Corrected conventional reference labels at their canonical museum data source so the asset synchronization retains them.

Validation: production static export, TypeScript, 10 numerical/interaction tests, subdirectory asset checks, static-browser hydration and Force selection, immutable source hashes, repeated byte-identical asset synchronization, and all five required repository publication audits passed.

## Horizontal exhibits and particle studies — 26 September 2026

The museum now presents twelve full-width slides with native horizontal swiping,
previous/next controls, a labeled exhibit picker, arrow-key navigation and direct
exhibit links. Long exhibit content scrolls inside its own slide. Inactive slides
are inert, reduced motion is respected, and resizing preserves the current slide.
Both cosmology exhibits remain visible in the picker.

The electromagnetic study has a dense yellow cloud confined to its left cone.
Weak-force particles spiral into collisions within the right cone and scatter
as smaller red particles. The common-origin sphere contains a yellow cloud and
surface collisions that produce smaller red dots. These are deterministic visual
analogies without physical rates or scales. The earlier interactive force-line
diagram is restored below the five studies with its qualitative scope intact.

Validation: 13 Node tests, 13 museum Python tests, TypeScript, focused lint,
production build/static export, repeated byte-identical asset synchronization,
and all five publication audits passed. Browser checks covered deep links,
picker/buttons, keyboard and horizontal gestures, desktop/390px layouts,
resize preservation, and the restored force-line controls.

## Children of BHSM and interpretive descriptions — 26 September 2026

Added a responsive, code-drawn Children of BHSM map below the welcome panel:
proposed core/topology, modes and geometry; the Standard Model particle families;
and structures from hadrons to galaxies. Its caption distinguishes proposed
relationships from established categories. The diagram retains the museum palette
and typography and reflows vertically on phones.

Removed particle-color language from the Forces captions and accessible labels.
Electromagnetism now describes limited surface availability associated with the
FSC in the supplied BHSM interpretation; weak motion describes decay. The Aether
node and its selected readout explicitly describe the lack of spacetime support.
The conceptual scope and absence of quantitative calibration remain explicit.

Validation: production export, TypeScript, focused lint, 13 Node tests, 13 museum
Python tests, and all five publication audits passed. Browser checks confirmed
the desktop diagram, no horizontal page overflow at 390px, the Aether readout,
and absence of particle-color wording in the Forces exhibit.

## Soundtrack controls at the exit — 26 September 2026

Moved the soundtrack panel into the final Sources & links slide and removed
its fixed overlay positioning. Audio remains mounted throughout the museum,
with the existing playlist and interaction-triggered playback. Desktop and
390px browser checks confirmed continuous playback across slides and working
play/pause controls. TypeScript, static export, 13 museum Python tests, and
all five required publication audits passed.

## Music starts with the visit — 26 September 2026

The soundtrack now starts from the first accepted click, completed pointer/touch
gesture, or keypress. Playback is requested synchronously inside the gesture;
denied attempts retain the listeners for another interaction. Successful or
manual playback removes the fallback so subsequent navigation respects Pause.
Controls remain on the final slide with no floating panel. Removed the ungated
autoplay attempt so entry and sound begin together on visitor interaction.

Four startup regression tests cover gesture activation, rejected-play retry,
manual-player exclusion, and cleanup. Browser checks confirmed Enter the science,
keyboard activation, continued playback, and deliberate pause persistence.
TypeScript, focused lint, static export, 13 museum Python tests, and all five
required publication audits passed.
