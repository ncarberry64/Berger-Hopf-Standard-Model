# Separate-paper Git handoff

The manuscript and calculation are complete as a standalone package. The
connected GitHub integration rejected creation of the branch
`research/bhsm-angular-lensing-20261021` with HTTP 403, “Resource not accessible
by integration.” No remote branch, commit or pull request was created by this
release operation. The existing PR #23 was not changed.

The supplied binary-capable patch adds only
`papers/bhsm_angular_lensing_20261021/` to the manuscript repository. It does
not edit earlier papers, numerical inputs or repository-wide configuration.
It can be reviewed and applied from a normal authorized local Codex workspace.

Recommended repository: `ncarberry64/Manuscript-Generation`.
Read-only base inspected for this handoff:
`5fd65ea18a6055dbc6028839c2918415e3c00f71` on `main`.
No `AGENTS.md` was present in that complete inspected tree. Check current
workspace instructions if the repository has changed before applying.

## Apply from an authorized local repository

Use a clean worktree based on the intended current main branch. Then:

```bash
git switch -c research/bhsm-angular-lensing-20261021
git apply --check /path/to/BHSM_Angular_Lensing_New_Paper.patch
git apply --index /path/to/BHSM_Angular_Lensing_New_Paper.patch
python papers/bhsm_angular_lensing_20261021/scripts/reproduce.py
python papers/bhsm_angular_lensing_20261021/scripts/build_manuscript.py
git diff --cached --stat
git commit -m "Add standalone BHSM angular transfer and time-delay paper"
```

The patch includes the reviewed PDF, source, figures, exact source identities,
response arrays and calculation receipts. A local replay can regenerate them;
review any generated differences before a further commit. Push the new branch
and open a **new draft PR** when that workspace's repository access permits it.
Do not fold this paper into the earlier observed-lens sprint by default.

## Suggested PR description

The retained closed BHSM effective realization had no standalone application
of its full n=2 angular family to linked shear and strong-lensing delays.
This paper derives and computes those responses for all six physical anchor
coordinates, then evaluates a specified nodal quadrupole with a fixed physical
SIS and source displacement.

The worked prediction is a cos(2 phi) delay response with amplitude
0.35321609 seconds at lens/source redshifts (0.3, 1.0) for the declared
normalized density seed. The paper also supplies an exact effective-potential
correspondence and a restricted shared-lens source-redshift contrast.

All nine offline replay stages completed. Independent angular-ray,
Jacobi-equation, image-solve, SI-unit and effective-potential checks accompany
the manuscript. The PDF compiles without unresolved references or overfull
boxes and was visually reviewed. No observational target data are used.

The effective action and initial amplitude remain conditional. The SIS is a
prescribed local encounter. The work claims neither microscopic state
selection nor observational detection or general mass-sheet degeneracy
breaking. Funding and competing-interest declarations require author
confirmation before journal submission.
