# Citizen Assist AI

Assistente digital de orientação ao cidadão, executado no terminal, em Python puro (sem bibliotecas externas).
Projeto da **Global Solution 2026.2 (CitizenTech)**, que atende em um único programa:

- **PCP** (Pensamento Computacional e Automação com Python): assistente com busca por pontuação, histórico, indicadores e CSV.
- **DSA** (Data Structures and Algorithms): gerenciamento dos registros em uma **lista encadeada própria**, com CRUD, pesquisa, **Merge Sort** e análise **Big-O**.
- **SERS** (Soluções em Energias Renováveis e Sustentáveis): calculadora e análise de energia do **banho quente**, comparando chuveiro elétrico, hábitos e **aquecedor solar** (ver seção 12 e `docs/energia/`).

> **Aviso:** este assistente **NÃO é um canal oficial** e nunca pede nem registra dados pessoais.

## 1. Integrantes

| Nome | RM |
|------|----|
| [PREENCHER] | [PREENCHER] |
| [PREENCHER] | [PREENCHER] |
| [PREENCHER] | [PREENCHER] |

## 2. Público e problema escolhidos

**Público:** jovens no primeiro emprego.

**Problema:** quem começa a trabalhar precisa de vários documentos e direitos ao mesmo tempo (Carteira de Trabalho Digital, CPF, conta gov.br, FGTS, título de eleitor, alistamento militar), e a informação está espalhada, em linguagem técnica e misturada com sites que parecem oficiais e não são (inclusive cobranças indevidas para emitir CPF ou carteira de trabalho). O assistente responde com base em **16 orientações** (12 de cidadania e trabalho, 4 de energia), mostrando fonte, data de verificação e aviso de limitação.

## 3. ODS relacionados

- **ODS 8** – Trabalho decente e crescimento econômico (entrada segura no mercado de trabalho, direitos trabalhistas).
- **ODS 10** – Redução das desigualdades (informação simples para quem tem menos acesso a orientação).
- **ODS 16** – Paz, justiça e instituições eficazes (acesso à informação pública e transparência de fontes).

## 4. Como executar

Requisito: Python 3.8 ou superior. Nada para instalar.

```bash
python main.py
```

Menu principal:

| Opção | O que faz |
|-------|-----------|
| 1 | Fazer uma pergunta em texto livre (busca por pontuação) |
| 2 | Navegar por categorias (`0` volta em todas as telas) |
| 3 | Ver indicadores |
| 4 | Exportar os atendimentos para `data/atendimentos.csv` |
| 5 | Gerenciar orientações: cadastrar, consultar por id, listar, atualizar, excluir, pesquisar e ordenar (DSA) |
| 6 | Calculadora de energia: chuveiro elétrico x hábitos x aquecedor solar (SERS) |
| 0 | Sair (pede nota de facilidade de 1 a 5; o CSV também é exportado ao sair) |

Para rodar todos os testes (45 cenários e 53 verificações) e regenerar as evidências (não altera a pasta `data/`):

```bash
python tests/gerar_evidencias.py
```

### Organização do projeto

```
citizen-assist-ai/
├── README.md
├── main.py               # menus e entrada do programa
├── orientacao.py         # classe Orientacao (registro + exibir())
├── base_conhecimento.py  # classe BaseConhecimento (JSON, busca com pontuação, CRUD, ordenação)
├── assistente.py         # classe Assistente (atendimento, histórico, indicadores, CSV)
├── lista_encadeada.py    # No e ListaEncadeada (estrutura implementada pela equipe, DSA)
├── energia.py            # SERS: cálculo, comparação, sensibilidade e recomendações de energia
├── data/
│   ├── base_conhecimento.json
│   ├── energia_dados.json    # SERS: parâmetros com origem, tipo, unidade, período e referências
│   ├── historico.json
│   └── atendimentos.csv  # gerado ao exportar
├── docs/
│   ├── DOCUMENTACAO_TECNICA.md   # DSA: lista, algoritmos e Big-O
│   ├── MATRIZ_REQUISITOS.md      # cada requisito das duas propostas e onde está
│   ├── TESTES.md                 # entrada, esperado e observado de cada cenário
│   ├── evidencias/               # saída completa do terminal de cada cenário
│   └── energia/                  # SERS: contexto, dados, cálculos, recomendações, referências, testes com usuários, roteiro
└── tests/ (gerar_evidencias.py, gerar_docs_energia.py)
```

Os 4 arquivos exigidos pelo PCP (`main.py`, `orientacao.py`, `base_conhecimento.py`, `assistente.py`) estão presentes. `lista_encadeada.py` é um quinto arquivo, criado para isolar a estrutura de dados do DSA.

## 5. Regra de pontuação usada

Pergunta, palavras-chave e título são normalizados (minúsculas, sem acentos, sem pontuação) por `normalizar()`.

