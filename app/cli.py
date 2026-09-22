"""Chat del asistente en la terminal (Parte C).

Uso:   python -m app.cli [--simulado]
Comandos:  /fuente   /reset   /salir
"""

import sys

from dotenv import load_dotenv

from app.asistente import Asistente
from app.modelo_simulado import ModeloSimulado

AVISO = (
    "Asistente del Reglamento de Estudiantes del TecNM.\n"
    "Es informativo: no sustituye a las autoridades del plantel.\n"
    "Comandos: /fuente  /reset  /salir"
)

PROBLEMA = (
    "\nNo pude obtener respuesta del modelo (%s).\n"
    "Revisa tu conexión y la clave GEMINI_API_KEY de tu archivo .env.\n"
    "Si el mensaje menciona GenerateRequestsPerDay, la cuota diaria ya se agotó\n"
    "y se renueva mañana. Tu pregunta no quedó guardada en la memoria."
)


def construir_asistente(simulado):
    """Arma el asistente con el modelo falso o con el real."""
    if simulado:
        return Asistente(ModeloSimulado(), modo="simulado")
    # Se importa aquí y no arriba para que --simulado no necesite la clave.
    from app.modelo import llamar_modelo
    return Asistente(llamar_modelo, modo="real")


def main(argumentos):
    load_dotenv()
    simulado = "--simulado" in argumentos
    asistente = construir_asistente(simulado)

    print(AVISO)
    print("Modo: %s | memoria: %d mensajes | bitácora: %s"
          % (asistente.modo, asistente.max_mensajes, asistente.ruta_log))

    turno = 0
    while True:
        try:
            pregunta = input("\nTú> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nHasta luego.")
            return 0

        if not pregunta:
            continue
        if pregunta == "/salir":
            print("Hasta luego.")
            return 0
        if pregunta == "/fuente":
            print(asistente.fuente())
            continue
        if pregunta == "/reset":
            asistente.reset()
            print("Memoria borrada.")
            continue

        turno += 1
        try:
            resultado = asistente.responder(pregunta, identificador="CLI-%d" % turno)
        except Exception as error:
            turno -= 1
            print(PROBLEMA % type(error).__name__)
            continue

        print()
        print(resultado["texto"])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))