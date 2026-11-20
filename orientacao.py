"""
 - guarda os dados de uma orientação e a exibe na tela
"""

from datetime import datetime

AVISO = "este assistente NÃO é um canal oficial."
PUBLICO_PADRAO = "Jovens no primeiro emprego"
MINIMO_PALAVRAS_CHAVE = 3
ANALISES_VALIDAS = ( "chuveiro","solar","tarifa","conceito","home_office","carreira")


class Orientacao:
    """Uma orientação ao cidadão (serviço, documento ou direito)."""

    def __init__(self, id, categoria, titulo, palavras_chave, resposta,
                 documentos, onde, fonte, verificado_em,
                 publico_alvo=PUBLICO_PADRAO, analise=None):
        self.analise = analise
        self.id = id
        self.categoria = categoria
        self.titulo = titulo
        self.palavras_chave = palavras_chave
        self.resposta = resposta
        self.documentos = documentos
        self.onde = onde
        self.fonte = fonte
        self.verificado_em = verificado_em
        self.publico_alvo = publico_alvo

    # ------------------------------------------------------------------
    # Validação
    # ------------------------------------------------------------------
    @staticmethod
    def validar(dados):
        """Devolve uma lista de mensagens de erro (vazia = dados válidos)."""
        if not isinstance(dados, dict):
            return ["o registro não é um dicionário"]

        erros = []

        identificador = dados.get("id")
        if isinstance(identificador, bool) or not isinstance(identificador, int):
            erros.append("id deve ser um número inteiro")
        elif identificador <= 0:
            erros.append("id deve ser maior que zero")

        for campo in ("categoria", "titulo", "resposta", "onde", "fonte",
                      "verificado_em"):
            valor = dados.get(campo)
            if not isinstance(valor, str) or not valor.strip():
                erros.append(f"campo obrigatório vazio ou ausente: {campo}")

        if "publico_alvo" in dados:
            valor = dados["publico_alvo"]
            if not isinstance(valor, str) or not valor.strip():
                erros.append("campo obrigatório vazio: publico_alvo")

        palavras = dados.get("palavras_chave")
        if (not isinstance(palavras, list)
                or not all(isinstance(p, str) and p.strip() for p in palavras)):
            erros.append("palavras_chave deve ser uma lista de textos não vazios")
        elif len(palavras) < MINIMO_PALAVRAS_CHAVE:
            erros.append(f"informe ao menos {MINIMO_PALAVRAS_CHAVE} palavras-chave")

        documentos = dados.get("documentos")
        if (not isinstance(documentos, list)
                or not all(isinstance(d, str) and d.strip() for d in documentos)):
            erros.append("documentos deve ser uma lista de textos (pode ser vazia)")

        fonte = dados.get("fonte")
        if isinstance(fonte, str) and fonte.strip() \
                and not fonte.strip().lower().startswith(("http://", "https://")):
            erros.append("fonte deve ser um endereço que começa com http:// ou https://")

        data = dados.get("verificado_em")
        if isinstance(data, str) and data.strip():
            try:
                datetime.strptime(data.strip(), "%Y-%m-%d")
            except ValueError:
                erros.append("verificado_em deve estar no formato AAAA-MM-DD")

        if dados.get("analise") is not None \
                and dados["analise"] not in ANALISES_VALIDAS:
            erros.append("analise deve ser uma de: " + ", ".join(ANALISES_VALIDAS))

        return erros

    # ------------------------------------------------------------------
    # Conversões
    # ------------------------------------------------------------------
    @classmethod
    def de_dicionario(cls, dados):
        """Cria uma Orientacao a partir de um dicionário JÁ validado."""
        return cls(
            id=dados["id"],
            categoria=dados["categoria"].strip(),
            titulo=dados["titulo"].strip(),
            palavras_chave=[p.strip() for p in dados["palavras_chave"]],
            resposta=dados["resposta"].strip(),
            documentos=[d.strip() for d in dados["documentos"]],
            onde=dados["onde"].strip(),
            fonte=dados["fonte"].strip(),
            verificado_em=dados["verificado_em"].strip(),
            publico_alvo=dados.get("publico_alvo", PUBLICO_PADRAO).strip(),
            analise=dados.get("analise"),
        )

    def para_dicionario(self):
        dados = {
            "id": self.id,
            "categoria": self.categoria,
            "titulo": self.titulo,
            "publico_alvo": self.publico_alvo,
            "palavras_chave": list(self.palavras_chave),
            "resposta": self.resposta,
            "documentos": list(self.documentos),
            "onde": self.onde,
            "fonte": self.fonte,
            "verificado_em": self.verificado_em,
        }
        if self.analise:
            dados["analise"] = self.analise
        return dados

    # ------------------------------------------------------------------
    # Exibição
    # ------------------------------------------------------------------
    def exibir(self, complemento=None):
        """Mostra a orientação completa (com fonte, data e aviso).

        complemento é uma lista opcional de linhas exibida antes do público e da fonte.
        """
        print(f"\n>> {self.titulo}  [{self.categoria}]")
        print(self.resposta)
        if self.documentos:
            print("Documentos necessários:")
            for documento in self.documentos:
                print(f"  - {documento}")
        else:
            print("Documentos necessários: nenhum informado")
        print(f"Onde: {self.onde}")
        if complemento:
            for linha in complemento:
                print(linha)
            print()
        print(f"Público: {self.publico_alvo}")
        print(f"Fonte: {self.fonte} (verificado em {self.verificado_em})")
        print(f"Aviso: {AVISO}")

    def resumo(self):
        """Uma linha, usada em listagens."""
        return f"[{self.id:>3}] {self.categoria:<11} {self.titulo}"

    def __repr__(self):
        return f"Orientacao(id={self.id}, titulo={self.titulo!r})"
