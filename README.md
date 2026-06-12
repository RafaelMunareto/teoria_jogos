# CRISP-DM - Simulacao Multiagente para Decisao Financeira Baseada em Teoria dos Jogos

## Estado Atual

O repositorio ainda nao possui implementacao. O projeto foi redirecionado para um problema de **decisao financeira**, com um recorte inicial recomendado:

**simular a alocacao de portfolio de investidores brasileiros entre renda fixa, fundos e renda variavel sob choques de juros, inflacao e comportamento de manada.**

## Aviso de Escopo

Este projeto deve ser tratado como pesquisa e modelagem computacional. Ele **nao** deve ser usado como recomendacao automatica de investimento.

## Resumo do Projeto

O objetivo e construir uma simulacao multiagente em que investidores com perfis distintos tomam decisoes recorrentes de alocacao de capital. Cada agente busca melhorar seu proprio retorno ajustado ao risco, mas o resultado agregado depende das decisoes dos demais, da liquidez e do ambiente macrofinanceiro.

Na primeira versao, o foco recomendado e:

- investidores pessoa fisica com perfis conservador, moderado e agressivo;
- ativos agregados, e nao papeis individuais demais;
- comparacao entre comportamento disciplinado, reativo e imitativo.

## Recorte Inicial Recomendado

### Tema

Decisao de alocacao de portfolio com agentes heterogeneos.

### Pergunta central

Como heterogeneidade de perfil, aprendizagem social e choques macroeconomicos alteram as decisoes de alocacao e o desempenho agregado de um mercado simplificado?

### Objetivo geral

Construir uma simulacao multiagente para comparar estrategias de alocacao financeira em cenarios de:

- juros altos e baixos;
- inflacao persistente ou controlada;
- informacao completa, ruidosa ou atrasada;
- baixa ou alta imitacao entre agentes.

### Objetivos especificos

- modelar agentes com preferencias de risco distintas;
- representar classes de ativos relevantes ao investidor brasileiro;
- incorporar variaveis macro como Selic, inflacao e cambio;
- medir herd behavior, rotatividade e concentracao de portfolio;
- comparar desempenho individual e estabilidade agregada.

## 1. Business Understanding (Entendimento do Problema Cientifico)

### Problema cientifico

Em mercados financeiros, a decisao de cada investidor nao depende apenas de fundamentos. Ela tambem responde a sinais de mercado, ao comportamento observado em outros agentes e a mudancas no ambiente macroeconomico. Isso cria um sistema interdependente, no qual decisoes individuais podem amplificar volatilidade, concentracao e perdas coletivas.

### Agentes do modelo

- Investidor conservador: prefere liquidez, baixa volatilidade e preservacao de capital.
- Investidor moderado: combina protecao e busca de retorno.
- Investidor agressivo: aceita maior risco e maior exposicao a renda variavel.
- Ambiente de mercado: reage ao fluxo agregado por meio de penalidades simplificadas de crowding, volatilidade ou custo de ajuste.

### Ativos agregados recomendados

- caixa / posicao neutra;
- Tesouro Selic;
- Tesouro IPCA+;
- fundos de renda fixa ou DI;
- renda variavel agregada, por exemplo indice ou ETF.

### Estrutura de jogo recomendada

- Jogo base: jogo repetido de alocacao de portfolio.
- Interacao: o payoff de cada agente depende do cenario macro e da escolha agregada dos demais.
- Benchmark individual: retorno ajustado ao risco.
- Benchmark coletivo: menor concentracao excessiva, menor drawdown agregado e maior robustez do sistema.

### Hipoteses de trabalho

