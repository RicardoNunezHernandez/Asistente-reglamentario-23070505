"""Pruebas sin red (Parte D).

Se ejecuta con:  python -m pruebas.prueba_citas
Usa assert; no hace falta pytest. Imprime OK al final.
"""

from app.citas import extraer_citas, validar_citas
from app.memoria import agregar, recortar
from app.reglamento import cargar_reglamento, indice_citas, texto_para_prompt

RUTA = "data/reglamento_estudiantes_tecnm.json"
reglamento = cargar_reglamento(RUTA)
indice = indice_citas(reglamento)
texto = texto_para_prompt(reglamento)

# --- El índice de citas (seccion 5.3) ---
assert len(indice) == 126
assert "9" in indice
assert "9.II" in indice
assert "14.3" in indice
assert "31.II" not in indice
assert "9.XIII" not in indice

# --- Dos lineas concretas de texto_para_prompt (seccion 5.2) ---
assert texto.startswith("REGLAMENTO DE ESTUDIANTES DEL TECNOLÓGICO NACIONAL DE MÉXICO")
assert "Art. 9, fracc. I. Amonestación verbal o por escrito de la conducta o acto cometido;" in texto
assert "TÍTULO TERCERO. DE LAS SANCIONES" in texto
assert "Art. 9 (párrafo final)." in texto
assert "Art. 14, fracc. 3." in texto

# --- Los tres formatos de extraer_citas (seccion 8.1) ---
assert extraer_citas("Art. 9") == ["9"]
assert extraer_citas("Artículo 9") == ["9"]
assert extraer_citas("artículo 9") == ["9"]
assert extraer_citas("Art. 9, fracc. II") == ["9.II"]
assert extraer_citas("Artículo 9 fracción II") == ["9.II"]
assert extraer_citas("art. 9, fracc. ii") == ["9.II"]
assert extraer_citas("Art. 14, numeral 3") == ["14.3"]
assert extraer_citas("artículo 14 numeral 3") == ["14.3"]

# --- Orden de aparicion, sin repetir, y texto sin citas ---
assert extraer_citas("Art. 8 y luego Art. 7") == ["8", "7"]
assert extraer_citas("Art. 9, fracc. I; Art. 9, fracc. I") == ["9.I"]
assert extraer_citas("No consta en el Reglamento de Estudiantes") == []

# --- validar_citas con validas e invalidas (seccion 8.2) ---
resultado = validar_citas(["9.II", "31.II", "7"], indice)
assert resultado["validas"] == ["9.II", "7"]
assert resultado["invalidas"] == ["31.II"]
assert validar_citas([], indice) == {"validas": [], "invalidas": []}

# --- La memoria corta (seccion 7.1) ---
historial = []
agregar(historial, "usuario", "u1")
agregar(historial, "modelo", "m1")
agregar(historial, "usuario", "u2")
assert historial[0] == {"rol": "usuario", "texto": "u1"}
assert recortar(historial, 0) == []
assert recortar(historial, -1) == []
assert [m["texto"] for m in recortar(historial, 2)] == ["u2"]
assert len(historial) == 3

# --- Aqui van los casos de SU traza (Partes E.1 y E.2) ---
# TODO: agregue un assert por cada uno de los textos T1..T6 de la traza E.2
# TODO: agregue los cuatro recortes de la traza E.1 (max_mensajes = 4)

# --- Aqui van las tres funciones puras del bot (seccion 12.3, Parte H) ---
# TODO: leer_permitidos, partir_mensaje y usuario_anonimo

print("OK")