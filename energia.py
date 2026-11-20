""" Cálculos de consumo e alternativas energéticas do Citizen Assist AI.
    O cenário de referência representa alguém que trabalha em home office.
"""

from pathlib import Path
import json
import math

BASE_DIR = Path(__file__).resolve().parent
CAMINHO_DADOS = BASE_DIR / "data" / "energia_dados.json"

def num(valor, casas=2):
    """Formata um número no padrão br"""
    return f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def reais(valor):
    """Formata um valor em reais."""
    return f"R$ {num(valor, 2)}"


class AnaliseEnergia:
    """Carrega premissas energéticas e calcula consumo, economia e solar."""

    def __init__(self, caminho_dados):
        self.caminho_dados = caminho_dados
        self.dados = {}
        self.avisos = []
        self.disponivel = False

    def carregar(self):
        """Carrega parâmetros e referências de energia a partir de JSON."""
        try:
            with open(CAMINHO_DADOS, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except FileNotFoundError:
            self.avisos.append(f"Arquivo de energia não encontrado: {self.caminho_dados}")
            return False
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as erro:
            self.avisos.append(f"Não foi possível carregar os dados de energia: {erro}")
            return False

        if not isinstance(dados, dict) or not isinstance(dados.get("referencia"), dict):
            self.avisos.append("O arquivo de energia possui formato inválido.")
            return False

        obrigatorios = (
            "potencia_notebook_w", "potencia_monitor_w", "potencia_lampada_w",
            "potencia_led_w", "horas_dia", "dias_mes", "horas_ociosas_dia",
            "tarifa_kwh", "solar_kwh_por_kwp_mes", "solar_referencia_kwp",
            "solar_preco_medio_rpw", "preco_led_reais",
        )
        referencia = dados["referencia"]
        ausentes = [campo for campo in obrigatorios if campo not in referencia]
        if ausentes:
            self.avisos.append("Parâmetros ausentes no arquivo de energia: " + ", ".join(ausentes))
            return False

        self.dados = dados
        self.disponivel = True
        return True

    def parametros_padrao(self):
        """Devolve uma cópia dos valores de referência para os prompts."""
        if not self.disponivel:
            return {}
        return dict(self.dados["referencia"])

    def calcular_home_office(
        self,
        potencia_computador_w,
        potencia_monitor_w,
        potencia_lampada_w,
        potencia_led_w,
        horas_dia,
        dias_mes,
        horas_ociosas_dia,
        tarifa_kwh,
        preco_led_reais,
    ):
        """Compara o consumo atual com medidas de eficiência e com energia solar.

        Fórmula de consumo: potência (W) / 1.000 × horas × dias = kWh.
        A economia comportamental considera o computador e o monitor desligados
        durante o período ocioso; a economia de iluminação troca a lâmpada atual
        por uma LED que ofereça iluminação adequada.
        """
        valores = {
            "potencia_computador_w": (potencia_computador_w, 1, 1500),
            "potencia_monitor_w": (potencia_monitor_w, 0, 500),
            "potencia_lampada_w": (potencia_lampada_w, 1, 200),
            "potencia_led_w": (potencia_led_w, 1, 60),
            "horas_dia": (horas_dia, 1, 16),
            "dias_mes": (dias_mes, 1, 31),
            "horas_ociosas_dia": (horas_ociosas_dia, 0, 16),
            "tarifa_kwh": (tarifa_kwh, 0.10, 5.00),
            "preco_led_reais": (preco_led_reais, 0, 200),
        }
        for nome, (valor, minimo, maximo) in valores.items():
            if isinstance(valor, bool) or not isinstance(valor, (int, float)):
                raise ValueError(f"{nome} deve ser numérico.")
            if not math.isfinite(valor) or not minimo <= valor <= maximo:
                raise ValueError(f"{nome} deve estar entre {minimo} e {maximo}.")

        if horas_ociosas_dia > horas_dia:
            raise ValueError("As horas ociosas não podem superar as horas de uso por dia.")

        aviso_led = potencia_led_w >= potencia_lampada_w

        horas_mes = horas_dia * dias_mes
        horas_ativas_pc = (horas_dia - horas_ociosas_dia) * dias_mes
        consumo_computador = potencia_computador_w * horas_mes / 1000
        consumo_monitor = potencia_monitor_w * horas_mes / 1000
        consumo_lampada = potencia_lampada_w * horas_mes / 1000
        consumo_base = consumo_computador + consumo_monitor + consumo_lampada

        consumo_pc_eficiente = potencia_computador_w * horas_ativas_pc / 1000
        consumo_monitor_eficiente = potencia_monitor_w * horas_ativas_pc / 1000
        consumo_led = potencia_led_w * horas_mes / 1000
        consumo_eficiente = (
            consumo_pc_eficiente + consumo_monitor_eficiente + consumo_led
        )

        economia_kwh = max(0.0, consumo_base - consumo_eficiente)
        economia_percentual = (
            100 * economia_kwh / consumo_base if consumo_base else 0.0
        )

        solar_kwh_por_kwp = self.dados["referencia"]["solar_kwh_por_kwp_mes"]
        solar_ideal_kwp = consumo_base / solar_kwh_por_kwp if solar_kwh_por_kwp else 0
        solar_kwp = self.dados["referencia"]["solar_referencia_kwp"]
        solar_preco_rpw = self.dados["referencia"]["solar_preco_medio_rpw"]
        solar_geracao_referencia = solar_kwp * solar_kwh_por_kwp
        solar_investimento = solar_kwp * 1000 * solar_preco_rpw

        economia_led_kwh = max(0.0, consumo_lampada - consumo_led)
        economia_led_reais = economia_led_kwh * tarifa_kwh

        return {
            "potencia_computador_w": float(potencia_computador_w),
            "potencia_monitor_w": float(potencia_monitor_w),
            "potencia_lampada_w": float(potencia_lampada_w),
            "potencia_led_w": float(potencia_led_w),
            "horas_dia": float(horas_dia),
            "dias_mes": int(dias_mes),
            "horas_ociosas_dia": float(horas_ociosas_dia),
            "horas_mes": horas_mes,
            "horas_ativas_pc_mes": horas_ativas_pc,
            "tarifa_kwh": float(tarifa_kwh),
            "consumo_computador_kwh": consumo_computador,
            "consumo_monitor_kwh": consumo_monitor,
            "consumo_lampada_kwh": consumo_lampada,
            "consumo_base_kwh": consumo_base,
            "consumo_pc_eficiente_kwh": consumo_pc_eficiente,
            "consumo_monitor_eficiente_kwh": consumo_monitor_eficiente,
            "consumo_led_kwh": consumo_led,
            "consumo_eficiente_kwh": consumo_eficiente,
            "economia_kwh": economia_kwh,
            "economia_percentual": economia_percentual,
            "custo_base_reais": consumo_base * tarifa_kwh,
            "custo_eficiente_reais": consumo_eficiente * tarifa_kwh,
            "economia_reais_mes": economia_kwh * tarifa_kwh,
            "economia_reais_ano": economia_kwh * tarifa_kwh * 12,
            "economia_led_kwh": economia_led_kwh,
            "economia_led_reais_mes": economia_led_reais,
            "preco_led_reais": float(preco_led_reais),
            "payback_led_meses": (
                preco_led_reais / economia_led_reais
                if economia_led_reais > 0 else None
            ),
            "aviso_led": aviso_led,
            "solar_ideal_kwp": solar_ideal_kwp,
            "solar_referencia_kwp": solar_kwp,
            "solar_geracao_referencia_kwh": solar_geracao_referencia,
            "solar_investimento_referencia_reais": solar_investimento,
            "solar_relacao_geracao_home_office": (
                solar_geracao_referencia / consumo_base if consumo_base else 0
            ),
        }

    def _calculo_padrao(self):
        """Executa o cenário de referência usado nas orientações."""
        p = self.parametros_padrao()
        return self.calcular_home_office(
            potencia_computador_w=p["potencia_notebook_w"],
            potencia_monitor_w=p["potencia_monitor_w"],
            potencia_lampada_w=p["potencia_lampada_w"],
            potencia_led_w=p["potencia_led_w"],
            horas_dia=p["horas_dia"],
            dias_mes=p["dias_mes"],
            horas_ociosas_dia=p["horas_ociosas_dia"],
            tarifa_kwh=p["tarifa_kwh"],
            preco_led_reais=p["preco_led_reais"],
        )

    def resumo_texto(self, analise):
        """Gera as linhas de apoio para a resposta da base de conhecimento."""
        if not self.disponivel:
            return ["Análise energética indisponível: confira energia_dados.json."]

        if analise in ("home_office", "economia"):
            p = self._calculo_padrao()
            return [
                "Cenário de referência (estimado): notebook + monitor + lâmpada, "
                f"{num(p['horas_dia'], 0)} h/dia e {p['dias_mes']} dias/mês.",
                f"Consumo atual estimado: {num(p['consumo_base_kwh'])} kWh/mês.",
                f"Com LED e desligamento no período ocioso: {num(p['consumo_eficiente_kwh'])} kWh/mês.",
                f"Redução estimada: {num(p['economia_kwh'])} kWh/mês "
                f"({num(p['economia_percentual'])}%).",
                f"Na iluminação, a LED economiza {num(p['economia_led_kwh'])} kWh/mês; "
                f"com preço de {reais(p['preco_led_reais'])}, retorno simples estimado: "
                + (f"{num(p['payback_led_meses'])} meses." if p["payback_led_meses"] is not None else "não calculável."),
                "Os números mudam conforme potência real, tempo de uso e tarifa da residência.",
            ]

        if analise == "solar":
            p = self._calculo_padrao()
            return [
                f"Demanda de referência do home office: {num(p['consumo_base_kwh'])} kWh/mês.",
                f"Potência fotovoltaica teórica proporcional: {num(p['solar_ideal_kwp'], 3)} kWp, "
                "usando a premissa aproximada de 120 kWh/mês por kWp.",
                f"Referência de mercado: sistema residencial de {num(p['solar_referencia_kwp'], 1)} kWp, "
                f"geração estimada de {num(p['solar_geracao_referencia_kwh'])} kWh/mês e "
                f"investimento médio de {reais(p['solar_investimento_referencia_reais'])}.",
                "Um sistema residencial padrão pode ser grande demais para alimentar somente "
                "um home office; avalie o consumo total da casa e as regras de compensação.",
            ]

        if analise == "tarifa":
            return [
                "Consumo em kWh = potência em watts ÷ 1.000 × horas de uso.",
                "Para uma estimativa, multiplique o kWh consumido pelo valor efetivo do kWh "
                "informado na conta de luz.",
                "O valor efetivo varia com distribuidora, tributos, bandeira, iluminação pública "
                "e regras de compensação; não use R$ 1,00 como tarifa universal.",
            ]

        if analise == "conceito":
            return [
                "Potência (W) indica a taxa de consumo do equipamento; energia (kWh) "
                "considera potência e tempo.",
                "Exemplo: 65 W × 8 h × 22 dias ÷ 1.000 = 11,44 kWh/mês.",
            ]

        if analise == "carreira":
            return [
                "Comece pelas ações sem custo: modo de suspensão, desligar monitor e "
                "luzes ao se ausentar e aproveitar luz natural.",
                "No trabalho presencial, siga as regras da empresa e não desligue "
                "equipamentos compartilhados ou críticos sem autorização.",
            ]

        return []

    def linhas_calculo_completo(self, p):
        """Monta uma comparação legível das alternativas e das premissas."""
        linhas = [
            "\n=== ANÁLISE ENERGÉTICA: PRIMEIRO HOME OFFICE ===",
            "Público: pessoa em início de carreira, trabalhando ou estudando em casa.",
            "Período: " + num(p["horas_dia"], 1) + " h/dia × " + str(p["dias_mes"]) +
            " dias/mês = " + num(p["horas_mes"], 1) + " horas/mês.",
            "\nALTERNATIVA 1 — CONSUMO ATUAL (REDE ELÉTRICA)",
            f"Notebook/computador: {num(p['consumo_computador_kwh'])} kWh/mês.",
            f"Monitor: {num(p['consumo_monitor_kwh'])} kWh/mês.",
            f"Iluminação atual: {num(p['consumo_lampada_kwh'])} kWh/mês.",
            f"Total estimado: {num(p['consumo_base_kwh'])} kWh/mês — "
            f"{reais(p['custo_base_reais'])}/mês.",
            "\nALTERNATIVA 2 — EFICIÊNCIA ENERGÉTICA (SEM TROCAR O COMPUTADOR)",
            f"Notebook + monitor em uso por {num(p['horas_dia'] - p['horas_ociosas_dia'], 1)} h/dia: "
            f"{num(p['consumo_pc_eficiente_kwh'] + p['consumo_monitor_eficiente_kwh'])} kWh/mês.",
            f"Lâmpada LED: {num(p['consumo_led_kwh'])} kWh/mês.",
            f"Novo total: {num(p['consumo_eficiente_kwh'])} kWh/mês — "
            f"{reais(p['custo_eficiente_reais'])}/mês.",
            f"Economia estimada: {num(p['economia_kwh'])} kWh/mês "
            f"({num(p['economia_percentual'])}%) ou {reais(p['economia_reais_mes'])}/mês.",
            f"Economia anual estimada: {reais(p['economia_reais_ano'])}, mantendo o mesmo padrão de uso.",
            f"Custo estimado da lâmpada LED: {reais(p['preco_led_reais'])}; economia apenas na iluminação: "
            f"{reais(p['economia_led_reais_mes'])}/mês.",
            (
                f"Retorno simples estimado da lâmpada: {num(p['payback_led_meses'])} meses."
                if p["payback_led_meses"] is not None
                else "Não há retorno calculável para a lâmpada informada, pois ela não reduz o consumo."
            ),
            "\nALTERNATIVA 3 — GERAÇÃO SOLAR FOTOVOLTAICA (FONTE RENOVÁVEL)",
            f"Potência teórica para gerar o consumo atual: {num(p['solar_ideal_kwp'], 3)} kWp.",
            f"Referência residencial de {num(p['solar_referencia_kwp'], 1)} kWp: "
            f"cerca de {num(p['solar_geracao_referencia_kwh'])} kWh/mês e "
            f"{reais(p['solar_investimento_referencia_reais'])} de investimento médio.",
            f"Essa geração de referência equivale a {num(p['solar_relacao_geracao_home_office'], 1)} vezes "
            "o consumo mensal deste home office; a capacidade excedente teria de atender outras "
            "cargas da casa ou seguir as regras de compensação.",
            "\nCOMO INTERPRETAR",
            f"Tarifa usada: {reais(p['tarifa_kwh'])}/kWh (valor informado/estimado pelo usuário).",
            "Priorize primeiro as medidas de eficiência: elas reduzem a demanda antes de "
            "dimensionar um sistema de geração.",
            "Impacto ambiental: reduzir o consumo evita demanda de geração e expansão "
            "desnecessárias na rede. A energia solar é renovável durante a operação, mas "
            "os módulos e componentes também têm impactos de fabricação e precisam de "
            "destinação e reciclagem adequadas ao fim da vida útil (IRENA/IEA-PVPS).",
            "A estimativa solar não é orçamento nem promessa de redução integral da fatura. "
            "A produção varia com cidade, orientação, sombra, clima e perdas; a compensação "
            "depende das regras da distribuidora e do enquadramento na Lei 14.300/2022.",
            "\nDICAS PARA QUEM ESTÁ COMEÇANDO NA CARREIRA",
            "1. Ative suspensão automática e desligue monitor/notebook em pausas longas.",
            "2. Use iluminação natural e LED; compare lúmens por watt e a etiqueta do Inmetro.",
            "3. No escritório, siga a política da empresa; não desligue servidores ou aparelhos compartilhados.",
            "4. Registre o kWh da conta antes e depois de começar o home office para identificar o aumento real.",
            "5. Antes de comprar equipamentos, compare potência, horas de uso, consumo mensal e custo total.",
            "\nFontes: EPE (PDE 2036, p. 23), Greener (Pesquisa SED, jun/2026), "
            "ANEEL (MMGD) e Inmetro (eficiência energética). Veja README_SERS.md.",
        ]
        if p["aviso_led"]:
            linhas.insert(
                linhas.index("\nCOMO INTERPRETAR"),
                "Atenção: a potência da LED informada não é menor que a lâmpada atual; "
                "essa troca não gera economia de iluminação neste cenário.",
            )
        return linhas
