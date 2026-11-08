# =====================================================================
# previsao.py - Previsão de geração eólica por regressão linear simples
#
# Ajusta uma reta  y^ = b0 + b1 * x  aos dados históricos pelo método
# dos mínimos quadrados (Cap. 7), sem bibliotecas externas:
#
#   b1 = soma((xi - x_med) * (yi - y_med)) / soma((xi - x_med)²)
#   b0 = y_med - b1 * x_med
#
# Na colônia, x é a velocidade do vento (m/s) e y é a energia eólica
# gerada (kW). O R² mostra quanto da variação de y a reta explica.
# =====================================================================


def media(valores: list) -> float:
    return sum(valores) / len(valores)


def ajustar_reta(x: list, y: list) -> tuple:
    """Devolve (b0, b1), o intercepto e a inclinação da reta de mínimos quadrados."""
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("as listas precisam ter o mesmo tamanho e pelo menos 2 leituras")

    x_med = media(x)
    y_med = media(y)

    soma_produtos = 0.0      # soma de (xi - x_med) * (yi - y_med)
    soma_quadrados = 0.0     # soma de (xi - x_med)²
    for xi, yi in zip(x, y):
        soma_produtos += (xi - x_med) * (yi - y_med)
        soma_quadrados += (xi - x_med) ** 2

    if soma_quadrados == 0:
        raise ValueError("todos os valores de x são iguais: não existe uma reta única")

    b1 = soma_produtos / soma_quadrados
    b0 = y_med - b1 * x_med
    return b0, b1


def prever(b0: float, b1: float, x: float) -> float:
    return b0 + b1 * x


def coeficiente_r2(x: list, y: list, b0: float, b1: float) -> float:
    """R² = 1 - soma((yi - yi^)²) / soma((yi - y_med)²)"""
    y_med = media(y)
    soma_residuos = 0.0      # erro que sobra depois da reta
    soma_total = 0.0         # variação total de y em torno da média
    for xi, yi in zip(x, y):
        soma_residuos += (yi - prever(b0, b1, xi)) ** 2
        soma_total += (yi - y_med) ** 2
    return 1 - soma_residuos / soma_total


# Executado só quando o arquivo é rodado sozinho (python previsao.py),
# para conferir o modelo com o histórico da colônia.
if __name__ == "__main__":
    from dados import historico

    vento = historico["vento_ms"]
    eolica = historico["eolica_kw"]

    b0, b1 = ajustar_reta(vento, eolica)
    r2 = coeficiente_r2(vento, eolica, b0, b1)

    print("MODELO DE PREVISÃO (vento -> geração eólica)")
    print(f"  reta: geração = {b0:.2f} + {b1:.2f} x vento")
    print(f"  R² = {r2:.4f}")

    print("\n  vento (m/s)   medido (kW)   previsto (kW)   erro (kW)")
    for xi, yi in zip(vento, eolica):
        previsto = prever(b0, b1, xi)
        print(f"  {xi:11.1f}   {yi:11.1f}   {previsto:13.1f}   {yi - previsto:9.1f}")

    print(f"\nEntrada: vento = 11 m/s -> previsão de geração eólica = {prever(b0, b1, 11):.1f} kW")
