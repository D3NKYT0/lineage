# Licença do Projeto PDL (Painel Definitivo Lineage)

## 📌 Resumo Executivo

O projeto **PDL (Painel Definitivo Lineage)** é um software de código aberto, 100% gratuito e distribuído sob a **Licença MIT**. 

Qualquer pessoa tem a liberdade de baixar, usar, modificar e distribuir o painel, seja para fins pessoais, educacionais ou comerciais.

O que comercializamos não é o código-fonte, mas sim os nossos **Serviços de Suporte (PDL PRO)**, que englobam a instalação, configuração, suporte técnico VIP e garantias de atualizações por parte da nossa equipe oficial.

---

## 🔓 Licença do Código-Fonte: MIT License

Todo o ecossistema do painel PDL, incluindo arquiteturas baseadas em templates, lógica de backend, integrações com o Lineage 2 e customizações de frontend, está coberto pela **Licença MIT**.

### Termos da Licença MIT

> Permite o uso comercial, modificação, distribuição e uso privado, desde que o aviso de direitos autorais e a permissão sejam incluídos em todas as cópias. O software é fornecido "como está", sem qualquer tipo de garantia expressa ou implícita.

*(Para o texto completo oficial em inglês da Licença MIT, consulte o repositório orginal ou o site opensource.org/licenses/MIT).*

---

## 🛠️ O que foi desenvolvido pela Equipe PDL

Embora todo o código seja 100% de código aberto, gostaríamos de esclarecer e creditar o escopo do que foi desenvolvido com exclusividade e dedicação pela Equipe PDL sobre a base dos templates:

- **Backend Completo (Django & Python):** Desenvolvido em **Python 3.14** e **Django**, incluindo API REST, autenticação (com 2FA), portais de pagamentos (Mercado Pago, Stripe, PayPal) e processamento assíncrono via **Celery** e **Redis**.
- **Integração Lineage 2:** Sincronização, leitura e escrita no banco de dados do L2, manipulação de contas, personagens e clãs via **PostgreSQL**.
- **Sistemas Exclusivos:** Carteira digital (Wallet), loja virtual, marketplace, leilões, rankings, minigames (roleta, caixas, etc.), sistema de licenciamento e notificações automáticas (via **Daphne/WebSockets**).
- **Frontend e Admin Customizado:** Todas as telas, dashboards e adaptações feitas sobre o tema base para atender exclusivamente ao projeto PDL.
- **Infraestrutura e DevOps:** Arquitetura 100% conteinerizada via **Docker** e **Docker Compose**, roteamento e gateway proxy via **Nginx**, e execução em servidores WSGI/ASGI (**Gunicorn** e **Daphne**). Módulo de mídia e validação utilizando **FFmpeg**.

