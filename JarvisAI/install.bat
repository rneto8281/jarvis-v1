@echo off
REM install.bat - Instala as dependencias do JarvisAI no ambiente virtual
REM ja existente (assume que setup.bat ja foi executado antes).

if not exist venv (
    echo Ambiente virtual nao encontrado. Rode setup.bat primeiro.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo Dependencias instaladas.
pause
