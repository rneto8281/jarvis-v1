@echo off
REM run.bat - Inicia o servidor do JarvisAI usando o ambiente virtual.

if not exist venv (
    echo Ambiente virtual nao encontrado. Rode setup.bat primeiro.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
python -m backend
pause
