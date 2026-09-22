"""Bot de Telegram: el segundo canal del mismo asistente (Parte H).

Uso:  python -m app.bot [--simulado]
Comandos:  /start   /fuente   /reset

Este archivo NO contiene lógica del asistente: recibe el texto, llama a
Asistente.responder y entrega la respuesta. Si mañana se cambiara Telegram
por otra cosa, sólo cambiaría este archivo.
"""

import asyncio
import hashlib
import logging
import os
import sys
from datetime import datetime

from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (ApplicationBuilder, CommandHandler, ContextTypes,
                          MessageHandler, filters)

from app.asistente import construir_asistente

LIMITE_TELEGRAM = 4096

BIENVENIDA = (
    "Asistente del Reglamento de Estudiantes del TecNM.\n\n"
    "Te respondo dudas sobre el Reglamento citando el artículo y la fracción "
    "exactos, y te digo cuando un tema no está en él.\n\n"
    "No soy autoridad del plantel: esto es informativo y no sustituye a la "
    "Dirección ni a Servicios Escolares.\n\n"
    "Privacidad: no escribas datos personales tuyos ni de nadie más. Tus "
    "mensajes pasan por los servidores de Telegram y de Google.\n\n"
    "Comandos: /fuente  /reset"
)

PRIVADO = (
    "Este bot es privado y sólo atiende a usuarios autorizados.\n"
    "Tu identificador de Telegram es: %d"
)

PROBLEMA = (
    "No pude obtener respuesta del modelo en este momento. "
    "Vuelve a intentarlo en un rato; tu pregunta no quedó guardada."
)


# --- funciones puras: sin red, se prueban en pruebas/prueba_citas.py ---

def leer_permitidos(texto):
    """Convierte '123, 456' en {123, 456}. Vacío = nadie autorizado."""
    permitidos = set()
    for parte in (texto or "").split(","):
        parte = parte.strip()
        if parte.lstrip("-").isdigit():
            permitidos.add(int(parte))
    return permitidos


def partir_mensaje(texto, limite=LIMITE_TELEGRAM):
    """Parte el texto en trozos de a lo más `limite`, cortando en salto de línea."""
    if len(texto) <= limite:
        return [texto]
    trozos = []
    resto = texto
    while len(resto) > limite:
        corte = resto.rfind("\n", 0, limite + 1)
        if corte <= 0:
            corte = limite
        trozos.append(resto[:corte])
        resto = resto[corte:].lstrip("\n")
    if resto:
        trozos.append(resto)
    return trozos


def usuario_anonimo(user_id):
    """Primeros 10 caracteres del SHA-256 del identificador. Nunca el real."""
    return hashlib.sha256(str(user_id).encode()).hexdigest()[:10]


# --- ayudantes ---

def autorizado(update, context):
    return update.effective_user.id in context.application.bot_data["permitidos"]


def asistente_de(chat_id, context):
    """Un Asistente por conversación: dos personas no comparten memoria."""
    datos = context.application.bot_data
    if chat_id not in datos["asistentes"]:
        datos["asistentes"][chat_id] = construir_asistente(
            datos["simulado"], corrida=datos["corrida"])
    return datos["asistentes"][chat_id]


async def enviar(mensaje, texto):
    """Entrega el texto en trozos que Telegram acepte."""
    for trozo in partir_mensaje(texto, LIMITE_TELEGRAM):
        await mensaje.reply_text(trozo)


async def con_escribiendo(chat, funcion, *args, **opciones):
    """Corre una función lenta en otro hilo sin congelar el bot (Anexo C.3)."""
    tarea = asyncio.ensure_future(asyncio.to_thread(funcion, *args, **opciones))
    while not tarea.done():
        await chat.send_action(ChatAction.TYPING)
        await asyncio.wait([tarea], timeout=4)
    return tarea.result()


# --- manejadores ---

async def inicio(update, context):
    if not autorizado(update, context):
        await update.effective_message.reply_text(PRIVADO % update.effective_user.id)
        return
    await update.effective_message.reply_text(BIENVENIDA)


async def fuente(update, context):
    if not autorizado(update, context):
        await update.effective_message.reply_text(PRIVADO % update.effective_user.id)
        return
    asistente = asistente_de(update.effective_chat.id, context)
    await update.effective_message.reply_text(asistente.fuente())


async def reiniciar(update, context):
    if not autorizado(update, context):
        await update.effective_message.reply_text(PRIVADO % update.effective_user.id)
        return
    asistente_de(update.effective_chat.id, context).reset()
    await update.effective_message.reply_text("Memoria borrada.")


async def pregunta(update, context):
    if not autorizado(update, context):
        await update.effective_message.reply_text(PRIVADO % update.effective_user.id)
        return

    datos = context.application.bot_data
    asistente = asistente_de(update.effective_chat.id, context)
    datos["turno"] += 1
    identificador = "TG-%d" % datos["turno"]
    extra = {"canal": "telegram", "usuario": usuario_anonimo(update.effective_user.id)}

    try:
        resultado = await con_escribiendo(
            update.effective_chat, asistente.responder,
            update.effective_message.text, identificador, extra)
    except Exception:
        datos["turno"] -= 1
        await update.effective_message.reply_text(PROBLEMA)
        return

    await enviar(update.effective_message, resultado["texto"])


def main(argumentos):
    load_dotenv()
    logging.basicConfig(level=logging.WARNING)
    # La URL de Telegram lleva el token dentro: en INFO se imprimiría en pantalla.
    logging.getLogger("httpx").setLevel(logging.WARNING)

    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    if not token:
        print("Falta TELEGRAM_BOT_TOKEN en el archivo .env")
        return 2

    permitidos = leer_permitidos(os.environ.get("TELEGRAM_USUARIOS_PERMITIDOS", ""))
    if not permitidos:
        print("Aviso: TELEGRAM_USUARIOS_PERMITIDOS está vacío; el bot no atenderá a nadie.")
        print("Escríbele al bot y te dirá tu identificador para que lo agregues al .env.")

    aplicacion = ApplicationBuilder().token(token).build()
    aplicacion.bot_data.update({
        "asistentes": {},
        "permitidos": permitidos,
        "simulado": "--simulado" in argumentos,
        "corrida": datetime.now().strftime("%Y%m%d-%H%M%S"),
        "turno": 0,
    })
    aplicacion.add_handler(CommandHandler("start", inicio))
    aplicacion.add_handler(CommandHandler("fuente", fuente))
    aplicacion.add_handler(CommandHandler("reset", reiniciar))
    aplicacion.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, pregunta))

    print("Bot en marcha (%s). Autorizados: %d. Ctrl+C para detener."
          % ("simulado" if "--simulado" in argumentos else "real", len(permitidos)))
    aplicacion.run_polling()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))