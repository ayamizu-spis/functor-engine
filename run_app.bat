@echo off
setlocal

REM Check if .venv exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
call .venv\Scripts\activate

echo Installing dependencies...
pip install -r functor_engine_web/backend/requirements.txt
pip install -r functor_engine_web/frontend/requirements.txt

echo Starting Backend Server...
start "Functor Engine Backend" cmd /k "call .venv\Scripts\activate && cd functor_engine_web/backend && uvicorn main:app --reload"

echo Starting Frontend App...
start "Functor Engine Frontend" cmd /k "call .venv\Scripts\activate && cd functor_engine_web/frontend && streamlit run app.py"

echo Functor Engine is running!
endlocal