| ID | Hipotese | Como testar |
| --- | --- | --- |
| H1 | Choques de alta de juros aumentam a migracao agregada para ativos de renda fixa e reduzem a participacao de renda variavel. | Comparar alocacoes medias antes e depois de choques na Selic. |
| H2 | Comportamento de manada aumenta concentracao de portfolio e piora drawdowns em momentos de estresse. | Simular diferentes niveis de imitacao e medir concentracao e perdas maximas. |
| H3 | Rebalanceamento muito frequente com sinais ruidosos reduz desempenho ajustado ao risco em relacao a estrategias mais lentas e disciplinadas. | Comparar Sharpe simplificado, turnover e retorno liquido por regime de decisao. |
| H4 | Maior heterogeneidade entre perfis de risco reduz sincronizacao extrema e melhora a estabilidade agregada do sistema. | Simular mercados homogeneos vs heterogeneos e medir volatilidade e dispersao das alocacoes. |

### Criterios de sucesso

- Produzir uma simulacao coerente com regimes macro observados nas bases.
- Medir alocacao media, turnover, concentracao e drawdown por cenario.
- Comparar desempenho de agentes e estabilidade do sistema.
- Identificar quando imitacao e reatividade degradam resultados agregados.

## 2. Data Understanding (Entendimento dos Dados)

### Bases selecionadas

As bases priorizadas para o recorte inicial estao listadas em [docs/bases.md](/Users/munareto/Documents/teoria_jogos/docs/bases.md:1).

| Base | Papel no projeto | Prioridade |
| --- | --- | --- |
| BCB / SGS | Series macrofinanceiras como juros e cambio | Alta |
| Tesouro Transparente | Taxas, vendas, resgates e perfil de investidores do Tesouro Direto | Alta |
| CVM Fundos | Patrimonio, cotistas, informes diarios e cadastro de fundos | Alta |
| B3 Historico | Cotas e precos historicos de ativos do mercado a vista | Media |

### Artigos e referencias base

As referencias iniciais foram organizadas em [docs/referencias.md](/Users/munareto/Documents/teoria_jogos/docs/referencias.md:1).

### Variaveis de interesse

- taxa Selic e variaveis macro de regime;
- precos, retornos e volatilidade por classe de ativo;
- perfil e movimentacao de investidores no Tesouro Direto;
- patrimonio liquido, cotistas e fluxos em fundos;
- pesos de alocacao por agente e classe de ativo;
- turnover, drawdown, concentracao e dispersao.

### Riscos e limitacoes iniciais

- A base da B3 e historica, mas nao vem ajustada por inflacao ou proventos.
- As bases da CVM e do Tesouro sao volumosas; a fase inicial deve trabalhar com agregacoes e amostras.
- O modelo nao observara a decisao real de cada investidor individual; ele inferira comportamentos por perfis sinteticos.

## 3. Data Preparation (Preparacao dos Dados)

### Pipeline recomendado

1. Baixar as series macro do BCB.
2. Baixar taxas, vendas e resgates do Tesouro Direto.
3. Baixar cadastro e informes diarios de fundos na CVM.
4. Construir classes agregadas de ativos para a simulacao.
5. Gerar agentes sinteticos com perfis de risco e regras de decisao.
6. Calibrar cenarios macro e regras de payoff.
7. Rodar simulacoes com diferentes niveis de imitacao, ruido e rebalanceamento.

### Saidas esperadas

- base macro consolidada;
- painel de ativos agregados;
- configuracao de agentes;
- cenarios de simulacao;
- metricas de risco, retorno e estabilidade.

## Estrutura Recomendada do Repositorio

```text
teoria_jogos/
├── README.md
├── docs/
│   ├── bases.md
│   └── referencias.md
├── data/
│   ├── raw/
│   ├── interim/
│   └── processed/
├── notebooks/
├── outputs/
└── src/
    ├── analysis/
    ├── data/
    ├── models/
    └── simulation/
```

## Proximas Etapas

1. Definir exatamente quais classes de ativos entrarao no baseline.
2. Baixar as primeiras bases oficiais e inspecionar esquema e granularidade.
3. Implementar agentes sinteticos e funcoes de utilidade simplificadas.
4. Rodar um baseline sem manada e outro com imitacao.
5. Medir impacto de choques de juros sobre a alocacao agregada.
