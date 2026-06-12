# CRISP-DM - Simulacao Multiagente para Decisao Financeira Baseada em Teoria dos Jogos

## Estado Atual

O projeto possui um baseline inicial implementado em Python, sem dependencias externas. O recorte atual e um problema de **decisao financeira**:

**simular a alocacao de portfolio de investidores brasileiros entre renda fixa, fundos e renda variavel sob choques de juros, inflacao e comportamento de manada.**

### Status do Projeto

O projeto esta **concluido como versao academica inicial e reprodutivel**. Ele coleta dados, enriquece renda variavel com B3, calibra parametros, aplica a calibracao no simulador, roda simulacoes, compara cenarios, gera graficos e escreve a avaliacao final das hipoteses em texto academico.

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

### Melhoria implementada - 2026-06-12, rodada 4

Foram concluidas as etapas finais solicitadas:

- periodo historico expandido para 2020-2025, totalizando 72 meses;
- ingestao B3/COTAHIST ampliada para intervalo anual com `--start-year` e `--end-year`;
- parametros calibrados aplicados diretamente no simulador quando `data/processed/calibration_params.json` existe;
- opcao `--no-calibration` para rodar o modelo com parametros padrao;
- metrica de retorno ajustado ao risco incluida no resumo e nas comparacoes;
- experimento H3 refinado para testar overtrading com sinal ruidoso, custo maior e turnover elevado;
- relatorio final academico gerado em [docs/relatorio_final.md](docs/relatorio_final.md);
- avaliacao objetiva das hipoteses atualizada em [docs/avaliacao_hipoteses.md](docs/avaliacao_hipoteses.md).

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

No baseline final de 2020-2025, a renda variavel usa `b3_cotahist_bova11`.

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
PYTHONPATH=src python3 -m teoria_jogos.cli fetch-bcb --start 01/01/2020 --end 31/12/2025
```

Saidas geradas:

- `data/raw/bcb/bcb_sgs_selic.csv`;
- `data/raw/bcb/bcb_sgs_ipca.csv`;
- `data/raw/bcb/bcb_sgs_usd_brl.csv`;
- `data/raw/bcb/bcb_sgs_ibovespa.csv`, quando disponivel;
- `data/processed/macro_bcb.csv`.

### Integrar renda variavel real via B3/COTAHIST

```bash
PYTHONPATH=src python3 -m teoria_jogos.cli fetch-b3-equity --start-year 2020 --end-year 2025 --symbol BOVA11
```

Saidas geradas:

- `data/raw/b3/COTAHIST_A2020.ZIP` ate `data/raw/b3/COTAHIST_A2025.ZIP`;
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
PYTHONPATH=src python3 -m teoria_jogos.cli fetch-cvm-funds --year-month 202512
```

Saidas geradas:

- `data/raw/cvm/inf_diario_fi_202512.zip`;
- `data/processed/cvm_funds_summary.csv`.

### Rodar simulacao com o CSV macro existente

```bash
PYTHONPATH=src python3 -m teoria_jogos.cli simulate --agents 90 --imitation 1.0 --seed 42 --calibration data/processed/calibration_params.json
```

Saidas geradas:

- `outputs/baseline_history.csv`;
- `outputs/baseline_summary.json`.

### Comparar cenarios de imitacao

```bash
PYTHONPATH=src python3 -m teoria_jogos.cli compare-scenarios --agents 90 --imitation-levels 0.0,1.0,2.0 --seed 42 --calibration data/processed/calibration_params.json
```

Saida gerada:

- `outputs/scenario_comparison.csv`.

### Comparar cenarios de choque

```bash
PYTHONPATH=src python3 -m teoria_jogos.cli compare-shocks --agents 90 --imitation 1.0 --seed 42 --calibration data/processed/calibration_params.json
```

Saida gerada:

- `outputs/shock_comparison.csv`.

### Comparar rebalanceamento e ruido

