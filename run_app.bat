@echo off
echo Installing dependencies...
pip install -r functor_engine_web/backend/requirements.txt
pip install -r functor_engine_web/frontend/requirements.txt

echo Starting Backend Server...
start "Functor Engine Backend" cmd /k "cd functor_engine_web/backend && uvicorn main:app --reload"

echo Starting Frontend App...
start "Functor Engine Frontend" cmd /k "cd functor_engine_web/frontend && streamlit run app.py"

echo Functor Engine is running!
