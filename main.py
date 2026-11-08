# =====================================================================
# main.py - Sistema inteligente da colônia Aurora Siger
#
# Junta as três partes do sistema, no fluxo entrada -> processamento -> saída:
#   dados.py     -> estado da colônia e histórico (entrada)
#   previsao.py  -> regressão linear vento x geração eólica
#   decisoes.py  -> regras, priorização e análise de energia (saída)
#
# Como rodar:  python main.py      (Python 3.8 ou mais recente)
# =====================================================================

from dados import historico, ler, gravar, listar
from previsao import ajustar_reta, prever, coeficiente_r2
from decisoes import (percentual_bateria, consumo_total, avaliar_regras,
                      priorizar, analisar_energia)


def titulo(texto: str) -> None:
    print("\n" + "=" * 70)
    print(texto)
    print("=" * 70)


def mostrar(mensagens: list) -> None:
    for mensagem in mensagens:
        print("  Saída: " + mensagem)


def mostrar_modelo(b0: float, b1: float, r2: float) -> None:
    titulo("1. MODELO DE PREVISÃO (histórico vento x geração eólica)")
    print(f"Leituras usadas: {len(historico['vento_ms'])}")
    print(f"Reta: geração eólica = {b0:.2f} + {b1:.2f} x vento   (R² = {r2:.4f})")


def operacao_atual(b0: float, b1: float) -> None:
    titulo("2. OPERAÇÃO DA PRÓXIMA HORA (dados atuais da colônia)")
    print("Sistemas:", listar(""), "| energia:", listar("energia"))

    # entrada: leitura dos dados pela hierarquia
    modulos = ler("operacional/modulos")
    carga = ler("energia/bateria/carga_kwh")
    capacidade = ler("energia/bateria/capacidade_kwh")
    vento = ler("ambiente/vento_ms")
    solar = ler("energia/solar/geracao_kw")

    # processamento: previsão e totais
    previsao_eolica = prever(b0, b1, vento)
    geracao = solar + previsao_eolica
    energia = percentual_bateria(carga, capacidade)
    consumo = consumo_total(modulos)

    print(f"\nEntrada: bateria {carga:.0f}/{capacidade:.0f} kWh = {energia:.0f}% | consumo {consumo:.0f} kW")
    print(f"         vento {vento:.0f} m/s -> eólica prevista {previsao_eolica:.1f} kW "
          f"+ solar {solar:.0f} kW = geração {geracao:.1f} kW")

    print("\nRegras de energia:")
    mostrar(avaliar_regras(energia, consumo, previsao_eolica))

    print("\nPriorização:")
    desligados = priorizar(modulos, geracao)
    if len(desligados) == 0:
        print("  Saída: nenhum módulo precisou ser desligado")
    for nome in desligados:
        print(f"  Saída: desligar {nome} ({modulos[nome]['consumo_kw']:.0f} kW)")
    consumo = consumo_total(modulos)
    print(f"  Consumo depois da priorização: {consumo:.0f} kW (suporte à vida continua ligado)")

    print("\nAnálise de energia:")
    mensagens, nova_carga = analisar_energia(geracao, consumo, carga, capacidade)
    mostrar(mensagens)
    gravar("energia/bateria/carga_kwh", nova_carga)
    print(f"  Bateria ao fim da hora: {nova_carga:.1f} kWh")


def exemplos_do_enunciado(b0: float, b1: float) -> None:
    titulo("3. EXEMPLOS DE ENTRADA E SAÍDA")

    print("Regras (energia em %, consumo em kW):")
    for energia, consumo, vento in [(40, 70, 11), (40, 50, 11), (30, 70, 6), (80, 70, 11)]:
        previsao_eolica = prever(b0, b1, vento)
        print(f"Entrada: energia = {energia}, consumo = {consumo}, vento = {vento} m/s "
              f"(eólica prevista {previsao_eolica:.1f} kW)")
        mostrar(avaliar_regras(energia, consumo, previsao_eolica))

    print("\nPrevisão:")
    print("Entrada: vento = 11")
    print(f"  Saída: previsão de energia de cerca de {prever(b0, b1, 11):.0f} kW")

    print("\nAnálise de energia (bateria de 200 kWh):")
    for geracao, consumo, carga in [(40, 70, 80), (80, 30, 80), (80, 30, 190), (40, 70, 10)]:
        print(f"Entrada: geração = {geracao}, consumo = {consumo}, bateria = {carga} kWh")
        mensagens, _ = analisar_energia(geracao, consumo, carga, 200)
        mostrar(mensagens)


def main() -> None:
    print("SISTEMA INTELIGENTE DA COLÔNIA AURORA SIGER")
    b0, b1 = ajustar_reta(historico["vento_ms"], historico["eolica_kw"])
    r2 = coeficiente_r2(historico["vento_ms"], historico["eolica_kw"], b0, b1)

    mostrar_modelo(b0, b1, r2)
    operacao_atual(b0, b1)
    exemplos_do_enunciado(b0, b1)


if __name__ == "__main__":
    main()
