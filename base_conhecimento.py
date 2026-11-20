"""BaseConhecimento: o conjunto de todas as orientações.

    lê o JSON, lista categorias e busca a melhor orientação (pontuação).
     guarda os registros em uma ListaEncadeada própria e oferece CRUD,
     pesquisa por atributo e ordenação (Merge Sort).
"""

import json
import os
from orientacao import Orientacao
from lista_encadeada import ListaEncadeada


# ----------------------------------------------------------------------
# Normalização de texto (sem acentos, sem pontuação, minúsculas)
# ----------------------------------------------------------------------
ACENTOS = {"á": "a", "à": "a", "ã": "a", "â": "a", "ä": "a",
           "é": "e", "è": "e", "ê": "e",
           "í": "i", "ì": "i",
           "ó": "o", "ò": "o", "õ": "o", "ô": "o",
           "ú": "u", "ù": "u", "ü": "u",
           "ç": "c"}
SINAIS = "?!.,;:()-/\"'"

LIMITE_ALTA = 6      # pontuação mínima para confiança ALTA
LIMITE_MEDIA = 3     # pontuação mínima para confiança MÉDIA
PONTOS_PALAVRA_CHAVE = 3
PONTOS_PALAVRA_TITULO = 1
TAMANHO_MIN_PALAVRA_TITULO = 4


def normalizar(texto):
    """Minúsculas, sem acentos, sem pontuação; devolve com espaço nas pontas.

    O espaço nas pontas permite procurar palavras inteiras: " sus " não
    aparece dentro de "sustentavel".
    """
    texto = texto.lower().strip()
    for letra, troca in ACENTOS.items():
        texto = texto.replace(letra, troca)
    for sinal in SINAIS:
        texto = texto.replace(sinal, " ")
    return " " + " ".join(texto.split()) + " "


def contem(texto, trecho):
    """Busca de substring por comparação direta: O(len(texto) * len(trecho))."""
    tam = len(trecho)
    for inicio in range(len(texto) - tam + 1):
        if texto[inicio:inicio + tam] == trecho:
            return True
    return False


def merge_sort_lista(itens, chave):
    """Merge Sort em lista comum (usado para ranquear resultados). O(n log n)."""
    if len(itens) <= 1:
        return list(itens)
    meio = len(itens) // 2
    esquerda = merge_sort_lista(itens[:meio], chave)
    direita = merge_sort_lista(itens[meio:], chave)
    resultado = []
    i = j = 0
    while i < len(esquerda) and j < len(direita):
        if chave(esquerda[i]) <= chave(direita[j]):
            resultado.append(esquerda[i])
            i += 1
        else:
            resultado.append(direita[j])
            j += 1
    resultado.extend(esquerda[i:])
    resultado.extend(direita[j:])
    return resultado


CRITERIOS_ORDENACAO = {
    "id": lambda o: o.id,
    "titulo": lambda o: normalizar(o.titulo),
    "categoria": lambda o: (normalizar(o.categoria), normalizar(o.titulo)),
}


