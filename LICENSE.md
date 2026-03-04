# Licença do Projeto PDL (Painel Definitivo Lineage)

## 📌 Resumo Executivo

O projeto **PDL (Painel Definitivo Lineage)** adota um modelo de **Licenciamento Duplo (Dual License)**. 
Isso significa que o projeto é composto por arquiteturas open source de terceiros e código proprietário desenvolvido exclusivamente pela equipe PDL.

- **Componentes Base (Frontend/Tema):** Distribuídos sob a Licença MIT (Livres).
- **Código PDL (Backend, Sistemas L2, Frontend Customizado):** Protegidos por direitos autorais (Proprietário), com regras de uso específicas divididas entre as modalidades **PDL FREE** (Não-Comercial) e **PDL PRO** (Comercial).

---

## 🔓 Parte 1: Componentes Open Source (Licença MIT)

O projeto utiliza como fundação o tema "Volt Pro" e outras bibliotecas. Estes componentes específicos permanecem sob a **Licença MIT**.

### O que é coberto pela MIT?
- **Tema Base:** Templates HTML/CSS originais do tema Volt Pro.
- **Bibliotecas:** Dependências JavaScript e CSS de terceiros (Bootstrap, jQuery, etc.).
- **Assets:** Ícones, fontes e recursos visuais originais do tema base.

### Copyright dos Componentes Base
```text
Copyright (c) 2019-presente AppSeed (http://appseed.us/)
```

### Termos da Licença MIT
> Permite o uso comercial, modificação, distribuição e uso privado destes componentes específicos, desde que o aviso de direitos autorais e a permissão sejam incluídos em todas as cópias. O software é fornecido "como está", sem garantias.
*(Para o texto completo em inglês da Licença MIT, consulte o repositório original dos componentes de terceiros).*

---

## 🔒 Parte 2: Código Proprietário PDL (Todos os Direitos Reservados)

Todo o ecossistema lógico, integrações, APIs e customizações criadas para o Lineage 2 pertencem à equipe PDL. **Este código NÃO é Open Source e NÃO está sob a licença MIT.**

### Copyright PDL
```text
Copyright (c) 2024-2026 Daniel Amaral / PDL Team (https://pdl.denky.dev.br). Todos os direitos reservados.
```

### O que é coberto (Código Proprietário)?
- **Backend Completo (Django & Python):** Desenvolvido em **Python 3.14** e **Django**, incluindo API REST, autenticação (com 2FA), portais de pagamentos (Mercado Pago, Stripe, PayPal) e processamento assíncrono via **Celery** e **Redis**.
- **Integração Lineage 2:** Sincronização, leitura e escrita no banco de dados do L2, manipulação de contas, personagens e clãs via **PostgreSQL**.
- **Sistemas Exclusivos:** Carteira digital (Wallet), loja virtual, marketplace, leilões, rankings, minigames (roleta, caixas, etc.), sistema de licenciamento e notificações automáticas (via **Daphne/WebSockets**).
- **Frontend e Admin Customizado:** Todas as telas, dashboards e adaptações feitas sobre o tema base para atender exclusivamente ao projeto PDL.
- **Infraestrutura e DevOps:** Arquitetura 100% conteinerizada via **Docker** e **Docker Compose**, roteamento e gateway proxy via **Nginx**, e execução em servidores WSGI/ASGI (**Gunicorn** e **Daphne**). Módulo de mídia e validação utilizando **FFmpeg**.

---

## ⚖️ Modalidades de Uso do Código Proprietário

O uso da Parte 2 (Código Proprietário) é regulado por duas modalidades vigentes:

### 🟢 PDL FREE (Uso Não-Comercial)
Licença voltada para testes, aprendizado e servidores privados comunitários sem fins lucrativos.

**✅ O que é Permitido:**
- Uso pessoal, educacional ou para desenvolvimento de testes locais.
- Deploy em servidores de Lineage 2 **estritamente não comerciais** (onde não há venda de itens, doações com recompensas ou comercialização de vantagens VIP).
- Estudar e modificar o código-fonte internamente para **uso próprio**.

**❌ O que é Restrito (Sem garantias do Free):**
- Não há suporte técnico ou garantia de implantação/funcionamento.
- Atualizações não são garantidas de forma ativa para a versão gratuita.

### 🔵 PDL PRO (Uso Comercial)
Licença comercial obrigatória para qualquer servidor de Lineage 2 que envolva monetização ou obtenção de renda (venda de moedas, itens, status VIP, doações recompensadas).

**❌ O que NÃO é Permitido (Mesmo com ou sem licença PRO):**
- Revender, sublicenciar, distribuir ou transformar o painel em modelo *Software as a Service* (SaaS) a terceiros.
- Criar produtos derivados para venda concorrente usando a base de código do PDL.
- Remover os créditos fixos, logotipos essenciais ou avisos de copyright do painel PDL.

**✅ Vantagens Inclusas na Licença PRO:**
- Conformidade e permissão legal imediata para utilizar os sistemas completos de monetização.
- Suporte técnico dedicado, prioritário e suporte com a configuração inicial.
- Atualizações regulares, correções de segurança e acesso a novas funcionalidades.
- Garantia de funcionamento atrelada via acordo e termos de serviço (SLA).

