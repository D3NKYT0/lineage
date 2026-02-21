# Sistema de Licenciamento (PDL)

> **Última atualização:** 21/02/2026

## 📋 Visão Geral

O Painel Definitivo Lineage (PDL) possui um sistema de licenciamento empresarial completo, desenhado para gerenciar licenças com segurança através de validação DNS, controle granular de funcionalidades e criptografia avançada.

## 🔐 Tipos de Licença

### PDL FREE - Licença Gratuita
- Funcionalidades essenciais do painel (Dashboard, Gerenciamento de Usuários, Sistema de Temas e API Básica).
- Sem limite de tempo.
- Apenas uma licença FREE por domínio.
- Sem funcionalidades avançadas, suporte prioritário e código fonte.

### PDL PRO - Licença Profissional
- Todas as funcionalidades do painel, incluindo ferramentas avançadas e Analytics.
- Contrato comercial obrigatório validado via DNS.
- Suporte prioritário (24/7), serviços de instalação e atualizações garantidas.
- Código fonte completo disponível.

## 🌐 Validação DNS TXT e Criptografia
A validação de contratos PDL PRO é feita offline, exclusivamente via registro DNS TXT no domínio oficial do fornecedor (ex: `denky.dev.br`). Não há consulta de API que exija dependência externa constante para validação.

### Exemplo de Registro DNS
```text
pdl-contract-CONTRATO-XXXX-001.denky.dev.br TXT "<valor_criptografado_aes_256>"
```
O valor no registro TXT é descriptografado localmente no backend do cliente através da chave `__Fernet__` simétrica, validando o vínculo autêntico e o número do contrato/domínio localmente.

## 🛡️ Middlewares de Proteção
O sistema implementa middlewares que monitoram o status das licenças de modo transparente nas requisições:

- **`apps.licence.middleware.LicenseMiddleware`**: Checa e valida as licenças com cache inteligente.
- **`apps.licence.middleware.LicenseFeatureMiddleware`**: Popula o controle de acesso por features (`request.can_use_feature(...)`).

Métricas como contador de verificações, taxa de sucesso/falha e varredura de tentativas de bypass são logadas ativamente no modelo `LicenseVerification`.

## 🎛️ Gestão via Painel Administrativo ou CLI

### Painel Web
- Visão geral, estatísticas em tempo real, monitoramento detalhado, paginação e controle manual de expirações. Configurado na rota `/license/`.

### CLI (Management Commands)
- **Geração Automática de Chaves**: `python manage.py generate_encryption_key` (Cria a chave inicial AES-256-GCM).
- **Relatórios**: `python manage.py license_report --type=pro --status=active`
- **Validação Secundária de DNS**: `python manage.py test_dns_validation --domain ex.com --contract n`
- **Geração de Licenças via Terminal**:
  ```bash
  python manage.py create_license --type pro --domain mysite.com --email webadmin@mysite.com --company "Company" --contract "CONTRATO-1"
  ```

## 🌍 Arquitetura e Integração

A aplicação reside no diretório `apps/licence/` e conta com APIs REST:
- `POST /license/api/activate/`: Ativação remota via payload.
- `GET /license/api/status/`: Retorno consolidado do status atual.
- `GET /license/api/features/?feature=X`: Endpoint unitário para checamento.

O módulo todo suporta `i18n` e logs detalhados de tentativas de acesso persistidos nas queries para monitoramento anti-fraude.
---

[ Voltar ao Índice](../INDEX.md)

