# Sistema de Verificação de Status do Servidor

Este módulo implementa um sistema de verificação de status do servidor de jogo baseado no sistema original do site PHP. Ele permite verificar se os servidores de jogo e login estão online através de verificação de portas TCP.

## 📋 Configuração

### Variáveis de Ambiente

Adicione as seguintes variáveis ao seu arquivo `.env`:

```env
# =========================== SERVER STATUS CONFIGURATION ===========================

# IP do servidor de jogo
GAME_SERVER_IP=192.168.1.100

# Porta do servidor de jogo (Game Server)
GAME_SERVER_PORT=7777

# Porta do servidor de login (Login Server)
LOGIN_SERVER_PORT=2106

# Timeout para verificação de conexão (em segundos)
SERVER_STATUS_TIMEOUT=1

# Forçar status do servidor (auto = verificação automática, on = sempre online, off = sempre offline)
FORCE_GAME_SERVER_STATUS=auto
FORCE_LOGIN_SERVER_STATUS=auto
```

### Configurações Disponíveis

| Variável | Descrição | Padrão | Opções |
|----------|-----------|--------|--------|
| `GAME_SERVER_IP` | IP do servidor de jogo | `127.0.0.1` | Qualquer IP válido |
| `GAME_SERVER_PORT` | Porta do servidor de jogo | `7777` | Qualquer porta válida |
| `LOGIN_SERVER_PORT` | Porta do servidor de login | `2106` | Qualquer porta válida |
| `SERVER_STATUS_TIMEOUT` | Timeout para verificação | `1` | Tempo em segundos |
| `FORCE_GAME_SERVER_STATUS` | Forçar status do game server | `auto` | `auto`, `on`, `off` |
| `FORCE_LOGIN_SERVER_STATUS` | Forçar status do login server | `auto` | `auto`, `on`, `off` |

## 🚀 Como Usar

### Importação

```python
from utils.server_status import (
    ServerStatusChecker,
    check_server_status,
    is_game_server_online,
    is_login_server_online,
    check_port
)
```

### Uso Básico

#### 1. Verificação Simples

```python
# Verificar se o servidor de jogo está online
if is_game_server_online():
    print("Servidor de jogo está ONLINE")
else:
    print("Servidor de jogo está OFFLINE")

# Verificar se o servidor de login está online
if is_login_server_online():
    print("Servidor de login está ONLINE")
else:
    print("Servidor de login está OFFLINE")
```

#### 2. Verificação Completa

```python
# Obter status completo de ambos os servidores
status = check_server_status()

print(f"Status Geral: {status['overall_status']}")
print(f"IP do Servidor: {status['server_ip']}")
print(f"Verificado em: {status['checked_at']}")

# Detalhes do servidor de jogo
game_status = status['game_server']
print(f"Game Server: {game_status['status']} (Porta: {game_status['port']})")

# Detalhes do servidor de login
login_status = status['login_server']
print(f"Login Server: {login_status['status']} (Porta: {login_status['port']})")
```

#### 3. Verificação de Porta Específica

```python
# Verificar uma porta específica
if check_port("google.com", 80, timeout=2):
    print("Porta 80 está aberta")
else:
    print("Porta 80 está fechada")
```

### Uso Avançado

#### Usando a Classe Diretamente

```python
# Criar instância do verificador
checker = ServerStatusChecker()

# Verificar apenas servidor de jogo
game_status = checker.get_game_server_status()
print(f"Status do Game Server: {game_status}")

# Verificar apenas servidor de login
login_status = checker.get_login_server_status()
print(f"Status do Login Server: {login_status}")

# Verificar porta personalizada
is_open = checker.check_port_connection("meuservidor.com", 8080, timeout=3)
print(f"Porta 8080: {'Aberta' if is_open else 'Fechada'}")
```

## 📊 Estrutura de Retorno

### Função `check_server_status()`

Retorna um dicionário com a seguinte estrutura:

```python
{
    'overall_status': 'online|offline|partial',
    'server_ip': '192.168.1.100',
    'checked_at': '2024-01-15T10:30:00.123456',
    'game_server': {
        'status': 'online|offline',
        'forced': True|False,
        'ip': '192.168.1.100',
        'port': 7777,
        'message': 'Servidor de jogo está online'
    },
    'login_server': {
        'status': 'online|offline',
        'forced': True|False,
        'ip': '192.168.1.100',
        'port': 2106,
        'message': 'Servidor de login está online'
    }
}
```

### Status Geral

- `online`: Ambos os servidores estão online
- `offline`: Ambos os servidores estão offline
- `partial`: Um servidor está online, outro offline

## 🌐 Uso em Views Django

### API Endpoint

```python
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from utils.server_status import check_server_status

@require_http_methods(["GET"])
def api_server_status(request):
    """API endpoint para verificar status do servidor"""
    try:
        status = check_server_status()
        return JsonResponse({
            'success': True,
            'data': status
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
```

### Context Processor

```python
# Em core/context_processors.py
from utils.server_status import check_server_status, is_game_server_online

def server_status_context(request):
    """Adiciona informações de status do servidor ao contexto"""
    return {
        'server_status': check_server_status(),
        'is_game_online': is_game_server_online(),
    }
```

## 🎨 Uso em Templates

### Template Exemplo

```html
{% if is_game_online %}
    <div class="server-status online">
        <span class="status-indicator"></span>
        <span class="status-text">Servidor Online</span>
    </div>
{% else %}
    <div class="server-status offline">
        <span class="status-indicator"></span>
        <span class="status-text">Servidor Offline</span>
    </div>
{% endif %}

<div class="server-details">
    <p>IP: {{ server_status.server_ip }}</p>
    <p>Status Geral: {{ server_status.overall_status }}</p>
    <p>Verificado em: {{ server_status.checked_at }}</p>
</div>
```

## 🧪 Testes

Execute os testes para verificar se tudo está funcionando:

```bash
python test/test_server_status.py
```

## ⚙️ Configurações Avançadas

### Forçar Status

Para forçar um status específico (útil para manutenção):

```env
# Forçar servidor sempre online
FORCE_GAME_SERVER_STATUS=on
FORCE_LOGIN_SERVER_STATUS=on

# Forçar servidor sempre offline
FORCE_GAME_SERVER_STATUS=off
FORCE_LOGIN_SERVER_STATUS=off

# Verificação automática (padrão)
FORCE_GAME_SERVER_STATUS=auto
FORCE_LOGIN_SERVER_STATUS=auto
```

### Timeout Personalizado

```env
# Timeout de 5 segundos para verificações mais lentas
SERVER_STATUS_TIMEOUT=5
```

## 🔧 Troubleshooting

### Problemas Comuns

1. **Servidor sempre aparece offline**
   - Verifique se o IP e porta estão corretos
   - Confirme se o servidor está rodando
   - Teste com `check_port()` diretamente

2. **Verificação muito lenta**
   - Reduza o `SERVER_STATUS_TIMEOUT`
   - Verifique a conectividade de rede

3. **Erro de conexão**
   - Verifique se o firewall não está bloqueando
   - Confirme se o servidor aceita conexões TCP

### Logs

O sistema registra logs de aviso quando há problemas:

```python
import logging
logger = logging.getLogger(__name__)
# Os logs aparecerão quando houver erros de conexão
```

## 📝 Exemplos Completos

Veja mais exemplos no arquivo `utils/server_status_example.py` 