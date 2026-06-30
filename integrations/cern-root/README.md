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

`ROOT_ADAPTER_LIVE_COMPILED_IN_CI_NOT_PRODUCTION_VALIDATED`

CI configures CMake against the pinned official ROOT 6.30.06 container,
compiles an `RDataFrame` target, and executes it through CTest. ROOT and a C++
compiler remain unavailable in the local development environment. Documented
ROOT-file schema validation, detector-software integration, and institutional
performance validation remain required.

## Portable compilation

```bash
cmake -S . -B build -DBUILD_ROOT_INTEGRATION=ON
cmake --build build --config Release
ctest --test-dir build --output-on-failure
```

Generic-safe code is the default. `-DENABLE_AVX2=ON` and
`-DENABLE_AVX512=ON` are opt-in, mutually exclusive target options; use them
only for homogeneous nodes that advertise the selected ISA.
