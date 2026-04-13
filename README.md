# Dashboard Análise de Produtos Faturados

Dashboard visual e interativo para análise e monitoramento de produtos faturados em tempo real. Desenvolvido com Streamlit para visualização dinâmica e filtros avançados.

## 📊 Funcionalidades Principais

### KPIs Executivos

- **Peças Faturadas**: Receita total no período selecionado
- **Volume**: Quantidade total de unidades faturadas
- **Pedidos**: Total de pedidos únicos
- **Ticket Médio por Pedido**: Valor médio por transação
- **Preço Médio Ponderado**: Valor unitário médio
- **Clientes Ativos**: Número de clientes distintos com produtos ativos

### Narrativa Executiva

- Resumo de 60 segundos com contexto do período
- Indicadores de tendência (crescimento/queda)
- Alertas de risco e oportunidades identificadas
- Compartilhamento de decisões recomendadas

### Modo Apresentação

Fluxo guiado em 4 etapas para reuniões executivas:

1. **Panorama**: Visão geral de receita, volume e tendências
2. **Riscos**: Concentração de clientes, queda de receita
3. **Oportunidades**: Produtos em crescimento, novos mercados
4. **Plano de Ação**: Recomendações estratégicas baseadas em dados

### Alertas Inteligentes

- 🟢 **Verde**: Métrica dentro da normalidade
- 🟡 **Amarelo**: Atenção necessária (aviso moderado)
- 🔴 **Vermelho**: Risco crítico (ação imediata)

Monitora:

- Concentração de receita por cliente (limite configurável)
- Queda de receita vs. período anterior
- Dispersão de preço per mil itens

### Metas e Comparações

- **Meta Mensal Configurável**: Defina via painel lateral
- **Comparação com**: 3 opções de baseline
  - Período anterior
  - Mesmo período do ano passado
  - Média móvel 3 meses
- **Atingimento de Meta**: Métrica visual com percentual

### Previsão Inteligente

- Projeção para os próximos 4 meses
- Detecção de sazonalidade automática
- Faixa provável (intervalo de confiança 80%)
- Cenários: Conservador (-10%), Base e Otimista (+10%)

### Análises Detalhadas

#### Clientes

- Pareto de clientes por receita (Top 8)
- Concentração dos 3 maiores
- Análise de risco de concentração

#### Produtos

- Curva ABC de produtos por impacto
- Top produtos em crescimento
- Produtos para escalar receita

#### Geografia

- Receita por estado
- Análise por cidade
- Distribuição geográfica

#### Detalhamento

- Tabela completa com filtros
- Download em CSV do recorte filtrado
- Análise linha por linha

## 🎯 Filtros Disponíveis

### Filtro de Data

- **Modo 1**: Período (data início e fim)
- **Modo 2**: Um dia específico
- Range dinâmico baseado em dados reais
- Validação automática de ordem (data inicial ≤ data final)

### Filtros Dimensionais

- Cliente (multiselect)
- Estado (multiselect)
- Cidade (multiselect)
- Produto (multiselect)
- Frete (multiselect)

### Comparação

Radio selector para escolher baseline de comparação

## 🚀 Como Rodar Localmente

### Pré-requisitos

- Python 3.8+
- pip (gerenciador de pacotes)

### Instalação

1. Clone o repositório:

```bash
git clone <URL-do-repositorio>
cd Dashboard\ Produtos\ Faturados\ for\ Lucas\ Chamas
```

2. Crie e ative um ambiente virtual:

```bash
# Windows
python -m venv .venv
.venv\Scripts\Activate.ps1

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Execute o app:

```bash
streamlit run app.py
```

5. Acesse no navegador:

```
http://localhost:8501
```

## 📊 Fonte dos Dados

A leitura é feita via **export CSV do Google Sheets compartilhado**. O app converte automaticamente links padrão do Sheets para o endpoint de exportação.

**Configuração esperada**: URL do Google Sheets no topo do `app.py` ou via variáveis de ambiente.

## 🛠️ Tecnologias Utilizadas

- **Streamlit**: Framework web para dados
- **Pandas**: Manipulação e análise de dados
- **NumPy**: Computação numérica
- **Plotly**: Visualizações interativas
- **SciPy**: Estatísticas avançadas

## ⚙️ Configurações

### Varáveis de Ambiente (opcional)

```python
SHEET_URL="<URL-do-seu-google-sheets>"
```

### Ajustes no Código

Edite diretamente em `app.py`:

- `COLORS`: Paleta de cores
- Step do input de meta (padrão: 10.000)
- Limite de concentração (padrão: 45%)
- Períodos de previsão (padrão: 4 meses)

## 📝 Observações de Qualidade de Dados

As colunas `Nota` e `CFOP` estão com **alta ausência** na base atual:

- **Nota**: ~99,6% de ausência
- **CFOP**: ~97,3% de ausência

Por isso, **não entram nas análises centrais** do dashboard.

## 🐛 Tratamento de Erros

- **Valores Inválidos**: Convertidos como `"R$ 0,00"` nas exibições
- **Divisão por Zero**: Protegida em cálculos de desvio padrão e médias
- **Dados Ausentes**: Ignorados automaticamente em agregações
- **Retry Automático**: Tenta reconectar 3x se falhar ao carregar dados (com backoff exponencial)

## 📊 Formato de Dados

### Entrada (CSV)

| Campo       | Formato                 | Obrigatório |
| ----------- | ----------------------- | ----------- |
| Data        | DD/MM/YYYY ou similar   | ✅ Sim      |
| Cliente     | Texto livre             | ✅ Sim      |
| Produto     | Texto livre             | ✅ Sim      |
| Quantidade  | Número inteiro          | ✅ Sim      |
| Valor Total | Número decimal (. ou ,) | ✅ Sim      |
| Estado      | UF (ex: SP)             | ✅ Sim      |
| Cidade      | Texto livre             | ✅ Sim      |

### Saída (Exibição)

```
Datas: DD/MM/YY (ex: 13/04/26)
Monetário: R$ 1.234.567,89
Inteiros: 1.234.567
Percentual: 45,5%
```

## 📈 Roadmap (Funcionalidades Futuras)

- [ ] Curva ABC dinâmica com score customizável
- [ ] Export de insights em PDF
- [ ] Integração com BI (Power BI, Tableau)
- [ ] Alertas por email
- [ ] Histórico de decisões
- [ ] Análise de cohort

## 📖 Help & Documentação

O dashboard inclui uma seção **"ℹ️ Como usar este dashboard"** na sidebar com explicações detalhadas de cada funcionalidade.

## 📞 Suporte

Para dúvidas, bugs ou sugestões, abra uma **Issue** no repositório.

## 📄 Licença

Este projeto é de uso interno. Todos os direitos reservados.
