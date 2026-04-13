# Análise de Produtos Faturados

Dashboard visual e dinâmico para análise de produtos faturados em tempo real.

## O que este painel entrega

- KPIs executivos: peças faturadas, volume, pedidos, ticket médio e preço médio ponderado.
- Narrativa executiva de 60 segundos para abrir apresentação com contexto e foco.
- Modo Apresentação com roteiro guiado em 4 etapas: Panorama, Riscos, Oportunidades e Plano.
- Alertas inteligentes com semáforo de risco (concentração, queda de receita e dispersão de preço).
- Metas configuráveis no painel lateral (meta mensal e limites de concentração).
- Aba de previsão para os próximos 4 meses com faixa provável e cenários conservador/base/otimista.
- Evolução mensal com comparação de período anterior.
- Pareto de clientes e curva ABC de produtos.
- Análise comercial por clientes.
- Análise geográfica por estado e cidade.
- Tabela detalhada com download do recorte filtrado.

## Como rodar localmente

1. Criar/ativar ambiente virtual.
2. Instalar dependências:

```bash
pip install -r requirements.txt
```

3. Executar o app:

```bash
streamlit run app.py
```

## Fonte dos dados

A leitura é feita via export CSV do Google Sheets compartilhado. O app converte automaticamente links padrão do Sheets para o endpoint de exportação.

## Observação de qualidade de dados

As colunas `Nota` e `CFOP` estão com alta ausência na base atual e, por isso, não entram nas análises centrais.
