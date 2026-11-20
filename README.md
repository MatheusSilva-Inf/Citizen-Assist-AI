# Citizen Assist AI

Assistente digital de orientação ao cidadão, executado no terminal, em Python puro (sem bibliotecas externas).
Projeto da **Global Solution 2026 (CitizenTech)**, que atende em um único programa:

- **PCP** (Pensamento Computacional e Automação com Python): assistente com busca por pontuação, histórico, indicadores e CSV.
- **DSA** (Data Structures and Algorithms): gerenciamento dos registros em uma **lista encadeada própria**, com CRUD, pesquisa, **Merge Sort** e análise **Big-O**.
- **SERS** (Soluções em Energias Renováveis e Sustentáveis): calculadora e análise de energia do **banho quente**, comparando chuveiro elétrico, hábitos e **aquecedor solar** (ver seção 12 e `docs/energia/`).

> **Aviso:** este assistente **NÃO é um canal oficial** e nunca pede nem registra dados pessoais.

## 1. Integrantes

| Nome | RM |
|------|----|
| [Matheus Evangelista Silva] | [568593] |
| [Murillo Lima de Carvalho] | [570156] |
| [João Pedro Sousa] | [573962] |

## 2. Público e problema escolhidos

**Público:** jovens no primeiro emprego ou iniciando carreira.

**Problema:** quem começa a trabalhar precisa de vários documentos e direitos ao mesmo tempo (Carteira de Trabalho Digital, CPF, conta gov.br, FGTS, título de eleitor, alistamento militar), e a informação está espalhada, em linguagem técnica e misturada com sites que parecem oficiais e não são (inclusive muitos tendo cobranças indevidas para emitir CPF ou carteira de trabalho). O assistente responde com base em **20 orientações**, mostrando fonte, data de verificação e aviso de limitação.

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
| 6 | Calculadora de energia: verifica o gasto com homeoffice e como economizar |
| 0 | Sair (pede nota de facilidade de 1 a 5; o CSV também é exportado ao sair) |


### Organização do projeto

```
citizen-assist-ai/
├── README.md
├── main.py               # menus e entrada do programa
├── orientacao.py         # classe Orientacao (registro + exibir())
├── base_conhecimento.py  # classe BaseConhecimento (JSON, busca com pontuação, CRUD, ordenação)
├── assistente.py         # classe Assistente (atendimento, histórico, indicadores, CSV)
├── lista_encadeada.py    # No e ListaEncadeada (estrutura implementada pela equipe, DSA)
├── energia.py            # cálculo, comparação, sensibilidade e recomendações de energia
├── data/
│   ├── base_conhecimento.json # Parâmetros para a resposta automatica
│   ├── energia_dados.json    # parâmetros com origem, tipo, unidade, período e referências
│   ├── historico.json

```


## 5. Regra de pontuação usada

Pergunta, palavras-chave e título são normalizados (minúsculas, sem acentos, sem pontuação).

| Regra | Pontos |
|-------|--------|
| Palavra-chave da orientação que aparece na pergunta | +3 (por palavra-chave) |
| Palavra da pergunta com 4 letras ou mais que aparece no título | +1 (cada palavra conta uma vez) |

| Melhor pontuação | Resultado |
|------------------|-----------|
| 6 ou mais | Confiança **ALTA** |
| 3 a 5 | Confiança **MÉDIA** |
| menos de 3 | "Não encontrei": sugere outras palavras e as categorias |

**Exemplo real:** "Como faço o cartão do SUS?" → a orientação 3 recebe +3 por `cartao do sus`, +3 por `sus` e +1 porque "cartao" está no título: **7 pontos, confiança ALTA**.

## 6. Atendimento, histórico e indicadores

- Cada **atendimento** é uma dúvida: começa na primeira pergunta e termina quando a pessoa responde `s` (ajudou) ou volta com `0`. Perguntas reescritas contam como **tentativas** do mesmo atendimento.
- Cada atendimento vai para `data/historico.json` com: data, origem (pergunta ou categoria), pergunta, id da orientação, se encontrou, se ajudou, tentativas e tempo em segundos.
- A **nota de facilidade (1 a 5)** é pedida ao sair e guardada no último atendimento da sessão.
- **Indicadores:** resposta encontrada (%), taxa de acerto (%), tempo médio para encontrar, tentativas por atendimento, facilidade de uso e lista de dúvidas sem solução.
- **CSV:** é gerado com `csv.DictWriter`.
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

## 9. Teste com usuários base

