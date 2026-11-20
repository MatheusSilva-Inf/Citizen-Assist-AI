"""Faz o atendimento (pergunta livre e navegação por categorias), bloqueia dados
pessoais, guarda o histórico em JSON, calcula indicadores e exporta CSV.
reúne as funções de leitura de teclado que nunca encerram o programa por entrada inválida.
"""

import csv
import json
import os
import time
from datetime import datetime
import math

from base_conhecimento import BaseConhecimento
from energia import num

LIMITE_DIGITOS_PESSOAIS = 8
ID_ORIENTACAO_CALCULADORA = 13
CAMPOS_CSV = [
    "data", "origem", "pergunta", "id_orientacao", "encontrou",
    "ajudou", "tentativas", "tempo_segundos", "nota_facilidade"
]


class EntradaEncerrada(Exception):
    """O teclado foi fechado (Ctrl+D / fim do arquivo de entrada)."""


class OperacaoCancelada(Exception):
    """O usuário digitou 'cancelar' durante um cadastro."""


def _entrada(prompt):
    try:
        return input(prompt)
    except EOFError:
        raise EntradaEncerrada()


def ler_texto(prompt, obrigatorio=True, permitir_cancelar=False):
    """Lê um texto; repete enquanto estiver vazio (se obrigatório)."""
    while True:
        texto = _entrada(prompt).strip()
        if permitir_cancelar and texto.lower() == "cancelar":
            raise OperacaoCancelada()
        if texto or not obrigatorio:
            return texto
        print("Atenção: este campo é obrigatório e não pode ficar vazio.")


def ler_opcao(prompt, minimo, maximo):
    """Lê um número inteiro entre minimo e maximo (inclusive)."""
    while True:
        texto = _entrada(prompt).strip()
        try:
            valor = int(texto)
        except ValueError:
            print(f"Opção inválida. Digite um número de {minimo} a {maximo}.")
            continue
        if minimo <= valor <= maximo:
            return valor
        print(f"Opção inválida. Digite um número de {minimo} a {maximo}.")


def ler_numero(prompt, minimo, maximo, padrao, inteiro=False):
    """Lê um número entre minimo e maximo. Enter devolve o valor padrão.

    Aceita vírgula decimal e permite cancelar a operação.
    """
    while True:
        texto = _entrada(prompt).strip().lower()
        if texto == "cancelar":
            raise OperacaoCancelada()
        if texto == "":
            return padrao
        try:
            valor = float(texto.replace(",", "."))
        except ValueError:
            print(
                f"Valor inválido. Digite um número entre "
                f"{num(minimo, 2)} e {num(maximo, 2)}."
            )
            continue

        if not math.isfinite(valor):
            print("Valor inválido.")
            continue
        if inteiro and valor != int(valor):
            print("Digite um número inteiro.")
            continue
        if not minimo <= valor <= maximo:
            print("Valor fora do intervalo permitido.")
            continue
        return int(valor) if inteiro else valor


def ler_sn(prompt):
    """Lê s/n. Devolve True para sim e False para não."""
    while True:
        texto = _entrada(prompt).strip().lower()
        if texto in ("s", "sim"):
            return True
        if texto in ("n", "nao", "não"):
            return False
        print("Resposta inválida. Digite s para sim ou n para não.")


def tem_dado_pessoal(texto):
    """Identifica possíveis dados pessoais para evitar seu armazenamento."""
    digitos = sum(1 for caractere in texto if caractere.isdigit())
    return digitos >= LIMITE_DIGITOS_PESSOAIS or "@" in texto


