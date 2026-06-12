# Bases de Dados Recomendadas

O projeto foi redirecionado para decisao financeira. Para a primeira versao, a melhor estrategia e trabalhar com bases **oficiais e abertas** do ecossistema financeiro brasileiro.

## Bases Prioritarias

| Base | Instituicao | O que foi verificado | Uso no projeto | Link |
| --- | --- | --- | --- | --- |
| SGS / BCData | Banco Central do Brasil | O SGS consolida e disponibiliza informacoes economico-financeiras e permite consulta automatizada via webservices. | Series macrofinanceiras para cenarios de juros, cambio e inflacao. | https://www4.bcb.gov.br/pec/series/port/aviso.asp?frame=1 |
| Selic - interface BCData | Banco Central do Brasil | A interface de consulta JSON do BCData/SGS informa o formato padrao da API para series. | Pipeline automatizada de juros. | https://dadosabertos.bcb.gov.br/dataset/11-taxa-de-juros---selic/resource/b73edc07-bbac-430c-a2cb-b1639e605fa8 |
| Dolar comercial diario | Banco Central do Brasil | O portal oferece cotacao diaria com formatos API, JSON e OData. | Variavel macro complementar para regime de mercado. | https://dadosabertos.bcb.gov.br/dataset/dolar-americano-usd-todos-os-boletins-diarios |
| IBOVESPA - SGS 7 | Banco Central do Brasil | A API retornou valores historicos para 2019, mas nao retornou observacoes para 2024 na consulta local. | Proxy historica opcional para renda variavel quando disponivel. | https://api.bcb.gov.br/dados/serie/bcdata.sgs.7/dados?formato=json |
| Taxas dos Titulos Ofertados pelo Tesouro Direto | Tesouro Transparente | O CKAN retornou recurso CSV `precotaxatesourodireto.csv`, modificado em 12/06/2026. | Retorno e atratividade relativa da renda fixa publica. | https://www.tesourotransparente.gov.br/ckan/dataset |
| Vendas do Tesouro Direto | Tesouro Transparente | O portal informava ultima atualizacao em 12/06/2026 e descreve volume diario de vendas por tipo de titulo e vencimento. | Proxy de preferencia revelada por classe de titulo. | https://www.tesourotransparente.gov.br/temas/divida-publica-federal/estatisticas-e-relatorios-da-divida-publica-federal |
| Resgates do Tesouro Direto | Tesouro Transparente | O portal informava ultima atualizacao em 12/06/2026 e separa resgates por recompra, vencimento e cupom. | Analise de saida, liquidez e rotatividade. | https://www.tesourotransparente.gov.br/temas/divida-publica-federal/estatisticas-e-relatorios-da-divida-publica-federal |
| Investidores do Tesouro Direto | Tesouro Transparente | O portal informava ultima atualizacao em 10/06/2026 e oferece base detalhada de investidores cadastrados. | Perfil, segmentacao e calibracao de agentes sinteticos. | https://www.tesourotransparente.gov.br/temas/divida-publica-federal/estatisticas-e-relatorios-da-divida-publica-federal |
| Fundos de Investimento | CVM | O diretorio publico retornou `inf_diario_fi_202512.zip`; o informe diario contem patrimonio, captacoes, resgates e cotistas. | Fluxos, patrimonio, cotistas e categorias de fundos. | https://dados.cvm.gov.br/dados/FI/DOC/INF_DIARIO/DADOS/ |
| Cotacoes historicas | B3 | Os endpoints COTAHIST anuais de 2020 a 2025 foram processados para `BOVA11`. | Proxy real de renda variavel agregada no baseline 2020-2025. | https://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_A2025.ZIP |

## O que cada base agrega

### 1. Banco Central do Brasil

- Base principal para caracterizar o regime macro.
- Ideal para juros, cambio e outras series economico-financeiras.
- Deve alimentar o modulo de cenarios.
- A serie SGS 7 de IBOVESPA foi integrada como opcional; se nao houver observacao no periodo, o simulador usa `synthetic_fallback`.

### 2. Tesouro Transparente

- Melhor fonte oficial para renda fixa publica da pessoa fisica.
- Permite observar atratividade dos titulos e, em alguma medida, comportamento agregado do investidor no Tesouro Direto.
- Muito util para calibrar agentes conservadores e moderados.
- Integrado no projeto por `fetch-tesouro`, gerando `data/processed/tesouro_rates_summary.csv`.

### 3. CVM

- Melhor base oficial para fundos de investimento.
- O informe diario e valioso para patrimonio, cota e numero de cotistas.
- Ajuda a representar a classe "fundos" sem depender de bases privadas.
- Integrado no projeto por `fetch-cvm-funds`, gerando `data/processed/cvm_funds_summary.csv`.

### 4. B3

- Fonte oficial para mercado a vista.
- Deve ser usada com cuidado porque as cotacoes historicas nao estao ajustadas por proventos nem inflacao.
- Para a fase 1, o ideal e construir uma serie agregada por indice, ETF ou cesta simples.
- Integrada no projeto por `fetch-b3-equity --start-year 2020 --end-year 2025`, usando `BOVA11` como proxy operacional de renda variavel.

## Ordem recomendada de ingestao

1. BCB / SGS
2. Tesouro Transparente
3. CVM Fundos
4. B3 Historico

## Observacoes metodologicas

- O baseline deve usar **classes de ativos agregadas**, nao centenas de ativos individuais.
- O foco inicial nao e prever mercado, mas estudar comportamento de alocacao sob interacao estrategica.
- Se quisermos um projeto mais proximo de credito, inadimplencia ou risco bancario, as bases devem ser revistas.
