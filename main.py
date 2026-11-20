import os
from datetime import date

from base_conhecimento import BaseConhecimento
from energia import AnaliseEnergia
from assistente import (
    Assistente,
    EntradaEncerrada,
    OperacaoCancelada,
    ler_opcao,
    ler_sn,
    ler_texto,
)

PASTA = os.path.dirname(os.path.abspath(__file__))
PASTA_DADOS = os.environ.get("CITIZEN_ASSIST_DATA") or PASTA

CAMPOS_ATUALIZAVEIS = {
    1: ("titulo", "Título"),
    2: ("categoria", "Categoria"),
    3: ("publico_alvo", "Público-alvo"),
    4: ("resposta", "Descrição/resposta"),
    5: ("documentos", "Documentos (separe por ;)"),
    6: ("onde", "Canal ou local de atendimento"),
    7: ("fonte", "Fonte (http...)"),
    8: ("verificado_em", "Data de verificação (AAAA-MM-DD)"),
    9: ("palavras_chave", "Palavras-chave (separe por ;)"),
}


def dividir_lista(texto):
    """Converte texto separado por ponto e vírgula em lista."""
    itens = []
    for parte in texto.replace(",", ";").split(";"):
        parte = parte.strip()
        if parte:
            itens.append(parte)
    return itens


def ler_id(prompt, cancelavel=False):
    """Lê um identificador inteiro positivo."""
    while True:
        texto = ler_texto(prompt, permitir_cancelar=cancelavel)
        try:
            valor = int(texto)
        except ValueError:
            print("Identificador inválido: digite um número inteiro.")
            continue

        if valor <= 0:
            print("Identificador deve ser maior que zero.")
            continue

        return valor


def mostrar_resumos(orientacoes):
    """Exibe um resumo dos registros recebidos."""
    if not orientacoes:
        print("Nenhum registro encontrado.")
        return

    print(f"{'ID':>5} {'Categoria':<11} Título")
    for orientacao in orientacoes:
        print(orientacao.resumo())

    print(f"({len(orientacoes)} registro(s))")


def cadastrar(base):
    """Cadastra uma nova orientação."""
    print("\n=== Cadastrar orientação ===")

    try:
        while True:
            identificador = ler_id(
                "Identificador: ", cancelavel=True
            )
            if base.consultar(identificador) is not None:
                print("Esse identificador já existe.")
                continue
            break

        dados = {"id": identificador}
        dados["titulo"] = ler_texto("Título: ", permitir_cancelar=True)
        dados["categoria"] = ler_texto("Categoria: ", permitir_cancelar=True)
        dados["publico_alvo"] = ler_texto(
            "Público-alvo: ", permitir_cancelar=True
        )
        dados["resposta"] = ler_texto(
            "Descrição/resposta: ", permitir_cancelar=True
        )
        dados["documentos"] = dividir_lista(
            ler_texto(
                "Documentos (separe por ;): ",
                obrigatorio=False,
                permitir_cancelar=True,
            )
        )
        dados["onde"] = ler_texto(
            "Canal ou local de atendimento: ",
            permitir_cancelar=True,
        )
        dados["fonte"] = ler_texto(
            "Fonte oficial: ", permitir_cancelar=True
        )

        hoje = date.today().isoformat()
        dados["verificado_em"] = ler_texto(
            f"Verificado em (Enter = {hoje}): ",
            obrigatorio=False,
            permitir_cancelar=True,
        ) or hoje

        dados["palavras_chave"] = dividir_lista(
            ler_texto(
                "Palavras-chave (separe por ;): ",
                permitir_cancelar=True,
            )
        )

    except OperacaoCancelada:
        print("Cadastro cancelado.")
        return

    ok, mensagem = base.cadastrar(dados)
    print(("OK: " if ok else "Erro: ") + mensagem)


def consultar(base):
    """Consulta uma orientação pelo identificador."""
    identificador = ler_id("\nIdentificador: ")
    orientacao = base.consultar(identificador)

    if orientacao is None:
        print("Registro não encontrado.")
    else:
        orientacao.exibir()


def listar(base):
    """Lista todas as orientações."""
    print("\n=== Registros cadastrados ===")
    mostrar_resumos(base.listar())