*Copyright (c) 2024-2026 Daniel Amaral / PDL Team (https://pdl.denky.dev.br).*

---

## 💼 Nosso Modelo de Negócio: Suporte PDL PRO

Como o software é livre, você pode configurá-lo e mantê-lo por conta própria (Modo *Do-It-Yourself* ou PDL Free). No entanto, para projetos que exigem estabilidade, segurança e tranquilidade, oferecemos os nossos **Serviços de Suporte Especializado**:

### 🟢 PDL Free (Faça você mesmo)
- ✅ Código aberto e gratuito sob a Licença MIT.
- ✅ Pode ser usado comercialmente.
- ❌ **Sem suporte técnico oficial ou ajuda de configuração.**
- ❌ **Sem garantia de implantação, estabilidade ou atualizações garantidas por nós.**

### 🔵 PDL PRO (Suporte e Serviços Premium)
Voltado para administradores que querem focar na gestão do seu servidor de Lineage 2, deixando a parte técnica e a gestão do painel conosco.
- ✅ **Suporte técnico dedicado, prioritário e auxílio na configuração inicial.**
- ✅ **Instalação, implantação e correções emergenciais.**
- ✅ **Atualizações regulares garantidas e acesso antecipado a novas funcionalidades.**
- ✅ **Garantia de funcionamento atrelada via acordo e termos de serviço (SLA).**

---

## 🌟 Tecnologias Empregadas e Créditos

O **PDL** é construído no ombro de gigantes tecnológicos. Reconhecemos e agradecemos as comunidades de código aberto que mantêm as seguintes tecnologias fundamentais, além da equipe AppSeed pelo tema Frontend base:

- **[Volt Pro (AppSeed)](https://appseed.us/):** Tema HTML/CSS base utilizado para criar as interfaces (Copyright c 2019 AppSeed).
- **[Python](https://www.python.org/) & [Django](https://www.djangoproject.com/):** Linguagem base e framework web robusto que sustenta o backend do projeto (PSF License / BSD License).
- **[PostgreSQL](https://www.postgresql.org/):** Banco de dados relacional avançado utilizado na estrutura principal (PostgreSQL License).
- **[Redis](https://redis.io/):** Banco de dados em memória, utilizado para mensageria, cache e brokers (BSD License).
- **[Celery](https://docs.celeryq.dev/):** Fila de tarefas distribuídas assíncronas em Python (BSD License).
- **[Docker](https://www.docker.com/):** Plataforma de conteinerização que garante padronização e escalabilidade do Codebase (Apache License 2.0).
- **[Nginx](https://nginx.org/):** Servidor web de alta performance usado como proxy reverso (2-clause BSD-like license).
- **[Gunicorn](https://gunicorn.org/) & [Daphne](https://github.com/django/daphne):** Servidores WSGI e ASGI para a execução do Django (MIT / BSD License).
- **[Lineage 2 (NCSoft)](https://lineage2.com):** Jogo originário em torno do qual foi desenvolvido todo o painel. Este painel é criado para administradores de servidores (L2J e correlatos) e respeita implicitamente as propriedades artísticas da NCSoft, não interferindo nos códigos proprietários do jogo em si.

---

## 📞 Contato e Suporte Oficial

Para adquirir o acesso ao nosso Suporte Especializado (PDL PRO) ou contatar a equipe oficial para outras questões:

- 🌐 **Site Principal:** [https://pdl.denky.dev.br](https://pdl.denky.dev.br)
- 📧 **E-mail:** [contato@denky.dev.br](mailto:contato@denky.dev.br)
- 🐙 **GitHub Oficial:** [https://github.com/D3NKYT0/lineage](https://github.com/D3NKYT0/lineage)

---

## ⚠️ Isenção de Responsabilidade Legal (Disclaimer)

ESTE SOFTWARE É FORNECIDO "COMO ESTÁ" (*AS IS*), SEM GARANTIAS DE QUALQUER TIPO, EXPRESSAS OU IMPLÍCITAS, INCLUINDO, MAS NÃO SE LIMITANDO A GARANTIAS DE COMERCIALIZAÇÃO, ADEQUAÇÃO A UM PROPÓSITO ESPECÍFICO E NÃO VIOLAÇÃO.

EM NENHUMA CIRCUNSTÂNCIA OS AUTORES, DESENVOLVEDORES (EQUIPE PDL) OU DETENTORES DOS DIREITOS AUTORAIS SERÃO OU PODERÃO SER RESPONSABILIZADOS POR QUALQUER RECLAMAÇÃO, DANO (SEJA DIRETO, INDIRETO, INCIDENTAL, ESPECIAL OU CONSEQUENTE INDEPENDENTE DE SUA NATUREZA) OU PARCELA DE RESPONSABILIDADE, SEJA EM EVENTOS EXERCIDOS DE AÇÃO COMPROBATÓRIA, INVASÕES SISTÊMICAS, PROBLEMAS NA INFRAESTRUTURA DE BANCO DE DADOS ALHEIA (L2) OU FALHAS NO CÓDIGO FONTE AFETADO POR TERCEIROS NO MESMO SERVIDOR. O USO DESTE PAINEL DE CONTROLE DEVE SEMPRE SER ACOMPANHADO DE BOAS PRÁTICAS DE SEGURANÇA E GERENCIAMENTO EXCLUSIVO DO PRÓPRIO ADMINISTRADOR LOCAL.

---

**Última Atualização:** 04 de Março de 2026  
**Versão do Documento:** 3.0
