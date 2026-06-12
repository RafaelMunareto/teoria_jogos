# CRISP-DM - Simulacao Multiagente para Decisao Financeira Baseada em Teoria dos Jogos

## Estado Atual

O projeto possui um baseline inicial implementado em Python, sem dependencias externas. O recorte atual e um problema de **decisao financeira**:

**simular a alocacao de portfolio de investidores brasileiros entre renda fixa, fundos e renda variavel sob choques de juros, inflacao e comportamento de manada.**

### Status do Projeto

O projeto **ainda nao esta concluido como estudo final**, mas ja possui uma versao inicial completa de pipeline: coleta dados, enriquece renda variavel com B3, roda simulacoes, compara cenarios, gera graficos, calibra parametros iniciais e escreve uma avaliacao automatica das hipoteses.

### Implementacao atual - 2026-06-12

Foi incluida a primeira versao executavel do projeto:

- pacote Python em `src/teoria_jogos`;
- CLI com comandos para baixar dados do BCB e rodar simulacao;
- comando `compare-scenarios` para comparar niveis de comportamento imitativo;
- comando `compare-shocks` para comparar cenarios macro de estresse;
- comando `compare-rebalance` para testar frequencia de rebalanceamento e ruido de sinal;
- comando `compare-profiles` para testar agentes heterogeneos vs homogeneos;
- comando `calibrate-parameters` para calibracao inicial com dados observados;
- comando `generate-report` para gerar tabelas, graficos SVG e avaliacao das hipoteses;
- ingestao das series SGS/BCB de Selic, IPCA e dolar;
- tentativa opcional de ingestao do IBOVESPA pela serie SGS 7;
- ingestao B3/COTAHIST com `BOVA11` como proxy real de renda variavel;
- ingestao inicial do Tesouro Transparente;
- ingestao inicial do informe diario de fundos da CVM;
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

A serie SGS 7 do BCB retornou dados historicos de IBOVESPA ate 30/09/2019 na consulta local. Para 2024, a API nao retornou observacoes; essa lacuna foi posteriormente coberta pelo COTAHIST da B3 com `BOVA11`.

### Melhoria implementada - 2026-06-12, rodada 3

Foram adicionadas as etapas que estavam em aberto:

- renda variavel real via B3/COTAHIST usando `BOVA11` como proxy operacional;
- resumo de taxas do Tesouro Direto via Tesouro Transparente;
- resumo de patrimonio, fluxos e cotistas de fundos via CVM;
- graficos SVG em `outputs/report/`;
- tabela final consolidada em `outputs/report/final_metrics.csv`;
- calibracao inicial em `data/processed/calibration_params.json`;
- avaliacao automatica das hipoteses em `docs/avaliacao_hipoteses.md`;
- experimentos H3 e H4 com rebalanceamento/ruido e perfis homogeneos/heterogeneos.

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
- `b3_cotahist_bova11`, quando o COTAHIST da B3 foi processado;
- `synthetic_fallback`, quando nao ha dado real no periodo solicitado.

No baseline atual de 2024, a renda variavel usa `b3_cotahist_bova11`.

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

### Integrar renda variavel real via B3/COTAHIST

```bash
PYTHONPATH=src python3 -m teoria_jogos.cli fetch-b3-equity --year 2024 --symbol BOVA11
```

Saidas geradas:

- `data/raw/b3/COTAHIST_A2024.ZIP`;
- `data/processed/equity_b3_daily.csv`;
- `data/processed/equity_b3_monthly.csv`;
- `data/processed/macro_bcb.csv`, enriquecido com `equity_return`.

### Ingerir Tesouro Transparente

```bash
PYTHONPATH=src python3 -m teoria_jogos.cli fetch-tesouro
```

Saidas geradas:

- `data/raw/tesouro/precotaxatesourodireto.csv`;
- `data/processed/tesouro_rates_summary.csv`.

### Ingerir CVM Fundos

```bash
PYTHONPATH=src python3 -m teoria_jogos.cli fetch-cvm-funds --year-month 202606
```

Saidas geradas:

- `data/raw/cvm/inf_diario_fi_202606.zip`;
- `data/processed/cvm_funds_summary.csv`.

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

### Comparar rebalanceamento e ruido

```bash
PYTHONPATH=src python3 -m teoria_jogos.cli compare-rebalance --agents 90 --imitation 1.0 --seed 42
```

Saida gerada:

- `outputs/rebalance_comparison.csv`.

### Comparar perfis de agentes

```bash
PYTHONPATH=src python3 -m teoria_jogos.cli compare-profiles --agents 90 --imitation 1.0 --seed 42
```

Saida gerada:

- `outputs/profile_comparison.csv`.

### Calibrar parametros iniciais

```bash
PYTHONPATH=src python3 -m teoria_jogos.cli calibrate-parameters
```

Saida gerada:

- `data/processed/calibration_params.json`.

### Gerar relatorio e avaliacao das hipoteses

```bash
PYTHONPATH=src python3 -m teoria_jogos.cli generate-report
```

Saidas geradas:

- `outputs/report/final_metrics.csv`;
- `outputs/report/shock_returns.svg`;
- `outputs/report/shock_equity_weights.svg`;
- `docs/avaliacao_hipoteses.md`.

### Rodar pipeline completo

```bash
PYTHONPATH=src python3 -m teoria_jogos.cli run-baseline --start 01/01/2024 --end 31/12/2024 --agents 90 --imitation 1.0 --seed 42
```

## Resultado do Baseline Executado

Execucao local realizada com dados BCB de 2024, B3/COTAHIST `BOVA11`, `90` agentes, `imitation=1.0` e `seed=42`.

