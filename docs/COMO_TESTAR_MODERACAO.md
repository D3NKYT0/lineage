# 🧪 Como Testar o Sistema de Moderação

## Problema Resolvido ✅

O erro que você encontrou foi devido ao script tentar importar Django diretamente. Criei **3 alternativas** para testar o sistema:

## 🚀 Opção 1: Command Django (RECOMENDADO)

Execute no terminal do seu projeto:

```bash
# Ativar o ambiente virtual
& D:/PROJETOS/SITE/.venv/Scripts/Activate.ps1

# Configurar os filtros padrão
python manage.py setup_moderation

# Testar o sistema básico
python manage.py test_moderation

# Teste com dados e performance
python manage.py test_moderation --create-test-data --performance
```

## 🎯 Opção 2: Script Simples (SEM DJANGO)

Execute o script independente:

```bash
# No diretório raiz do projeto
python test_moderation_simple.py
```

Este script simula os filtros sem precisar do Django.

## 🔧 Opção 3: Django Shell

Use o shell interativo do Django:

```bash
# Entrar no shell Django
python manage.py shell

# Dentro do shell, cole este código:
from apps.main.social.models import ContentFilter

# Verificar filtros ativos
active_filters = ContentFilter.objects.filter(is_active=True)
print(f"Filtros ativos: {active_filters.count()}")

# Testar um filtro
if active_filters.exists():
    test_filter = active_filters.first()
    result = test_filter.matches_content("teste de conteúdo")
    print(f"Resultado: {result}")
```

## 📋 O Que Cada Teste Faz

### `python manage.py setup_moderation`
- Cria **25+ filtros** pré-configurados
- Categorias: spam, palavrões, pornografia, URLs suspeitas, etc.
- Filtros específicos para o Brasil
- Mensagem de sucesso com estatísticas

### `python manage.py test_moderation`
- Testa detecção de conteúdo com exemplos reais
- Mostra quais filtros foram acionados
- Gera relatório do sistema
- Opcionalmente cria dados de teste

### `python test_moderation_simple.py`
- Demonstração sem Django
- Simula detecção de conteúdo
- Mostra estatísticas dos filtros
- Não precisa de configuração

## 🎯 Exemplos de Conteúdo Testado

| Conteúdo | Categoria | Ação |
|----------|-----------|------|
| "Ganhe dinheiro fácil!" | Spam Comercial | Flag |
| "Que merda de situação!" | Palavrão | Flag |
| "Vem ver minhas nudes" | Conteúdo Adulto | Auto Hide |
| "bit.ly/suspeito" | URL Suspeita | Flag |
| "PIX grátis!" | Golpe Brasileiro | Flag |
| "Boa tarde pessoal!" | Normal | ✅ Aprovado |

## 🛠️ Gerenciamento

Após configurar, acesse:

- **Filtros**: `http://localhost:8000/admin/social/contentfilter/`
- **Denúncias**: `http://localhost:8000/admin/social/report/`
- **Logs**: `http://localhost:8000/admin/social/moderationlog/`

## 📊 Resultado Esperado

Quando executar `python manage.py setup_moderation`, você verá:

```
🛡️  SISTEMA DE MODERAÇÃO CONFIGURADO COM SUCESSO!
============================================================
📊 Estatísticas:
   • Filtros criados: 25
   • Filtros atualizados: 0
   • Total de filtros ativos: 26

🎯 Categorias de filtros configuradas:
   • Spam e Marketing
   • Palavrões e Linguagem Inadequada
   • Conteúdo Pornográfico e Adulto
   • URLs e Sites Suspeitos
   • Discurso de Ódio e Discriminação
   • Fake News e Desinformação
   • Comportamentos Suspeitos
   • Filtros Específicos do Brasil
```

## ⚡ Solução Rápida

Se quiser testar AGORA mesmo sem configurar nada:

```bash
python test_moderation_simple.py
```

Este comando funciona imediatamente e mostra como o sistema detecta conteúdo problemático! 🎉