**Testes**: foram feitos 10 testes para testar o programa, esse histórico ainda está disponível para ser visto em histórico_teste, tendo sido realizado nos dias 12,13 e 14 de novembro com cada uma das respectivas pessoas.

**Dúvidas sem solução:** O sistema por não utilizar llm não é capaz de personalizar o suficiente seus testes, gerando falha nas respostas quando o usuário tenta digitiar algo específico, como "quanto eu economizaria se fizesse x coisa", além disso erros de digitação também são incapazes de serem entendidos, como trocar letra, podendo ser ruim para pessoas com dificuldade em escrita.

**Melhoria feita a partir do teste:** foi notado que uma pessoa tentou pesquisar sobre o gov, porém não digitou "gov.br", apenas gov, e não achou, com isso adicionamos gov à base.


## 10. Limitações

- Só responde o que está na base (20 orientações); fora disso diz "não encontrei".
- A busca compara palavras exatas, sem entender sinônimos, erros de digitação ou o contexto da frase. Por isso, "13 salario" só é entendido depois de a palavra-chave ser incluída (ver cenário P08).
- A regra de 8 ou mais dígitos pode bloquear perguntas legítimas com números longos (por exemplo, o número de uma lei).
- As informações públicas mudam (prazos, taxas, telefones): a data de verificação existe para lembrar disso.
- O alistamento militar tem prazo anual; a orientação informa que o de 2026 já terminou.

## 11. Vídeo técnico

