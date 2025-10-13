@echo off
REM JLPT Test Manager - Windows Test Runner Script

echo ========================================
echo JLPT Test Manager - Test Suite (Windows)
echo ========================================
echo.

REM Activate virtual environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate
) else (
    echo Error: Virtual environment not found!
    echo Please run init.bat first.
    pause
    exit /b 1
)

REM Check if pytest is installed
python -c "import pytest" 2>nul
if errorlevel 1 (
    echo Installing test dependencies...
    pip install -r requirements-dev.txt
)

echo.
echo Running tests...
echo.

REM Run tests based on argument
if "%1"=="" goto all_tests
if "%1"=="models" goto models_tests
if "%1"=="routes" goto routes_tests
if "%1"=="import" goto import_tests
if "%1"=="admin" goto admin_tests
if "%1"=="integration" goto integration_tests
if "%1"=="coverage" goto coverage_tests
if "%1"=="fast" goto fast_tests
goto all_tests

:models_tests
echo Running model tests...
pytest tests/test_models.py -v
goto end

:routes_tests
echo Running route tests...
pytest tests/test_routes.py -v
goto end

:import_tests
echo Running import tests...
pytest tests/test_import.py -v
goto end

:admin_tests
echo Running admin tests...
pytest tests/test_admin.py -v
goto end

:integration_tests
echo Running integration tests...
pytest tests/test_integration.py -v
goto end

:coverage_tests
echo Running tests with coverage...
pytest tests/ --cov=. --cov-report=html --cov-report=term
echo.
echo Coverage report generated in htmlcov\index.html
goto end

:fast_tests
echo Running fast tests (no integration)...
pytest tests/ -v -m "not integration"
goto end

:all_tests
echo Running all tests...
pytest tests/ -v

:end
echo.
echo ========================================
echo Tests completed!
echo ========================================
pause

