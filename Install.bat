@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

set "SERVICE_NAME=LanchoneteControl"
set "PORT=8020"
set "BIND=0.0.0.0"

set "BASE_DIR=%~dp0"
set "BASE_DIR=%BASE_DIR:~0,-1%"
cd /d "%BASE_DIR%"

REM ======= LOG =======
if not exist "logs" mkdir "logs"
for /f "tokens=1-3 delims=/: " %%a in ("%date%") do set "D=%%c%%b%%a"
for /f "tokens=1-3 delims=:. " %%a in ("%time%") do set "T=%%a%%b%%c"
set "LOG=logs\install-%D%-%T%.log"

echo =========================================================> "%LOG%"
echo  INSTALL LOG - %date% %time%>> "%LOG%"
echo  Pasta: %CD%>> "%LOG%"
echo =========================================================>> "%LOG%"

echo.
echo [INFO] Log: %LOG%
echo [INFO] Pasta do projeto: %CD%
echo.

REM ======= FUNÇÃO DE LOG =======
set "NSSM=%CD%\nssm.exe"

REM ======= CHECAR ADMIN =======
echo [1] Verificando permissao de Administrador...
net session >nul 2>&1
if errorlevel 1 (
  echo [ERRO] Execute este .bat como ADMINISTRADOR.
  echo [ERRO] Execute este .bat como ADMINISTRADOR.>> "%LOG%"
  pause
  exit /b 1
)
echo OK>> "%LOG%"

REM ======= VALIDACOES =======
echo [2] Validando arquivos do projeto...
if not exist "manage.py" (
  echo [ERRO] manage.py nao encontrado em %CD%
  echo [ERRO] manage.py nao encontrado.>> "%LOG%"
  pause
  exit /b 1
)

if not exist "%NSSM%" (
  echo [ERRO] nssm.exe nao encontrado em %CD%
  echo [ERRO] nssm.exe nao encontrado.>> "%LOG%"
  pause
  exit /b 1
)

echo OK>> "%LOG%"

REM ======= PYTHON =======
echo [3] Verificando Python (py launcher)...
py -3 --version >> "%LOG%" 2>&1
if errorlevel 1 (
  echo [ERRO] Nao encontrei o launcher "py -3". Instale o Python 3 e marque "Add to PATH".
  echo [ERRO] py -3 falhou.>> "%LOG%"
  pause
  exit /b 1
)

REM ======= VENV =======
echo [4] Criando/validando venv...
if not exist "venv\Scripts\python.exe" (
  echo  - Criando venv... (py -3 -m venv venv)
  echo [CMD] py -3 -m venv venv>> "%LOG%"
  py -3 -m venv venv >> "%LOG%" 2>&1
  if errorlevel 1 (
    echo [ERRO] Falha ao criar venv. Veja o log.
    echo [ERRO] Falha ao criar venv.>> "%LOG%"
    pause
    exit /b 1
  )
) else (
  echo  - venv ja existe.
)
echo OK>> "%LOG%"

REM ======= ATIVAR VENV =======
echo [5] Ativando venv...
call "venv\Scripts\activate.bat" >> "%LOG%" 2>&1
if errorlevel 1 (
  echo [ERRO] Falha ao ativar venv. Veja o log.
  echo [ERRO] Falha ao ativar venv.>> "%LOG%"
  pause
  exit /b 1
)

REM ======= PIP =======
echo [6] Atualizando pip e instalando dependencias...
echo [CMD] python -m pip install --upgrade pip>> "%LOG%"
python -m pip install --upgrade pip >> "%LOG%" 2>&1
if errorlevel 1 (
  echo [ERRO] Falha ao atualizar pip. Veja o log.
  echo [ERRO] pip upgrade falhou.>> "%LOG%"
  pause
  exit /b 1
)

if exist "requirements.txt" (
  echo [CMD] pip install -r requirements.txt>> "%LOG%"
  pip install -r requirements.txt >> "%LOG%" 2>&1
  if errorlevel 1 (
    echo [ERRO] Falha ao instalar requirements. Veja o log.
    echo [ERRO] pip install requirements falhou.>> "%LOG%"
    pause
    exit /b 1
  )
) else (
  echo [WARN] requirements.txt nao encontrado.>> "%LOG%"
)

