# CERN ROOT Integration

This optional adapter exposes the BHSM-inspired direct boundary-coordinate map
inside a standard PyROOT `RDataFrame` workflow. It does not replace detector
propagation, track fitting, material interaction, Geant4, or experiment
software.

## Drop-in usage

```python
import ROOT
from bhsm_root import install, add_boundary_columns

install(ROOT)
df = add_boundary_columns(df, t="t", x="x", y="y", z="z")
```

The second line is the drop-in transformation. It adds:

```text
bhsm_radius
bhsm_ux
bhsm_uy
bhsm_uz
bhsm_minkowski_interval
```

The wrapper calls the header-only function:

```cpp
auto state = bhsm::root::MapBoundaryState(t, x, y, z);
```

## Runtime status

`OPTIONAL_ROOT_ADAPTER_NOT_RUNTIME_VALIDATED_IN_REPOSITORY_CI`

ROOT and a C++ compiler were unavailable in the development environment. The
API contract and generated `RDataFrame.Define` expressions are tested offline,
but live ROOT compilation and experiment-specific validation remain required.
