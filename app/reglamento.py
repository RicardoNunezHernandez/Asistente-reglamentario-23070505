"""El Reglamento dentro del prompt (Parte A).

El JSON del docente tiene 22 artículos y 104 fracciones. Cada artículo trae
siempre 'numero', 'titulo' y 'encabezado'; 'fracciones' y 'cierre' sólo
aparecen en los artículos que las tienen.
"""

import json


def cargar_reglamento(ruta):
    """Lee el JSON del Reglamento y lo devuelve como diccionario."""
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def texto_para_prompt(reglamento):
    """Devuelve el Reglamento como texto, una línea por cita posible.

    El formato de cada línea es el mismo con el que el modelo debe citar.
    """
    lineas = [reglamento["documento"].upper()]
    titulo_anterior = None
    for art in reglamento["articulos"]:
        titulo = art["titulo"]
        if titulo != titulo_anterior:
            lineas.append("")
            lineas.append(titulo.upper())
            titulo_anterior = titulo
        numero = art["numero"]
        lineas.append("Art. %s. %s" % (numero, art["encabezado"]))
        for fraccion in art.get("fracciones", []):
            lineas.append("Art. %s, fracc. %s. %s" % (numero, fraccion["id"], fraccion["texto"]))
        if "cierre" in art:
            lineas.append("Art. %s (párrafo final). %s" % (numero, art["cierre"]))
    if reglamento.get("transitorios"):
        lineas.append("")
        lineas.append("TRANSITORIOS")
        for t in reglamento["transitorios"]:
            lineas.append("%s. %s" % (t["id"], t["texto"]))
    return "\n".join(lineas)


def indice_citas(reglamento):
    """Devuelve el conjunto de claves de cita que existen: '9', '9.II', '14.3'."""
    indice = set()
    for art in reglamento["articulos"]:
        numero = str(art["numero"])
        indice.add(numero)
        for fraccion in art.get("fracciones", []):
            indice.add("%s.%s" % (numero, fraccion["id"]))
    return indice