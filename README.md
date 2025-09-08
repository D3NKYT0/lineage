# Painel Definitivo Lineage [1.14](https://l2jprmeium.com)

<img align="right" height="180" src="https://i.imgur.com/EzJCcrr.png"/>

 A Platafrma L2JPremium é um painel que nasceu com a missão de oferecer ferramentas poderosas para administradores de servidores privados de Lineage 2. Inicialmente voltado à análise de riscos e estabilidade dos servidores, o projeto evoluiu e se consolidou como uma solução completa para prospecção, gerenciamento e operação de servidores.

## Tecnologias Utilizadas

- **Django**: Framework web principal que permite a construção de aplicações rapidamente, com suporte a autenticação, gerenciamento de banco de dados e muito mais.
- **Daphne**: Servidor WSGI/ASGI responsável por servir a aplicação Django, oferecendo alta performance e capacidade para lidar com múltiplas requisições simultâneas.
- **Celery**: Biblioteca que permite a execução de tarefas assíncronas em segundo plano, como envio de e-mails e processamento de dados.
- **Redis**: Sistema de gerenciamento de dados em memória utilizado como broker de mensagens para o Celery, melhorando o desempenho da aplicação.
- **Nginx**: Servidor web reverso que gerencia requisições HTTP e serve arquivos estáticos e de mídia.
- **Docker**: Utilizado para containerização da aplicação, garantindo consistência e facilidade de deployment em diferentes ambientes.
- **Docker Compose**: Ferramenta que orquestra múltiplos containers, facilitando a configuração e execução dos serviços.

## Estrutura do Projeto

### Serviços Definidos no Docker Compose

- **site**: Serviço principal que roda o Django com Daphne.
- **celery**: Worker do Celery que processa tarefas em segundo plano.
- **celery-beat**: Agendador de tarefas do Celery que executa tarefas em horários programados.
- **flower**: Interface de monitoramento para o Celery.
- **nginx**: Servidor web que atua como proxy reverso para o serviço Django.
- **redis**: Banco de dados em memória utilizado como broker de mensagens.

### Volumes Utilizados

- `logs`: Para armazenar logs da aplicação.
- `static`: Para armazenar arquivos estáticos da aplicação.
- `media`: Para armazenar arquivos de mídia enviados pelos usuários.

### Rede

- **lineage_network**: Rede criada para interconectar todos os serviços.

#

<p align="center">
<img height="280" src="https://i.imgur.com/SJV9SQw.png">
</p>