| Regra | Pontos |
|-------|--------|
| Palavra-chave da orientação que aparece na pergunta | +3 (por palavra-chave) |
| Palavra da pergunta com 4 letras ou mais que aparece no título | +1 (cada palavra conta uma vez) |

| Melhor pontuação | Resultado |
|------------------|-----------|
| 6 ou mais | Confiança **ALTA** |
| 3 a 5 | Confiança **MÉDIA** |
| menos de 3 | "Não encontrei": sugere outras palavras e as categorias |

`buscar()` devolve uma **lista de tuplas** `(pontos, orientacao)` da maior para a menor pontuação (empate: menor id). O assistente mostra a melhor orientação e até duas alternativas. Os pesos e limites são os do enunciado, sem ajustes.

**Exemplo real:** "Como faço o cartão do SUS?" → a orientação 3 recebe +3 por `cartao do sus`, +3 por `sus` e +1 porque "cartao" está no título: **7 pontos, confiança ALTA** (cenário P01 em `docs/TESTES.md`).

## 6. Atendimento, histórico e indicadores

- Cada **atendimento** é uma dúvida: começa na primeira pergunta e termina quando a pessoa responde `s` (ajudou) ou volta com `0`. Perguntas reescritas contam como **tentativas** do mesmo atendimento.
- Cada atendimento vai para `data/historico.json` com: data, origem (pergunta ou categoria), pergunta, id da orientação, se encontrou, se ajudou, tentativas e tempo em segundos (`time.time()`).
- A **nota de facilidade (1 a 5)** é pedida ao sair e guardada no último atendimento da sessão.
- **Indicadores:** resposta encontrada (%), taxa de acerto (%), tempo médio para encontrar, tentativas por atendimento, facilidade de uso e lista de dúvidas sem solução.
- **CSV:** `data/atendimentos.csv`, gerado com `csv.DictWriter`.
- **Dados pessoais:** pergunta com 8 ou mais dígitos ou com `@` é recusada, não é buscada e **não é registrada**.
- **Arquivos:** JSON da base ausente ou corrompido não derruba o programa (mostra aviso e abre com a base vazia).

## 7. Integrações com outras disciplinas

- **DSA:** a base de conhecimento é guardada em uma **lista encadeada implementada pela equipe** (`lista_encadeada.py`), com inserção, percurso, busca, atualização, remoção e **Merge Sort**. A análise Big-O está em `docs/DOCUMENTACAO_TECNICA.md`.
- A busca por pontuação (PCP) continua sendo a base da resposta, como o enunciado exige.
- Não foram usados modelos de IA nem APIs externas.

## 8. Fontes consultadas

Pesquisa feita em 12/11/2026. Cada orientação traz a fonte oficial e a data em `data/base_conhecimento.json`.

- Ministério do Trabalho e Emprego – https://www.gov.br/trabalho-e-emprego e serviço https://www.gov.br/pt-br/servicos/realizar-denuncia-trabalhista
- Receita Federal – https://www.gov.br/receitafederal/pt-br
- Ministério da Saúde / Meu SUS Digital – https://www.gov.br/saude
- Tribunal Superior Eleitoral – https://www.tse.jus.br/servicos-eleitorais/autoatendimento-eleitoral
- Carteira de Identidade Nacional – https://www.gov.br/identidade
- Governo Digital (conta gov.br) – https://www.gov.br/governodigital
- Exército Brasileiro (Alistamento Online) – https://alistamento.eb.mil.br
- Caixa (FGTS) – https://www.caixa.gov.br/extrato-fgts
- Consumidor.gov.br – https://www.consumidor.gov.br
- Portaria SEPRT nº 1.065/2019 (Carteira de Trabalho Digital) e Agência Brasil/Agência Gov (alistamento, CIN, Cartão SUS)

> **Atenção, equipe:** parte das informações foi conferida em reportagens que citam o órgão oficial (e não só na página do órgão). **Antes de entregar, reabra cada link acima, confirme o conteúdo e atualize `verificado_em`.** Telefones, prazos e valores mudam.

## 9. Teste com usuários

> **[PREENCHER pela equipe]** O enunciado exige testar com pelo menos 3 pessoas de fora da equipe, somando 10 atendimentos ou mais, **antes** de gravar o vídeo. Não registre nomes nem dados dessas pessoas. Os valores abaixo saem da opção 3 do menu (Ver indicadores).

| Indicador | Resultado |
|-----------|-----------|
| Pessoas testadas / atendimentos | [PREENCHER] / [PREENCHER] |
| Resposta encontrada (%) | [PREENCHER] |
| Taxa de acerto: ajudou (%) | [PREENCHER] |
| Tempo médio para encontrar | [PREENCHER] |
| Tentativas por atendimento | [PREENCHER] |
| Facilidade de uso (1 a 5) | [PREENCHER] |

**Dúvidas sem solução:** [PREENCHER]

