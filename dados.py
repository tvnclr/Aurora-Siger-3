# =====================================================================
# dados.py - Dados da colônia Aurora Siger
#
# Guarda o estado atual da colônia num dicionário hierárquico
# (colônia -> sistema -> subsistema -> valor) e o histórico de leituras
# do vento em listas. As funções no fim do arquivo permitem navegar
# pela hierarquia usando um caminho de texto, como "energia/solar".
#
# Unidades: potência em kW, energia armazenada em kWh, vento em m/s,
# temperatura em °C.
# =====================================================================

colonia = {
    "energia": {
        "solar": {
            "geracao_kw": 25.0,
        },
        "eolica": {
            "geracao_kw": 27.0,      # última leitura do gerador eólico
        },
        "bateria": {
            "capacidade_kwh": 200.0,
            "carga_kwh": 80.0,
        },
    },
    "ambiente": {
        "temperatura_interna_c": 21.0,
        "temperatura_externa_c": -60.0,
        "vento_ms": 11.0,
    },
    "operacional": {
        # prioridade 1 = mais importante; essencial = nunca pode ser desligado
        "modulos": {
            "suporte_vida":       {"consumo_kw": 20.0, "prioridade": 1, "essencial": True,  "ligado": True},
            "habitacao":          {"consumo_kw": 12.0, "prioridade": 2, "essencial": True,  "ligado": True},
            "estufa":             {"consumo_kw": 10.0, "prioridade": 3, "essencial": True,  "ligado": True},
            "comunicacao":        {"consumo_kw": 6.0,  "prioridade": 4, "essencial": True,  "ligado": True},
            "laboratorio":        {"consumo_kw": 9.0,  "prioridade": 5, "essencial": False, "ligado": True},
            "oficina":            {"consumo_kw": 8.0,  "prioridade": 6, "essencial": False, "ligado": True},
            "iluminacao_externa": {"consumo_kw": 5.0,  "prioridade": 7, "essencial": False, "ligado": True},
        },
    },
}

# Histórico de leituras: a posição i das duas listas é a mesma leitura
# (vento medido e energia eólica gerada naquele momento).
historico = {
    "vento_ms":  [6.0, 7.0, 8.0, 9.0, 10.0, 12.0, 13.0, 14.0],
    "eolica_kw": [15.0, 17.0, 20.0, 22.0, 25.0, 30.0, 32.0, 35.0],
}


def ler(caminho: str):
    """Devolve o valor guardado em um caminho, ex.: ler("energia/bateria/carga_kwh")."""
    atual = colonia
    for chave in caminho.split("/"):
        if not isinstance(atual, dict) or chave not in atual:
            return None          # caminho não existe
        atual = atual[chave]
    return atual


def gravar(caminho: str, valor) -> bool:
    """Troca um valor que já existe, ex.: gravar("ambiente/vento_ms", 9.0).
    Devolve False se o caminho não existir (não cria chaves novas)."""
    chaves = caminho.split("/")
    pai = ler("/".join(chaves[:-1])) if len(chaves) > 1 else colonia
    if not isinstance(pai, dict) or chaves[-1] not in pai:
        return False
    pai[chaves[-1]] = valor
    return True


def listar(caminho: str = "") -> list:
    """Lista o que existe dentro de um ponto da hierarquia (a raiz, se o caminho for vazio)."""
    if caminho == "":
        no = colonia
    else:
        no = ler(caminho)
    if isinstance(no, dict):
        return list(no.keys())
    return []


def mostrar_hierarquia(no: dict = None, nivel: int = 0) -> None:
    """Imprime a hierarquia inteira com recuo por nível."""
    if no is None:
        no = colonia
    for chave, valor in no.items():
        if isinstance(valor, dict):
            print("    " * nivel + chave)
            mostrar_hierarquia(valor, nivel + 1)
        else:
            print("    " * nivel + f"{chave}: {valor}")


# Executado só quando o arquivo é rodado sozinho (python dados.py),
# para conferir os dados antes das outras fases.
if __name__ == "__main__":
    print("HIERARQUIA DA COLÔNIA")
    mostrar_hierarquia()

    print("\nSubsistemas de energia:", listar("energia"))
    print("Carga da bateria:", ler("energia/bateria/carga_kwh"), "kWh")
    print("Consumo do suporte à vida:", ler("operacional/modulos/suporte_vida/consumo_kw"), "kW")
    print("Caminho inexistente:", ler("energia/nuclear"))

    print("\nHISTÓRICO (vento x geração eólica)")
    for vento, energia in zip(historico["vento_ms"], historico["eolica_kw"]):
        print(f"  vento {vento:4.1f} m/s -> {energia:4.1f} kW")
