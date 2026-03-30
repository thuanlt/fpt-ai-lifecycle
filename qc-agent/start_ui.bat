@echo off
rem -------------------------------------------------
rem Prepare and start the Flask Web UI
rem -------------------------------------------------

setlocal

rem 1. Verify Python and pip are available
where python >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Install Python 3.10+ first.
    exit /b 1
)

where pip >nul 2>&1
if errorlevel 1 (
    echo ❌ pip is not installed. Install pip first.
    exit /b 1
)

rem 2. Activate virtual environment
if not exist "%~dp0venv\Scripts\activate.bat" (
    echo ❌ Venv chưa được tạo. Chạy lệnh: python -m venv venv
    exit /b 1
)
call "%~dp0venv\Scripts\activate.bat"

rem 3. Install required Python packages (only if not already installed)
python -c "import flask, flask_cors, requests, bs4, pypdf, docx, openpyxl, pptx, langchain, openai, qdrant_client, sentence_transformers, chromadb, mcp, asgiref" >nul 2>&1
if errorlevel 1 (
    echo 📦 Installing/Updating Python dependencies...
    pip install -q --upgrade ^
        Flask ^
        Flask-Cors ^
        requests ^
        beautifulsoup4 ^
        pypdf ^
        python-docx ^
        openpyxl ^
        python-pptx ^
        langchain ^
        langchain-text-splitters ^
        openai ^
        qdrant-client ^
        sentence-transformers ^
        chromadb ^
        mcp ^
        asgiref ^
        "flask[async]"
    if errorlevel 1 (
        echo ❌ Failed to install Python packages.
        exit /b 1
    )
) else (
    echo ✅ Dependencies already satisfied. Skipping install.
)

rem 4. Launch Flask server
echo 🔥 Launching Flask UI on http://127.0.0.1:5001...
set PYTHONPATH=%PYTHONPATH%;.\src;.\web_ui

@REM # Thiết lập để không đi qua Proxy khi gọi chính máy mình (localhost)
set NO_PROXY=localhost,127.0.0.1
set no_proxy=localhost,127.0.0.1

python web_ui\server.py

endlocal
