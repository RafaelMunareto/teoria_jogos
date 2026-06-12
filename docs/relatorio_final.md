# Relatorio Final - Simulacao Multiagente de Decisao Financeira

## Resumo

Este projeto implementa uma simulacao multiagente de alocacao financeira para investidores brasileiros. O problema e tratado como um jogo repetido: agentes conservadores, moderados e agressivos escolhem pesos entre caixa, Tesouro Selic, Tesouro IPCA+, fundos de renda fixa e renda variavel. O payoff individual depende dos retornos observados, do custo de rebalanceamento e da interacao agregada via imitacao e penalidade de crowding.

A versao final inicial usa dados macro do BCB, proxy de renda variavel via B3/COTAHIST com BOVA11, resumo de taxas do Tesouro Transparente e agregado de fundos da CVM. Os parametros calibrados sao aplicados no simulador quando o arquivo `data/processed/calibration_params.json` esta disponivel; caso contrario, o modelo usa parametros padrao documentados no codigo.

## Metodologia

A simulacao principal roda 72 periodos mensais com 90 agentes. Cada periodo combina retorno observado ou aproximado por classe de ativo, preferencia de risco do perfil, componente de imitacao, penalidade de concentracao e custo de giro. A metrica central de desempenho e o retorno ajustado ao risco, calculado como retorno medio mensal dividido pela volatilidade mensal do retorno medio.

O experimento H3 foi refinado para nao depender apenas de retorno acumulado bruto. Como rebalanceamentos frequentes podem reduzir risco ao mesmo tempo em que elevam custos e turnover, a avaliacao final compara eficiencia risco-retorno e giro medio entre estrategias lentas/disciplinadas e estrategias rapidas/ruidosas.

## Resultados Principais

No baseline, o retorno acumulado medio foi 64.05%, com retorno medio mensal de 0.70%, volatilidade mensal de 1.36%, retorno ajustado ao risco de 0.5136 e max drawdown de -5.21%.
A carteira agregada final ficou distribuida entre Selic (20.59%), IPCA+ (18.18%), fundos RF (19.16%), caixa (17.30%) e renda variavel (24.76%).

A leitura economica e que o modelo produz uma resposta defensiva quando aumentam juros, inflacao ou estresse em renda variavel. O choque combinado aumenta a preferencia por ativos de menor risco e reduz a exposicao final a renda variavel, comportamento coerente com investidores avessos a perda em ambiente macro adverso.

## Avaliacao das Hipoteses

| Hipotese | Status | Evidencia sintetica |
| --- | --- | --- |
| H1 | parcialmente sustentada | No choque de alta de juros, o peso em Tesouro Selic foi 22.54%, contra 20.59% no cenario sem choque. |
| H2 | inconclusiva | Com imitacao 2.0, o HHI final foi 0.2031; com imitacao 0.0, foi 0.2038. |
| H3 | parcialmente sustentada | O cenario `very_fast_noisy` teve retorno ajustado ao risco de 0.3392, contra 0.4840 em `slow_clean`; o turnover foi 42.67% contra 2.40%. |
| H4 | parcialmente sustentada | O drawdown heterogeneo foi -5.21%; no mercado homogeneo agressivo, foi -8.31%. |

## Interpretacao Economica

H1 e sustentada de forma parcial porque o choque de juros desloca alocacao para Selic, mas nao elimina totalmente outros ativos. Isso e coerente com a arquitetura do modelo: os agentes mantem ancoras de perfil e nao maximizam somente retorno corrente.

H2 depende da magnitude do parametro de imitacao. Nesta execucao, o HHI final nao aumentou quando a imitacao passou de 0.0 para 2.0, indicando que a penalidade de crowding mitigou a concentracao excessiva. Assim, a hipotese fica inconclusiva nesta parametrizacao, embora os choques ainda mostrem deslocamento defensivo relevante.

H3 foi reformulada corretamente como teste de eficiencia, nao apenas de retorno bruto. Em alguns cenarios, reagir rapido pode preservar capital ao reduzir renda variavel; por isso, o criterio final considera retorno ajustado ao risco, turnover e custo de rebalanceamento. Quando o sinal e ruidoso e o giro cresce, a estrategia perde eficiencia relativa.

H4 sugere que a heterogeneidade ajuda a reduzir sincronizacao extrema frente a um mercado composto apenas por agentes agressivos. A conclusao e parcial porque a heterogeneidade tambem inclui agentes moderados e conservadores, portanto o ganho pode vir tanto da diversidade quanto da menor exposicao media ao risco.

## Limitacoes

O modelo nao estima decisoes individuais reais; ele simula agentes sinteticos calibrados por agregados publicos. O BOVA11 e uma proxy operacional de renda variavel e nao representa todo o mercado acionionario brasileiro. A serie B3/COTAHIST nao e ajustada por proventos. O custo de rebalanceamento e simplificado e deve ser validado em trabalhos futuros.

## Conclusao

O projeto esta concluido como versao academica inicial e reprodutivel. Ele permite coletar dados, calibrar parametros, executar simulacoes e avaliar H1-H4. Os resultados mais consistentes sao a resposta defensiva a choques macro, a penalizacao de estrategias ruidosas quando avaliadas por eficiencia risco-retorno e o papel estabilizador parcial da heterogeneidade. O efeito puro de imitacao sobre concentracao ficou inconclusivo nesta rodada. O cenario de estresse combinado fechou com retorno acumulado de 53.25%, enquanto o estresse especifico em renda variavel reduziu o peso final dessa classe para 9.86%.
