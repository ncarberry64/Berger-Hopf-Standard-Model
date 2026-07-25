# BHSM HEP Environment Setup

These scripts provide a CERN-like institutional HEP handoff package for the
bounded minimal collider-interface subset.

They do not install proprietary Wolfram software, bypass licenses, fabricate
validation evidence, or generate fake event files. Use institutionally approved
runtime installations and map them through environment variables when needed.

## Windows CMake and ROOT

The native and CERN ROOT C++ targets require:

- CMake 3.20 or newer;
- Visual Studio 2022 Build Tools with the C++ workload;
- a ROOT binary built for Visual Studio 2022 and the installed Python ABI;
- ROOT's transitive runtime libraries.

The validated local combination is CMake 4.4.0, Visual Studio 2022 Build Tools
17.14, Python 3.11.9, ROOT 6.40.02 for `win64.python311.vc17`, and SQLite
3.53.4 x64.

The ROOT 6.40.02 Windows archive currently needs two packaging completions:

1. copy `bin\cppyy\libcppyy.pyd` to `bin\libcppyy.pyd` for PyROOT;
2. install the official x64 `sqlite3.dll` in `bin` for RDataFrame.

After those files are present, activate the local runtime:

```powershell
./scripts/setup/activate_bhsm_root.ps1
```

Use `-RootHome` and `-Python311` when the tools are installed elsewhere.
The script validates every required runtime file before changing the current
PowerShell environment.

Configure and test the ROOT integration:

```powershell
cmake -S . -B build/root-windows -G "Visual Studio 17 2022" -A x64 `
  -DBUILD_NATIVE_BENCHMARK=ON -DBUILD_ROOT_INTEGRATION=ON
cmake --build build/root-windows --config Release --parallel
ctest --test-dir build/root-windows -C Release --output-on-failure
```

