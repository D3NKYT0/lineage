# Hub de Tops: Especificações de Interface e Interatividade

> **Última atualização:** 21/02/2026

O ambiente de "Tops/Rankings" do servidor utiliza um ecossistema de ponta-a-ponta moderno visando estética premium, transições cinematográficas e alta responsividade.

## 🎨 Paleta e Layout Visual (CSS)

Toda a arquitetura de apresentação usa tabelas semânticas injetadas com gradientes escuros refinados baseadas na custom style sheet principal: `static/default/css/tops.css`.

### Metodologia de Design
- **Rankings Principais**: Componentes da linha base ganham box-shadow nativo fornecendo profundidade.
- **Destaque Triplo (Top 3)**: A injeção da folha condicional avança estilizações de brilho sobre o pódio de 1º, 2º e 3º lugares. Identidade de cores baseadas nas premiações esportivas - Ouro, Prata e Bronze somadas ao destaque dinâmico de texto (fw-bold). Clãs também têm crests automaticamente posicionadas e responsivas dependendo do viewport do dispositivo.

## ⚙️ Dinamismo em Elementos Ocultos (Enhanced Effects)

O painel base não confia apenas em opacidades. Elementos injetam rotinas e frames de `tops-tables-enhanced.css`.
- Classes que acionam efeitos de luz nas bordas invisíveis da linha ativa.
- "Hover transforms" complexos atuam numa escala vetorial de X, Y. Levantam visualmente os dados sem empurrar as colunas vizinhas, garantindo transição imaculada de cores e ícones na mesma célula.

## ⚡ Automação Via JavaScript (`tops-tables.js`)

Ao longo do hub, ferramentas estáticas de Javascript englobam os componentes permitindo funcionalidades como mini-aplicações autônomas:

### Interações Avançadas Embutidas
- **Busca Global em Tempo Real**: Adição de campos reativos automáticos gerando Live Search. Tabelas ocultam linhas suavemente através de fade ao invés de remoções secas em "display: none".
- **Sistema de Sorting Nativo**: Componentes cabeçalhos criam triggers para ordenação manual de forma numérica e textual com suporte de direções e ícone setorial acionado por mouse.
- **Manipulação de Focus Select**: Isolamento e seleção interativa via mouse e tracking por acessibilidade em navegadores.

## 📱 Suporte a Responsividade (Breakpoints Padrão)

Tabelas nativamente são destrutíveis em aparelhos, toda configuração compensa perdas de eixo adaptando de modo dinâmico:
- `<768px`: Redução do peso semântico, eliminação de colunas visuais opcionais com `table-responsive`.
- `<576px`: Compactação máxima. Iconografia de clãs minimizadas sob efeitos essenciais, garantindo framerates lisos (60fps limit). Mapeamento de crest e avatares suprimidos dinamicamente de event handlers custosos na DOM mobile.

---

[ Voltar ao Índice](../INDEX.md)

