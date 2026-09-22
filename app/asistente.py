"""Une todo: una pregunta entra, una respuesta revisada sale.

La terminal (cli.py), el lote (lote.py) y el bot de Telegram (bot.py) usan
este mismo Asistente. Ninguno de ellos arma prompts, recorta memoria ni
extrae citas por su cuenta.
"""

import json
import os
import time
from datetime import datetime

from app.citas import extraer_citas, validar_citas
from app.memoria import agregar, quitar_ultimo, recortar
from app.reglamento import cargar_reglamento, indice_citas, texto_para_prompt

MARCA_NO_CONSTA = "no consta en el reglamento"
PLANTILLA_AVISO = "[Aviso] Estas citas no existen en el Reglamento: %s"

CAMPOS = ["ts", "corrida", "modo", "id", "pregunta", "respuesta", "citas",
          "citas_invalidas", "no_consta", "mensajes_enviados", "tokens_entrada",
          "tokens_salida", "modelo", "segundos"]


class Asistente:
    """Un turno de conversación: agregar, recortar, llamar, verificar, registrar."""

    def __init__(self, llamar, modo="real",
                 ruta_reglamento="data/reglamento_estudiantes_tecnm.json",
                 ruta_sistema="prompts/sistema.md",
                 max_mensajes=None, carpeta_logs="logs", corrida=None):
        self.llamar = llamar
        self.modo = modo
        self.reglamento = cargar_reglamento(ruta_reglamento)
        self.indice = indice_citas(self.reglamento)
        with open(ruta_sistema, encoding="utf-8") as f:
            plantilla = f.read()
        self.sistema = plantilla.replace("{REGLAMENTO}", texto_para_prompt(self.reglamento))
        if max_mensajes is None:
            max_mensajes = int(os.environ.get("MAX_MENSAJES", "6"))
        self.max_mensajes = max_mensajes
        self.historial = []
        self.corrida = corrida or datetime.now().strftime("%Y%m%d-%H%M%S")
        os.makedirs(carpeta_logs, exist_ok=True)
        self.ruta_log = os.path.join(carpeta_logs, "corrida-%s.jsonl" % self.corrida)

    # --- comandos ---

    def fuente(self):
        """Qué documento se consulta y cuándo se aprobó (comando /fuente)."""
        return "%s\nAprobado el %s\nDifusión: %s" % (
            self.reglamento["documento"],
            self.reglamento["aprobacion"],
            self.reglamento["difusion"],
        )

    def reset(self):
        """Borra la memoria de la conversación (comando /reset)."""
        self.historial = []

    # --- bitácora ---

    def _anotar(self, evento):
        with open(self.ruta_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(evento, ensure_ascii=False) + "\n")

    # --- un turno ---

    def responder(self, pregunta, identificador=None, extra=None):
        """Devuelve {'texto', 'evento', 'validacion'} y escribe una línea de bitácora."""
        agregar(self.historial, "usuario", pregunta)
        enviados = recortar(self.historial, self.max_mensajes)

        inicio = time.time()
        try:
            respuesta = self.llamar(enviados, self.sistema)
        except Exception as error:
            quitar_ultimo(self.historial)
            evento = dict.fromkeys(CAMPOS)
            evento.update({
                "ts": datetime.now().isoformat(timespec="seconds"),
                "corrida": self.corrida,
                "modo": self.modo,
                "id": identificador,
                "pregunta": pregunta,
                "mensajes_enviados": len(enviados),
                "segundos": round(time.time() - inicio, 2),
                "error": "%s: %s" % (type(error).__name__, error),
            })
            if extra:
                evento.update(extra)
            self._anotar(evento)
            raise

        segundos = round(time.time() - inicio, 2)
        texto = respuesta["texto"]
        agregar(self.historial, "modelo", texto)

        citas = extraer_citas(texto)
        validacion = validar_citas(citas, self.indice)

        mostrado = texto
        if validacion["invalidas"]:
            mostrado += "\n\n" + PLANTILLA_AVISO % ", ".join(validacion["invalidas"])

        evento = {
            "ts": datetime.now().isoformat(timespec="seconds"),
            "corrida": self.corrida,
            "modo": self.modo,
            "id": identificador,
            "pregunta": pregunta,
            "respuesta": texto,
            "citas": citas,
            "citas_invalidas": validacion["invalidas"],
            "no_consta": MARCA_NO_CONSTA in texto.lower(),
            "mensajes_enviados": len(enviados),
            "tokens_entrada": respuesta["tokens_entrada"],
            "tokens_salida": respuesta["tokens_salida"],
            "modelo": respuesta["modelo"],
            "segundos": segundos,
        }
        if extra:
            evento.update(extra)
        self._anotar(evento)
        return {"texto": mostrado, "evento": evento, "validacion": validacion}