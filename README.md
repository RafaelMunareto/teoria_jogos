# CRISP-DM - Simulacao Multiagente para Decisao Financeira Baseada em Teoria dos Jogos

## Estado Atual

O projeto possui um baseline inicial implementado em Python, sem dependencias externas. O recorte atual e um problema de **decisao financeira**:

**simular a alocacao de portfolio de investidores brasileiros entre renda fixa, fundos e renda variavel sob choques de juros, inflacao e comportamento de manada.**

### Status do Projeto

O projeto **ainda nao esta concluido**. A fase atual e de baseline/prototipo: ja existe uma pipeline executavel com comparacao de cenarios, mas ainda faltam calibracao empirica, integracao de mais bases oficiais, graficos finais e avaliacao conclusiva das hipoteses.

### Implementacao atual - 2026-06-12

Foi incluida a primeira versao executavel do projeto:

- pacote Python em `src/teoria_jogos`;
- CLI com comandos para baixar dados do BCB e rodar simulacao;
- comando `compare-scenarios` para comparar niveis de comportamento imitativo;
- comando `compare-shocks` para comparar cenarios macro de estresse;
- ingestao das series SGS/BCB de Selic, IPCA e dolar;
- tentativa opcional de ingestao do IBOVESPA pela serie SGS 7;
- consolidacao mensal em `data/processed/macro_bcb.csv`;
- simulacao multiagente baseline com investidores conservadores, moderados e agressivos;
- metricas de retorno medio, turnover, concentracao HHI, drawdown e pesos finais;
- testes unitarios em `tests/`.

### Melhoria implementada - 2026-06-12

A funcao de escolha de portfolio foi refinada para reduzir concentracao artificial em um unico ativo. A regra atual combina:

- retorno esperado do ativo no periodo;
- penalidade de risco por perfil de investidor;
- ancora de perfil, preservando preferencias conservadoras, moderadas e agressivas;
- componente de imitacao do mercado;
- penalidade de crowding quando um ativo fica acima do peso-base do perfil.

Tambem foi incluido um comparador automatico de cenarios para testar diferentes niveis de imitacao.

### Melhoria implementada - 2026-06-12, rodada 2

Foram adicionadas duas melhorias:

- a renda variavel agora usa `equity_return` real quando a coluna existe no painel macro;
- foram incluidos cenarios de choque: `rate_hike`, `inflation_spike`, `equity_stress` e `combined_stress`.

A serie SGS 7 do BCB retornou dados historicos de IBOVESPA ate 30/09/2019 na consulta local. Para 2024, a API nao retornou observacoes, entao o pipeline marcou `equity_return_source=synthetic_fallback` e manteve a renda variavel sintetica no baseline atual.

Os arquivos em `data/` e `outputs/` sao gerados localmente e nao sao versionados, conforme `.gitignore`.

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

### Ativos do baseline implementado

- `cash`;
- `tesouro_selic`;
- `tesouro_ipca`;
- `fundos_rf`;
- `renda_variavel`.

A renda variavel pode vir de duas fontes:

- `ibovespa_sgs_7`, quando a serie historica do SGS/BCB esta disponivel para o periodo;
- `synthetic_fallback`, quando nao ha dado real no periodo solicitado.

No baseline de 2024, a renda variavel ainda usa `synthetic_fallback`. A integracao com B3 ou outra proxy aberta atualizada continua como etapa futura.

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

As bases priorizadas para o recorte inicial estao listadas em [docs/bases.md](docs/bases.md).

| Base | Papel no projeto | Prioridade |
| --- | --- | --- |
| BCB / SGS | Series macrofinanceiras como juros e cambio | Alta |
| Tesouro Transparente | Taxas, vendas, resgates e perfil de investidores do Tesouro Direto | Alta |
| CVM Fundos | Patrimonio, cotistas, informes diarios e cadastro de fundos | Alta |
| B3 Historico | Cotas e precos historicos de ativos do mercado a vista | Media |

### Artigos e referencias base

As referencias iniciais foram organizadas em [docs/referencias.md](docs/referencias.md).

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

## Como Rodar

### Validar testes

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

### Baixar dados macro do BCB

```bash
PYTHONPATH=src python3 -m teoria_jogos.cli fetch-bcb --start 01/01/2024 --end 31/12/2024
```

Saidas geradas:

- `data/raw/bcb/bcb_sgs_selic.csv`;
- `data/raw/bcb/bcb_sgs_ipca.csv`;
- `data/raw/bcb/bcb_sgs_usd_brl.csv`;
- `data/raw/bcb/bcb_sgs_ibovespa.csv`, quando disponivel;
- `data/processed/macro_bcb.csv`.

