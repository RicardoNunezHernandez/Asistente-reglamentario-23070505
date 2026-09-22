"""Corre el banco de pruebas (Parte F).

Uso:  python -m app.lote data/preguntas_prueba.json [--simulado] [--solo R05,C1]

Cada pregunta suelta empieza con la memoria vacía; los turnos de una
conversación la comparten. Entre llamadas reales espera 4 segundos.
Si un turno falla, se registra en la bitácora y el lote sigue; si el que
falla es de una conversación, se omiten los turnos que le seguían.
"""

import json
import sys
import time

from dotenv import load_dotenv

from app.asistente import construir_asistente

ESPERA_REAL = 4


def parsear(argumentos):
    """Separa la ruta del banco, el modo y los identificadores de --solo."""
    ruta, solo, simulado = None, None, False
    n = 0
    while n < len(argumentos):
        actual = argumentos[n]
        if actual == "--simulado":
            simulado = True
        elif actual == "--solo" and n + 1 < len(argumentos):
            solo = {x.strip() for x in argumentos[n + 1].split(",") if x.strip()}
            n += 1
        elif actual.startswith("--solo="):
            solo = {x.strip() for x in actual.split("=", 1)[1].split(",") if x.strip()}
        elif not actual.startswith("--") and ruta is None:
            ruta = actual
        n += 1
    return ruta, solo, simulado


def seleccionar(banco, solo):
    """Filtra preguntas sueltas y conversaciones completas por identificador."""
    preguntas = banco.get("preguntas", [])
    conversaciones = banco.get("conversaciones", [])
    if solo is not None:
        preguntas = [p for p in preguntas if p["id"] in solo]
        conversaciones = [c for c in conversaciones if c["id"] in solo]
    return preguntas, conversaciones


def linea(identificador, resultado):
    evento = resultado["evento"]
    marca = "!" if evento["citas_invalidas"] else " "
    return "%-6s %s citas=%-22s enviados=%d  ent=%-6d sal=%-5d %.2fs" % (
        identificador, marca, ",".join(evento["citas"]) or "-",
        evento["mensajes_enviados"], evento["tokens_entrada"],
        evento["tokens_salida"], evento["segundos"],
    )


def main(argumentos):
    load_dotenv()
    ruta, solo_valores, simulado = parsear(argumentos)
    if ruta is None:
        print("Uso: python -m app.lote data/preguntas_prueba.json [--simulado] [--solo R05,C1]")
        return 2

    with open(ruta, encoding="utf-8") as f:
        banco = json.load(f)
    preguntas, conversaciones = seleccionar(banco, solo_valores)

    asistente = construir_asistente(simulado)
    print("Modo: %s | bitácora: %s" % (asistente.modo, asistente.ruta_log))
    print("%d preguntas sueltas y %d conversaciones" % (len(preguntas), len(conversaciones)))
    print()

    primera = True
    fallos = 0

    for pregunta in preguntas:
        asistente.reset()
        if not primera and not simulado:
            time.sleep(ESPERA_REAL)
        primera = False
        try:
            resultado = asistente.responder(pregunta["pregunta"], identificador=pregunta["id"])
            print(linea(pregunta["id"], resultado))
        except Exception as error:
            fallos += 1
            print("%-6s ERROR %s: %s" % (pregunta["id"], type(error).__name__, error))

    for conversacion in conversaciones:
        asistente.reset()
        for numero, turno in enumerate(conversacion["turnos"], 1):
            identificador = "%s-%d" % (conversacion["id"], numero)
            if not primera and not simulado:
                time.sleep(ESPERA_REAL)
            primera = False
            try:
                resultado = asistente.responder(turno, identificador=identificador)
                print(linea(identificador, resultado))
            except Exception as error:
                fallos += 1
                print("%-6s ERROR %s: %s" % (identificador, type(error).__name__, error))
                print("%-6s se omiten los turnos restantes de %s" % ("", conversacion["id"]))
                break

    print()
    print("Turnos con error: %d. Bitácora: %s" % (fallos, asistente.ruta_log))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))