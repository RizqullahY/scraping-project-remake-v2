@echo off
setlocal

if not "%~1"=="" (
    set "commit_message=%~1"
) else (
    for /f "tokens=1-5 delims=/: " %%a in ('echo %date% %time%') do (
        set "YYYY=%%c"
        set "MM=%%a"
        set "DD=%%b"
        set "HH=%%d"
        set "MIN=%%e"
    )

    set "date_now=%YYYY%-%MM%-%DD% %HH%:%MIN%"
    set "commit_message=Automatic commit: %date_now%"
)

git add .
git commit -m "%commit_message%"
git push origin master

endlocal
exit /b 0