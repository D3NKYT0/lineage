# L2JPremium 1.11.0 – Sistema Matriz-Filial de Contas (Explicação Técnica)

## Visão Geral
O recurso Matriz-Filial permite que múltiplos servidores Lineage 2 (filiais) sejam gerenciados sob uma estrutura centralizada (matriz), compartilhando ou isolando dados conforme a necessidade do projeto. O sistema foi desenhado para ser flexível, seguro e facilmente integrável a diferentes arquiteturas.

---

## Como Funciona

### 1. Configuração via Ambiente
- O modo de operação é definido por variáveis de ambiente:
  - `LINEAGE_ACCOUNT_MODE=native` ou `api`
  - `LINEAGE_QUERY_MODULE` define a versão do banco Lineage 2 para cada filial.
- Cada filial pode ter seu próprio conjunto de variáveis de conexão (host, user, password, db, port), permitindo múltiplos bancos simultâneos.

### 2. Abstração de Acesso
- O sistema utiliza **importação dinâmica** para carregar a classe de queries adequada para cada filial, via `get_query_class`.
- O acesso às contas do jogo é feito por meio de uma interface unificada (`LineageAccount`), independente do modo (nativo ou API).

### 3. Hierarquia Matriz-Filial
- A matriz centraliza a gestão de usuários, permissões e políticas globais.
- Cada filial pode operar de forma independente, mas segue as regras da matriz.
- O painel permite alternar entre filiais, visualizar dados agregados ou filtrados por filial.

### 4. Integração Multi-Servidor
- Suporte a múltiplos bancos de dados simultâneos.
- Possibilidade de adicionar/remover filiais sem reiniciar o sistema.
- Cada operação (consulta, registro, vinculação) é roteada para o banco/filial correto de acordo com o contexto do usuário ou da requisição.

### 5. Segurança e Isolamento
- Cada filial tem seu próprio escopo de dados, evitando vazamento entre servidores.
- Permissões e acessos são controlados por níveis (matriz, filial, usuário).
- Auditoria centralizada: todas as operações são logadas e podem ser auditadas pela matriz.

### 6. API e Extensibilidade
- O sistema expõe endpoints REST para integração com sistemas externos, automações e painéis customizados.
- A interface de programação é a mesma para todos os modos, facilitando manutenção e evolução do código.

---

## Principais Componentes Técnicos

- **apps/lineage/server/lineage_account_manager.py**  
  Gerencia o modo de operação (nativo/API) e a interface de acesso às contas.

- **utils/dynamic_import.py**  
  Responsável por importar dinamicamente a classe de queries conforme a filial e versão do Lineage 2.

- **Variáveis de Ambiente**  
  Permitem configurar múltiplas conexões e modos de operação sem alterar o código.

- **Decorators e Middlewares**  
  Garantem autenticação, autorização e roteamento correto das operações entre matriz e filiais.

- **Relatórios e Dashboards**  
  Agregam dados de todas as filiais, permitindo análises globais ou segmentadas.

---

## Exemplo de Configuração Multi-Filial

```env
# Matriz (painel principal)
LINEAGE_ACCOUNT_MODE=native

# Filial 1
LINEAGE1_DB_NAME=l2jdb1
LINEAGE1_DB_USER=l2user1
LINEAGE1_DB_PASSWORD=senha1
LINEAGE1_DB_HOST=192.168.1.101
LINEAGE1_DB_PORT=3306
LINEAGE1_QUERY_MODULE=acis

# Filial 2
LINEAGE2_DB_NAME=l2jdb2
LINEAGE2_DB_USER=l2user2
LINEAGE2_DB_PASSWORD=senha2
LINEAGE2_DB_HOST=192.168.1.102
LINEAGE2_DB_PORT=3306
LINEAGE2_QUERY_MODULE=remastered
```

No código, basta selecionar a filial desejada para que todas as operações sejam roteadas para o banco correto.

---

## Fluxo de Operação (Simplificado)

```mermaid
graph TD
    A[Usuário seleciona filial] --> B[Configuração dinâmica de conexão]
    B --> C[Importação da query correta]
    C --> D[Operação de conta]
    D --> E[Execução no banco da filial]
    E --> F[Retorno para o painel]
```

---

## Vantagens para Desenvolvedores

- **Escalabilidade:** Adicione quantas filiais quiser, sem reescrever código.
- **Manutenção:** Interface única para todos os modos e bancos.
- **Extensibilidade:** Fácil integração com APIs, automações e sistemas externos.
- **Segurança:** Isolamento de dados e permissões por filial.
- **Observabilidade:** Auditoria centralizada e logs detalhados.

---

## Resumo Técnico

O sistema Matriz-Filial do L2JPremium 1.11.0 foi projetado para ambientes profissionais, com foco em flexibilidade, segurança e facilidade de integração. Ele abstrai a complexidade de múltiplos bancos e servidores, oferecendo uma experiência unificada tanto para administradores quanto para desenvolvedores.

Se você precisa de um painel multi-servidor, escalável e pronto para integrações corporativas, o L2JPremium 1.11.0 entrega tudo isso de forma open source e altamente configurável. 