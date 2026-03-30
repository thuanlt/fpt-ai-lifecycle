@echo off
rem -------------------------------------------------
rem Build Docker image for the Playwright sandbox
rem -------------------------------------------------

setlocal EnableDelayedExpansion

rem --- Configuration -------------------------------------------------
set "IMAGE_NAME=qc-agent-framework"
set "TAG=latest"
set "PROXY=http://10.36.232.10:8080"

rem --- Build Process --------------------------------------------------
echo ▶️ Building Docker image: %IMAGE_NAME%:%TAG%
docker build --build-arg HTTP_PROXY=%PROXY% --build-arg HTTPS_PROXY=%PROXY% -t "%IMAGE_NAME%:%TAG%" .
if errorlevel 1 (
    echo ❌ Docker build failed.
    exit /b 1
)

echo ✅ Docker image built successfully!
echo    Image: %IMAGE_NAME%:%TAG%
echo    To run it, use:
echo    docker run -it --rm %IMAGE_NAME%:%TAG%
endlocal
