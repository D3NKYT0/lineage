# 🎨 Design System — PDL

> **Última atualização:** 21/02/2026

## Visão Geral
O Design System do Painel Definitivo Lineage (PDL) estabelece os padrões visuais consistentes em toda a plataforma, garantindo uma experiência de usuário (UX) coesa e moderna.

---

## 🎨 Paleta de Cores

```css
/* Cores Principais */
--primary-color: #1976d2;      /* Azul principal */
--secondary-color: #dc004e;    /* Rosa/Vermelho */
--accent-color: #ffc107;       /* Dourado */
--success-color: #4caf50;      /* Verde */
--warning-color: #ff9800;      /* Laranja */
--error-color: #f44336;        /* Vermelho */

/* Cores Neutras */
--background-light: #fafafa;
--background-dark: #121212;
--text-primary: #212121;
--text-secondary: #757575;
```

---

## 🔤 Tipografia

- **Fonte Principal**: Inter (Google Fonts)
- **Hierarquia Clara**: H1-H6 com espaçamentos otimizados
- **Legibilidade**: Contraste elevado e tamanhos acessíveis
- **Responsividade**: Escala tipográfica adaptativa para mobile e desktop

---

## 🧩 Componentes Base

- **Botões**: Estados hover, focus e disabled aprimorados e com feedback de interação
- **Cards**: Sombras sutis e bordas levemente arredondadas para destaque de blocos de conteúdo
- **Formulários**: Validação visual color-coded (verde/vermelho) e feedback descritivo imediato
- **Navegação**: Breadcrumbs claros e menus contextuais adaptativos

---

## 📱 Interface Responsiva & Grid System

Utilizamos um **Mobile-First Approach**:
```css
/* Breakpoints Otimizados */
--mobile: 320px;
--tablet: 768px;
--desktop: 1024px;
--large: 1440px;
```

### Grid System Flexível
- **12 colunas** em desktop
- **8 colunas** em tablet
- **4 colunas** em mobile
- **Gutters** (espaçamentos) responsivos nativos

### Componentes Adaptativos
- **Sidebar**: Oculta/colapsa em dispositivos mobile
- **Tabelas**: Uso de scroll horizontal `overflow-x: auto` em telas pequenas
- **Modais**: Expandem para full-screen em dispositivos móveis para facilitar a interação
- **Navegação**: Hamburger menu utilizado nativamente para economizar espaço de tela

---

## ✨ Animações e Transições

### Micro-interações Comuns
- **Hover Effects**: Transições suaves e naturais (0.2s)
- **Loading States**: Uso de Skeleton screens para minimizar sensação de espera
- **Page Transitions**: Effetos *Fade in/out* para trocas de páginas ou abas
- **Scroll Animations**: Elementos surgindo dinamicamente (*Reveal on scroll*)

### Performance Otimizada
O Design System preza pelo desempenho de processamento visual:
- **CSS Transforms**: Uso extensivo de aceleração de hardware
- **Will-change**: Aviso antecipado ao navegador para otimização de animações chave
- **Reduced Motion**: Respeito a painéis/interfaces configuradas para redução de movimento (Acessibilidade)

---

[ Voltar ao Índice](../INDEX.md)