class BaseConhecimento:
    def __init__(self, caminho):
        self.caminho = caminho
        self.orientacoes = ListaEncadeada()   # lista encadeada de Orientacao
        self.avisos = []                      # problemas achados ao carregar

    # ------------------------------------------------------------------
    # Arquivo JSON
    # ------------------------------------------------------------------
    def carregar(self):
        """Lê o JSON e cria os objetos Orientacao. Nunca derruba o programa.

        Devolve True se o arquivo foi lido; False se estava ausente,
        corrompido ou com formato inesperado (a base fica vazia).
        """
        self.orientacoes = ListaEncadeada()
        self.avisos = []
        try:
            with open(self.caminho, "r", encoding="utf-8") as arquivo:
                bruto = json.load(arquivo)
        except FileNotFoundError:
            self.avisos.append(f"Arquivo da base não encontrado: {self.caminho}")
            return False
        except json.JSONDecodeError as erro:
            self.avisos.append(f"Arquivo da base corrompido (JSON inválido): {erro}")
            return False
        except (OSError, UnicodeDecodeError) as erro:
            self.avisos.append(f"Não foi possível ler a base: {erro}")
            return False

        if not isinstance(bruto, list):
            self.avisos.append("A base deve ser uma lista de orientações.")
            return False

        for posicao, registro in enumerate(bruto, start=1):
            erros = Orientacao.validar(registro)
            if erros:
                self.avisos.append(
                    f"Registro {posicao} ignorado: " + "; ".join(erros))
                continue
            if self.orientacoes.buscar_por_id(registro["id"]) is not None:
                self.avisos.append(
                    f"Registro {posicao} ignorado: id {registro['id']} duplicado")
                continue
            self.orientacoes.inserir_fim(Orientacao.de_dicionario(registro))
        return True

    def salvar(self):
        """Grava a lista no JSON (arquivo temporário + troca atômica)."""
        dados = [o.para_dicionario() for o in self.orientacoes]
        temporario = self.caminho + ".tmp"
        try:
            pasta = os.path.dirname(self.caminho)
            if pasta:
                os.makedirs(pasta, exist_ok=True)
            with open(temporario, "w", encoding="utf-8") as arquivo:
                json.dump(dados, arquivo, ensure_ascii=False, indent=2)
            os.replace(temporario, self.caminho)
            return True
        except OSError as erro:
            self.avisos.append(f"Não foi possível salvar a base: {erro}")
            return False

    # ------------------------------------------------------------------
    # busca com pontuação
    # ------------------------------------------------------------------
    def categorias(self):
        """Categorias sem repetição, em ordem alfabética."""
        nomes = []
        for orientacao in self.orientacoes:
            if orientacao.categoria not in nomes:
                nomes.append(orientacao.categoria)
        return merge_sort_lista(nomes, normalizar)

    def por_categoria(self, categoria):
        return [o for o in self.orientacoes if o.categoria == categoria]

    def pontuar(self, pergunta, orientacao):
        """Pontos de uma orientação para a pergunta.

        +3 por palavra-chave da orientação que aparece na pergunta;
        +1 por palavra da pergunta (4 letras ou mais) que aparece no título.
        """
        pergunta_norm = normalizar(pergunta)
        titulo_norm = normalizar(orientacao.titulo)
        pontos = 0

        for palavra_chave in orientacao.palavras_chave:
            if contem(pergunta_norm, normalizar(palavra_chave)):
                pontos += PONTOS_PALAVRA_CHAVE

        ja_contadas = []
        for palavra in pergunta_norm.split():
            if len(palavra) >= TAMANHO_MIN_PALAVRA_TITULO \
                    and palavra not in ja_contadas:
                ja_contadas.append(palavra)
                if contem(titulo_norm, " " + palavra + " "):
                    pontos += PONTOS_PALAVRA_TITULO
        return pontos

    def buscar(self, pergunta):
        """Lista de tuplas (pontos, orientacao), da maior para a menor.

        Só entram orientações com pelo menos 1 ponto. Empates são
        desempatados pelo menor id.
        """
        resultados = []
        for orientacao in self.orientacoes:
            pontos = self.pontuar(pergunta, orientacao)
            if pontos > 0:
                resultados.append((pontos, orientacao))
        return merge_sort_lista(resultados, lambda t: (-t[0], t[1].id))

    @staticmethod
    def confianca(pontos):
        """'ALTA', 'MÉDIA' ou None (não encontrou) conforme os pontos."""
        if pontos >= LIMITE_ALTA:
            return "ALTA"
        if pontos >= LIMITE_MEDIA:
            return "MÉDIA"
        return None

    # ------------------------------------------------------------------
    #  CRUD, pesquisa e ordenação
    # ------------------------------------------------------------------
    def _gravar(self):
        return "" if self.salvar() else " (atenção: não foi possível gravar o arquivo)"

    def cadastrar(self, dados):
        erros = Orientacao.validar(dados)
        if erros:
            return False, "Dados inválidos: " + "; ".join(erros)
        if self.orientacoes.buscar_por_id(dados["id"]) is not None:
            return False, f"Já existe um registro com o id {dados['id']}."
        self.orientacoes.inserir_fim(Orientacao.de_dicionario(dados))
        return True, f"Registro {dados['id']} cadastrado." + self._gravar()

    def consultar(self, identificador):
        return self.orientacoes.buscar_por_id(identificador)

    def listar(self):
        return self.orientacoes.para_lista()

    def atualizar(self, identificador, novos_campos):
        atual = self.orientacoes.buscar_por_id(identificador)
        if atual is None:
            return False, f"Registro {identificador} não encontrado."
        dados = atual.para_dicionario()
        dados.update(novos_campos)
        dados["id"] = identificador            # o id nunca muda
        erros = Orientacao.validar(dados)
        if erros:
            return False, "Dados inválidos: " + "; ".join(erros)
        self.orientacoes.atualizar(identificador, Orientacao.de_dicionario(dados))
        return True, f"Registro {identificador} atualizado." + self._gravar()

    def excluir(self, identificador):
        removido = self.orientacoes.remover_por_id(identificador)
        if removido is None:
            return False, f"Registro {identificador} não encontrado."
        return True, f"Registro {identificador} excluído." + self._gravar()

    def pesquisar(self, atributo, termo):
        """Pesquisa linear por 'titulo', 'categoria' ou 'palavra_chave'."""
        termo_norm = normalizar(termo).strip()
        if not termo_norm:
            return []
        encontrados = []
        for orientacao in self.orientacoes:
            if atributo == "titulo":
                textos = [normalizar(orientacao.titulo)]
            elif atributo == "categoria":
                textos = [normalizar(orientacao.categoria)]
            elif atributo == "palavra_chave":
                textos = [normalizar(p) for p in orientacao.palavras_chave]
            else:
                return []
            for texto in textos:
                if contem(texto, termo_norm):
                    encontrados.append(orientacao)
                    break
        return encontrados

    def ordenar(self, criterio):
        """Ordena a lista encadeada por 'id', 'titulo' ou 'categoria'."""
        if criterio not in CRITERIOS_ORDENACAO:
            return False, "Critério de ordenação inválido."
        self.orientacoes.ordenar(CRITERIOS_ORDENACAO[criterio])
        return True, f"Registros ordenados por {criterio}." + self._gravar()
