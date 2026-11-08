# Sistema inteligente da colônia Aurora Siger

Atividade integradora da Fase 3 de Ciência da Computação (FIAP).

O sistema lê os dados da colônia (energia, clima e consumo dos módulos), prevê a
geração eólica com uma regressão linear e decide o que fazer: gerar alertas,
ativar o modo economia, desligar módulos não essenciais e indicar o que fazer com
a energia que sobra ou falta. O fluxo é sempre **entrada → processamento → saída**.

## Como rodar

Precisa só do Python 3.8 ou mais recente. Nenhuma biblioteca externa é usada.

```
python main.py
```

Cada parte também roda sozinha para conferência: `python dados.py` mostra a
hierarquia dos dados e `python previsao.py` mostra a reta e os erros de cada leitura.

## Estrutura

| Arquivo | Papel |
|---|---|
| `dados.py` | **Dados**: estado da colônia num dicionário hierárquico (energia → solar / eólica / bateria; ambiente; operacional → módulos) e histórico de vento × geração eólica em listas. Funções `ler`, `gravar`, `listar` e `mostrar_hierarquia` navegam pela hierarquia com caminhos como `"energia/bateria/carga_kwh"`. |
| `previsao.py` | **Modelo**: regressão linear simples por mínimos quadrados, calculada à mão (`ajustar_reta`, `prever`, `coeficiente_r2`). |
| `decisoes.py` | **Decisões**: regras com `if / elif / else`, priorização dos módulos e análise de geração × consumo × bateria. |
| `main.py` | Junta tudo: lê os dados, faz a previsão, aplica as regras e mostra as saídas. |

## Regras usadas

| Situação | Saída |
|---|---|
| energia < 50 % **e** consumo > 60 kW **e** eólica prevista < 20 kW | `ALERTA CRÍTICO` + modo economia e desligar não essenciais |
| energia < 50 % **e** consumo > 60 kW | `ALERTA: reduzir consumo` + ativar modo economia |
| energia < 50 % | `ALERTA: reduzir consumo` |
| caso contrário | `NORMAL` |
| consumo dos módulos maior que a geração prevista (priorização) | desliga módulos não essenciais (do menos para o mais importante) até caber; o suporte à vida nunca desliga |
| consumo > geração (análise de energia) | `ALERTA: consumo maior que geração` (a bateria cobre a diferença, se tiver carga) |
| geração > consumo (análise de energia) | `SUGESTÃO: armazenar energia excedente` (o que não couber na bateria é aviso de desperdício) |

## Exemplos de entrada e saída

Trechos da execução de `python main.py`.

Regra combinada (exemplo do enunciado):

```
Entrada: energia = 40, consumo = 70, vento = 11 m/s (eólica prevista 27.3 kW)
  Saída: ALERTA: reduzir consumo
  Saída: AÇÃO: ativar modo economia
```

Previsão por regressão:

```
Entrada: vento = 11
  Saída: previsão de energia de cerca de 27 kW
```

Análise de energia:

```
Entrada: geração = 40, consumo = 70, bateria = 80 kWh
  Saída: ALERTA: consumo maior que geração
  Saída: AÇÃO: usar 30.0 kWh da bateria (restam 50.0 kWh)
Entrada: geração = 80, consumo = 30, bateria = 80 kWh
  Saída: SUGESTÃO: armazenar energia excedente (50.0 kWh na bateria)
```

Operação completa da próxima hora com os dados atuais da colônia:

```
Entrada: bateria 80/200 kWh = 40% | consumo 70 kW
         vento 11 m/s -> eólica prevista 27.3 kW + solar 25 kW = geração 52.3 kW

Regras de energia:
  Saída: ALERTA: reduzir consumo
  Saída: AÇÃO: ativar modo economia

Priorização:
  Saída: desligar iluminacao_externa (5 kW)
  Saída: desligar oficina (8 kW)
  Saída: desligar laboratorio (9 kW)
  Consumo depois da priorização: 48 kW (suporte à vida continua ligado)

Análise de energia:
  Saída: SUGESTÃO: armazenar energia excedente (4.3 kWh na bateria)
  Bateria ao fim da hora: 84.3 kWh
```

## Autor

Gabriel Tancler Armada · RM 574883 · Turma 1CCOR-2026
