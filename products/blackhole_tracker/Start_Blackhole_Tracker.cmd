@echo off
setlocal
pushd "%~dp0"
python -c "import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)" >nul 2>&1
if not errorlevel 1 (
    set "BT_PYTHON=python"
    goto launch
)
py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)" >nul 2>&1
if not errorlevel 1 (
    set "BT_PYTHON=py -3"
    goto launch
)
echo Python 3.11 or newer was not found. Install Python from python.org and
echo enable its PATH option, or install the Windows py launcher. Then retry.
if not defined BHSM_TRACKER_NONINTERACTIVE pause
popd
exit /b 2
:launch
%BT_PYTHON% "scripts\launch_local.py" %*
set "BT_EXIT=%ERRORLEVEL%"
if not "%BT_EXIT%"=="0" if not defined BHSM_TRACKER_NONINTERACTIVE pause
popd
exit /b %BT_EXIT%