Link: **[(https://youtu.be/6qi5W1Cfo7A)]**


## 12.a Energia (SERS)

**Público:** pessoas em início de carreira que trabalham ou estudam em casa e passam a ter parte da conta de luz como despesa própria.

**Necessidade energética:** manter o home office (notebook, monitor e iluminação, 8 h por dia, 22 dias por mês) gastando só a energia necessária, ou seja, reduzir a energia desperdiçada: computador e monitor ligados sem uso e lâmpada antiga de alto consumo.

**Pergunta respondida:** Para atender a mesma necessidade, vale mais manter o consumo atual, adotar medidas de eficiência (desligar o que está ocioso e trocar a lâmpada por LED) ou olhar para a geração solar fotovoltaica (fonte renovável)?

link do vídeo específico de SERS: **[(https://youtu.be/wD4TloDzDIo)]**

## 12.b Funcionalidades de energia

1. Cálculo de consumo e custo: energia em kWh de notebook, monitor e lâmpada, custo mensal e anual, com validação de todos os valores (faixas, tipos, nan/infinito, horas ociosas maiores que as horas de uso).

2. Comparação de 3 alternativas para a mesma necessidade e o mesmo período: consumo atual, eficiência e solar fotovoltaica.

3. Texto de apoio às respostas do assistente: as orientações da categoria Energia trazem números calculados por energia.py, e não texto escrito à mão. Tipos de análise: home_office, economia, solar, tarifa, conceito e carreira.

4. Relatório completo: premissas, 3 alternativas, interpretação, impacto ambiental, dicas e fontes, para a calculadora de energia do menu.

## 12.c Dados, origem, unidades, período e premissas

Os valores ficam em `data/energia_dados.json` e podem ser trocados pelo usuário. Período de referência: **12/11/2026**.

| Parâmetro | Valor | Unidade | Tipo | Origem / justificativa |
|-----------|-------|---------|------|------------------------|
| `potencia_notebook_w` | 65 | W | **estimado** | Potência típica de notebook em uso; substituir pela potência real do carregador/etiqueta |
| `potencia_monitor_w` | 30 | W | **estimado** | Monitor de escritório típico; substituir pelo valor do aparelho |
| `potencia_lampada_w` | 40 | W | **estimado** | Lâmpada atual de alto consumo (hipótese) |
| `potencia_led_w` | 9 | W | **estimado** | LED escolhida para dar iluminação equivalente; conferir lúmens na etiqueta (Inmetro/PBE) |
| `horas_dia` | 8 | h/dia | **premissa** | Jornada de trabalho |
| `dias_mes` | 22 | dias/mês | **premissa** | Dias úteis do mês |
| `horas_ociosas_dia` | 1 | h/dia | **premissa** | Tempo em que notebook e monitor ficam ligados sem uso (pausas, almoço) |
| `tarifa_kwh` | 1,00 | R$/kWh | **ilustrativa** | Valor editável; o usuário deve usar o kWh **da própria conta de luz** (varia com distribuidora, tributos e bandeira) |
| `solar_kwh_por_kwp_mes` | 120 | kWh/mês por kWp | **premissa aproximada** | Produção média de 1 kWp instalado; varia com cidade, orientação, sombra e clima |
| `solar_referencia_kwp` | 2,0 | kWp | **referência de mercado** | Sistema residencial de referência |
| `solar_preco_medio_rpw` | 3,62 | R$/Wp (jun/2026) | **referência de mercado** | Preço médio de sistema residencial de 2 kWp, segundo a Greener (jun/2026, p. 46) |
| `preco_led_reais` | 15,00 | R$ | **hipótese didática** | Preço de uma lâmpada LED; editável |

**Faixas aceitas pela validação:** computador 1 a 1.500 W; monitor 0 a 500 W; lâmpada 1 a 200 W; LED 1 a 60 W; horas por dia 1 a 16; dias por mês 1 a 31; horas ociosas 0 a 16 (e nunca mais que as horas por dia); tarifa R$ 0,10 a R$ 5,00; preço da LED R$ 0 a R$ 200.

## 12.d Cálculos feitos

- Energia (kWh) = potência (W) ÷ 1.000 × horas
- horas/mês = horas por dia × dias por mês
- horas ativas/mês = (horas por dia − horas ociosas) × dias por mês
- consumo atual = (notebook + monitor + lâmpada) × horas/mês ÷ 1.000
- Consumo eficiente = (notebook + monitor) × horas ativas/mês ÷ 1.000 + LED × horas/mês ÷ 1.000
- economia (kWh) = consumo atual − consumo eficiente; custo = kWh × tarifa; economia anual = economia mensal × 12
- retorno da LED (meses) = preço da LED ÷ economia mensal da iluminação
- Solar: kWp teórico = consumo atual ÷ 120; geração de referência = kWp de referência × 120; investimento de referência = kWp × 1.000 × preço por Wp

## 12.e Justificativas pelo impacto ambiental

- **Reduzir o consumo** evita demanda de geração e de expansão da rede; é o impacto positivo mais direto e imediato deste projeto, é feito pensando em trocar lampada pra led por exemplo ou desligar monitores ociosos
- **Solar fotovoltaica** gera energia renovável durante a operação.

## 12.f Referências 

| # | Referência | Data | Usada para | Link |
|---|------------|------|------------|------|
| 1 | EPE. *PDE 2036 - Caderno de Eficiência Energética e Recursos Energéticos Distribuídos*, p. 23 | 04/11/2026 | Papel da eficiência energética e da geração distribuída | https://epe.gov.br/sites-pt/publicacoes-dados-abertos/publicacoes/PublicacoesArquivos/publicacao-982/topico-851/PDE%202036_Caderno%20Efici%C3%AAncia%20e%20RED_v1_2026-11-04.pdf |
| 2 | Greener. *Estudo Estratégico - Soluções Energéticas Distribuídas*, 1º semestre de 2026, p. 46 | jun/2026 | Preço médio do sistema residencial (R$ 3,62/Wp) | https://greenerstorage.blob.core.windows.net/public/estudos/SED_2S_2026.pdf |
| 3 | ANEEL. *Micro e Minigeração Distribuída* | 09/06/2026 | Regras de geração distribuída e compensação | https://www.gov.br/aneel/pt-br/assuntos/geracao-distribuida |
| 4 | Inmetro. *Eficiência Energética: dicas para reduzir o consumo e economizar na conta de luz* | 29/10/2026 | Dicas de eficiência | https://www.gov.br/inmetro/pt-br/centrais-de-conteudo/noticias/2026/dia-mundial-da-eficiencia-energetica-inmetro-da-dicas-para-reduzir-o-consumo-e-economizar-na-conta-de-luz |
| 5 | Inmetro. *Lâmpadas - tabelas de eficiência energética e Sistema PBE* | 13/07/2026 | Comparar lâmpadas pela etiqueta | https://www.gov.br/inmetro/pt-br/assuntos/regulamentacao/avaliacao-da-conformidade/programa-brasileiro-de-etiquetagem/tabelas-de-eficiencia-energetica/lampadas |
| 6 | IRENA e IEA-PVPS. *End-of-Life Management: Solar Photovoltaic Panels*, p. 11 e 47-57 | jun/2016 | Impacto do fim de vida dos módulos | https://www.irena.org/-/media/Files/IRENA/Agency/Publication/2016/IRENA_IEAPVPS_End-of-Life_Solar_PV_Panels_2016.pdf |
