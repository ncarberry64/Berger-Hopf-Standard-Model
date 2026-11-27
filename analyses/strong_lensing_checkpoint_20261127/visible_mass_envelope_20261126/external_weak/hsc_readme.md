# galaxy_halo_connection_in_HSC
This repository contains various measurements performed for the publication titled - "Galaxy-dark matter connection of photometric galaxies from the HSC-SSP Survey: Galaxy-galaxy lensing and the halo model"

```bash
.
├── abundances
│   ├── I20_z1_abundances_z0.30_to_0.55.csv
│   ├── I20_z2_abundances_z0.55_to_0.80.csv
│   ├── M13_double_schechter_func_abundances_z0.2_to_0.5.csv
│   └── M13_single_schechter_func_abundances_z0.5_to_1.0.csv
├── radialbins.csv
├── README.md
├── wls_covariance_matrices
│   ├── cov_mat_z1_stelM_thresh_10.0.txt
│   ├── cov_mat_z1_stelM_thresh_10.2.txt
│   ├── cov_mat_z1_stelM_thresh_10.4.txt
│   ├── cov_mat_z1_stelM_thresh_10.6.txt
│   ├── cov_mat_z1_stelM_thresh_10.8.txt
│   ├── cov_mat_z1_stelM_thresh_11.0.txt
│   ├── cov_mat_z1_stelM_thresh_8.6.txt
│   ├── cov_mat_z1_stelM_thresh_8.8.txt
│   ├── cov_mat_z1_stelM_thresh_9.0.txt
│   ├── cov_mat_z1_stelM_thresh_9.2.txt
│   ├── cov_mat_z1_stelM_thresh_9.4.txt
│   ├── cov_mat_z1_stelM_thresh_9.6.txt
│   ├── cov_mat_z1_stelM_thresh_9.8.txt
│   ├── cov_mat_z2_stelM_thresh_10.0.txt
│   ├── cov_mat_z2_stelM_thresh_10.2.txt
│   ├── cov_mat_z2_stelM_thresh_10.4.txt
│   ├── cov_mat_z2_stelM_thresh_10.6.txt
│   ├── cov_mat_z2_stelM_thresh_10.8.txt
│   ├── cov_mat_z2_stelM_thresh_11.0.txt
│   ├── cov_mat_z2_stelM_thresh_11.2.txt
│   ├── cov_mat_z2_stelM_thresh_9.0.txt
│   ├── cov_mat_z2_stelM_thresh_9.2.txt
│   ├── cov_mat_z2_stelM_thresh_9.4.txt
│   ├── cov_mat_z2_stelM_thresh_9.6.txt
│   ├── cov_mat_z2_stelM_thresh_9.8.txt
│   ├── wlsErr_zbin_1.csv
│   └── wlsErr_zbin_2.csv
├── wls_lenses_threshold_bins
│   ├── wls_zbin_1.csv
│   └── wls_zbin_2.csv
├── zbin_1_constraints.csv
└── zbin_2_constraints.csv
```

* Files and Directories related to Measurements of observables from data:

	* radialbins.csv: The 10 radial bins used for the measurement of lensing signals in this work.
 
	* abundances: measured abundaces of the stellar mass threshold samples from `Ishikawa et al. 2020` (I20).
 
	* WLS_lenses_threshold_bins: Measured Weak Lensing Signals for the same thresholds.
		* wls_zbin_\*.csv: Signals for redshift bins 1 and 2.
 
	* WLS_covariance_matrices: Covariance matrices obtained from above measurements using Jackknife technique.
		* cov_mat_z\*\_stelM_thresh_\*.txt: Covariance matrices for the 10 radial bins. Read this file as a numpy matrix. Elements i,j correspond to the covariance between i^{th} and j^{th} radial bin in a given threshold sample.
		* wlsErr_zbin_\*.csv: Square root of the diagonal components of the matrices = standad deviation of the lensing signal in each of the 10 radial bins, obtained for each stellar mass threshold sample.

* Files and Directories related to modelling of the observables:
	* zbin_*_constraints: 1-sigma constraints from joint fitting of lensing of HSC galaxies with abundances from I20.