---

## 🌟 Tecnologias Empregadas e Créditos

O **PDL** é construído no ombro de gigantes tecnológicos. Reconhecemos e agradecemos as comunidades de código aberto que mantêm as seguintes tecnologias fundamentais:

- **[Python](https://www.python.org/) & [Django](https://www.djangoproject.com/):** Linguagem base e framework web robusto que sustenta o backend do projeto (PSF License / BSD License).
- **[PostgreSQL](https://www.postgresql.org/):** Banco de dados relacional avançado utilizado na estrutura principal (PostgreSQL License).
- **[Redis](https://redis.io/):** Banco de dados em memória, utilizado para mensageria, cache e brokers (BSD License).
- **[Celery](https://docs.celeryq.dev/):** Fila de tarefas distribuídas assíncronas em Python (BSD License).
- **[Docker](https://www.docker.com/):** Plataforma de conteinerização que garante padronização e escalabilidade do Codebase (Apache License 2.0).
- **[Nginx](https://nginx.org/):** Servidor web de alta performance usado como proxy reverso (2-clause BSD-like license).
- **[Gunicorn](https://gunicorn.org/) & [Daphne](https://github.com/django/daphne):** Servidores WSGI e ASGI para a execução do Django (MIT / BSD License).
- **[Lineage 2 (NCSoft)](https://lineage2.com):** Jogo originário em torno do qual foi desenvolvido todo o painel. Este painel é criado para administradores de servidores (L2J e correlatos) e respeita implicitamente as propriedades artísticas da NCSoft na representação em painel, não interferindo nos códigos proprietários do jogo em si.

---

## 📋 Tabela Resumo de Licenciamento

| Sistema / Abaixo descrito        | Tipo de Licença      | Uso Comercial (Com monetização) | Suporte Técnico e Updates  |
|----------------------------------|----------------------|---------------------------------|----------------------------|
| **Frontend Base (Volt/Libs)**    | MIT Orientado        | ✅ Permitido integralmente      | ❌ Nenhum                   |
| **Backend & Lógica da API PDL**  | Proprietário PDL     | ⚠️ Restrito (Apenas PDL PRO)    | ✅ Exclusivo PDL PRO        |
| **Integração no BD Lineage 2**   | Proprietário PDL     | ⚠️ Restrito (Apenas PDL PRO)    | ✅ Exclusivo PDL PRO        |
| **Módulos Fiscais (Loja/Pagto)** | Proprietário PDL     | ⚠️ Restrito (Apenas PDL PRO)    | ✅ Exclusivo PDL PRO        |
| **Documentação Técnica**         | MIT Orientado        | ✅ Permitido integralmente      | ❌ Nenhum                   |

---

## 📞 Contato e Soluções Administrativas

Para regularizar seu projeto, solicitar orçamentos, requisitar módulos sob medida ou adquirir a Licença PDL PRO com os suportes atrelados, use os canais oficiais abaixo:

- 🌐 **Site Principal:** [https://pdl.denky.dev.br](https://pdl.denky.dev.br)
- 📧 **E-mail:** [contato@denky.dev.br](mailto:contato@denky.dev.br)
- 🐙 **GitHub Oficial:** [https://github.com/D3NKYT0/lineage](https://github.com/D3NKYT0/lineage)

*(Isenção: Para suporte aos componentes MIT originais do layout base, contate a desenvolvedora AppSeed via support@appseed.us).*

---

## ⚠️ Isenção de Responsabilidade Legal (Disclaimer)

ESTE SOFTWARE É FORNECIDO "COMO ESTÁ" (*AS IS*), SEM GARANTIAS DE QUALQUER TIPO, EXPRESSAS OU IMPLÍCITAS, INCLUINDO, MAS NÃO SE LIMITANDO A GARANTIAS DE COMERCIALIZAÇÃO, ADEQUAÇÃO A UM PROPÓSITO ESPECÍFICO E NÃO VIOLAÇÃO.

EM NENHUMA CIRCUNSTÂNCIA OS AUTORES, DESENVOLVEDORES (EQUIPE PDL) OU DETENTORES DOS DIREITOS AUTORAIS SERÃO OU PODERÃO SER RESPONSABILIZADOS POR QUALQUER RECLAMAÇÃO, DANO (SEJA DIRETO, INDIRETO, INCIDENTAL, ESPECIAL OU CONSEQUENTE INDEPENDENTE DE SUA NATUREZA) OU PARCELA DE RESPONSABILIDADE, SEJA EM EVENTOS EXERCIDOS DE AÇÃO COMPROBATÓRIA, INVASÕES SISTÊMICAS, PROBLEMAS NA INFRAESTRUTURA DE BANCO DE DADOS ALHEIA (L2) OU FALHAS NO CÓDIGO FONTE AFETADO POR TERCEIROS NO MESMO SERVIDOR. O USO DESTE PAINEL DE CONTROLE DEVE SEMPRE SER ACOMPANHADO DE BOAS PRÁTICAS DE SEGURANÇA E GERENCIMENTO EXCLUSIVO DO PRÓPRIO ADMINISTRADOR LOCAL.

---

**Última Atualização:** 04 de Março de 2026  
**Versão do Documento:** 2.1
