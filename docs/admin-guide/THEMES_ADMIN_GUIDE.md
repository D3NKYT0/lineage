# Gerenciamento de Temas (Themes)

> **Última atualização:** 21/02/2026

O PDL oferece flexibilidade absurda através do app nativo de *Themes*. O sistema não depende de injetores complexos e os administradores podem transitar de designs minimalistas para layouts profundos baseados num simples clique.

## 🎨 O Que é um Tema no PDL?

Um tema é um conjunto estruturado injetado que contém a customização e re-sobrescrição do `CSS`, paletas de cores globais (variáveis CSS exclusivas) e re-rendereização de botões, barras e componentes de login, mantendo o back-end principal instato, livre de dependências ou *spaghetti codes*.

## 🌓 Dark Mode e Light Mode Inatos

Por design padrão, o sistema principal que hospeda o core do Painel (Default Design System) baseia seu roteiro visual no conceito do Neumorphism e interage passivamente com os Modos Claros/Escuros dos navegadores e celulares, adaptando automaticamente o painel para não explodir os olhos de jogadores a noite.

1. **Ativando Manualmente**: Vá no ícone superior esquerdo (Sol/Lua) e force o salvamento do cookie local do navegador.
2. Temas nativos respondem à *Preferência do Sistema*.

## 🖌️ Como Instalar e Alternar Temas Customizados

Para implementar o trabalho de um Front-End parceiro que montou pastas customizadas com layouts novos:
1. Certifique-se de que a estrutura e a pasta raiz com o nome exato do novo tema localizem-se dentro da diretoria raiz `apps/main/themes/`.
2. O sistema injeta dinamicamente o novo tema, sobrescrevendo as referências base do `base.html`.
3. É possível acompanhar as variações de pasta, pois arquivos nomeados corretamente (por ex: `button-glow.css` ou bibliotecas Bootstrap inteiras) serão aplicados a todas as rotas atreladas àquele Theme Code. Se um tema tentar acessar um template HTML que ele mesmo não re-escreveu, a aplicação busca automaticamente a versão "Coringada" (Fallback) do template original, impossibilitando erros *Página Não Encontrada (404)*.

*Aviso ao dono do Projeto*: Caso encomende novos designs, oriente o desenvolvedor à leitura completa do **THEME_DEVELOPER_GUIDE.md**. É absolutamente indestrutível e seguro rodar quantos temas quiser em paralelo na sua Staff (Testes Locais).

---

[ Voltar ao Índice](../INDEX.md)

