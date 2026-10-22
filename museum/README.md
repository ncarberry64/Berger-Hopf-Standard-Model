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
The exhibit is a browser demonstration; inference runs in the local Python
application, not on the static Museum host. Preserve the research-license
notices supplied with the software.

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