REM ======= MIGRATIONS =======
echo [7] Rodando migracoes...
echo [CMD] python manage.py makemigrations>> "%LOG%"
python manage.py makemigrations >> "%LOG%" 2>&1
if errorlevel 1 (
  echo [ERRO] makemigrations falhou. Veja o log.
  pause
  exit /b 1
)

echo [CMD] python manage.py migrate>> "%LOG%"
python manage.py migrate >> "%LOG%" 2>&1
if errorlevel 1 (
  echo [ERRO] migrate falhou. Veja o log.
  pause
  exit /b 1
)

REM ======= COLLECTSTATIC =======
echo [8] collectstatic...
echo [CMD] python manage.py collectstatic --noinput>> "%LOG%"
python manage.py collectstatic --noinput >> "%LOG%" 2>&1

REM ======= NSSM SERVICE =======
echo [9] Instalando servico no NSSM...
set "PY_EXE=%CD%\venv\Scripts\python.exe"

echo [CMD] "%NSSM%" stop "%SERVICE_NAME%">> "%LOG%"
"%NSSM%" stop "%SERVICE_NAME%" >> "%LOG%" 2>&1

echo [CMD] "%NSSM%" remove "%SERVICE_NAME%" confirm>> "%LOG%"
"%NSSM%" remove "%SERVICE_NAME%" confirm >> "%LOG%" 2>&1

echo [CMD] "%NSSM%" install "%SERVICE_NAME%" "%PY_EXE%" "manage.py runserver %BIND%:%PORT%">> "%LOG%"
"%NSSM%" install "%SERVICE_NAME%" "%PY_EXE%" "manage.py runserver %BIND%:%PORT%" >> "%LOG%" 2>&1
if errorlevel 1 (
  echo [ERRO] NSSM install falhou. Veja o log.
  pause
  exit /b 1
)

echo [CMD] "%NSSM%" set "%SERVICE_NAME%" AppDirectory "%CD%">> "%LOG%"
"%NSSM%" set "%SERVICE_NAME%" AppDirectory "%CD%" >> "%LOG%" 2>&1

echo [CMD] "%NSSM%" set "%SERVICE_NAME%" Start SERVICE_AUTO_START>> "%LOG%"
"%NSSM%" set "%SERVICE_NAME%" Start SERVICE_AUTO_START >> "%LOG%" 2>&1

REM logs do serviço
if not exist "%CD%\logs" mkdir "%CD%\logs"
"%NSSM%" set "%SERVICE_NAME%" AppStdout "%CD%\logs\stdout.log" >> "%LOG%" 2>&1
"%NSSM%" set "%SERVICE_NAME%" AppStderr "%CD%\logs\stderr.log" >> "%LOG%" 2>&1
"%NSSM%" set "%SERVICE_NAME%" AppRotateFiles 1 >> "%LOG%" 2>&1
"%NSSM%" set "%SERVICE_NAME%" AppRotateOnline 1 >> "%LOG%" 2>&1
"%NSSM%" set "%SERVICE_NAME%" AppRotateSeconds 86400 >> "%LOG%" 2>&1
"%NSSM%" set "%SERVICE_NAME%" AppRotateBytes 1048576 >> "%LOG%" 2>&1

echo [CMD] "%NSSM%" start "%SERVICE_NAME%">> "%LOG%"
"%NSSM%" start "%SERVICE_NAME%" >> "%LOG%" 2>&1
if errorlevel 1 (
  echo [ERRO] Servico instalado mas nao iniciou. Veja logs em .\logs\stdout.log / stderr.log
  pause
  exit /b 1
)

echo.
echo =========================================================
echo  OK! Instalado e iniciado: %SERVICE_NAME%
echo  URL: http://localhost:%PORT%
echo  Log instalacao: %LOG%
echo  Logs do servico: .\logs\stdout.log e .\logs\stderr.log
echo =========================================================
pause
exit /b 0
