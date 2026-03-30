@echo off
rem -------------------------------------------------
rem Start Vector DB (Qdrant) in a Docker container
rem -------------------------------------------------

setlocal

rem Verify Docker is installed
docker version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed or not in PATH.
    exit /b 1
)

rem Run Qdrant container (persistent storage in qdrant_data folder)
set "STORAGE_DIR=%~dp0qdrant_data"
mkdir "%STORAGE_DIR%" >nul 2>&1

rem Check if container already running
set "CONTAINER_ID="
for /f "tokens=*" %%i in ('docker ps -q -f "name=^qdrant_db$"') do set "CONTAINER_ID=%%i"
if defined CONTAINER_ID (
    echo ✅ Qdrant container 'qdrant_db' is already running.
) else (
    echo 🚀 Starting Qdrant container...
    docker pull qdrant/qdrant
    docker run -d --rm -p 6333:6333 -v "%STORAGE_DIR%:/qdrant/storage" --name qdrant_db qdrant/qdrant
    if errorlevel 1 (
        echo ❌ Failed to start Qdrant container.
        exit /b 1
    )
    echo ✅ Qdrant container started. Data persisted at %STORAGE_DIR%
)

endlocal
