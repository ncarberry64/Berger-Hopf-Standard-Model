@echo off
setlocal
call "%~dp0Start_Blackhole_Tracker.cmd" --page skytrack %*
exit /b %ERRORLEVEL%
