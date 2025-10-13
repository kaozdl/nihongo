@echo off
REM JLPT Test Manager - Windows Initialization Script

echo ========================================
echo JLPT Test Manager - Setup Script (Windows)
echo ========================================
echo.

REM Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created
) else (
    echo Virtual environment already exists
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate

echo.
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Initializing database...
flask init-db

echo.
echo ========================================
echo Setup complete!
echo.
echo To create an admin user, run:
echo   venv\Scripts\activate
echo   flask create-admin
echo.
echo To start the application, run:
echo   venv\Scripts\activate
echo   flask run
echo.
echo Then visit: http://localhost:5000
echo ========================================
echo.
pause

