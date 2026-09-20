"""Memoria corta de la conversación (Parte C).

Un mensaje es un diccionario {"rol": "usuario" | "modelo", "texto": str}.
El historial es una lista de mensajes.
"""

ROLES_VALIDOS = ("usuario", "modelo")


def agregar(historial, rol, texto):
    """Agrega un mensaje al final del historial.

    Modifica la lista recibida y no devuelve nada (contrato: -> None).
    """
    if rol not in ROLES_VALIDOS:
        raise ValueError(
            "rol inválido: %r. Use 'usuario' o 'modelo'." % (rol,)
        )
    historial.append({"rol": rol, "texto": texto})


def recortar(historial, max_mensajes):
    """Devuelve una lista NUEVA con los últimos max_mensajes mensajes.

    Si el primer mensaje del recorte es del modelo, se descarta: la
    conversación que se envía al modelo debe empezar con el usuario.
    Nunca modifica el historial original.
    """
    if max_mensajes <= 0:
        return []
    recorte = historial[-max_mensajes:]
    if recorte and recorte[0]["rol"] == "modelo":
        recorte = recorte[1:]
    return recorte


def quitar_ultimo(historial):
    """Quita el último mensaje del historial.

    Se usa cuando la llamada al modelo falla: la pregunta sin respuesta
    no debe quedarse en la memoria.
    """
    if historial:
        historial.pop()
        