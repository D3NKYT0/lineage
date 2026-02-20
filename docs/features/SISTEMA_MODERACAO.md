# 🛡️ Sistema de Moderação e Filtros

## Visão Geral

O sistema de moderação é uma solução abrangente para manter a qualidade do conteúdo na rede social, com múltiplas camadas de proteção contra spam, conteúdo inadequado e comportamentos maliciosos.

## 📋 Características Principais

### 🚀 Configuração Rápida
```bash
# Configurar filtros padrão
python manage.py setup_moderation
```

### 🎯 Categorias de Filtros

#### 1. **Spam e Marketing**
- Palavras comerciais suspeitas
- Medicamentos e suplementos
- Jogos de azar e apostas
- Esquemas financeiros fraudulentos

#### 2. **Linguagem Inadequada (Português)**
- Palavrões comuns (nível moderado)
- Linguagem ofensiva (nível severo)
- Expressões com símbolos mascarados

#### 3. **Conteúdo Pornográfico**
- Palavras explícitas
- Termos sexuais
- Links para sites adultos conhecidos

#### 4. **URLs e Sites Suspeitos**
- Encurtadores de URL duvidosos
- Domínios de phishing conhecidos
- Sites fraudulentos de criptomoedas
- Múltiplas URLs em sequência

#### 5. **Discurso de Ódio**
- Linguagem racista
- Conteúdo homofóbico
- Discriminação religiosa

#### 6. **Fake News e Desinformação**
- Desinformação médica
- Teorias da conspiração

#### 7. **Comportamentos Suspeitos**
- Conteúdo repetitivo
- Excesso de maiúsculas
- Uso excessivo de emojis
- Compartilhamento de informações pessoais

#### 8. **Específicos do Brasil**
- Golpes brasileiros comuns
- Sites de apostas populares

## 🔧 Configuração

### Filtros Automáticos

Os filtros são aplicados automaticamente em:
- ✅ Posts
- ✅ Comentários  
- ✅ Nomes de usuário (seletivo)

### Ações Disponíveis

1. **Flag** - Marcar para revisão manual
2. **Auto Hide** - Ocultar automaticamente
3. **Auto Delete** - Deletar automaticamente
4. **Notify Moderator** - Notificar moderadores

### Tipos de Filtros

1. **Keyword** - Palavras-chave simples
2. **Regex** - Expressões regulares
3. **Spam Pattern** - Padrões automáticos de spam
4. **URL Pattern** - Padrões de URLs

## 🎛️ Painel de Moderação

### Dashboard Principal
- Estatísticas de denúncias
- Relatórios urgentes  
- Ações recentes
- Gráficos de atividade

### Gerenciamento de Denúncias
- **Status**: Pendente → Em Revisão → Resolvido/Descartado
- **Prioridades**: Baixa, Média, Alta, Urgente
- **Atribuição**: Automática a moderadores
- **Tipos**: Spam, Conteúdo Inapropriado, Assédio, etc.

### Ações de Moderação
- Advertências
- Ocultar/Deletar conteúdo
- Suspender usuários (temporário/permanente)
- Banir usuários
- Aprovar/destacar conteúdo

## 📊 Validação de Mídia

### Imagens
- **Tamanho máximo**: 10MB (posts), 5MB (avatares)
- **Formatos**: JPEG, PNG, WEBP, GIF
- **Resolução máxima**: 1920x1080px
- **Processamento automático**: Otimização, redimensionamento
- **Avatar**: Redimensionado para 400x400px

### Vídeos
- **Tamanho máximo**: 100MB
- **Duração máxima**: 5 minutos
- **Formatos**: MP4, MOV, AVI, WEBM
- **Processamento**: Compressão automática para web

### Recursos Avançados
- Remoção automática de metadados EXIF
- Otimização para web
- Thumbnails automáticos
- Validação de conteúdo

## 🔒 Middleware de Proteção

### ContentFilterMiddleware
Aplica filtros automaticamente durante a criação de conteúdo.

### SpamProtectionMiddleware
- Rate limiting por usuário
- Detecção de padrões suspeitos
- Proteção contra posts massivos

## 📝 Logs e Auditoria

### ModerationLog
- Registro imutável de todas as ações
- Rastreamento de IP e User Agent
- Histórico completo para auditoria
- Export para CSV

## 🛠️ Dependências

### Obrigatórias
```bash
pip install Pillow>=10.0.0
```

### Opcionais (Recomendadas)
```bash
# Para processamento avançado de vídeos
# Requer ffmpeg no sistema
sudo apt-get install ffmpeg  # Ubuntu/Debian

# Para detecção de conteúdo NSFW
pip install tensorflow nudenet

# Para detecção de faces
pip install face-recognition opencv-python
```

## 🚀 Uso

### 1. Configuração Inicial
```bash
python manage.py setup_moderation
```

### 2. Acessar Painel Admin
```
/admin/social/contentfilter/
```

### 3. Monitorar Denúncias
```
/admin/social/report/
```

### 4. Verificar Logs
```
/admin/social/moderationlog/
```

## ⚙️ Personalização

### Criar Filtro Customizado
```python
from apps.main.social.models import ContentFilter

ContentFilter.objects.create(
    name='Meu Filtro Personalizado',
    filter_type='keyword',
    pattern='palavra1 palavra2 palavra3',
    action='flag',
    description='Descrição do filtro',
    apply_to_posts=True,
    apply_to_comments=True,
    is_active=True
)
```

### Regex Avançado
```python
ContentFilter.objects.create(
    name='Detecção de CPF',
    filter_type='regex', 
    pattern=r'\d{3}[-.]?\d{3}[-.]?\d{3}[-.]?\d{2}',
    action='flag',
    description='Detecta possível compartilhamento de CPF'
)
```

## 🎯 Boas Práticas

### Para Administradores
1. **Monitore regularmente** os logs de moderação
2. **Ajuste filtros** baseado nos resultados
3. **Treine moderadores** nas ferramentas disponíveis
4. **Configure notificações** para denúncias urgentes

### Para Desenvolvedores
1. **Teste filtros** em ambiente de desenvolvimento
2. **Monitore performance** dos middlewares
3. **Mantenha backups** das configurações
4. **Documente mudanças** nos filtros

## 🔍 Troubleshooting

### Filtros não funcionando
1. Verificar se estão ativos: `is_active=True`
2. Confirmar aplicação correta: `apply_to_posts`, `apply_to_comments`
3. Testar regex em ferramenta online
4. Verificar logs de erro

### Performance lenta
1. Otimizar regexes complexas
2. Reduzir número de filtros ativos
3. Usar cache para filtros frequentes
4. Monitorar middleware overhead

### Falsos positivos
1. Ajustar sensibilidade dos filtros
2. Usar listas de exceções
3. Revisar padrões muito amplos
4. Feedback dos usuários

## 📞 Suporte

Para dúvidas ou problemas:
1. Verificar logs de erro
2. Consultar documentação técnica
3. Contatar equipe de desenvolvimento
4. Reportar bugs no repositório

---

**Última atualização**: Dezembro 2024  
**Versão**: 2.0  
**Compatibilidade**: Django 4.x+