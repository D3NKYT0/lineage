# Sistema de Temas e Templates

> **Última atualização:** 21/02/2026

## Visão Geral
O sistema de temas do PDL é uma Engine robusta que permite customizar a aparência completa da plataforma pública através do envio de pacotes ZIP contendo templates HTML, estilos CSS, scripts JS e assets. O sistema foi desenhado para ser dinâmico, suportar internacionalização nativa e operar de forma isolada do código-fonte, garantindo segurança e facilidade em atualizações.

---

## Como Funciona (Alto Nível)
1. **Upload e Validação:** O administrador envia um arquivo ZIP pelo painel. O sistema valida estruturalmente o conteúdo e garante proteções de segurança (file types autorizados, limites de tamanho e proteção contra path traversal).
2. **Extração e Registro:** Os arquivos são alocados no diretório estático correto e as configurações (definidas em um arquivo interno `theme.json`) são mapeadas para o banco de dados. Variáveis customizadas do tema são instantaneamente geradas.
3. **Ativação e Fallbacks:** Apenas um tema pode estar ativo por vez no sistema. Ao ativar, todos os visitantes passam a receber os templates da nova interface gráfica. Caso algum arquivo ou rota não exista no tema atual, o PDL automaticamente engatilha um sistema de fallback inteligente para o template padrão (Core), impedindo qualquer quebra de visualização para o usuário (Erro 500).
4. **Desinstalação Limpa:** Quando excluído, os arquivos ZIP e as pastas em disco atreladas ao tema são completamente expurgadas para manter a plataforma íntegra.

---

## 📚 Índice da Documentação de Temas

Para evitar repetições, toda a inteligência e detalhes técnicos do Sistema de Temas foram ramificados em guias especializados baseados no que você deseja fazer:

### Começando
* 🎨 **[Tutorial: Como Criar um Tema](GUIDE_CREATE_THEME.md)**
  Aprenda o passo a passo de como montar a estrutura de arquivos e pastas, empacotar seu ZIP e ver os requisitos de segurança e limites de tamanho de upload.

### Programação e Customização
* 💻 **[Guia do Desenvolvedor de Temas](THEME_DEVELOPER_GUIDE.md)**
  Onde a magia acontece. Aprenda como funcionam e são processadas as Variáveis Multilíngues de Tema, Arquitetura de Herança de layouts, processamento de contexto global (Context Processors) e o detalhamento do renderizador `render_theme_page`.

* 🗂️ **[Mapeamento de Rotas de Templates](THEME_TEMPLATES_ROUTES.md)**
  Lista exata documentando quais templates HTML você precisa nomear e onde eles devem ser dispostos para sobrescrever cada página nativa do Core original (Tops, Wiki, Páginas Essenciais, Autenticação, etc).

* 💉 **[Mapeamento do Index Context](THEME_INDEX_CONTEXT.md)**
  Guia super avançado documentando exclusivamente a grande quantidade estrutural de Variáveis passadas para o principal template de qualquer tema (`index.html`), como a renderização em tempo real de contadores, players fakes, notícias e clãs top ranking.

### Tratamento e Proteção
* 🚨 **[Tratamento de Erros e Prevenção de Quebras](THEME_ERROR_HANDLING.md)**
  Descreve a implementação tecnológica de proteção em sandbox do visualizador, garantindo que o seu servidor nunca vai reportar *500 Internal Error* para visitantes, mesmo que os designers insiram templates absurdos, com URLs extintas ou sintaxes fatais do Django (NoReverseMatch / TemplateSyntaxError).

---

[ Voltar ao Índice Geral](../INDEX.md)
