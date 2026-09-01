# Museum asset provenance

- Nine animated exhibits and their static fallbacks are synchronized from
  `../docs/assets/`. The lead exhibit is the deterministic PR #98 animation of
  CMS dimuon Open Data Record 303; its compact sample, pinned source checksum,
  DOI, CC0 license, and benchmark boundary live under
  `../docs/assets/pr98_cms_open_data_animation/`.
- The CMS animation still is also used as the social preview. The other eight
  exhibit records are indexed by `../docs/assets/bhsm_readme_visual_status.json`.
- `public/bhsm-symbol.svg` is reused from the sibling Bubo Research Node project
  (`frontend/src/assets/bhsm-symbol.svg`). That project identifies the mark as
  an original repository asset and publishes it under the MIT License.
- `public/cms-detector-simon-waldherr.jpg` is the photograph “CERN LHC CMS 15”
  by Simon Waldherr (2019), downloaded from Wikimedia Commons and used under
  CC BY-SA 4.0. It is unmodified apart from browser-responsive presentation.
  Source: https://commons.wikimedia.org/wiki/File:CERN_LHC_CMS_15.jpg
  Downloaded 1280-pixel derivative SHA-256:
  `94A31A6DD05C7CEC9326D37AA4DEFB5CCDF6D0ECACD287A0E86FCA2CDEE06B78`.
- Lucide interface icons are supplied by the declared `lucide-react` package.
