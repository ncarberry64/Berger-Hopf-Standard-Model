# Museum asset provenance

- Nine animated exhibits and their static fallbacks are synchronized from
  `../docs/assets/`. The lead exhibit is the deterministic PR #98 animation of
  CMS dimuon Open Data Record 303; its compact sample, pinned source checksum,
  DOI, CC0 license, and benchmark boundary live under
  `../docs/assets/pr98_cms_open_data_animation/`.
- The CMS animation still is also used as the social preview. Its checked-in
  64-event, 128-vector sample is copied to `public/data/` for the interactive
  selector. The other eight exhibit records are indexed by
  `../docs/assets/bhsm_readme_visual_status.json`.
- The temporary spectrum reads
  `../data/museum/bhsm_simulated_particle_spectrum_v1.json`. Its dimensionless
  positions and intensities are deterministic simulated museum data; familiar
  particle labels are orientation references, not mass predictions or fits.
- `public/bhsm-symbol.svg` is reused from the sibling Bubo Research Node project
  (`frontend/src/assets/bhsm-symbol.svg`). That project identifies the mark as
  an original repository asset and publishes it under the MIT License.
- Lucide interface icons are supplied by the declared `lucide-react` package.
