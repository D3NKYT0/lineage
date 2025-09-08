# Configuração de Login Social

Este documento explica como configurar o sistema de login social no PDL.

## Variáveis de Ambiente

Adicione as seguintes variáveis ao seu arquivo `.env`:

```env
# Configuração Geral de Login Social
SOCIAL_LOGIN_ENABLED=True
SOCIAL_LOGIN_SHOW_SECTION=True

# Configuração Individual dos Provedores
SOCIAL_LOGIN_GOOGLE_ENABLED=True
SOCIAL_LOGIN_GITHUB_ENABLED=True
SOCIAL_LOGIN_DISCORD_ENABLED=True

# Credenciais dos Provedores (já existentes)
GOOGLE_CLIENT_ID=seu_google_client_id
GOOGLE_SECRET_KEY=seu_google_secret_key
GITHUB_CLINET_ID=seu_github_client_id
GITHUB_SECRET_KEY=seu_github_secret_key
DISCORD_CLIENT_ID=seu_discord_client_id
DISCORD_SECRET_KEY=seu_discord_secret_key
```

## Opções de Configuração

### SOCIAL_LOGIN_ENABLED
- **Padrão**: `True`
- **Descrição**: Habilita ou desabilita completamente o sistema de login social
- **Valores**: `True` ou `False`

### SOCIAL_LOGIN_SHOW_SECTION
- **Padrão**: `True`
- **Descrição**: Controla se a seção de login social é exibida nos templates
- **Valores**: `True` ou `False`

### SOCIAL_LOGIN_GOOGLE_ENABLED
- **Padrão**: `True`
- **Descrição**: Habilita ou desabilita especificamente o login com Google
- **Valores**: `True` ou `False`

### SOCIAL_LOGIN_GITHUB_ENABLED
- **Padrão**: `True`
- **Descrição**: Habilita ou desabilita especificamente o login com GitHub
- **Valores**: `True` ou `False`

### SOCIAL_LOGIN_DISCORD_ENABLED
- **Padrão**: `True`
- **Descrição**: Habilita ou desabilita especificamente o login com Discord
- **Valores**: `True` ou `False`

## Exemplos de Uso

### Desabilitar completamente o login social
```env
SOCIAL_LOGIN_ENABLED=False
```

### Mostrar apenas Google e Discord
```env
SOCIAL_LOGIN_ENABLED=True
SOCIAL_LOGIN_SHOW_SECTION=True
SOCIAL_LOGIN_GOOGLE_ENABLED=True
SOCIAL_LOGIN_GITHUB_ENABLED=False
SOCIAL_LOGIN_DISCORD_ENABLED=True
```

### Ocultar a seção de login social
```env
SOCIAL_LOGIN_ENABLED=True
SOCIAL_LOGIN_SHOW_SECTION=False
```

## Como Funciona

1. **Context Processor**: O sistema usa um context processor (`social_login_config`) que fornece as configurações aos templates
2. **Templates**: Os templates verificam essas configurações antes de exibir os botões de login social
3. **Configuração Dinâmica**: As configurações são lidas do arquivo `.env` e podem ser alteradas sem reiniciar o servidor (dependendo da configuração de cache)

## Templates Afetados

- `apps/main/home/templates/accounts_custom/sign-in.html` - Página de login

## Variáveis Disponíveis nos Templates

As seguintes variáveis estão disponíveis em todos os templates:

- `SOCIAL_LOGIN_ENABLED` - Se o login social está habilitado
- `SOCIAL_LOGIN_SHOW_SECTION` - Se a seção deve ser exibida
- `SOCIAL_LOGIN_GOOGLE_ENABLED` - Se o Google está habilitado
- `SOCIAL_LOGIN_GITHUB_ENABLED` - Se o GitHub está habilitado
- `SOCIAL_LOGIN_DISCORD_ENABLED` - Se o Discord está habilitado

## Exemplo de Uso no Template

```html
{% if SOCIAL_LOGIN_ENABLED and SOCIAL_LOGIN_SHOW_SECTION %}
  <div class="social-login-section">
    {% if SOCIAL_LOGIN_GOOGLE_ENABLED %}
      <!-- Botão do Google -->
    {% endif %}
    
    {% if SOCIAL_LOGIN_GITHUB_ENABLED %}
      <!-- Botão do GitHub -->
    {% endif %}
    
    {% if SOCIAL_LOGIN_DISCORD_ENABLED %}
      <!-- Botão do Discord -->
    {% endif %}
  </div>
{% endif %}
``` 