**Melhoria feita a partir do teste:** [PREENCHER] (ex.: nova palavra-chave incluída no JSON).

> O `data/historico.json` entregue está **vazio de propósito**: os testes automáticos rodam em cópias temporárias e não são atendimentos reais. Os atendimentos reais do teste com usuários devem ser gerados rodando `python main.py`.

## 10. Limitações

- Só responde o que está na base (16 orientações); fora disso diz "não encontrei".
- A busca compara palavras exatas, sem entender sinônimos, erros de digitação ou o contexto da frase. Por isso, "13 salario" só é entendido depois de a palavra-chave ser incluída (ver cenário P08).
- A regra de 8 ou mais dígitos pode bloquear perguntas legítimas com números longos (por exemplo, o número de uma lei).
- As informações públicas mudam (prazos, taxas, telefones): a data de verificação existe para lembrar disso.
- O alistamento militar tem prazo anual; a orientação informa que o de 2026 já terminou.
- A lista encadeada exige varrer os nós para achar um id (O(n)); para 12 ou algumas centenas de registros isso é desprezível.

## 11. Vídeo técnico

Link (YouTube, não listado, 5 a 8 minutos): **[PREENCHER]**

Roteiro obrigatório e onde mostrar cada item:

1. Equipe, público e problema (até 30 s).
2. JSON: um registro explicado, dicionários e tuplas → `data/base_conhecimento.json`, `buscar()`.
3. Classes: atributos, métodos, `self` e composição → `Assistente` → `BaseConhecimento` → `ListaEncadeada` → `Orientacao`.
4. Busca: `normalizar()` e `pontuar()` com uma pergunta real → exemplo do cartão do SUS (7 pontos).
5. Execução: encontrada, não encontrada, entrada inválida, dado pessoal bloqueado e categorias.
6. **Alteração ao vivo:** menu 5 → 4 (Atualizar) → incluir palavra-chave → a pergunta antes não encontrada passa a ser encontrada (cenário P08).
7. `historico.json`, CSV exportado e indicadores do teste.
8. Uma decisão técnica (ex.: Merge Sort em lista encadeada) e uma limitação (ex.: busca só por palavras exatas).

Todos os integrantes devem falar. Não é permitida narração com IA ou voz sintética.

## 12. Energia (SERS): banho quente, hábitos e aquecedor solar

> Contribuição de energia identificada: `energia.py`, `data/energia_dados.json`, orientações 13 a 16, opção 6 do menu e `docs/energia/`.

**Público e necessidade:** jovens no primeiro emprego e o **banho quente** (chuveiro elétrico), que pesa na conta de luz.
**Pergunta:** manter o chuveiro, mudar hábitos ou instalar **aquecedor solar de água** (solar térmico, não fotovoltaico)?

**Resultado de referência** (3 pessoas, 10 min, 5.500 W, R$ 0,82/kWh, 10 anos; **estimativas, não garantias**):

| Alternativa | kWh/mês | R$/mês | Investimento | Retorno |
|-------------|---------|--------|--------------|---------|
| Chuveiro atual | 82,5 | 67,65 | - | - |
| Hábitos (7 min + modo verão) | 49,5 | 40,61 | 0 | imediato |
| Aquecedor solar (renovável) | 24,8 | 20,30 | R$ 4.500 | 8 anos |
| Hábitos + solar | 14,9 | 12,18 | R$ 4.500 | 6 anos e 10 meses (13 anos e 3 meses para o solar depois dos hábitos) |

O solar se paga em 10 anos só se o chuveiro gastar mais de ~65 kWh/mês; com preço de R$ 6.000 o saldo fica negativo. O ganho de CO2 é pequeno (a rede elétrica brasileira é limpa).

Documentação: [`docs/energia/README_ENERGIA.md`](docs/energia/README_ENERGIA.md) (contexto e funcionalidades),
[`DADOS_E_PREMISSAS.md`](docs/energia/DADOS_E_PREMISSAS.md), [`CALCULOS.md`](docs/energia/CALCULOS.md),
[`RECOMENDACOES.md`](docs/energia/RECOMENDACOES.md), [`REFERENCIAS.md`](docs/energia/REFERENCIAS.md),
[`TESTES_USUARIOS.md`](docs/energia/TESTES_USUARIOS.md), [`ROTEIRO_VIDEO_ENERGIA.md`](docs/energia/ROTEIRO_VIDEO_ENERGIA.md).

**Limitações:** simulação publicada (Viçosa-MG), sem manutenção, financiamento, inflação, gás nem fotovoltaico; tarifa sem tributos; fonte oficial de bandeiras (ANEEL) a reconferir. **Testes com usuários de energia:** [PREENCHER pela equipe em `docs/energia/TESTES_USUARIOS.md`].
Link do vídeo SERS (YouTube, não listado, até 3 min): **[PREENCHER]**
