@echo off
setlocal
call "%~dp0Start_Blackhole_Tracker.cmd" --page atlas %*
exit /b %ERRORLEVEL%