class Assistente:
    """Controla as conversas, histórico, indicadores e análise energética."""

    def __init__(
        self, nome, base, caminho_historico=None,
        caminho_csv=None, energia=None
    ):
        self.nome = nome
        self.base = base
        self.energia = energia
        pasta = os.path.dirname(base.caminho)

        self.caminho_historico = (
            caminho_historico or os.path.join(pasta, "historico.json")
        )
        self.caminho_csv = (
            caminho_csv or os.path.join(pasta, "atendimentos.csv")
        )

        self.historico = []
        self.atendimentos_da_sessao = 0
        self.avisos = []
        self._carregar_historico()

    def _carregar_historico(self):
        """Recupera os atendimentos anteriores."""
        try:
            with open(self.caminho_historico, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except FileNotFoundError:
            return
        except (json.JSONDecodeError, OSError, UnicodeDecodeError):
            self.avisos.append(
                "Histórico ausente ou corrompido: começando um novo."
            )
            return

        if not isinstance(dados, list):
            self.avisos.append("Histórico com formato inesperado.")
            return

        self.historico.extend(
            item for item in dados if isinstance(item, dict)
        )

    def _salvar_historico(self):
        """Salva o histórico em JSON."""
        temporario = self.caminho_historico + ".tmp"
        try:
            pasta = os.path.dirname(self.caminho_historico)
            if pasta:
                os.makedirs(pasta, exist_ok=True)

            with open(temporario, "w", encoding="utf-8") as arquivo:
                json.dump(
                    self.historico, arquivo,
                    ensure_ascii=False, indent=2
                )
            os.replace(temporario, self.caminho_historico)
        except OSError as erro:
            print(f"Aviso: não foi possível salvar o histórico ({erro}).")

    def registrar(
        self, origem, pergunta, id_orientacao, encontrou,
        ajudou, tentativas, inicio
    ):
        """Registra um atendimento realizado pelo usuário."""
        atendimento = {
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "origem": origem,
            "pergunta": pergunta,
            "id_orientacao": id_orientacao,
            "encontrou": encontrou,
            "ajudou": ajudou,
            "tentativas": tentativas,
            "tempo_segundos": round(time.time() - inicio, 1),
            "nota_facilidade": None,
        }

        self.historico.append(atendimento)
        self.atendimentos_da_sessao += 1
        self._salvar_historico()

    def perguntar(self):
        """Recebe dúvidas livres e procura orientações relacionadas."""
        inicio = None
        tentativas = 0
        encontrou = False
        ultima_pergunta = ""
        ultimo_id = None

        while True:
            texto = ler_texto(
                "\nDigite sua dúvida (0 para voltar): ",
                obrigatorio=False
            )

            if texto == "0":
                if tentativas > 0:
                    self.registrar(
                        "pergunta", ultima_pergunta, ultimo_id,
                        encontrou, False, tentativas, inicio
                    )
                return

            if not texto:
                print("Escreva sua dúvida ou digite 0 para voltar.")
                continue

            if tem_dado_pessoal(texto):
                print(
                    "Não digite CPF, telefone ou e-mail. "
                    "Reescreva sua pergunta."
                )
                continue

            if inicio is None:
                inicio = time.time()

            tentativas += 1
            ultima_pergunta = texto

            resultados = self.base.buscar(texto)

            if not resultados or self.base.confianca(resultados[0][0]) is None:
                self._mostrar_nao_encontrei()
                continue

            pontos, melhor = resultados[0]
            encontrou = True
            ultimo_id = melhor.id

            print("\n" + "=" * 60)
            melhor.exibir()
            self._complemento_analise(melhor)
            print("=" * 60)

            if ler_sn("\nEssa orientação ajudou? (s/n): "):
                self.registrar(
                    "pergunta", ultima_pergunta, ultimo_id,
                    True, True, tentativas, inicio
                )
                self.pedir_nota()
                return

    def _complemento_analise(self, orientacao):
        """Acrescenta cálculos energéticos quando a orientação é de SERS."""
        if not self.energia or not self.energia.disponivel:
            return

        categoria = str(orientacao.categoria).lower()
        palavras = (
            "energia", "home office", "solar", "economia",
            "desperdício", "desperdicio"
        )

        if any(palavra in categoria for palavra in palavras):
            print("\nANÁLISE ENERGÉTICA COMPLEMENTAR:")
            for linha in self.energia.resumo_texto("home_office"):
                print("- " + linha)

    def _mostrar_nao_encontrei(self):
        """Informa quando a base não contém resposta adequada."""
        print("\nNão encontrei uma orientação suficientemente relacionada.")
        print("Tente usar outras palavras ou navegar pelas categorias.")

    def navegar(self):
        """Permite escolher uma categoria da base de conhecimento."""
        categorias = self.base.categorias()

        if not categorias:
            print("Não existem categorias cadastradas.")
            return

        print("\n=== Categorias disponíveis ===")
        for indice, categoria in enumerate(categorias, start=1):
            print(f"  {indice}. {categoria}")
        print("  0. Voltar")

        escolha = ler_opcao("Escolha: ", 0, len(categorias))
        if escolha == 0:
            return

        self._navegar_categoria(categorias[escolha - 1])

    def _navegar_categoria(self, categoria):
        """Lista e exibe orientações de uma categoria."""
        orientacoes = self.base.por_categoria(categoria)

        if not orientacoes:
            print("Nenhuma orientação encontrada.")
            return

        print(f"\n=== {categoria} ===")
        for orientacao in orientacoes:
            orientacao.exibir()

    def calculadora_energia(self):
        """Solicita dados do usuário e compara alternativas energéticas."""
        if not self.energia or not self.energia.disponivel:
            print("Calculadora indisponível. Confira energia_dados.json.")
            return

        p = self.energia.parametros_padrao()

        print("\n=== ECONOMIA DE ENERGIA NO PRIMEIRO HOME OFFICE ===")
        print("Pressione Enter para aceitar o valor sugerido.")
        print("Digite 'cancelar' para interromper o cálculo.\n")

        try:
            computador = ler_numero(
                f"Potência do notebook/computador (W) [{p['potencia_notebook_w']}]: ",
                1, 1500, p["potencia_notebook_w"]
            )
            monitor = ler_numero(
                f"Potência do monitor (W) [{p['potencia_monitor_w']}]: ",
                0, 500, p["potencia_monitor_w"]
            )
            lampada = ler_numero(
                f"Potência da lâmpada atual (W) [{p['potencia_lampada_w']}]: ",
                1, 200, p["potencia_lampada_w"]
            )
            led = ler_numero(
                f"Potência da lâmpada LED (W) [{p['potencia_led_w']}]: ",
                1, 60, p["potencia_led_w"]
            )
            horas = ler_numero(
                f"Horas de uso por dia [{p['horas_dia']}]: ",
                1, 16, p["horas_dia"]
            )
            dias = ler_numero(
                f"Dias de uso no mês [{p['dias_mes']}]: ",
                1, 31, p["dias_mes"], inteiro=True
            )
            ociosas = ler_numero(
                f"Horas ociosas por dia [{p['horas_ociosas_dia']}]: ",
                0, 16, p["horas_ociosas_dia"]
            )
            tarifa = ler_numero(
                f"Tarifa em R$/kWh [{p['tarifa_kwh']}]: ",
                0.10, 5, p["tarifa_kwh"]
            )
            preco_led = ler_numero(
                f"Preço da lâmpada LED em reais [{p['preco_led_reais']}]: ",
                0, 200, p["preco_led_reais"]
            )

            resultado = self.energia.calcular_home_office(
                computador, monitor, lampada, led,
                horas, dias, ociosas, tarifa, preco_led
            )

        except (OperacaoCancelada, ValueError) as erro:
            print(f"\nCálculo cancelado ou inválido: {erro}")
            return

        for linha in self.energia.linhas_calculo_completo(resultado):
            print(linha)

    def pedir_nota(self):
        """Registra uma avaliação simples de facilidade de uso."""
        if not self.historico:
            return

        nota = ler_numero(
            "De 1 a 5, quão fácil foi encontrar a orientação? ",
            1, 5, 5, inteiro=True
        )
        self.historico[-1]["nota_facilidade"] = nota
        self._salvar_historico()

    def indicadores(self):
        """Calcula indicadores gerais dos atendimentos."""
        total = len(self.historico)
        encontrados = sum(
            1 for item in self.historico if item.get("encontrou")
        )
        ajudaram = sum(
            1 for item in self.historico if item.get("ajudou")
        )

        notas = [
            item["nota_facilidade"]
            for item in self.historico
            if isinstance(item.get("nota_facilidade"), (int, float))
        ]

        return {
            "total": total,
            "encontrados": encontrados,
            "ajudaram": ajudaram,
            "taxa_encontrados": encontrados / total * 100 if total else 0,
            "taxa_ajuda": ajudaram / total * 100 if total else 0,
            "media_facilidade": sum(notas) / len(notas) if notas else None,
        }

    def exibir_indicadores(self):
        """Apresenta os indicadores de atendimento."""
        dados = self.indicadores()

        print("\n=== INDICADORES DO ASSISTENTE ===")
        print(f"Atendimentos: {dados['total']}")
        print(f"Orientações encontradas: {dados['encontrados']}")
        print(f"Taxa de localização: {num(dados['taxa_encontrados'])}%")
        print(f"Atendimentos úteis: {dados['ajudaram']}")
        print(f"Taxa de utilidade: {num(dados['taxa_ajuda'])}%")

        if dados["media_facilidade"] is not None:
            print(
                "Média de facilidade: "
                f"{num(dados['media_facilidade'])}/5"
            )
        else:
            print("Ainda não existem avaliações de facilidade.")

    def exportar_csv(self):
        """Exporta o histórico de atendimentos em formato CSV."""
        try:
            pasta = os.path.dirname(self.caminho_csv)
            if pasta:
                os.makedirs(pasta, exist_ok=True)

            with open(
                self.caminho_csv, "w",
                encoding="utf-8-sig", newline=""
            ) as arquivo:
                escritor = csv.DictWriter(
                    arquivo, fieldnames=CAMPOS_CSV,
                    delimiter=";"
                )
                escritor.writeheader()
                escritor.writerows(self.historico)

            return True

        except OSError as erro:
            print(f"Erro ao exportar CSV: {erro}")
            return False
