# Configuração do FFmpeg no Windows

Este documento explica como configurar o FFmpeg para validação de vídeos na aplicação.

## Método 1: Script Automático (Recomendado)

1. Execute o arquivo `setup_ffmpeg_windows.bat` como administrador
2. O script irá:
   - Detectar automaticamente onde está o FFmpeg
   - Adicionar ao PATH do Windows
   - Testar a instalação

## Método 2: Configuração Manual

### Adicionar ao PATH manualmente:

1. **Via Interface Gráfica:**
   - Pressione `Win + R`, digite `sysdm.cpl` e pressione Enter
   - Vá para a aba "Avançado"
   - Clique em "Variáveis de Ambiente"
   - Na seção "Variáveis do usuário", encontre "Path" e clique em "Editar"
   - Clique em "Novo" e adicione: `C:\ffmpeg\bin` (ou `C:\ffmpeg` se os executáveis estiverem diretamente na pasta)
   - Clique "OK" em todas as janelas

2. **Via PowerShell (Execute como Administrador):**
   ```powershell
   # Verificar PATH atual
   $env:PATH
   
   # Adicionar FFmpeg ao PATH do usuário
   [Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";C:\ffmpeg\bin", "User")
   
   # OU para PATH do sistema (requer admin)
   [Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";C:\ffmpeg\bin", "Machine")
   ```

## Método 3: Configuração no Django

Se não quiser modificar o PATH do sistema, adicione no seu `settings.py`:

```python
# Configuração do FFmpeg
FFPROBE_PATH = r'C:\ffmpeg\bin\ffprobe.exe'  # ou C:\ffmpeg\ffprobe.exe
```

## Verificação da Instalação

Execute no prompt de comando:
```cmd
ffprobe -version
```

Ou se configurou via settings:
```cmd
python manage.py shell
>>> from utils.media_validators import FFPROBE_PATH
>>> print(FFPROBE_PATH)
```

## Estrutura de Pastas Esperada

Certifique-se que você tem esta estrutura:

```
C:\ffmpeg\
├── bin\
│   ├── ffmpeg.exe
│   ├── ffprobe.exe
│   └── ffplay.exe
OU
├── ffmpeg.exe
├── ffprobe.exe
└── ffplay.exe
```

## Troubleshooting

### Erro: "ffprobe não encontrado"
- Verifique se os arquivos estão no local correto
- Execute `setup_ffmpeg_windows.bat` novamente
- Reinicie o prompt de comando e a aplicação Django

### Erro: "Acesso negado"
- Execute o script como administrador
- Ou use a configuração via `settings.py`

### Erro: "Arquivo corrompido"
- Baixe novamente o FFmpeg do site oficial: https://ffmpeg.org/download.html
- Use a versão "release builds" para Windows

## Download do FFmpeg

Se não tiver o FFmpeg:
1. Acesse: https://ffmpeg.org/download.html
2. Clique em "Windows"
3. Escolha "Windows builds by BtbN" ou similar
4. Baixe a versão "release"
5. Extraia para `C:\ffmpeg\`