| Metrica | Valor |
| --- | --- |
| Periodos | 12 |
| Retorno acumulado medio | 6.19% |
| Retorno medio mensal | 0.50% |
| Volatilidade mensal do retorno medio | 0.56% |
| Max drawdown | -0.29% |
| Concentracao HHI final | 0.2085 |
| Peso final em caixa | 21.03% |
| Peso final em Tesouro Selic | 24.68% |
| Peso final em Tesouro IPCA+ | 21.24% |
| Peso final em fundos RF | 20.81% |
| Peso final em renda variavel | 12.24% |

Leitura tecnica: com `BOVA11` real de 2024, a renda variavel fica bem menor que no fallback sintetico, refletindo a sequencia negativa do ativo no fim de 2024.

## Comparacao de Cenarios

Execucao local com dados BCB de 2024, B3/COTAHIST `BOVA11`, `90` agentes e `seed=42`.

| Cenario | Retorno acumulado medio | HHI final | Peso final em renda variavel |
| --- | --- | --- | --- |
| `imitation=0.0` | 6.17% | 0.2082 | 12.51% |
| `imitation=1.0` | 6.19% | 0.2085 | 12.24% |
| `imitation=2.0` | 6.22% | 0.2089 | 11.98% |

Leitura tecnica: a imitacao aumenta levemente o HHI e reduz renda variavel. O efeito ainda e moderado, mas agora sustenta parcialmente a hipotese de concentracao por comportamento imitativo.

## Comparacao de Choques

Execucao local com dados BCB de 2024, B3/COTAHIST `BOVA11`, `90` agentes, `imitation=1.0` e `seed=42`.

| Cenario | Retorno acumulado medio | Max drawdown | Peso final em Selic | Peso final em renda variavel |
| --- | --- | --- | --- | --- |
| `none` | 6.19% | -0.29% | 24.68% | 12.24% |
| `rate_hike` | 6.38% | -0.30% | 26.51% | 9.46% |
| `inflation_spike` | 6.19% | -0.32% | 24.97% | 10.33% |
| `equity_stress` | 2.82% | -1.15% | 28.71% | 5.11% |
| `combined_stress` | 4.51% | -0.44% | 30.16% | 3.58% |

Leitura tecnica: os cenarios de estresse produzem deslocamento defensivo, com aumento de caixa/Selic e queda expressiva em renda variavel.

## Comparacao de Rebalanceamento

Execucao local com dados BCB de 2024, B3/COTAHIST `BOVA11`, `90` agentes e `seed=42`.

| Cenario | Retorno acumulado medio | Max drawdown | Peso final em renda variavel |
| --- | --- | --- | --- |
| `slow_clean` | 6.21% | -0.12% | 14.80% |
| `base_clean` | 6.19% | -0.29% | 12.24% |
| `fast_clean` | 6.34% | -0.47% | 10.20% |
| `fast_noisy` | 6.36% | -0.44% | 10.12% |
| `very_fast_noisy` | 6.55% | -0.54% | 8.79% |

Leitura tecnica: H3 nao foi sustentada nesta configuracao, porque rebalanceamento mais rapido com ruido nao reduziu retorno acumulado. O custo apareceu mais em drawdown e reducao de renda variavel.

## Comparacao de Perfis

Execucao local com dados BCB de 2024, B3/COTAHIST `BOVA11`, `90` agentes e `seed=42`.

| Cenario | Retorno acumulado medio | Max drawdown | Peso final em renda variavel |
| --- | --- | --- | --- |
| `heterogeneous` | 6.19% | -0.29% | 12.24% |
| `homogeneous_conservador` | 6.89% | -0.06% | 12.71% |
| `homogeneous_moderado` | 6.10% | -0.31% | 12.84% |
| `homogeneous_agressivo` | 5.55% | -0.51% | 11.25% |

Leitura tecnica: H4 foi parcialmente sustentada contra o perfil homogeneo agressivo, pois a populacao heterogenea teve drawdown menor.

## Calibracao Inicial

Arquivo gerado: `data/processed/calibration_params.json`.

| Parametro observado | Valor |
| --- | --- |
| Volatilidade mensal Selic | 0.06% |
| Volatilidade mensal IPCA | 0.21% |
| Volatilidade mensal renda variavel BOVA11 | 3.16% |
| Fluxo liquido CVM / patrimonio liquido | 0.37% |
| Risco sugerido para renda variavel | 0.1579 |
| Crowding penalty sugerido | 0.0500 |

## Avaliacao das Hipoteses

A avaliacao automatica foi salva em [docs/avaliacao_hipoteses.md](docs/avaliacao_hipoteses.md).

| Hipotese | Status inicial |
| --- | --- |
| H1 | Parcialmente sustentada |
| H2 | Parcialmente sustentada |
| H3 | Nao sustentada |
| H4 | Parcialmente sustentada |

## Estrutura Recomendada do Repositorio

```text
teoria_jogos/
|-- README.md
|-- pyproject.toml
|-- docs/
|   |-- bases.md
|   |-- referencias.md
|   `-- avaliacao_hipoteses.md
|-- data/
|   |-- raw/
|   |-- interim/
|   `-- processed/
|-- notebooks/
|-- outputs/
|   `-- report/
|-- src/
|   `-- teoria_jogos/
|       |-- analysis/
|       |-- data/
|       |-- models/
|       `-- simulation/
`-- tests/
```

## Proximas Etapas

1. Revisar a interpretacao economica dos resultados e transformar a avaliacao automatica em texto final.
2. Aplicar os parametros calibrados diretamente no simulador ou justificar por que eles ficarao apenas como referencia.
3. Expandir o periodo historico para mais de um ano, idealmente 2020-2025.
4. Refinar o experimento H3, porque o resultado atual nao sustentou a hipotese.
5. Preparar uma versao final do relatorio academico/projeto.
