"""Citas verificables (Parte D).

El prompt le pide al modelo que cite con un formato exacto; este módulo es
el que comprueba, con código, que esas citas existan de verdad.
"""

import re

# Art. 9  |  Artículo 9  |  art. 9                        -> "9"
# Art. 9, fracc. II  |  artículo 9 fracción ii            -> "9.II"
# Art. 14, numeral 3  |  artículo 14 numeral 3            -> "14.3"
PATRON_CITA = re.compile(
    r"\b(?:art[íi]culo|art\.?)\s*(\d+)"
    r"(?:"
    r"\s*,?\s*(?:fracc\.|fracci[óo]n|fracc\b)\s*([IVXLCDM]+)\b"
    r"|"
    r"\s*,?\s*numeral\s*(\d+)\b"
    r")?",
    re.IGNORECASE,
)


def extraer_citas(texto):
    """Devuelve las citas del texto, en orden de aparición y sin repetir."""
    citas = []
    for articulo, romana, numeral in PATRON_CITA.findall(texto):
        if romana:
            clave = "%s.%s" % (articulo, romana.upper())
        elif numeral:
            clave = "%s.%s" % (articulo, numeral)
        else:
            clave = articulo
        if clave not in citas:
            citas.append(clave)
    return citas


def validar_citas(citas, indice):
    """Separa las citas en las que existen en el índice y las que no."""
    return {
        "validas": [c for c in citas if c in indice],
        "invalidas": [c for c in citas if c not in indice],
    }