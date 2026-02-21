# PDL 1.10.0 - Sistema de Licenciamento Completo

> **Última atualização:** 21/02/2026

## Painel Definitivo Lineage
### Sistema de Licenciamento Empresarial com Validação DNS e Criptografia Avançada

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Tipos de Licença](#tipos-de-licença)
3. [Validação DNS TXT](#validação-dns-txt)
4. [Middleware de Verificação](#middleware-de-verificação)
5. [API REST](#api-rest)
6. [Painel Administrativo](#painel-administrativo)
7. [Comandos CLI](#comandos-cli)
8. [Sistema de Funcionalidades](#sistema-de-funcionalidades)
9. [Métricas e Analytics](#métricas-e-analytics)
10. [Segurança](#segurança)
11. [Suporte Multilíngue](#suporte-multilíngue)
12. [Estrutura de Arquivos](#estrutura-de-arquivos)
13. [Instalação e Configuração](#instalação-e-configuração)
14. [Exemplos de Uso](#exemplos-de-uso)
15. [FAQ](#faq)

---

## 🚀 Visão Geral

A versão 1.10.0 do Painel Definitivo Lineage (PDL) introduz um sistema de licenciamento empresarial completo, revolucionando a forma como servidores privados gerenciam suas licenças com segurança máxima, validação DNS e controle granular de funcionalidades.

### Principais Características

- ✅ **Sistema de licenciamento empresarial completo**
- 🌐 **Validação DNS TXT com criptografia AES-256-GCM**
- 🛡️ **Middleware de verificação automática**
- 🌐 **API REST completa para integração**
- 🎛️ **Painel administrativo web completo**
- ⚙️ **Comandos CLI para gerenciamento**
- 🔧 **Controle granular de funcionalidades**
- 📊 **Sistema de métricas e analytics**
- 🔐 **Segurança de nível empresarial**
- 🌍 **Suporte multilíngue nativo**

---

## 🔐 Tipos de Licença

### PDL FREE - Licença Gratuita

**Recursos Incluídos:**
- Funcionalidades essenciais do painel
- Sem limite de tempo (nunca expira)
- Apenas uma licença FREE por domínio
- Suporte comunitário

**Limitações:**
- Funcionalidades básicas apenas
- Sem suporte prioritário
- Sem código fonte
- Sem serviços de instalação

### PDL PRO - Licença Profissional

**Recursos Incluídos:**
- Todas as funcionalidades do painel
- Contrato comercial com validação DNS
- Suporte prioritário e personalizado (24/7)
- Código fonte completo
- Serviços de instalação e integração
- Limite de horas de suporte configurável
- Personalizações exclusivas

**Validações Especiais:**
- Contrato comercial obrigatório
- Validação via DNS TXT
- Criptografia AES-256-GCM
- Monitoramento contínuo

---

## 🌐 Validação DNS TXT com Criptografia Avançada

A validação de contratos PDL PRO é feita exclusivamente via registro DNS TXT no domínio **denky.dev.br**. Não há consulta a API ou DNS do cliente.

### Exemplo de Registro DNS

```
# Exemplo de registro DNS TXT
pdl-contract-CONTRATO-2024-001.denky.dev.br TXT "<valor_criptografado>"
```

O valor criptografado deve ser gerado pelo script oficial do DENKY, usando a mesma chave Fernet configurada no projeto do cliente.

### Processo de Validação

1. **Geração do Contrato:** O dono do projeto gera o valor criptografado para o contrato usando o script standalone.
2. **Publicação no DNS:** O valor é publicado em denky.dev.br como registro TXT.
3. **Validação no Cliente:** O sistema do cliente busca o valor do DNS, descriptografa com a chave Fernet e confere se o número do contrato e domínio batem.

---

## 🛡️ Middleware de Verificação Automática

### Verificação Automática

O sistema implementa um middleware que monitora licenças em tempo real:

**Funcionalidades:**
- Validação de licença a cada requisição
- Cache inteligente para performance
- Logs detalhados de todas as verificações
- Detecção de tentativas de bypass

### Monitoramento em Tempo Real

**Métricas Coletadas:**
- Contador de verificações
- Tempo de resposta médio
- Taxa de sucesso/falha
- Histórico completo de verificações

### Configuração do Middleware

```python
MIDDLEWARE = [
    # ... outros middlewares
    'apps.licence.middleware.LicenseMiddleware',
]
```

---

## 🌐 API REST Completa para Integração

### Endpoints Disponíveis

#### 1. API de Ativação
```bash
POST /licence/api/activate/
```

**Parâmetros:**
```json
{
    "license_key": "PDL-XXXX-XXXX-XXXX",
    "domain": "exemplo.com",
    "contact_email": "admin@exemplo.com",
    "company_name": "Empresa Exemplo",
    "contact_phone": "+55 11 99999-9999"
}
```

**Resposta de Sucesso:**
```json
{
    "success": true,
    "message": "Licença ativada com sucesso"
}
```

#### 2. API de Status
```bash
GET /licence/api/status/
```

**Resposta:**
```json
{
    "success": true,
    "is_valid": true,
    "license_info": {
        "license_key": "PDL-XXXX-XXXX-XXXX",
        "license_type": "pro",
        "status": "active",
        "domain": "exemplo.com",
        "expires_at": "2025-12-31",
        "features": {
            "support": true,
            "updates": true,
            "customization": true
        }
    }
}
```

#### 3. API de Funcionalidades
```bash
GET /licence/api/features/?feature=support
```

**Resposta:**
```json
{
    "success": true,
    "feature": "support",
    "can_use": true
}
```

### Exemplos de Uso

#### JavaScript
```javascript
// Verificar status da licença
async function checkLicenseStatus() {
    try {
        const response = await fetch('/licence/api/status/');
        const data = await response.json();
        
        if (data.success && data.is_valid) {
            console.log('Licença válida:', data.license_info);
        } else {
            console.log('Licença inválida ou expirada');
        }
    } catch (error) {
        console.error('Erro ao verificar licença:', error);
    }
}

// Verificar funcionalidade específica
async function canUseFeature(feature) {
    try {
        const response = await fetch(`/licence/api/features/?feature=${feature}`);
        const data = await response.json();
        
        return data.success && data.can_use;
    } catch (error) {
        console.error('Erro ao verificar funcionalidade:', error);
        return false;
    }
}
```

#### Python
```python
import requests

def check_license_status():
    response = requests.get('http://exemplo.com/licence/api/status/')
    data = response.json()
    
    if data['success'] and data['is_valid']:
        print('Licença válida:', data['license_info'])
    else:
        print('Licença inválida ou expirada')

def can_use_feature(feature):
    response = requests.get(f'http://exemplo.com/licence/api/features/?feature={feature}')
    data = response.json()
    
    return data['success'] and data['can_use']
```

#### cURL
```bash
# Verificar status
curl http://exemplo.com/licence/api/status/

# Verificar funcionalidade
curl "http://exemplo.com/licence/api/features/?feature=support"

# Ativar licença
curl -X POST http://exemplo.com/licence/api/activate/ \
  -H "Content-Type: application/json" \
  -d '{
    "license_key": "PDL-XXXX-XXXX-XXXX",
    "domain": "exemplo.com",
    "contact_email": "admin@exemplo.com"
  }'
```

---

## 🎛️ Painel Administrativo Completo

### Dashboard Principal

**Funcionalidades:**
- Visão geral de todas as licenças
- Estatísticas em tempo real
- Gráficos de uso e performance
- Alertas de licenças próximas do vencimento

### Gerenciamento de Licenças

**Operações Disponíveis:**
- Criação de licenças FREE e PRO
- Edição de informações de clientes
- Ativação/desativação de licenças
- Renovação automática e manual
- Exclusão de licenças

### Monitoramento Detalhado

**Recursos de Monitoramento:**
- Histórico completo de verificações
- Logs de tentativas de acesso
- Métricas de performance
- Relatórios de uso

### Interface Web

**Características:**
- Design responsivo
- Interface intuitiva
- Filtros avançados
- Paginação inteligente
- Exportação de dados

---

## ⚙️ Comandos de Gerenciamento CLI

### Geração de Chaves de Criptografia

```bash
python manage.py generate_encryption_key
```

**Funcionalidade:** Gera chave AES-256-GCM segura para criptografia de contratos.

### Teste de Validação DNS

```bash
python manage.py test_dns_validation --domain exemplo.com --contract 12345
```

**Funcionalidade:** Testa validação de contrato via DNS TXT.

**Parâmetros:**
- `--domain`: Domínio a ser testado
- `--contract`: Número do contrato
- `--verbose`: Modo detalhado

### Relatórios de Licenças

```bash
python manage.py license_report --type=pro --status=active
```

**Funcionalidade:** Gera relatórios detalhados de licenças.

**Parâmetros:**
- `--type`: Tipo de licença (free/pro)
- `--status`: Status da licença (active/expired/suspended)
- `--format`: Formato do relatório (json/csv/html)

---

## 🔧 Sistema de Funcionalidades Granular

### Controle Preciso de Recursos

O sistema permite controle granular de funcionalidades baseado no tipo de licença:

#### Funcionalidades PDL FREE

**Recursos Básicos:**
- Dashboard básico
- Gerenciamento de usuários
- Relatórios essenciais
- Suporte comunitário

**Limitações:**
- Sem funcionalidades avançadas
- Sem suporte prioritário
- Sem código fonte

#### Funcionalidades PDL PRO

**Recursos Completos:**
- Dashboard completo
- Todas as funcionalidades avançadas
- Suporte prioritário (24/7)
- Código fonte completo
- Serviços de instalação
- Integração com banco de dados
- Personalizações exclusivas

### Verificação de Funcionalidades

```python
# Verificar se funcionalidade está disponível
if license_manager.can_use_feature('support'):
    # Executar funcionalidade de suporte
    pass
```

---

## 📊 Sistema de Métricas e Analytics

### Métricas de Uso

**Dados Coletados:**
- Horas de suporte utilizadas
- Funcionalidades mais acessadas
- Performance de verificações
- Padrões de uso por cliente

### Relatórios Automáticos

**Tipos de Relatório:**
- Relatórios mensais de uso
- Alertas de vencimento
- Análise de performance
- Estatísticas de clientes

### Dashboard de Analytics

**Visualizações Disponíveis:**
- Gráficos de uso ao longo do tempo
- Comparação entre licenças FREE e PRO
- Análise de performance
- Tendências de uso

---

## 🔐 Segurança de Nível Empresarial

### Proteções Implementadas

**Camadas de Segurança:**
- Validação de domínio rigorosa
- Criptografia AES-256-GCM
- Rate limiting por IP
- Logs de auditoria completos
- Blacklist de licenças revogadas

### Detecção de Fraude

**Mecanismos de Proteção:**
- Monitoramento de tentativas de bypass
- Análise de padrões suspeitos
- Alertas automáticos
- Bloqueio preventivo

### Validações de Segurança

**Verificações Automáticas:**
- Validação de domínio
- Verificação de expiração
- Controle de tentativas de acesso
- Monitoramento de IPs suspeitos

---

## 🌍 Suporte Multilíngue Completo

### Idiomas Suportados

**Traduções Disponíveis:**
- 🇧🇷 **Português** - Interface completa
- 🇺🇸 **Inglês** - Documentação técnica
- 🇪🇸 **Espanhol** - Suporte ao cliente

### Configuração de Idioma

```python
# Configuração de idioma
LANGUAGE_CODE = 'pt-br'
USE_I18N = True
USE_L10N = True

LANGUAGES = [
    ('pt-br', 'Português'),
    ('en', 'English'),
    ('es', 'Español'),
]
```

---

## 📋 Estrutura de Arquivos Organizada

### Organização Modular e Escalável

```
apps/licence/
├── models.py          # Modelos de dados
├── views.py           # Views web e APIs
├── admin.py           # Interface administrativa
├── manager.py         # Gerenciador de licenças
├── utils.py           # Utilitários e criptografia
├── middleware.py      # Middleware de verificação
├── urls.py            # Rotas da aplicação
├── templates/         # Templates HTML
│   └── licence/
│       ├── dashboard.html
│       ├── list.html
│       ├── create.html
│       ├── detail.html
│       ├── edit.html
│       └── status.html
├── management/        # Comandos CLI
│   └── commands/
│       ├── generate_encryption_key.py
│       └── test_dns_validation.py
└── migrations/        # Migrações do banco
```

### Descrição dos Arquivos

**models.py:** Define os modelos License e LicenseVerification
**views.py:** Implementa as views web e APIs REST
**admin.py:** Configura a interface administrativa do Django
**manager.py:** Gerencia operações de licenciamento
**utils.py:** Utilitários para criptografia e validação DNS
**middleware.py:** Middleware de verificação automática
**urls.py:** Define as rotas da aplicação

---

## 🛠️ Instalação e Configuração

### Configuração

```python
# settings.py

# Chave Fernet usada para validar contratos PRO
LICENSE_CONFIG = {
    'ENCRYPTION_KEY': 'SUA_CHAVE_FERNET_AQUI',
    'DNS_TIMEOUT': 10,
}
```

- **ENCRYPTION_KEY:** Deve ser a mesma chave usada no script gerador de contratos.
- **DNS_TIMEOUT:** Tempo limite para consulta DNS.

Remova qualquer configuração relacionada a API, domínio do cliente ou variáveis como PDL_DNS_PREFIX, PDL_ENCRYPTION_KEY, PDL_LICENSE_CACHE_TTL, PDL_VERIFICATION_RATE_LIMIT, PDL_DNS_PREFIX, PDL_ENCRYPTION_KEY, etc.

---

## 📝 Exemplos de Uso

### Validação de Contrato PRO

O sistema do cliente irá buscar o registro DNS:

```
pdl-contract-<numero_contrato>.denky.dev.br TXT "<valor_criptografado>"
```

E irá descriptografar usando a chave Fernet configurada. Se o número do contrato e domínio batem, a licença é válida.

### Criação de Licença FREE

```python
from apps.main.licence.manager import license_manager

# Criar licença FREE
success, result = license_manager.create_free_license(
    domain="exemplo.com",
    contact_email="admin@exemplo.com",
    company_name="Empresa Exemplo",
    contact_phone="+55 11 99999-9999"
)

if success:
    print(f"Licença FREE criada: {result}")
else:
    print(f"Erro: {result}")
```

### Criação de Licença PRO

```python
# Criar licença PRO
success, result = license_manager.create_pro_license(
    domain="exemplo.com",
    contact_email="admin@exemplo.com",
    company_name="Empresa Exemplo",
    contact_phone="+55 11 99999-9999",
    contract_number="12345"
)

if success:
    print(f"Licença PRO criada: {result}")
else:
    print(f"Erro: {result}")
```

### Verificação de Licença

```python
# Verificar status da licença
is_valid = license_manager.check_license_status()
if is_valid:
    print("Licença válida")
else:
    print("Licença inválida ou expirada")

# Verificar funcionalidade específica
can_use_support = license_manager.can_use_feature('support')
if can_use_support:
    print("Funcionalidade de suporte disponível")
```

### Ativação Remota

```python
# Ativar licença remotamente
success, message = license_manager.activate_license(
    license_key="PDL-XXXX-XXXX-XXXX",
    domain="exemplo.com",
    contact_email="admin@exemplo.com",
    company_name="Empresa Exemplo"
)

if success:
    print("Licença ativada com sucesso")
else:
    print(f"Erro na ativação: {message}")
```

---

## ❓ FAQ

### Perguntas Frequentes

**Q: Como funciona a validação DNS?**
A: O sistema gera um número de contrato único, criptografa com AES-256-GCM e o cliente adiciona um registro TXT no DNS. O sistema verifica automaticamente via DNS.

**Q: Posso ter múltiplas licenças FREE?**
A: Não, apenas uma licença FREE é permitida por domínio.

**Q: Como renovar uma licença?**
A: Licenças podem ser renovadas através do painel administrativo ou via API, adicionando dias ao período de expiração.

**Q: O que acontece se a licença expirar?**
A: O sistema automaticamente desativa funcionalidades avançadas e exibe alertas de renovação.

**Q: Como funciona o suporte prioritário?**
A: Licenças PRO incluem suporte prioritário com limite de horas configurável e acesso direto à equipe técnica.

**Q: Posso migrar de FREE para PRO?**
A: Sim, é possível fazer upgrade de FREE para PRO através do painel administrativo.

**Q: Como funciona a criptografia?**
A: O sistema usa AES-256-GCM para criptografar dados sensíveis como números de contrato.

**Q: Posso usar a API sem autenticação?**
A: As APIs de verificação são públicas, mas as de gerenciamento requerem autenticação de superusuário.

---

## 📞 Suporte

### Canais de Suporte

**PDL FREE:**
- Documentação online
- Fórum da comunidade
- GitHub Issues

**PDL PRO:**
- Suporte prioritário 24/7
- Email dedicado
- Chat em tempo real
- Telefone de emergência

### Documentação Adicional

- **Guia de Instalação:** docs/INSTALLATION.md
- **Guia de Configuração:** docs/CONFIGURATION.md
- **Referência da API:** docs/API_REFERENCE.md
- **Exemplos de Código:** docs/CODE_EXAMPLES.md

---

## 📄 Licença

Este software é licenciado sob a licença MIT. Veja o arquivo LICENSE.md para mais detalhes.

---

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor, leia o guia de contribuição antes de submeter pull requests.

---

**© 2025 Painel Definitivo Lineage - Todos os direitos reservados** 
---

[ Voltar ao Índice](../INDEX.md)

