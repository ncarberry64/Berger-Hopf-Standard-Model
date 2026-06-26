# Runtime Asset Manifest

Machine-readable artifact:

```text
artifacts/BHSM_runtime_asset_manifest_v1_7.json
```

Tracked assets:

- Python;
- WolframScript;
- WolframKernel;
- Mathematica;
- FeynRules;
- optional FeynArts/FormCalc;
- MadGraph5_aMC;
- optional HepMC;
- optional ROOT;
- optional LHAPDF.

Wolfram assets are treated as restricted external runtimes. They are not
downloaded automatically and must be supplied through a licensed or otherwise
authorized installation.

FeynRules and MadGraph may be mapped or installed only from official/legal
sources. Large downloads are not committed to the repository by default.

