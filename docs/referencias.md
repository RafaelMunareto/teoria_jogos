# Referencias Iniciais

As referencias abaixo formam uma base teorica suficiente para iniciar a modelagem do projeto.

## Referencias centrais

| Referencia | Papel no projeto | Link |
| --- | --- | --- |
| Wardrop, J. G. (1952). *Some Theoretical Aspects of Road Traffic Research.* | Referencia fundacional para equilibrio em redes de trafego. | https://doi.org/10.1680/ipeds.1952.11259 |
| Rosenthal, R. W. (1973). *A class of games possessing pure-strategy Nash equilibria.* | Base teorica para jogos de congestionamento com equilibrio puro. | https://doi.org/10.1007/BF01737559 |
| Steinberg, R.; Zangwill, W. I. (1983). *The Prevalence of Braess' Paradox.* | Sustenta testes de efeitos paradoxais ao adicionar rotas ou informacao. | https://doi.org/10.1287/trsc.17.3.301 |
| Roughgarden, T. (2007). *Routing Games* in *Algorithmic Game Theory.* | Resume modelos de routing games e a ineficiencia dos equilibrios. | https://www.cambridge.org/core/books/abs/algorithmic-game-theory/routing-games/F46FD3C0B8087B5D74A736E37EAC4C4F |
| Shou, Z.; Chen, X.; Fu, Y.; Di, X. (2022). *Multi-Agent Reinforcement Learning for Markov Routing Games: A New Modeling Paradigm For Dynamic Traffic Assignment.* | Ponte entre jogos de roteamento, aprendizado multiagente e equilibrio dinamico. | https://doi.org/10.1016/j.trc.2022.103560 |

## Como usar essas referencias

### Bloco 1: fundamento teorico

- Wardrop (1952)
- Rosenthal (1973)
- Roughgarden (2007)

Esse trio sustenta a definicao de agentes egoistas, equilibrio de rede e medida de ineficiencia coletiva.

### Bloco 2: comportamento paradoxal e intervencao

- Steinberg e Zangwill (1983)

Essa referencia e importante para justificar experimentos em que mais informacao, mais capacidade ou novas rotas nao geram melhora agregada.

### Bloco 3: extensao computacional moderna

- Shou et al. (2022)

Essa referencia e a melhor ponte para uma fase posterior em que a simulacao evolua de um jogo estatico para um ambiente com aprendizado multiagente.

## Observacoes metodologicas

- O projeto nao precisa comecar com aprendizado por reforco.
- O baseline recomendado e um modelo mais simples de jogo de congestionamento com comparacao entre equilibrio egoista e system optimum.
- O uso de aprendizado multiagente deve entrar apenas depois que a pipeline de dados e o baseline estiverem estaveis.