```bash
PYTHONPATH=src python3 -m teoria_jogos.cli compare-rebalance --agents 90 --imitation 1.0 --seed 42 --calibration data/processed/calibration_params.json
```

Saida gerada:

- `outputs/rebalance_comparison.csv`.

### Comparar perfis de agentes

```bash
PYTHONPATH=src python3 -m teoria_jogos.cli compare-profiles --agents 90 --imitation 1.0 --seed 42 --calibration data/processed/calibration_params.json
```

Saida gerada:

- `outputs/profile_comparison.csv`.

### Calibrar parametros iniciais

Execute depois das ingestoes BCB, B3, Tesouro e CVM, antes das simulacoes finais.

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
- `docs/avaliacao_hipoteses.md`;
- `docs/relatorio_final.md`.

### Rodar baseline simples

```bash
PYTHONPATH=src python3 -m teoria_jogos.cli run-baseline --start 01/01/2020 --end 31/12/2025 --agents 90 --imitation 1.0 --seed 42 --calibration data/processed/calibration_params.json
```

Observacao: `run-baseline` baixa apenas o painel macro do BCB e executa a simulacao. Para reproduzir a versao final do projeto, execute tambem B3, Tesouro, CVM, calibracao, simulacoes comparativas e `generate-report`.

## Resultado do Baseline Executado

Execucao local realizada com dados BCB e B3/COTAHIST `BOVA11` de 2020-2025, `90` agentes, `imitation=1.0`, `seed=42` e calibracao aplicada de `data/processed/calibration_params.json`.

| Metrica | Valor |
| --- | --- |
| Periodos | 72 |
| Retorno acumulado medio | 64.05% |
| Retorno medio mensal | 0.70% |
| Volatilidade mensal do retorno medio | 1.36% |
| Retorno ajustado ao risco | 0.5136 |
| Turnover medio | 4.86% |
| Max drawdown | -5.21% |
| Concentracao HHI final | 0.2034 |
| Peso final em caixa | 17.30% |
| Peso final em Tesouro Selic | 20.59% |
| Peso final em Tesouro IPCA+ | 18.18% |
| Peso final em fundos RF | 19.16% |
| Peso final em renda variavel | 24.76% |

Leitura tecnica: no periodo 2020-2025, a carteira agregada termina mais diversificada que no recorte de 2024. A calibracao elevou o risco atribuido a renda variavel para refletir a volatilidade historica de `BOVA11`, mas o retorno acumulado do periodo ainda manteve exposicao relevante a essa classe.

## Comparacao de Cenarios

Execucao local com dados de 2020-2025, `90` agentes, `seed=42` e calibracao aplicada.

| Cenario | Retorno acumulado medio | Retorno ajustado ao risco | HHI final | Peso final em renda variavel |
| --- | --- | --- | --- | --- |
| `imitation=0.0` | 64.36% | 0.5109 | 0.2038 | 24.96% |
| `imitation=1.0` | 64.05% | 0.5136 | 0.2034 | 24.76% |
| `imitation=2.0` | 63.73% | 0.5162 | 0.2031 | 24.55% |

Leitura tecnica: H2 ficou inconclusiva nesta rodada. A imitacao reduziu levemente o retorno acumulado e a exposicao a renda variavel, mas nao elevou o HHI final. A penalidade de crowding parece conter a concentracao pura por imitacao.

## Comparacao de Choques

Execucao local com dados de 2020-2025, `90` agentes, `imitation=1.0`, `seed=42` e calibracao aplicada.

| Cenario | Retorno acumulado medio | Max drawdown | Peso final em Selic | Peso final em renda variavel |
| --- | --- | --- | --- | --- |
| `none` | 64.05% | -5.21% | 20.59% | 24.76% |
| `rate_hike` | 61.19% | -5.21% | 22.54% | 19.93% |
| `inflation_spike` | 60.54% | -5.21% | 20.97% | 21.54% |
| `equity_stress` | 32.92% | -5.21% | 25.98% | 9.86% |
| `combined_stress` | 53.25% | -5.21% | 28.27% | 5.55% |

