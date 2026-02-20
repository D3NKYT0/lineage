# Sistema de Captcha no Login

## Visão Geral

O sistema implementa um mecanismo de proteção contra ataques de força bruta no login, exigindo captcha após um número configurável de tentativas falhadas.

## Configuração

### Variáveis de Ambiente

Adicione a seguinte variável ao seu arquivo `.env`:

```bash
# Número máximo de tentativas de login antes de exigir captcha
CONFIG_LOGIN_MAX_ATTEMPTS=3
```

### Configuração do hCaptcha

Certifique-se de que as seguintes variáveis estão configuradas:

```bash
CONFIG_HCAPTCHA_SITE_KEY=sua_chave_do_site
CONFIG_HCAPTCHA_SECRET_KEY=sua_chave_secreta
```

## Como Funciona

1. **Rastreamento de Tentativas**: O middleware `LoginAttemptsMiddleware` rastreia todas as tentativas de login por IP
2. **Contador de Tentativas**: Após cada tentativa falhada, o contador é incrementado
3. **Exigência de Captcha**: Quando o número de tentativas atinge o limite configurado, o captcha se torna obrigatório (ex: após 3 tentativas falhadas, a 4ª tentativa requer captcha)
4. **Reset Automático**: As tentativas são resetadas automaticamente após um login bem-sucedido
5. **Expiração**: As tentativas expiram automaticamente após 1 hora

## Componentes do Sistema

### Middleware (middlewares/login_attempts.py)

- Rastreia tentativas de login por IP
- Incrementa contador em caso de falha
- Fornece métodos estáticos para verificar estado

### Formulário de Login (apps/main/home/forms.py)

- Adiciona campo de captcha quando necessário
- Valida token do captcha

### View de Login (apps/main/home/views/accounts.py)

- Verifica se captcha é necessário
- Valida token do captcha
- Reseta tentativas após login bem-sucedido

### Template (apps/main/home/templates/accounts_custom/sign-in.html)

- Exibe captcha quando necessário
- Mostra alerta informativo
- Inclui JavaScript para integração com hCaptcha

## Funcionalidades

### Alertas Visuais

Quando o captcha é necessário, o usuário vê:
- Alerta de aviso com ícone
- Contador de tentativas (ex: "Tentativas: 3/3")
- Widget do hCaptcha

### Validação

- Captcha obrigatório após X tentativas
- Validação do token do hCaptcha
- Mensagens de erro apropriadas

### Segurança

- Rastreamento por IP
- Expiração automática das tentativas
- Reset após login bem-sucedido
- Logs de segurança

## Personalização

### Alterar Número de Tentativas

Modifique a variável `CONFIG_LOGIN_MAX_ATTEMPTS` no arquivo `.env`:

```bash
CONFIG_LOGIN_MAX_ATTEMPTS=5  # Exige captcha após 5 tentativas
```

### Alterar Tempo de Expiração

No arquivo `middlewares/login_attempts.py`, modifique o valor em segundos:

```python
cache.set(cache_key, attempts, 3600)  # 1 hora
```

### Personalizar Mensagens

As mensagens podem ser personalizadas no arquivo `apps/main/home/views/accounts.py`:

```python
form.add_error(None, _("Sua mensagem personalizada aqui."))
```

## Logs

O sistema gera logs para monitoramento:

- `Login bem-sucedido para IP X.X.X.X, tentativas resetadas`
- `Tentativa de login falhou para IP X.X.X.X, tentativa N`

## Compatibilidade

- Funciona com o sistema de 2FA existente
- Compatível com login social
- Integrado com o sistema de licenças
- Funciona em conjunto com outros middlewares de segurança

## Troubleshooting

### Captcha não aparece

1. Verifique se `CONFIG_HCAPTCHA_SITE_KEY` está configurado
2. Confirme se o número de tentativas foi atingido
3. Verifique os logs do middleware

### Captcha sempre aparece

1. Verifique se as tentativas estão sendo resetadas corretamente
2. Confirme se o cache está funcionando
3. Verifique se o IP está sendo detectado corretamente

### Erro de validação do captcha

1. Verifique se `CONFIG_HCAPTCHA_SECRET_KEY` está correto
2. Confirme se o token está sendo enviado corretamente
3. Verifique a conectividade com hCaptcha 