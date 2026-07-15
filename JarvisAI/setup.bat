@echo off
REM setup.bat - Configura o JarvisAI do zero: cria o ambiente virtual
REM e instala todas as dependencias. Rode este script uma unica vez.

echo ============================================
echo   JarvisAI - Configuracao inicial
echo ============================================

python --version >nul 2>&1
if errorlevel 1 (
    echo Python nao foi encontrado no PATH. Instale o Python 3.11+ antes de continuar.
    pause
    exit /b 1
)

if not exist venv (
    echo Criando ambiente virtual em .\venv ...
    python -m venv venv
)

call venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo ============================================
echo   Configuracao concluida.
echo   Use run.bat para iniciar o JarvisAI.
echo ============================================
pause
