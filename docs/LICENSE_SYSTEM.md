# Sistema de Licenciamento L2JPremium

## Visão Geral

O sistema de licenciamento L2JPremium (Painel Definitivo Lineage) é um sistema completo para gerenciar licenças de software, suportando dois tipos de licenças:

- **L2JPremium FREE**: Licença gratuita para uso livre
- **L2JPremium PRO**: Licença profissional com vínculo contratual

## Arquitetura

### Estrutura do App `licence`

```
apps/licence/
├── __init__.py
├── admin.py              # Interface administrativa
├── apps.py               # Configuração do app
├── manager.py            # Gerenciador de licenças
├── middleware.py         # Middlewares de verificação
├── models.py             # Modelos de dados
├── urls.py               # URLs do app
├── views.py              # Views e APIs
├── activate_license.py   # Script interativo
└── management/
    └── commands/
        ├── create_license.py
        └── check_license.py
```

### Modelos

#### License
- `license_type`: Tipo da licença (free/pro)
- `license_key`: Chave única da licença
- `domain`: Domínio ativado
- `company_name`: Nome da empresa/cliente
- `contact_email`: E-mail de contato
- `contact_phone`: Telefone de contato
- `status`: Status da licença (active/expired/suspended/pending)
- `activated_at`: Data de ativação
- `expires_at`: Data de expiração
- `verification_count`: Contador de verificações
- `contract_number`: Número do contrato (L2JPremium PRO)
- `support_hours_used`: Horas de suporte utilizadas
- `support_hours_limit`: Limite de horas de suporte
- `features_enabled`: Funcionalidades habilitadas (JSON)
- `notes`: Observações

#### LicenseVerification
- `license`: Licença relacionada
- `verification_date`: Data da verificação
- `ip_address`: Endereço IP
- `user_agent`: User Agent
- `success`: Verificação bem-sucedida
- `error_message`: Mensagem de erro
- `response_time`: Tempo de resposta

## Funcionalidades

### L2JPremium FREE
- ✅ Painel administrativo
- ✅ Funcionalidades básicas
- ✅ Sistema de temas
- ✅ Acesso à API
- ❌ Suporte oficial
- ❌ Atualizações garantidas
- ❌ Personalização
- ❌ Suporte prioritário

### L2JPremium PRO
- ✅ Todas as funcionalidades FREE
- ✅ Suporte técnico
- ✅ Atualizações automáticas
- ✅ Personalização avançada
- ✅ Suporte prioritário
- ✅ Código fonte completo
- ✅ Serviço de instalação
- ✅ Integração com banco de dados

## Uso

### 1. Configuração

Adicione o app `licence` ao `INSTALLED_APPS` em `settings.py`:

```python
INSTALLED_APPS = [
    # ...
    "apps.licence",
    # ...
]
```

Adicione os middlewares em `settings.py`:

```python
MIDDLEWARE = [
    # ...
    "apps.licence.middleware.LicenseMiddleware",
    "apps.licence.middleware.LicenseFeatureMiddleware",
    # ...
]
```

### 2. Migrações

Execute as migrações para criar as tabelas:

```bash
python manage.py makemigrations licence
python manage.py migrate
```

### 3. Comandos de Gerenciamento

#### Criar Licença

```bash
# L2JPremium FREE
python manage.py create_license --type free --domain meusite.com --email contato@meusite.com

# L2JPremium PRO
python manage.py create_license --type pro --domain meusite.com --email contato@meusite.com --company "Minha Empresa" --contract "CONTRATO-2024-001"
```

#### Verificar Licenças

```bash
# Verificação básica
python manage.py check_license

# Verificação detalhada
python manage.py check_license --detailed

# Verificar licença específica
python manage.py check_license --domain meusite.com
```

### 4. Script Interativo

Execute o script interativo para gerenciar licenças:

```bash
python apps/licence/activate_license.py
```

### 5. Interface Web

Acesse a interface web em `/license/` para gerenciar licenças através do navegador.

