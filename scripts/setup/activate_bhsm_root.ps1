[CmdletBinding()]
param(
    [string]$RootHome = (Join-Path $env:USERPROFILE "Tools\ROOT-6.40.02\root"),
    [string]$Python311 = (Join-Path $env:LOCALAPPDATA "Programs\Python\Python311\python.exe")
)

$ErrorActionPreference = "Stop"
$rootHomePath = (Resolve-Path -LiteralPath $RootHome).Path
$rootBin = Join-Path $rootHomePath "bin"

$requiredFiles = @(
    (Join-Path $rootBin "root.exe"),
    (Join-Path $rootHomePath "cmake\ROOTConfig.cmake"),
    (Join-Path $rootBin "libcppyy.pyd"),
    (Join-Path $rootBin "sqlite3.dll"),
    $Python311
)

foreach ($requiredFile in $requiredFiles) {
    if (-not (Test-Path -LiteralPath $requiredFile -PathType Leaf)) {
        throw "Required BHSM ROOT dependency is missing: $requiredFile"
    }
}

$cmakeCommand = Get-Command cmake -ErrorAction SilentlyContinue
if (-not $cmakeCommand) {
    $cmakeBin = Join-Path $env:ProgramFiles "CMake\bin"
    $cmakeExe = Join-Path $cmakeBin "cmake.exe"
    if (-not (Test-Path -LiteralPath $cmakeExe -PathType Leaf)) {
        throw "CMake is not on PATH and was not found at: $cmakeExe"
    }
    $env:PATH = "$cmakeBin;$env:PATH"
}

$env:ROOTSYS = $rootHomePath
$env:PATH = "$rootBin;$env:PATH"
$env:CMAKE_PREFIX_PATH = "$rootHomePath;$env:CMAKE_PREFIX_PATH"
$env:PYTHONPATH = "$rootBin;$env:PYTHONPATH"
$env:BHSM_PYTHON311 = (Resolve-Path -LiteralPath $Python311).Path

$rootVersion = & (Join-Path $rootBin "root-config.bat") --version
$pythonVersion = & $env:BHSM_PYTHON311 --version
$cmakeVersion = (& cmake --version | Select-Object -First 1)

Write-Output "BHSM ROOT environment activated."
Write-Output "ROOTSYS=$env:ROOTSYS"
Write-Output "ROOT=$rootVersion"
Write-Output "Python=$pythonVersion"
Write-Output "CMake=$cmakeVersion"
