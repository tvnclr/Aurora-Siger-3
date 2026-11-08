# =====================================================================
# decisoes.py - Regras de decisão da colônia
#
# Recebe os dados já lidos (números e o dicionário de módulos), aplica
# as regras com if / elif / else e devolve mensagens de saída no
# formato "ALERTA: ..." ou "SUGESTÃO: ...".
#
#   1. regras de energia: regra básica, regra combinada e regra crítica
#   2. priorização: desliga módulos não essenciais quando falta energia
#   3. análise de energia: compara geração, consumo e bateria
# =====================================================================

# Limites usados nas regras
ENERGIA_BAIXA = 50.0       # % de carga da bateria
CONSUMO_ALTO = 60.0        # kW
PREVISAO_FRACA = 20.0      # kW de geração eólica prevista (vento abaixo de ~8 m/s)


def percentual_bateria(carga_kwh: float, capacidade_kwh: float) -> float:
    return carga_kwh / capacidade_kwh * 100


def consumo_total(modulos: dict) -> float:
    """Soma o consumo só dos módulos ligados."""
    total = 0.0
    for modulo in modulos.values():
        if modulo["ligado"]:
            total += modulo["consumo_kw"]
    return total


# ---------------------------------------------------------------------
# 1. Regras de energia
# ---------------------------------------------------------------------
def avaliar_regras(energia: float, consumo: float, previsao_eolica: float) -> list:
    """Devolve a lista de ações para o nível de energia (%), o consumo (kW)
    e a geração eólica prevista (kW). Testa da situação mais grave para a
    mais leve, por isso só um dos blocos é executado."""
    energia_baixa = energia < ENERGIA_BAIXA
    consumo_alto = consumo > CONSUMO_ALTO
    previsao_ruim = previsao_eolica < PREVISAO_FRACA

    if energia_baixa and consumo_alto and previsao_ruim:
        return ["ALERTA CRÍTICO: energia baixa, consumo alto e pouco vento previsto",
                "AÇÃO: ativar modo economia e desligar sistemas não essenciais"]
    elif energia_baixa and consumo_alto:
        return ["ALERTA: reduzir consumo",
                "AÇÃO: ativar modo economia"]
    elif energia_baixa:
        return ["ALERTA: reduzir consumo"]
    else:
        return ["NORMAL: energia suficiente, nenhuma ação necessária"]


# ---------------------------------------------------------------------
# 2. Priorização
# ---------------------------------------------------------------------
def priorizar(modulos: dict, geracao_kw: float) -> list:
    """Desliga módulos não essenciais, do menos importante para o mais
    importante, até o consumo caber na geração. Módulos essenciais (como
    o suporte à vida) nunca são desligados. Devolve os nomes desligados."""
    desligados = []
    while consumo_total(modulos) > geracao_kw:
        # procura o não essencial ligado com o maior número de prioridade
        # (prioridade 1 = mais importante, então o maior número sai primeiro)
        escolhido = None
        for nome, modulo in modulos.items():
            if modulo["ligado"] and not modulo["essencial"]:
                if escolhido is None or modulo["prioridade"] > modulos[escolhido]["prioridade"]:
                    escolhido = nome
        if escolhido is None:
            break                  # só sobraram essenciais: a diferença sai da bateria
        modulos[escolhido]["ligado"] = False
        desligados.append(escolhido)
    return desligados


# ---------------------------------------------------------------------
# 3. Análise de energia (balanço de 1 hora: kW x 1 h = kWh)
# ---------------------------------------------------------------------
def analisar_energia(geracao: float, consumo: float, carga_kwh: float, capacidade_kwh: float) -> tuple:
    """Compara geração e consumo e decide o que fazer com a bateria.
    Devolve (mensagens, nova carga da bateria em kWh)."""
    saldo = geracao - consumo

    if saldo < 0:
        falta = -saldo
        if carga_kwh >= falta:
            return (["ALERTA: consumo maior que geração",
                     f"AÇÃO: usar {falta:.1f} kWh da bateria (restam {carga_kwh - falta:.1f} kWh)"],
                    carga_kwh - falta)
        else:
            return (["ALERTA CRÍTICO: consumo maior que geração e bateria insuficiente",
                     f"AÇÃO: faltam {falta - carga_kwh:.1f} kWh, desligar sistemas não essenciais"],
                    0.0)
    elif saldo > 0:
        espaco = capacidade_kwh - carga_kwh
        guardado = min(saldo, espaco)
        mensagens = [f"SUGESTÃO: armazenar energia excedente ({guardado:.1f} kWh na bateria)"]
        if saldo > espaco:
            mensagens.append(f"AVISO: bateria cheia, {saldo - espaco:.1f} kWh seriam desperdiçados")
        return mensagens, carga_kwh + guardado
    else:
        return ["NORMAL: geração igual ao consumo"], carga_kwh
