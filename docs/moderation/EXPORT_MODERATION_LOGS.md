# 📊 Sistema de Export de Logs de Moderação

> **Última atualização:** 21/02/2026

## Visão Geral

O sistema de export de logs permite gerar relatórios detalhados das ações de moderação em formatos Excel e CSV, com formatação profissional e estatísticas completas.

## ✨ Características

### 📈 **Excel Formatado (.xlsx)**
- **2 Abas**: Dados principais + Estatísticas
- **Formatação Profissional**: Cores, bordas, fontes padronizadas
- **Colunas Ajustadas**: Larguras otimizadas para leitura
- **Dados Limpos**: Navegador simplificado, datas brasileiras
- **Estatísticas Automáticas**: Contadores por tipo e moderador
- **Filtros Aplicados**: Mostra quais filtros foram usados

### 📄 **CSV Compatível (.csv)**
- **Encoding UTF-8**: Acentos corretos no Excel
- **Separadores Padrão**: Vírgulas para máxima compatibilidade
- **Dados Estruturados**: Fácil importação em outras ferramentas

## 🚀 Como Usar

### 1. **Acesso ao Sistema**
```
/social/moderation/logs/
```

### 2. **Aplicar Filtros (Opcional)**
- **Tipo de Ação**: Filtrar por tipo específico
- **Moderador**: Filtrar por moderador específico  
- **Data Inicial/Final**: Filtrar por período

### 3. **Exportar**
- Clique no botão **"Exportar"**
- Escolha **Excel** ou **CSV**
- Download automático com nome descritivo

## 📋 Estrutura dos Dados

### Colunas Exportadas
| Coluna | Descrição | Formato |
|--------|-----------|---------|
| **Data/Hora** | Timestamp da ação | dd/mm/yyyy HH:mm:ss |
| **Moderador** | Nome completo ou username | Texto |
| **Tipo de Ação** | Ação realizada (traduzida) | Texto |
| **Tipo do Alvo** | post/comment/user/report | Texto |
| **ID do Alvo** | Identificador único | Número |
| **Descrição** | Descrição da ação | Texto (limitado a 300 chars) |
| **Detalhes** | Informações adicionais | Texto (limitado a 300 chars) |
| **IP** | Endereço IP do moderador | xxx.xxx.xxx.xxx |
| **Navegador** | Chrome/Firefox/Safari/Edge/Outro | Texto |

### Nomes de Arquivo
```
logs_moderacao_YYYYMMDD_HHMMSS.xlsx
logs_moderacao_acao_content_hidden_20241215_143022.xlsx
logs_moderacao_desde_2024-12-01_20241215_143022.csv
```

## 📊 Aba de Estatísticas (Só Excel)

### Informações Incluídas
- **Cabeçalho do Relatório**
  - Data/hora de geração
  - Total de registros
  - Filtros aplicados

- **Ações por Tipo**
  - Contagem de cada tipo de ação
  - Ordenado por quantidade (decrescente)

- **Ações por Moderador**
  - Contagem por moderador
  - Inclui "Sistema Automático"
  - Ordenado por quantidade (decrescente)

## 🎨 Formatação Excel

### Cabeçalho
- **Fonte**: Calibri 11, negrito, branco
- **Fundo**: Azul (#2E75B6)
- **Alinhamento**: Centro
- **Bordas**: Finas, cinza

### Dados
- **Fonte**: Calibri 10
- **Alinhamento**: Esquerda, quebra de texto
- **Bordas**: Finas, cinza claro
- **Cores Alternadas**: Hover effect

### Larguras Otimizadas
- Data/Hora: 16 chars
- Moderador: 18 chars
- Tipo de Ação: 22 chars
- Descrição: 45 chars
- Detalhes: 35 chars

## ⚙️ Configuração Técnica

### Dependências
```bash
pip install openpyxl>=3.1.0
```

### URLs Disponíveis
```python
# Excel
/social/moderation/logs/export/excel/

# CSV  
/social/moderation/logs/export/csv/
```

### Parâmetros de Query
- `action_type`: Filtrar por tipo de ação
- `moderator`: ID do moderador
- `date_from`: Data inicial (YYYY-MM-DD)
- `date_to`: Data final (YYYY-MM-DD)

## 🔒 Segurança

### Permissões Necessárias
```python
'social.can_view_moderation_logs'
```

### Limitações
- **Máximo**: 10.000 registros por export (Excel)
- **Ilimitado**: CSV (mas pode ser lento para muitos dados)
- **Timeout**: 5 minutos máximo de processamento

### Dados Sensíveis
- **IPs**: Incluídos (necessários para auditoria)
- **User Agents**: Simplificados (só navegador principal)
- **Descrições**: Limitadas a 300 caracteres

## 📈 Performance

### Otimizações
- Query com `select_related('moderator')`
- Limite de 10k registros para Excel
- Processamento em lote
- Cache de formatação

### Tempos Esperados
- **100 registros**: < 1 segundo
- **1.000 registros**: 2-3 segundos
- **10.000 registros**: 10-15 segundos

## 🐛 Troubleshooting

### Erro: "openpyxl não instalado"
```bash
pip install openpyxl
```

### Excel não abre corretamente
- Verificar encoding UTF-8
- Verificar extensão .xlsx
- Testar com LibreOffice primeiro

### CSV com acentos errados
- O sistema já inclui BOM UTF-8
- Abrir no Excel: Dados > Obter Dados > Do Arquivo > CSV
- Escolher encoding UTF-8

### Export muito lento
- Aplicar filtros de data mais restritivos
- Usar CSV para grandes volumes
- Verificar se há índices no banco

## 💡 Dicas de Uso

### Para Relatórios Gerenciais
1. Filtrar por período (últimos 30 dias)
2. Exportar em Excel
3. Usar aba de estatísticas
4. Criar gráficos no Excel

### Para Auditoria Técnica
1. Filtrar por moderador específico
2. Exportar em CSV
3. Importar em ferramenta de análise
4. Cruzar com outros logs

### Para Análise de Tendências
1. Export mensal de todos os dados
2. Comparar estatísticas entre períodos
3. Identificar padrões de moderação
4. Ajustar filtros automáticos

## 🔗 Integrações

### Admin Django
- Ações no admin também exportam
- Filtros similares aplicados
- Mesma formatação

### API (Futuro)
```python
# Endpoint planejado
GET /api/v1/moderation/logs/export/
```

### Automação (Futuro)
- Export agendado semanal/mensal
- Envio por email
- Upload para storage externo

---

**Última atualização**: Dezembro 2024  
**Versão**: 1.0  
**Compatibilidade**: Excel 2016+, LibreOffice 6+

---

[ Voltar ao Índice](../INDEX.md)

