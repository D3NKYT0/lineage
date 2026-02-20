# Sistema de Temas e Templates

## Visão Geral
O sistema de temas permite customizar a aparência do site enviando pacotes ZIP contendo templates, estilos, scripts e assets. Cada tema pode ser ativado/desativado e possui variáveis configuráveis para internacionalização e personalização visual.

---

## Como Funciona
- **Modelo principal:** `Theme` (apps.main.administrator.models)
- **Upload:** O admin envia um arquivo ZIP contendo o tema
- **Validação:** O ZIP deve conter `theme.json` com metadados obrigatórios (`name`, `slug`, etc.)
- **Extração:** Arquivos são extraídos para `themes/installed/<slug>/`
- **Ativação:** Apenas um tema pode estar ativo por vez. Ao ativar um tema, os demais são desativados
- **Remoção:** Ao excluir um tema, o ZIP e a pasta extraída são removidos

---

## Estrutura Esperada do ZIP
- Arquivos permitidos: `.html`, `.css`, `.js`, imagens, fontes, etc.
- Arquivo obrigatório: `theme.json` com metadados e variáveis
- Exemplo de `theme.json`:
  ```json
  {
    "name": "Tema Exemplo",
    "slug": "tema-exemplo",
    "version": "1.0",
    "author": "Seu Nome",
    "description": "Descrição do tema.",
    "variables": [
      {
        "name": "Cor Primária",
        "tipo": "string",
        "valor_pt": "#123456",
        "valor_en": "#123456",
        "valor_es": "#123456"
      }
    ]
  }
  ```

---

## Variáveis de Tema
- Definidas em `theme.json` e salvas como `ThemeVariable`
- Suporte a internacionalização (`valor_pt`, `valor_en`, `valor_es`)
- Disponível no contexto dos templates via context processor
- Exemplo de uso no template:
  ```django
  <style>body { background: {{ tema_exemplo_cor_primaria }}; }</style>
  ```

---

## Contexto de Templates
O context processor `active_theme` injeta no contexto:
- `active_theme` — slug do tema ativo
- `base_template` — caminho para o base.html do tema
- `theme_slug`, `path_theme`, `theme_files`

O context processor `theme_variables` injeta todas as variáveis do tema.  
O context processor `background_setting` injeta a imagem de fundo ativa.

---

## Renderização de Páginas
- Função `render_theme_page` (em `utils/render_theme_page.py`):
  - Tenta renderizar o template do tema ativo
  - Se não existir, usa o template padrão
- Exemplo de uso:
  ```python
  return render_theme_page(request, 'public', 'index.html', context)
  ```

---

## Servindo Arquivos do Tema
- A view `serve_theme_file` serve arquivos HTML do tema ativo de forma segura
- Verifica existência do arquivo e retorna 404 se não encontrado

---

## Segurança
- Apenas extensões permitidas são extraídas
- Caminhos validados para evitar path traversal
- Tamanho máximo do ZIP: 30MB

---

## Dicas
- Inclua sempre um `base.html` no tema para herança de templates
- Use variáveis para facilitar customização sem editar arquivos
- Teste o tema em múltiplos idiomas

---

## Documentação Relacionada
- [Guia de Criação de Temas](GUIDE_CREATE_THEME.md)
- [Guia do Desenvolvedor de Temas](THEME_DEVELOPER_GUIDE.md)
- [Rotas de Templates de Tema](THEME_TEMPLATES_ROUTES.md)
