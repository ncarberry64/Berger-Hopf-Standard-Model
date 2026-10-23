# BHSM Museum source

The Museum presents animated, interactive exhibits connected to the formal
[BHSM research repository](https://github.com/ncarberry64/Berger-Hopf-Standard-Model).
The [public Museum](https://ncarberry64.github.io/Berger-Hopf-Standard-Model/)
and its [Sites mirror](https://bhsm-reconstructed-museum.ncarberry64.chatgpt.site)
retain the same scientific distinctions. Museum demonstrations and comparison
references do not supply inputs to BHSM solvers.

## Review the Blackhole Tracker manuscript

Start with the [researcher guide](../docs/BLACKHOLE_TRACKER_RESEARCH_START.md)
for the paper, reviewed PDF, formal code citation, local app and complete
export/replay workflow. The [Blackhole Tracker exhibit](https://ncarberry64.github.io/Berger-Hopf-Standard-Model/#blackhole-tracker)
adds a synthetic animation and access to the reviewed product downloads.
The primary-target panel designates previously published Gaia18ajz as
the provisional lead, preserves all eight literature alternatives and keeps
the known OB110462 benchmark and brown-dwarf comparison separate. Its exact
target program and evidence-status record are under
`public/research/blackhole-tracker/primary-target-20261023-v1/`. The program
changes neither the frozen 155-direction atlas nor the 1,808-model spectrum.
The animation remains an independent synthetic teaching model; it supplies no
measured Gaia18ajz lens track. Scientific publication and public deployment
remain held for the candidate/evidence review. The prepared RC6 distribution
binds the tested product ZIP, wheel, 49-page reviewed PDF and complete source
packet to their exact hashes and immutable formal product/paper/reviewer pins.
Its 266 upstream product files and 891-member reviewer packet retain the
318-test/66-subtest software verification scope. One new notebook was executed
in RC6; the first five notebooks retain their historical execution evidence.
The exact RC5 receipt and all 14 referenced artifacts remain unchanged beside
the older releases. `DISTRIBUTION_0.2.0rc6.pending.json` is an immutable record
of the earlier incomplete preparation; its null fields are historical and do
not describe the final RC6 distribution. No local build or review asserts a
public deployment, journal submission or confirmed candidate result.
The envelopment-search narrative follows the immutable
[23 October author clarification](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/blob/7ebc9f226e0d9abc68e2ec61c90a8b262081c733/docs/BHSM_TRACKER_ENVELOPMENT_SEARCH_CLARIFICATION_20261023.md).
It asks which kinds of envelopment could produce the hypersurface's
gravitational topography. The author's **BHSM envelope-boundary differential**
is broader than conventional rotational frame dragging; ordinary rotating
matter can produce the conventional effect. Compact, extended and
dark-matter-like responses need explicit models and discriminating data;
identical optical responses stay degenerate. This wording adds no classifier,
spin measurement, hypersphere radius or second gravitational response.
Release 0.2.0rc4 retains the separate frozen real-observation pilot:
100 historical OGLE-III events, 76,344 native measurements, 89 inadequate
simple-model/noise screens, 11 passing chi-square screens and two qualified
archival follow-up targets. Both target masses remain unresolved; no new
black-hole interpretation is established. A distinct 2023 known-system joint
astrometry/parallax benchmark tests three declared model/noise candidates.
Every candidate fails adequacy, so no reliable mass or new black-hole
interpretation is accepted by that campaign. Software checks and saved-state
replay do not override this negative result. The animation remains synthetic.
The exhibit is a browser demonstration; inference runs in the local Python
application, not on the static Museum host. Preserve the research-license
notices supplied with the software.

The 0.2.0rc2 download bytes and receipt remain under
`public/research/blackhole-tracker/history/0.2.0rc2/`. The exact rc3 receipt is
at `DISTRIBUTION_0.2.0rc3.json`, with an archive copy under
`history/0.2.0rc3/`. Its relative artifact URLs continue to resolve at the
release root without duplicating the large source ZIP. Current artifacts have
versioned filenames and their own distribution receipt. The real-pilot
public tables, protocol, provenance and two derived residual plots are under
`public/research/blackhole-tracker/pilot-20261022-v1/`; native per-point
observations remain external. `lib/blackhole-tracker-example.json` retains
the earlier immutable synthetic-fixture source pin independently of the new
product/paper release pins. The separate joint diagnostic figure, compact
provenance and unsent manual calibration-data request are under
`public/research/blackhole-tracker/joint-20261022-v2/`. The reviewed
`BHSM_OB110462_2023_SourcePack_v1.zip` contains exact author observations,
licenses, exposure-header prefixes and the verification/refetch helper. Its
third-party rights are preserved; BHSM licensing does not replace them.

Joint app research explicitly opts into Astropy: use
`Start_Blackhole_Tracker_Joint.cmd`, pass `--astrometry` to the base launcher,
or install the source/wheel with `[astrometry]`. Opening a page does not
install dependencies. The base resolved/native-photometry app remains a
separate installation contract.
`scripts/package-tracker-distribution.py` reproduces the portable wrapper from
the exact product-only source ZIP, its SHA-256, formal/upstream commit IDs and
release version. It adds the two canonical notices and a per-file source
manifest with deterministic ZIP metadata. Rebuild the current wrapper twice
and require byte-identical results before distribution; its own SHA-256 is
recorded externally in `DISTRIBUTION.json`. Historical rc3 artifacts keep their
original hashes and recorded failed CI distinctions.

## Develop and verify

Use Node.js 24 and pnpm 11.19, matching the existing CI. From `museum/`:

```text
pnpm install --frozen-lockfile
pnpm test:science
pnpm exec tsc --noEmit
pnpm build:pages
```

`pnpm dev` starts the local preview. `build:pages` compiles and exports the
static site to `dist/pages/`. The `prebuild`/`predev` asset synchronization
also regenerates the curated AI navigation. `dist/`, dependencies and local
preview state are build products, not research sources.

The deck order is declared in `lib/museum-slides.mjs`; review statements and
AI topics are in `lib/museum-review.mjs` and `lib/ai-guide.mjs`. Register new
exhibits consistently in those files and `app/page.tsx`. Reuse the deck's
visibility, pause and reduced-motion behavior. Verify controls, mobile layout,
direct fragment navigation and downloads in an actual browser.

`scripts/sync-assets.mjs` refreshes generated exhibit/data directories. Add
new generated assets to its explicit inputs or keep reviewed distributions
under their retained `public/research/` path. Source pins, manifests and
download hashes must agree before publication.

## Publish through the existing hosts

`.github/workflows/museum-pages.yml` builds and deploys GitHub Pages on
relevant `main` changes or manual dispatch. The existing `github-pages`
environment restricts deployment branches; a successful PR build does not
by itself publish the public site. Preserve that protection and the existing
audience. The Sites mirror uses the project ID in `.openai/hosting.json`;
update that project rather than creating a replacement site.

See the [Museum update contract](../docs/MUSEUM_SCIENCE_UPDATE.md) for
source-owned scientific promotion. Research-product demonstrations retain
their stated assumptions and do not promote unproved physical claims.
