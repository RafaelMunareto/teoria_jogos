# Bases de Dados Recomendadas

Este projeto ainda nao tinha um dominio aplicado definido. Para viabilizar uma primeira versao consistente, as bases abaixo foram selecionadas para um recorte inicial em mobilidade urbana na RMSP.

## Bases Prioritarias

| Base | Instituicao | O que foi verificado | Uso no projeto | Link |
| --- | --- | --- | --- | --- |
| Pesquisa Origem e Destino 2023 | Metro de Sao Paulo | A pagina informa que o estudo revela novos padroes de deslocamento na RMSP e disponibiliza relatorio e base publica. | Demanda de passageiros, zonas e padroes agregados de deslocamento. | https://www.metro.sp.gov.br/pesquisa-od/ |
| Pesquisa OD 2023 - anexos | Portal da Transparencia do Metro | O portal mostra recurso publico em formato zip, publicado em 12/02/2025 e modificado em 20/02/2025. | Insumos tabulares da pesquisa OD. | https://transparencia.metrosp.com.br/dataset/pesquisa-origem-e-destino-2023-anexos |
| Pesquisa OD 2023 - relatorio sintese | Portal da Transparencia do Metro | O portal mostra relatorio publico em PDF, publicado em 18/02/2025 e modificado em 01/04/2025. | Base conceitual, indicadores e leitura inicial. | https://transparencia.metrosp.com.br/dataset/pesquisa-origem-e-destino-2023-relat%C3%B3rio-s%C3%ADntese |
| Pesquisa Origem e Destino de Cargas | CET Sao Paulo | A CET disponibiliza Base OD Cargas, layout/dicionario e mapas de zoneamento. | Fase 2: agentes de carga, setores economicos, veiculos e fluxos logisticos. | https://www.cetsp.com.br/consultas/caminhoes/pesquisa-origem-e-destino-de-cargas/download-banco-de-dados-e-mapas.aspx |
| OpenStreetMap Sudeste | Geofabrik / OSM | O extrato `sudeste-latest.osm.pbf` estava atualizado ate 2026-06-11T20:21:44Z no momento da consulta. | Rede viaria, arestas, conectividade e geometria espacial. | https://download.geofabrik.de/south-america/brazil/sudeste.html |
| API Olho Vivo | SPTrans | A documentacao confirma acesso a linhas, paradas, corredores e detalhes cadastrais por HTTPS. | Oferta de transporte coletivo, corredores e paradas. | https://www.sptrans.com.br/desenvolvedores/api-do-olho-vivo-guia-de-referencia/documentacao-api/ |
| SIMOB | ANTP | A ANTP informa consolidacao de dados e indicadores de mobilidade urbana para municipios com mais de 60 mil habitantes. | Benchmarking, calibracao macro e validacao de ordem de grandeza. | https://www.antp.org.br/sistema-de-informacoes-da-mobilidade/apresentacao.html |

## O que cada base agrega

### 1. Pesquisa OD 2023 - Metro SP

- Melhor base inicial para estimar demanda agregada de passageiros.
- Prioridade maxima para a fase 1 do projeto.
- O esquema detalhado da base ainda precisa ser confirmado apos download.

### 2. Pesquisa OD Cargas - CET

- Base mais forte para introduzir agentes logisticos.
- A CET explicita que a pesquisa relaciona quantidade de carga, caracteristicas das viagens, veiculos, setores economicos, porte das empresas e natureza das atividades.
- Ideal para a fase 2, quando o baseline de passageiros ja estiver funcional.

### 3. OpenStreetMap / Geofabrik

- Fornece o esqueleto espacial da simulacao.
- Deve ser usado para construir o grafo de rotas, capacidades simplificadas e corredores criticos.

### 4. API Olho Vivo - SPTrans

- Permite recuperar informacoes de linhas, paradas e corredores.
- Ajuda a representar oferta de transporte coletivo e cenarios de deslocamento modal.

### 5. SIMOB - ANTP

- Serve menos para a microdinamica e mais para calibracao de indicadores agregados.
- E util para checar se os resultados simulados ficam em uma faixa plausivel.

## Ordem recomendada de ingestao

1. Pesquisa OD 2023 - Metro SP
2. OpenStreetMap / Geofabrik
3. API Olho Vivo - SPTrans
4. Pesquisa OD Cargas - CET
5. SIMOB - ANTP

## Observacoes

- A escolha dessas bases e uma decisao de estruturacao, nao uma restricao definitiva do projeto.
- Se o tema final migrar de mobilidade para outro dominio, esta lista deve ser revisada.