## APIs

### Ativação de Licença

```http
POST /license/api/activate/
Content-Type: application/json

{
    "license_key": "XXXX-XXXX-XXXX-XXXX-XXXX-XXXX-XXXX-XXXX",
    "domain": "meusite.com",
    "contact_email": "contato@meusite.com",
    "company_name": "Minha Empresa",
    "contact_phone": "(11) 99999-9999"
}
```

### Verificar Status

```http
GET /license/api/status/
```

### Verificar Funcionalidades

```http
GET /license/api/features/
GET /license/api/features/?feature=support
```

## Middleware

### LicenseMiddleware
Verifica a validade da licença em tempo real e redireciona para página de status se necessário.

### LicenseFeatureMiddleware
Adiciona informações da licença ao request:
- `request.license_info`: Informações da licença atual
- `request.can_use_feature(feature)`: Verifica se uma funcionalidade está disponível

## Uso no Código

### Verificar Licença

```python
from apps.main.licence.manager import license_manager

# Verificar se a licença está válida
if license_manager.check_license_status():
    print("Licença válida")
else:
    print("Licença inválida")

# Verificar funcionalidade específica
if license_manager.can_use_feature('support'):
    print("Suporte disponível")
```

### Em Templates

```html
{% if request.can_use_feature('support') %}
    <div class="support-widget">
        <!-- Widget de suporte -->
    </div>
{% endif %}
```

### Em Views

```python
def minha_view(request):
    if not request.can_use_feature('customization'):
        messages.warning(request, "Personalização não disponível na sua licença")
        return redirect('home')
    
    # Lógica da view
```

## Monitoramento

### Logs de Verificação
Todas as verificações de licença são registradas no modelo `LicenseVerification` com:
- Data/hora da verificação
- IP do cliente
- User Agent
- Status da verificação
- Tempo de resposta
- Mensagens de erro

### Cache
O sistema utiliza cache para otimizar as verificações:
- Cache de 1 hora para informações da licença
- Verificação remota a cada 24 horas

## Segurança

### Chaves de Licença
- Geradas automaticamente com 32 caracteres
- Formato: XXXX-XXXX-XXXX-XXXX-XXXX-XXXX-XXXX-XXXX
- Únicas por licença

### Verificação Remota
O sistema suporta verificação remota através de API (configurável no `manager.py`).

### Middleware de Proteção
- Verifica licença em todas as requisições
- Lista de URLs exentas configurável
- Redirecionamento automático para página de status

## Personalização

### Funcionalidades
As funcionalidades são definidas no método `get_default_features()` do modelo `License`.

### Middleware
Os middlewares podem ser personalizados para diferentes comportamentos de verificação.

### Templates
Os templates estão em `templates/licence/` e podem ser personalizados conforme necessário.

## Troubleshooting

### Licença não encontrada
1. Verifique se existe uma licença ativa no banco de dados
2. Execute `python manage.py check_license --detailed`
3. Verifique os logs de verificação

### Verificação falhando
1. Verifique a conectividade de rede
2. Confirme se a API de verificação remota está funcionando
3. Verifique os logs de erro no modelo `LicenseVerification`

### Middleware não funcionando
1. Confirme se os middlewares estão no `MIDDLEWARE` em `settings.py`
2. Verifique se o app `licence` está em `INSTALLED_APPS`
3. Reinicie o servidor Django

## Suporte

Para suporte técnico:
- **L2JPremium FREE**: Comunidade e documentação
- **L2JPremium PRO**: Suporte profissional incluído

### Contatos
- E-mail: suporte@L2JPremium.com
- Documentação: https://L2JPremium.com
- Comunidade: https://L2JPremium.com

## Changelog

### v1.0.0
- Sistema inicial de licenciamento
- Suporte a L2JPremium FREE e L2JPremium PRO
- Middleware de verificação
- APIs de ativação e status
- Interface administrativa
- Comandos de gerenciamento
- Script interativo
- Documentação completa 