[![Supported Python versions](https://img.shields.io/pypi/pyversions/Django.svg)](https://www.djangoproject.com/)


## Como Instalar

```bash
Instalar a Plataforma L2JPremium:

sudo mkdir -p /var/pdl
cd /var/pdl

nano setup.sh
>> copie o conteudo desse arquivo para dentro <<
https://github.com/jacksonfelipe/lineage/blob/main/setup/setup.sh
>> e salve o arquivo. <<

chmod +x setup.sh
./setup.sh

>> O processo de instalação vai seguir e finalizar. <<
>> Obs: fique atento ao processo do SETUP, pois ele vai precisar de você <<

LOGO APÓS EDITE O ARQUIVO ABAIXO DENTRO DA PASTA [ cd lineage ]:
 - nano .env
EDITE TUDO O QUE PRECISA E SALVE.

DEPOIS DISSO EXECUTE O ARQUIVO DE BUILD:

./build.sh

PARABENS! FINALIZAMOS!

AGORA É SO FICAR EXECUTANDO O COMANDO:
./build.sh

TODA VEZ QUE APARECER UMA VERSÃO NOVA!
```


## Como migrar o banco de dados

```bash
$ >> entre na pasta [ cd /var/pdl/lineage ] e execute o comando abaixo <<
$ ./build.sh
```


## Como fazer backup do banco de dados

```bash
$ >> entre na pasta [ cd /var/pdl/lineage ] e execute o comando abaixo <<
$ >> copie o conteudo desse arquivo para dentro <<
$ https://github.com/jacksonfelipe/lineage/blob/main/setup/backup.sh
$ >> e salve o arquivo. <<
$ chmod +x backup.sh
$ crontab -e
$ 0 3 * * * /var/pdl/lineage/backup.sh >> /var/pdl/backup.log 2>&1
```


## Como testar (produção)

```bash
https://l2jprmeium.com/
```

## Sobre Mim
>Desenvolvedor - Daniel Amaral Recife/PE
- Emails:  contato@l2jpremium.com
- Discord: jacksonfelipe


## Grupo de Staffs:

**Núcleo de Programação**

- Daniel Amaral (Desenvolvedor - FullStack/FullCycle)

**Apoio e Testers**

- Daniel Amaral (Desenvolvedor - FullStack/FullCycle)

**Gestão**

- Daniel Amaral (Desenvolvedor - FullStack/FullCycle)

## Estrutura do Código

O projeto é codificado utilizando uma estrutura simples e intuitiva, apresentada abaixo:

```bash
< RAIZ DO PROJETO >
   |
   |-- apps/
   |    |
   |    |-- main/
   |    |    |-- administrator/              # Administração
   |    |    |-- auditor/                    # Auditoria do sistema
   |    |    |-- faq/                        # FAQ (Perguntas Frequentes)
   |    |    |-- home/                       # App principal - Página inicial
   |    |    |-- message/                    # Mensagens e Amigos
   |    |    |-- news/                       # Notícias e Blog
   |    |    |-- notification/               # Notificações do sistema
   |    |    |-- solicitation/               # Solicitações e Suporte
   |    |
   |    |-- lineage/
   |    |    |-- accountancy/                # Módulo de contabilidade e registros financeiros do servidor Lineage 2
   |    |    |-- auction/                    # Sistema de leilões de itens entre jogadores no servidor Lineage 2
   |    |    |-- games/                      # Funcionalidades relacionadas a minigames, roletas e caixas de prêmios
   |    |    |-- inventory/                  # Gerenciamento de inventário dos personagens e movimentações de itens
   |    |    |-- payment/                    # Integração com sistemas de pagamento (ex: PayPal) para compras no servidor
   |    |    |-- reports/                    # Geração de relatórios administrativos e estatísticas do servidor
   |    |    |-- server/                     # Ferramentas de administração e monitoramento do status do servidor Lineage 2
   |    |    |-- shop/                       # Loja virtual de itens e serviços do servidor Lineage 2
   |    |    |-- wallet/                     # Sistema de carteira virtual para saldo e transações dos jogadores
   |
   |-- core/
   |    |-- settings.py                      # Configurações do projeto
   |    |-- urls.py                          # Roteamento do projeto
   |    |-- *.py                             # Demais Arquivos
   |
   |-- requirements.txt                      # Dependências do projeto
   |-- manage.py                             # Script de inicialização do Django
   |-- ...                                   # Demais Arquivos
   |
   |-- ************************************************************************
```

<br />

## Como Customizar 

Quando um arquivo de template é carregado no controlador, o `Django` escaneia todos os diretórios de templates, começando pelos definidos pelo usuário, e retorna o primeiro encontrado ou um erro caso o template não seja encontrado. O tema utilizado para estilizar esse projeto inicial fornece os seguintes arquivos:

```bash
< RAIZ_DA_BIBLIOTECA_UI >                      
   |
   |-- templates/                     # Pasta Raiz dos Templates
   |    |          
   |    |-- accounts_custom/          # (pasta no app home)    
   |    |    |-- auth-signin.html     # Página de Login
   |    |    |-- auth-signup.html     # Página de Cadastro
   |    |    |-- *.html               # Demais Paginas
   |    |
   |    |-- includes/       
   |    |    |-- footer.html          # Componente de Rodapé
   |    |    |-- sidebar.html         # Componente da Barra Lateral
   |    |    |-- navigation.html      # Barra de Navegação
   |    |    |-- scripts.html         # Componente de Scripts
   |    |    |-- *.html               # Demais includes
   |    |
   |    |-- layouts/       
   |    |    |-- base.html            # Página Mestra
   |    |    |-- base-auth.html       # Página Mestra para Páginas de Autenticação
   |    |    |-- *.html               # Demais layouts
   |    |
   |    |-- pages/       
   |         |-- *.html               # Todas as outras páginas
   |    
   |-- ************************************************************************
```
