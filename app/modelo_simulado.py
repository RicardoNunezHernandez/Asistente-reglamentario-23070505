"""Modelo simulado con guion fijo (Parte B).

No usa la red ni gasta cuota. Tiene la misma firma y devuelve el mismo
diccionario que app.modelo.llamar_modelo, pero con "modelo": "simulado".
Sirve para desarrollar y depurar el resto del programa cuantas veces
haga falta.
"""

GUION = [
    # 1. Respuesta correcta, con una cita que SI existe en el indice.
    "Respuesta: Sí. El Reglamento te obliga a portar la credencial que te otorga "
    "el TecNM de manera visible, y a mostrarla cuando te la pidan.\n"
    "Fundamento: Art. 7, fracc. XV\n"
    "Confianza: alta",
    # 2. Tema que el Reglamento no trata: no consta, y sin ninguna cita.
    "Respuesta: No consta en el Reglamento de Estudiantes. Ese tema corresponde "
    "al Manual de Lineamientos Académico-Administrativos del TecNM; conviene que "
    "lo consultes en Servicios Escolares de tu plantel.\n"
    "Fundamento: No consta en el Reglamento de Estudiantes\n"
    "Confianza: alta",
    # 3. Cita inventada: el articulo 31 no existe. validar_citas debe marcarla.
    "Respuesta: El plazo para inconformarte corre a partir de que te notifican "
    "la sanción y se presenta por escrito ante la Dirección del plantel.\n"
    "Fundamento: Art. 31, fracc. II\n"
    "Confianza: media",
]


def estimar_tokens(texto):
    """Estimación barata de tokens: un token por cada cuatro caracteres."""
    return len(texto) // 4


class ModeloSimulado:
    """Invocable con la misma firma que llamar_modelo(historial, sistema)."""

    def __init__(self, guion=None):
        self.guion = list(guion) if guion else list(GUION)
        self.llamadas = 0

    def __call__(self, historial, sistema):
        texto = self.guion[self.llamadas % len(self.guion)]
        self.llamadas += 1
        entrada = estimar_tokens(sistema)
        for mensaje in historial:
            entrada += estimar_tokens(mensaje["texto"])
        return {
            "texto": texto,
            "tokens_entrada": entrada,
            "tokens_salida": estimar_tokens(texto),
            "modelo": "simulado",
        }

    def reiniciar(self):
        """Vuelve el guion a su primera respuesta (lo usa /reset)."""
        self.llamadas = 0