Leitura tecnica: H1 foi parcialmente sustentada. O choque de juros aumenta o peso final em Selic e reduz renda variavel. Os choques de renda variavel e combinado geram deslocamento defensivo ainda mais forte.

## Comparacao de Rebalanceamento

Execucao local com dados de 2020-2025, `90` agentes, `seed=42` e calibracao aplicada.

| Cenario | Retorno acumulado medio | Retorno ajustado ao risco | Turnover medio | Peso final em renda variavel |
| --- | --- | --- | --- | --- |
| `slow_clean` | 61.20% | 0.4840 | 2.40% | 23.60% |
| `base_clean` | 64.05% | 0.5136 | 4.86% | 24.76% |
| `fast_clean` | 68.66% | 0.5359 | 7.38% | 24.42% |
| `fast_noisy` | 67.99% | 0.5294 | 14.20% | 24.06% |
| `very_fast_noisy` | 37.67% | 0.3392 | 42.67% | 23.47% |

Leitura tecnica: H3 foi refinada para medir eficiencia risco-retorno e overtrading. Rebalancear mais rapido sem ruido nao piorou o resultado; a hipotese aparece apenas no caso `very_fast_noisy`, com sinal muito ruidoso, custo efetivo maior e turnover de 42.67%.

## Comparacao de Perfis

Execucao local com dados de 2020-2025, `90` agentes, `seed=42` e calibracao aplicada.

| Cenario | Retorno acumulado medio | Retorno ajustado ao risco | Max drawdown | Peso final em renda variavel |
| --- | --- | --- | --- | --- |
| `heterogeneous` | 64.05% | 0.5136 | -5.21% | 24.76% |
| `homogeneous_conservador` | 66.06% | 0.6487 | -2.05% | 21.82% |
| `homogeneous_moderado` | 64.23% | 0.5039 | -5.36% | 25.31% |
| `homogeneous_agressivo` | 61.70% | 0.4139 | -8.31% | 27.45% |

Leitura tecnica: H4 foi parcialmente sustentada contra o mercado homogeneo agressivo. A populacao heterogenea teve drawdown menor e melhor retorno ajustado ao risco que o perfil agressivo puro, embora o perfil conservador homogeneo tenha sido mais estavel.

## Calibracao Final Aplicada

Arquivo gerado: `data/processed/calibration_params.json`.

| Parametro observado | Valor |
| --- | --- |
| Volatilidade mensal Selic | 0.36% |
| Volatilidade mensal IPCA | 0.43% |
| Volatilidade mensal renda variavel BOVA11 | 6.66% |
| Fluxo liquido CVM / patrimonio liquido | 0.08% |
| Risco sugerido para renda variavel | 0.3331 |
| Crowding penalty sugerido | 0.0284 |

A calibracao foi aplicada diretamente nas simulacoes finais. O resumo do baseline registra `calibration_source=data/processed/calibration_params.json`.

## Avaliacao das Hipoteses

A avaliacao objetiva foi salva em [docs/avaliacao_hipoteses.md](docs/avaliacao_hipoteses.md), e o texto academico final foi salvo em [docs/relatorio_final.md](docs/relatorio_final.md).

| Hipotese | Status final |
| --- | --- |
| H1 | Parcialmente sustentada |
| H2 | Inconclusiva |
| H3 | Parcialmente sustentada |
| H4 | Parcialmente sustentada |

## Estrutura Recomendada do Repositorio

```text
teoria_jogos/
|-- README.md
|-- pyproject.toml
|-- docs/
|   |-- bases.md
|   |-- referencias.md
|   |-- avaliacao_hipoteses.md
|   `-- relatorio_final.md
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

1. Revisar o texto final com o professor/orientador para ajustar linguagem e exigencias formais.
2. Se necessario, incluir referencias bibliograficas adicionais no formato exigido pela disciplina.
3. Opcionalmente ampliar a proxy de renda variavel para mais ativos ou indices alem de `BOVA11`.
