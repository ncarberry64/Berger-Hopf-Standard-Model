@echo off
setlocal
rem This explicit joint launcher opts into installing the optional Astropy dependency.
call "%~dp0Start_Blackhole_Tracker.cmd" --astrometry --page joint %*
exit /b %ERRORLEVEL%