### Rodar simulacao com o CSV macro existente

```bash
PYTHONPATH=src python3 -m teoria_jogos.cli simulate --agents 90 --imitation 1.0 --seed 42
```

Saidas geradas:

- `outputs/baseline_history.csv`;
- `outputs/baseline_summary.json`.

### Comparar cenarios de imitacao

```bash
PYTHONPATH=src python3 -m teoria_jogos.cli compare-scenarios --agents 90 --imitation-levels 0.0,1.0,2.0 --seed 42
```

Saida gerada:

- `outputs/scenario_comparison.csv`.

### Comparar cenarios de choque

```bash
PYTHONPATH=src python3 -m teoria_jogos.cli compare-shocks --agents 90 --imitation 1.0 --seed 42
```

Saida gerada:

- `outputs/shock_comparison.csv`.

### Rodar pipeline completo

```bash
PYTHONPATH=src python3 -m teoria_jogos.cli run-baseline --start 01/01/2024 --end 31/12/2024 --agents 90 --imitation 1.0 --seed 42
```

## Resultado do Baseline Executado

Execucao local realizada com dados BCB de 2024, `90` agentes, `imitation=1.0` e `seed=42`.

| Metrica | Valor |
| --- | --- |
| Periodos | 12 |
| Retorno acumulado medio | 9.25% |
| Retorno medio mensal | 0.74% |
| Volatilidade mensal do retorno medio | 0.45% |
| Max drawdown | -0.18% |
| Concentracao HHI final | 0.2023 |
| Peso final em caixa | 17.43% |
| Peso final em Tesouro Selic | 20.68% |
| Peso final em Tesouro IPCA+ | 19.22% |
| Peso final em fundos RF | 18.86% |
| Peso final em renda variavel | 23.80% |

Leitura tecnica: a nova regra reduziu a concentracao excessiva em `tesouro_selic` e passou a produzir uma carteira agregada mais diversificada. O baseline ainda depende de renda variavel sintetica, portanto a proxima validacao precisa integrar uma serie real ou proxy aberta.

## Comparacao de Cenarios

Execucao local com dados BCB de 2024, `90` agentes e `seed=42`.

| Cenario | Retorno acumulado medio | HHI final | Peso final em renda variavel |
| --- | --- | --- | --- |
| `imitation=0.0` | 9.27% | 0.2029 | 24.23% |
| `imitation=1.0` | 9.25% | 0.2023 | 23.80% |
| `imitation=2.0` | 9.23% | 0.2018 | 23.37% |

Leitura tecnica: nesta formulacao, aumentar imitacao reduziu levemente retorno e renda variavel, mas ainda nao produziu comportamento de manada forte. Isso indica que o componente de imitacao precisa ficar mais sensivel em cenarios de estresse ou com informacao ruidosa para testar melhor a hipotese H2.

## Comparacao de Choques

Execucao local com dados BCB de 2024, `90` agentes, `imitation=1.0` e `seed=42`.

| Cenario | Retorno acumulado medio | Max drawdown | Peso final em Selic | Peso final em renda variavel |
| --- | --- | --- | --- | --- |
| `none` | 9.25% | -0.18% | 20.68% | 23.80% |
| `rate_hike` | 7.55% | -0.18% | 24.68% | 12.57% |
| `inflation_spike` | 7.37% | -0.18% | 23.07% | 13.90% |
| `equity_stress` | 3.95% | -0.66% | 27.61% | 5.95% |
| `combined_stress` | 5.38% | -0.59% | 29.20% | 3.94% |

Leitura tecnica: os cenarios de estresse ja produzem deslocamento defensivo, com aumento de caixa/Selic e queda expressiva em renda variavel. Isso melhora a capacidade do projeto de testar H1 e H2, embora a validacao final ainda dependa de dados reais mais atuais de renda variavel.

## Estrutura Recomendada do Repositorio

```text
teoria_jogos/
|-- README.md
|-- pyproject.toml
|-- docs/
|   |-- bases.md
|   `-- referencias.md
|-- data/
|   |-- raw/
|   |-- interim/
|   `-- processed/
|-- notebooks/
|-- outputs/
|-- src/
|   `-- teoria_jogos/
|       |-- analysis/
|       |-- data/
|       |-- models/
|       `-- simulation/
`-- tests/
```

## Proximas Etapas

1. Integrar serie real atualizada de renda variavel pela B3 ou por proxy aberta adequada.
2. Incluir ingestao inicial de Tesouro Transparente e CVM Fundos.
3. Adicionar graficos e tabelas finais para analise das hipoteses.
4. Calibrar parametros de risco, crowding e imitacao com dados observados.
5. Escrever a avaliacao final das hipoteses H1-H4.