def atualizar(base):
    """Atualiza um campo de uma orientação."""
    identificador = ler_id("\nIdentificador: ")
    orientacao = base.consultar(identificador)

    if orientacao is None:
        print("Registro não encontrado.")
        return

    orientacao.exibir()

    print("\nQual campo deseja alterar?")
    for numero, (_, rotulo) in CAMPOS_ATUALIZAVEIS.items():
        print(f"  {numero}. {rotulo}")
    print("  0. Voltar")

    escolha = ler_opcao("Escolha: ", 0, len(CAMPOS_ATUALIZAVEIS))
    if escolha == 0:
        return

    campo, rotulo = CAMPOS_ATUALIZAVEIS[escolha]

    if campo in ("documentos", "palavras_chave"):
        valor = dividir_lista(ler_texto(f"Novo valor de {rotulo}: "))
    else:
        valor = ler_texto(f"Novo valor de {rotulo}: ")

    ok, mensagem = base.atualizar(identificador, {campo: valor})
    print(("OK: " if ok else "Erro: ") + mensagem)


def excluir(base):
    """Exclui uma orientação após confirmação."""
    identificador = ler_id("\nIdentificador: ")
    orientacao = base.consultar(identificador)

    if orientacao is None:
        print("Registro não encontrado.")
        return

    print(orientacao.resumo())

    if not ler_sn("Confirma a exclusão? (s/n): "):
        print("Exclusão cancelada.")
        return

    ok, mensagem = base.excluir(identificador)
    print(("OK: " if ok else "Erro: ") + mensagem)


def pesquisar(base):
    """Pesquisa por título, categoria ou palavra-chave."""
    print("\nPesquisar por:")
    print("  1. Título")
    print("  2. Categoria")
    print("  3. Palavra-chave")
    print("  0. Voltar")

    escolha = ler_opcao("Escolha: ", 0, 3)
    if escolha == 0:
        return

    atributo = {
        1: "titulo",
        2: "categoria",
        3: "palavra_chave",
    }[escolha]

    termo = ler_texto("Termo da pesquisa: ")
    mostrar_resumos(base.pesquisar(atributo, termo))


def ordenar(base):
    """Ordena os registros por identificador, título ou categoria."""
    print("\nOrdenar por:")
    print("  1. Identificador")
    print("  2. Título")
    print("  3. Categoria")
    print("  0. Voltar")

    escolha = ler_opcao("Escolha: ", 0, 3)
    if escolha == 0:
        return

    criterio = {
        1: "id",
        2: "titulo",
        3: "categoria",
    }[escolha]

    ok, mensagem = base.ordenar(criterio)
    print(("OK: " if ok else "Erro: ") + mensagem)

    if ok:
        mostrar_resumos(base.listar())


def menu_gestao(base):
    """Exibe o menu de gerenciamento das orientações."""
    acoes = {
        1: cadastrar,
        2: consultar,
        3: listar,
        4: atualizar,
        5: excluir,
        6: pesquisar,
        7: ordenar,
    }

    while True:
        print("\n=== Gestão das orientações ===")
        print("  1. Cadastrar")
        print("  2. Consultar")
        print("  3. Listar")
        print("  4. Atualizar")
        print("  5. Excluir")
        print("  6. Pesquisar")
        print("  7. Ordenar")
        print("  0. Voltar")

        escolha = ler_opcao("Escolha: ", 0, 7)
        if escolha == 0:
            return

        acoes[escolha](base)


def menu_principal(assistente):
    """Exibe o menu principal do Citizen Assist AI."""
    while True:
        print(f"\n=== {assistente.nome} ===")
        print("  1. Fazer uma pergunta")
        print("  2. Navegar por categorias")
        print("  3. Ver indicadores")
        print("  4. Exportar atendimentos para CSV")
        print("  5. Gerenciar orientações")
        print("  6. Ajuda para Economizar")
        print("  0. Sair")

        escolha = ler_opcao("Escolha: ", 0, 6)

        if escolha == 0:
            return
        elif escolha == 1:
            assistente.perguntar()
        elif escolha == 2:
            assistente.navegar()
        elif escolha == 3:
            assistente.exibir_indicadores()
        elif escolha == 4:
            if assistente.exportar_csv():
                print(f"CSV exportado em: {assistente.caminho_csv}")
        elif escolha == 5:
            menu_gestao(assistente.base)
        elif escolha == 6:
            assistente.calculadora_energia()


def main():
    """Inicializa a base, a análise energética e o assistente."""
    caminho_base = os.path.join(
        PASTA_DADOS, "base_conhecimento.json"
    )
    caminho_energia = os.path.join(
        PASTA_DADOS, "energia_dados.json"
    )

    base = BaseConhecimento("data/base_conhecimento.json")
    base.carregar()

    energia = AnaliseEnergia(caminho_energia)
    energia.carregar()

    assistente = Assistente(
        "Citizen Assist AI",
        base,
        energia=energia,
    )

    for aviso in base.avisos + energia.avisos + assistente.avisos:
        print("Aviso:", aviso)

    try:
        menu_principal(assistente)
    except EntradaEncerrada:
        print("\nEntrada encerrada. Até logo!")


if __name__ == "__main__":
    main()
