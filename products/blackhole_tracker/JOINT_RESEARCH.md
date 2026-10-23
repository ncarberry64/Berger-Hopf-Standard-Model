# Joint photometry and astrometry research

The formal source, software citation and reviewer record are the
[BHSM repository](https://github.com/ncarberry64/Berger-Hopf-Standard-Model).
The joint route preserves actual unresolved magnitudes and angular centroids.
It does not create resolved images, flux ratios, delays or distances.

Install the matching local wheel with its `astrometry` extra, including Astropy.
The ordinary resolved and native-photometry routes do not require this extra.

    python -m pip install "./bhsm_blackhole_tracker-0.2.0rc4-py3-none-any.whl[astrometry]"
    blackhole-tracker serve --open

For the complete Windows source package, double-click **`Start_Blackhole_Tracker_Joint.cmd`**. This is an explicit request to install/check Astropy in the package's local `.venv`; the standard launcher keeps the base installation. You can also run `Start_Blackhole_Tracker.cmd --astrometry --check-install` to install/check the extra and exit, then launch normally. Close an existing app before updating its environment.

For an existing Windows source environment, run `.\.venv\Scripts\python.exe -m pip install ".[astrometry]"` from the unpacked product folder. Linux/macOS users can run their virtual environment's Python with the wheel-extra installation command above. See [README.md](README.md#enable-joint-astrometry-explicitly) for complete setup commands. Opening a web page never installs dependencies.

Open **Joint astrometry research** in the app. Select the reviewed 2023
`BHSM_OB110462_2023_SourcePack_v1.zip` for direct native benchmark import,
import a versioned calibrated joint JSON, or verify and open a saved result.
The source ZIP's SHA-256 is checked before any contained data are imported.
It contains public author data and exposure headers with their own attribution
and rights; those rights are not replaced by BHSM licensing. No archived helper
is executed by the app. A result is never loaded automatically.
Choose the declared method, inspect its bounds and clock/frame assumptions,
then run all prescribed starts. Export the replay bundle before closing.
The app displays every row in each selected instrument and every angular row.
Reopening a result recomputes its recorded diagnostics and status as well as
its predictions; changing a saved label cannot certify a failed model. A
failed search keeps every attempted start in an explicitly downloadable
diagnostic JSON and supplies no converged physical parameters.

## What mass requires

The BHSM Einstein/GHY exterior has one ordinary compact-lens optical potential,
counted once. In that sector,

    theta_E^2 = kappa M pi_rel
    pi_E = pi_rel / theta_E
    M = theta_E / (kappa pi_E)
    mu_rel = theta_E / t_E

The code derives kappa from nominal solar GM and exact c/AU, with angles in mas.
Native angular centroids constrain theta_E and annual photometric parallax
constrains pi_E. A long event alone supplies neither scale. An unidentified
parallax, active artificial cap, missing noise checks or failed systematic
tests prevent a supported mass interval. A compact exterior does not identify
a horizon, the proposed nongeometric core or a separate membrane potential.
Absolute lens motion and lens distance require independent absolute-frame and
source-distance calibration. They remain unavailable in the relative-frame
benchmark. A black-hole interpretation additionally requires evidence against
a luminous stellar lens, incompatible binaries and other alternatives.

## Two retained method versions

`joint_mass.py` and `joint_workflow.py` preserve v1 exactly. Its known-system
diagonal fit retains residual correlation; its additive OU model fails the
noise controls. Its saved conditional point masses are diagnostic results,
not accepted black-hole measurements. The browser transports original JSON
text losslessly to preserve v1's numeric-spelling-dependent input hashes.

`joint_mass_v2.py` and `joint_workflow_v2.py` are a separately versioned extension
after the v1 diagnostics. They use a centered numerical time basis and
canonical numeric JSON hashing. The primary OU model preserves supplied
marginal errors. A separately declared scale-plus-floor calibration competitor
models effective errors as nuisance parameters without changing native errors.
Both use the complete normalized Gaussian likelihood, including determinant
cost. Neither covariance is claimed to have been supplied by the observers.
All model choices, failed alternatives and acceptance checks belong in the
validation record; selecting a model because its mass is desirable is invalid.

## Native known-system import

The 2023 route uses corrected author OGLE photometry and Lam & Lu's v2 HST
Table 2, with the matching 82 exposure headers and a hashed timing map. It is
separate from the original 2022 Zenodo benchmark; no ambiguous old epoch is
silently repaired. The importer requires these files in one directory:

- `OGLE-2011-BLG-0462-new.txt`
- `LamLu2023v2__hst_data_table.txt`
- `LAM_LU_2023_HST_EXPOSURE_TIME_MAPPING.json`
- `MAST_2023_Table2_header_receipt.json`
- `MAST_header_prefixes/` with the mapped header prefixes

Primary sources are [Lam & Lu 2023](https://arxiv.org/abs/2308.03302) and the
[corrected OGLE data deposit](https://doi.org/10.5281/zenodo.20056044).
Their corrections/error floors are already applied. Do not apply them again.
The calendar-to-exposure timing map gives observed visit windows; it does not
recover unknown author averaging weights. The OGLE underlying clock remains
an explicitly assumed convention with a required sensitivity check.

    blackhole-tracker joint import DATA_DIRECTORY joint_input.json
    blackhole-tracker validate joint_input.json
    blackhole-tracker joint fit joint_input.json joint_result.json --gp
    blackhole-tracker export-joint joint_result.json --output exported
    blackhole-tracker joint profile joint_input.json joint_result.json mass_profile.json
    blackhole-tracker replay exported --output replayed

Use `blackhole-tracker joint --scientific-version v1 ...` for archived v1.
Use `python -m bhtracker.joint_workflow_v2 --help` for detailed fit options.
Other targets require explicit `analysis.bounds` and `analysis.initial_guess`
in their input; the engine does not assume every event occurred in 2011.
No absent native clock, frame, covariance or angular measurement is inferred
from a catalog name or a published mass.

## Export, replay and acceptance are different checks

The bundle retains native input and raw bytes, exclusions, source-row IDs,
model options, all starts, predictions, residuals, a report, all-row plots and
a SHA-256 manifest. Forward replay verifies the exact scientific source and
saved state, including physical parameters. It does not rerun optimization.
Refit and fixed-mass profiling are separate commands and can take many minutes.

Before using a mass interval, inspect the complete competing-mode profile,
finite-grid crossings, nuisance boundaries, both noise tails and residual
dependence, simulation controls, calibration/brightness/season/seeing checks,
blocked predictive checks, timing and frame sensitivity, and lens-light
assumptions. A replay pass, optimizer success or scalar upper-tail p-value
alone does not establish scientific acceptance. Search aliases and prior
literature before any novelty claim. An archival follow-up is not a live alert.
