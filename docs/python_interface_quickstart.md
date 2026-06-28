# Python interface quickstart

Install the repository environment:

```powershell
python -m pip install -e .
```

Define a geometry and inspect its dimensionless outputs:

```python
from bhsm.interface import HypersphericalGeometry

geometry = HypersphericalGeometry(
    curvature_indices=(5.0, 2.0),
    hopf_coefficients=(1.0,),
    anisotropy=1.15,
    boundary_coupling=0.8,
    sector="reviewer_example",
)
print(geometry.geometric_metric())
print(geometry.geometric_tension())
```

Calibrate and solve explicitly:

```python
from bhsm.interface import GeometricUnitMapper, ParticleMassSolver

mapper = GeometricUnitMapper.from_anchor(
    anchor_tension=geometry.geometric_tension(),
    anchor_mass_gev=80.3692,
    anchor_particle="W_boson",
    anchor_source="PDG 2024 W-boson listing",
)
result = ParticleMassSolver().solve_mass(
    geometry, "W_boson", initial_guess_gev=80.0, mapper=mapper
)
print(result.to_dict())
```

If a particle mass is used to calibrate the geometric-to-physical unit scale, that same particle cannot be counted as an independent prediction in that run.

Run the offline examples:

```powershell
python examples/bhsm_solve_w_and_neutrino.py
python examples/bhsm_custom_geometry_scan.py
```

Inspect the prediction registry and build an offline report:

```powershell
python -m bhsm.interface registry
python -m bhsm.interface report --anchor W_boson --particles W_boson,electron_neutrino --format json
```

The v1.2.0 release-candidate quickstart is indexed at
`docs/bhsm_v1_2_0_python_quickstart.md`.

```powershell
python -m bhsm.interface gallery --format markdown
python -m bhsm.interface notebook-pack --check
python -m bhsm.interface theorem-blockers
```

The electron-neutrino comparison is treated as an upper-limit comparison unless a vetted central experimental mass reference is explicitly supplied.

Run focused tests:

```powershell
python -m pytest -q tests/test_python_interface_*.py
```

For completed BHSM formulas, pass custom metric, tension, or residual callables;
do not treat the default interface equations as a theorem.
