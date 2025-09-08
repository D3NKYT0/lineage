@echo off
echo Configurando FFmpeg no PATH do Windows...

REM Verificar se já existe no PATH
where ffprobe >nul 2>&1
if %errorlevel% == 0 (
    echo FFmpeg já está configurado no PATH!
    ffprobe -version
    pause
    exit /b 0
)

REM Verificar se existe em C:\ffmpeg
if exist "C:\ffmpeg\bin\ffprobe.exe" (
    set FFMPEG_PATH=C:\ffmpeg\bin
    echo FFmpeg encontrado em C:\ffmpeg\bin\
) else if exist "C:\ffmpeg\ffprobe.exe" (
    set FFMPEG_PATH=C:\ffmpeg
    echo FFmpeg encontrado em C:\ffmpeg\
) else (
    echo ERRO: FFmpeg não encontrado em C:\ffmpeg\
    echo Por favor, certifique-se de que os arquivos ffmpeg.exe e ffprobe.exe estão em:
    echo - C:\ffmpeg\bin\ OU
    echo - C:\ffmpeg\
    pause
    exit /b 1
)

echo.
echo Adicionando %FFMPEG_PATH% ao PATH do sistema...

REM Adicionar ao PATH do usuário atual (mais seguro)
for /f "tokens=2*" %%a in ('reg query "HKCU\Environment" /v PATH 2^>nul') do set "current_path=%%b"

if not defined current_path (
    set "new_path=%FFMPEG_PATH%"
) else (
    echo %current_path% | find /i "%FFMPEG_PATH%" >nul
    if errorlevel 1 (
        set "new_path=%current_path%;%FFMPEG_PATH%"
    ) else (
        echo %FFMPEG_PATH% já está no PATH!
        goto :test_installation
    )
)

reg add "HKCU\Environment" /v PATH /t REG_EXPAND_SZ /d "%new_path%" /f >nul

if errorlevel 1 (
    echo ERRO: Não foi possível modificar o PATH. Execute como administrador.
    pause
    exit /b 1
)

echo PATH atualizado com sucesso!
echo.

:test_installation
echo Testando instalação...
echo Nota: Pode ser necessário reiniciar o prompt de comando ou aplicação para que as mudanças tenham efeito.

REM Testar diretamente com o caminho completo
"%FFMPEG_PATH%\ffprobe.exe" -version 2>nul || "%FFMPEG_PATH%\ffprobe" -version 2>nul

if errorlevel 1 (
    echo AVISO: Teste direto falhou. Verifique os arquivos em %FFMPEG_PATH%
) else (
    echo ✓ FFmpeg está funcionando corretamente!
)

echo.
echo IMPORTANTE: 
echo - Reinicie seu prompt de comando
echo - Reinicie sua aplicação Django
echo - Reinicie seu IDE/editor se necessário
echo.
pause
