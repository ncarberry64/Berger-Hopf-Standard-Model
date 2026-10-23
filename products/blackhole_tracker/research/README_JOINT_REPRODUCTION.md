# Reproduce the2023 joint research campaign

Software source/citation: the formal [BHSM repository](https://github.com/ncarberry64/Berger-Hopf-Standard-Model).
This is an exploratory research mass route. All three prespecified real-data
candidates failed adequacy; running the code does not automatically identify a
black hole. The100-event photometric pilot is a separate frozen analysis.

1. Obtain `BHSM_OB110462_2023_SourcePack_v1.zip` from the accompanying BHSM release.
   Its SHA256 is `71d36a03e4ba275e91bea62f4784a5193f34ad32d3777b637453f91151bafa99`.
   The pack also contains primary URLs, rights/citations and an independent
   fetch/verification helper. Keep the downloaded author observations unchanged.
2. Use the recorded environment for exact input/time-bit reproduction:
   Python3.14,NumPy2.4.6,SciPy1.17.1,Astropy7.2.0. Install the product and its
   astrometry/dev extras, then run the19 focused joint tests. A different
   environment is a separately recorded reproduction if derived times change;
   the wrapper refuses to silently mix results.
3. From the formal BHSM repository root, verify the exact observations without fitting:

   ```powershell
   python products/blackhole_tracker/research/reproduce_joint_campaign.py --sourcepack "PATH/TO/BHSM_OB110462_2023_SourcePack_v1.zip" --output "PATH/TO/NEW_OUTPUT" --verify-only
   ```

4. Run the full frozen campaign in that output directory:

   ```powershell
   python products/blackhole_tracker/research/reproduce_joint_campaign.py --sourcepack "PATH/TO/BHSM_OB110462_2023_SourcePack_v1.zip" --output "PATH/TO/NEW_OUTPUT"
   ```

In the manuscript development workspace, replace `products/blackhole_tracker/`
with `product/` in those commands. The formal BHSM repository is the reviewer source.
The wrapper works from any current directory when invoked by its absolute path;
`--repository` can explicitly select the checkout. The package is located as
either development `product/` or formal `products/blackhole_tracker/`; the
script also resolves its own package location independently of current directory. It verifies all three frozen scientific/import/workflow source pins and raw
hashes, imports15533nativeOGLErows while retaining the published12500-row primary
window plus21HSTphotometric/21angularrows, records the environment/citation,
and copies byte-exact original drivers into output. No C: workspace path is
required. ZIP extraction checks traversal/symlinks and preserves existing bytes.

Default stages run G0/G1/G2 with16 starts and fixed1800-evaluation continuations,
31-point and refined conditional mass profiles, the disclosed original UTC
conditional prediction and corrected v2.1 whole-night prediction, and20 fixed-seed
parametric controls per OU family (including truth profiles/night predictions).
The complete run can take substantial computing time. `--stages` can select
`baselines,profiles,predictions,controls,summary`; completed compatible outputs
are reused after strict schema/input/source/likelihood and baseline linkage
checks. Twenty-control completion requires all full sample artifacts. Unknown
stage names are rejected. Incomplete control outputs are copied to a resume snapshot before
regeneration. Every command and log is retained. Use a separate output per
concurrent campaign/environment.

`joint_campaign_drivers/ORIGINAL_DRIVER_MANIFEST.json` pins the original driver
bytes; scientific source6eaf0504... and internal protocol/source commit5bb9419...
are independently pinned. Drivers remain unchanged; the wrapper supplies portable
locations and structured command arguments. Full native fits/controls belong in
external audit/release storage, avoiding repeated10MB datasets inGit. The public
audit retains compact tables, profiles, controls summaries and diagnostic plots.

Interpret results using the versioned acceptance receipt. An optimizer can converge
and still fit an inadequate noise model. Profile support levels are conditional,
cap/unresolved points interrupt limits, and20local controls do not establish precise
coverage. Unknown-target use needs explicit physical domains/initial guesses,
verified time/frame/astrometry and independent darkness evidence. No absent mass,
distance,absolutePM,horizon or core quantity should be filled from duration.
