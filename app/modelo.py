"""La única función del programa que habla con Gemini (Parte B).

Ningún otro archivo del proyecto importa google.genai. Si mañana el curso
cambiara de proveedor, sólo habría que reescribir este archivo.
"""

import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

MODELO_POR_OMISION = "gemini-3.5-flash"
ROLES_SDK = {"usuario": "user", "modelo": "model"}

_cliente = None


def _obtener_cliente():
    """Crea el cliente una sola vez, y sólo cuando de verdad se va a usar.

    Se crea aquí y no al importar el módulo para que `--simulado` funcione
    en una máquina sin GEMINI_API_KEY.
    """
    global _cliente
    if _cliente is None:
        _cliente = genai.Client(
            api_key=os.environ["GEMINI_API_KEY"],
            http_options=types.HttpOptions(
                retry_options=types.HttpRetryOptions(
                    attempts=5, initial_delay=2.0, max_delay=30.0
                )
            ),
        )
    return _cliente


def a_formato_sdk(historial):
    """Convierte los mensajes del contrato al formato del SDK."""
    return [
        types.Content(role=ROLES_SDK[m["rol"]], parts=[types.Part(text=m["texto"])])
        for m in historial
    ]


def llamar_modelo(historial, sistema):
    """Una llamada a Gemini. Devuelve texto y tokens según el contrato."""
    nombre = os.environ.get("GEMINI_MODEL", MODELO_POR_OMISION)
    respuesta = _obtener_cliente().models.generate_content(
        model=nombre,
        contents=a_formato_sdk(historial),
        config=types.GenerateContentConfig(system_instruction=sistema),
    )
    uso = respuesta.usage_metadata
    pensamiento = getattr(uso, "thoughts_token_count", 0) or 0
    return {
        "texto": respuesta.text or "",
        "tokens_entrada": uso.prompt_token_count or 0,
        "tokens_salida": (uso.candidates_token_count or 0) + pensamiento,
        "modelo": nombre,
    }