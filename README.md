# CRISP-DM - Simulacao Multiagente Baseada em Teoria dos Jogos

## Estado Atual

Este repositorio ainda nao possui implementacao. Para estruturar o projeto com um caminho viavel, foi definido um recorte inicial recomendado:

**simular escolhas estrategicas de mobilidade urbana na Regiao Metropolitana de Sao Paulo (RMSP) como um jogo de congestionamento**, comparando equilibrio egoista, cenarios coordenados e politicas de intervencao.

Esse recorte e adaptavel. Se depois voce quiser migrar para outro dominio, a estrutura abaixo continua valida.

## Resumo do Projeto

O projeto passa a investigar como agentes com objetivos proprios tomam decisoes de rota, horario e uso de infraestrutura em uma rede urbana congestionada. A ideia central e modelar a cidade como um sistema multiagente em que o custo de cada agente depende das escolhas dos demais.

Na primeira versao, o foco recomendado e:

- agentes de deslocamento pendular;
- agentes de carga urbana como extensao de fase 2;
- um gestor publico opcional, modelado como regulador ou lider de um jogo do tipo Stackelberg.

## Recorte Inicial Recomendado

### Tema

Jogos de congestionamento aplicados a mobilidade urbana da RMSP.

### Pergunta central

Como escolhas estrategicas descentralizadas alteram o desempenho global da rede urbana quando passageiros e operadores de carga competem pelos mesmos recursos viarios?

### Objetivo geral

Construir uma simulacao multiagente capaz de comparar:

- equilibrio descentralizado dos agentes;
- solucao socialmente coordenada;
- cenarios de intervencao do poder publico.

### Objetivos especificos

- representar a rede urbana e os corredores relevantes;
- estimar demandas de deslocamento a partir de bases publicas;
- definir funcoes de custo dependentes de congestionamento;
- medir ineficiencia do equilibrio estrategico;
- testar politicas como informacao de rota, janelas de carga e deslocamento modal.

## 1. Business Understanding (Entendimento do Problema Cientifico)

### Problema cientifico

Em sistemas urbanos, cada agente tenta minimizar seu proprio custo de deslocamento, mas o resultado agregado pode ser ineficiente. Esse tipo de conflito entre racionalidade individual e desempenho coletivo e um problema classico de teoria dos jogos e e especialmente relevante em redes de transporte congestionadas.

### Agentes do modelo

- Passageiros: escolhem rota, horario e, em versoes futuras, modo de transporte.
- Operadores de carga: escolhem janelas, rotas e perfis de distribuicao.
- Gestor publico: altera regras, incentivos ou restricoes da rede.

### Estrutura de jogo recomendada

- Jogo base: congestion game / routing game.
- Equilibrio de referencia: equilibrio egoista dos agentes.
- Comparacao normativa: system optimum.
- Extensao futura: jogo lider-seguidor para avaliar politicas publicas.

### Hipoteses de trabalho

| ID | Hipotese | Como testar |
| --- | --- | --- |
| H1 | O equilibrio egoista produz maior atraso medio e maior custo total do que uma alocacao coordenada da demanda. | Comparar equilibrio descentralizado vs system optimum em cenarios identicos de demanda. |
| H2 | Informacao de rota disponibilizada apenas para parte dos agentes pode deslocar congestionamento e piorar o desempenho agregado em corredores criticos. | Rodar cenarios com informacao total, parcial e nula. |
| H3 | Politicas de janela horaria para carga urbana reduzem mais o custo total da rede do que restricoes uniformes e pouco segmentadas. | Comparar cenarios com janelas por zona/setor vs restricoes genericas. |
| H4 | Pequenas mudancas modais em corredores saturados reduzem desproporcionalmente o custo coletivo da rede. | Simular transferencia parcial de demanda do carro para o transporte coletivo. |

### Criterios de sucesso

- Conseguir reproduzir padroes agregados coerentes com as bases observadas.
- Medir tempo medio, atraso total e custo total por cenario.
- Estimar diferenca entre equilibrio egoista e solucao coordenada.
- Produzir cenarios comparaveis e interpretaveis para suporte a decisao.

## 2. Data Understanding (Entendimento dos Dados)

### Bases selecionadas

As bases priorizadas para o recorte inicial estao listadas em [docs/bases.md](/Users/munareto/Documents/teoria_jogos/docs/bases.md:1).

| Base | Papel no projeto | Prioridade |
| --- | --- | --- |
| Pesquisa Origem e Destino 2023 - Metro SP | Estimar demanda de passageiros e padroes de deslocamento na RMSP | Alta |
| Pesquisa OD Cargas - CET SP | Modelar agentes de carga urbana, setores e fluxos logisticos | Media |
| OpenStreetMap / Geofabrik Sudeste | Construir a rede viaria para simulacao | Alta |
| API Olho Vivo - SPTrans | Representar oferta basica de linhas, paradas e corredores | Media |
| SIMOB - ANTP | Calibrar indicadores agregados e benchmarking | Media |

### Artigos e referencias base

As referencias iniciais foram organizadas em [docs/referencias.md](/Users/munareto/Documents/teoria_jogos/docs/referencias.md:1).

### Variaveis de interesse

As variaveis abaixo combinam itens confirmados nas fontes e campos derivados da modelagem:

- origem e destino por zona;
- tipo de agente;
- horario ou janela de deslocamento;
- tipo de veiculo ou modo;
- atributos da rede viaria;
- custos de percurso dependentes de uso;
- parametros de politica publica por cenario.

### Riscos e limitacoes iniciais

- O esquema detalhado da base OD 2023 do Metro precisa ser confirmado apos download.
- A integracao entre passageiros e carga aumenta bastante a complexidade; por isso, a fase 1 deve priorizar passageiros.
- Dados operacionais detalhados de tempo real podem exigir simplificacoes ou cenarios sinteticos.

## 3. Data Preparation (Preparacao dos Dados)

### Pipeline recomendado

1. Catalogar e baixar as bases publicas prioritarias.
2. Padronizar identificadores de zonas e recortes espaciais.
3. Extrair a rede viaria do OpenStreetMap.
4. Construir matrizes OD de passageiros.
5. Adicionar agentes de carga como extensao de fase 2.
6. Gerar agentes sinteticos a partir das distribuicoes observadas.
7. Definir funcoes de custo, capacidade e penalidade por congestionamento.

### Saidas esperadas

- grafo viario processado;
- matrizes OD por cenario;
- configuracoes de agentes;
- parametros de custo por aresta ou corredor;
- conjuntos de cenarios para simulacao.

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

1. Baixar e inspecionar a base da Pesquisa OD 2023 do Metro.
2. Baixar a rede viaria do OpenStreetMap para o recorte escolhido.
3. Definir o primeiro modelo de custo por congestionamento.
4. Implementar uma simulacao baseline com agentes de passageiros.
5. Adicionar agentes de carga e politicas de intervencao na fase seguinte.
