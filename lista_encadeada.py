class No:
    """Nó da lista: guarda um dado e a referência para o próximo nó."""
    def __init__(self, dado):
        self.dado = dado
        self.proximo = None


class ListaEncadeada:
    def __init__(self):
        self.inicio = None   # primeiro nó
        self.fim = None      # último nó (permite inserção O(1) no fim)
        self.tamanho = 0

    # ------------------------------------------------------------------
    # Consultas simples
    # ------------------------------------------------------------------
    def esta_vazia(self):
        return self.inicio is None

    def __len__(self):
        return self.tamanho

    # ------------------------------------------------------------------
    # Inserção
    # ------------------------------------------------------------------
    def inserir_fim(self, dado):
        """Insere no final. Custo O(1)"""
        novo = No(dado)
        if self.inicio is None:
            self.inicio = novo
            self.fim = novo
        else:
            self.fim.proximo = novo
            self.fim = novo
        self.tamanho += 1

    def inserir_inicio(self, dado):
        """Insere no começo. Custo O(1)."""
        novo = No(dado)
        novo.proximo = self.inicio
        self.inicio = novo
        if self.fim is None:
            self.fim = novo
        self.tamanho += 1

    # ------------------------------------------------------------------
    # Percurso
    # ------------------------------------------------------------------
    def __iter__(self):
        """Percorre os nós do início ao fim devolvendo cada dado. O(n)."""
        atual = self.inicio
        while atual is not None:
            yield atual.dado
            atual = atual.proximo

    def para_lista(self):
        """Cópia dos dados em ordem (usada só para exibição/gravação). O(n)."""
        itens = []
        atual = self.inicio
        while atual is not None:
            itens.append(atual.dado)
            atual = atual.proximo
        return itens

    # ------------------------------------------------------------------
    # Busca linear por identificador
    # ------------------------------------------------------------------
    def _no_por_id(self, identificador):
        atual = self.inicio
        while atual is not None:
            if atual.dado.id == identificador:
                return atual
            atual = atual.proximo
        return None

    def buscar_por_id(self, identificador):
        """Busca linear: pior caso O(n), melhor caso O(1)."""
        no = self._no_por_id(identificador)
        return no.dado if no is not None else None

    # ------------------------------------------------------------------
    # Atualização
    # ------------------------------------------------------------------
    def atualizar(self, identificador, novo_dado):
        """Troca o dado do nó com o id informado. O(n) (a busca domina)."""
        no = self._no_por_id(identificador)
        if no is None:
            return False
        no.dado = novo_dado
        return True

    # ------------------------------------------------------------------
    # Remoção
    # ------------------------------------------------------------------
    def remover_por_id(self, identificador):
        """Remove o nó com o id informado e devolve o dado removido (ou None).

        Trata os três casos: remover o primeiro, um do meio e o último O(n).
        """
        anterior = None
        atual = self.inicio
        while atual is not None:
            if atual.dado.id == identificador:
                if anterior is None:          # removendo o primeiro nó
                    self.inicio = atual.proximo
                else:                         # removendo do meio ou do fim
                    anterior.proximo = atual.proximo
                if atual is self.fim:         # removendo o último nó
                    self.fim = anterior
                atual.proximo = None
                self.tamanho -= 1
                return atual.dado
            anterior = atual
            atual = atual.proximo
        return None

    # ------------------------------------------------------------------
    # Ordenação: Merge Sort sobre os próprios nós 
    # ------------------------------------------------------------------
    def ordenar(self, chave):
        """Ordena em ordem crescente pela função chave(dado).

        Merge Sort em lista encadeada: custa O(n log n) em tempo; usa O(log n) de pilha de recursão e não cria nós novos.
        """
        self.inicio = self._merge_sort(self.inicio, chave)
        atual = self.inicio
        while atual is not None and atual.proximo is not None:
            atual = atual.proximo
        self.fim = atual

    def _merge_sort(self, no, chave):
        if no is None or no.proximo is None:
            return no
        ultimo_da_primeira = self._fim_da_primeira_metade(no)
        segunda = ultimo_da_primeira.proximo
        ultimo_da_primeira.proximo = None            # corta a lista em duas
        esquerda = self._merge_sort(no, chave)
        direita = self._merge_sort(segunda, chave)
        return self._intercalar(esquerda, direita, chave)

    @staticmethod
    def _fim_da_primeira_metade(no):
        lento = no
        rapido = no.proximo
        while rapido is not None and rapido.proximo is not None:
            lento = lento.proximo
            rapido = rapido.proximo.proximo
        return lento

    @staticmethod
    def _intercalar(a, b, chave):
        cabeca = No(None)          # nó auxiliar (sentinela)
        cauda = cabeca
        while a is not None and b is not None:
            if chave(a.dado) <= chave(b.dado):   # <= mantém a estabilidade
                cauda.proximo = a
                a = a.proximo
            else:
                cauda.proximo = b
                b = b.proximo
            cauda = cauda.proximo
        cauda.proximo = a if a is not None else b
        return cabeca.proximo
