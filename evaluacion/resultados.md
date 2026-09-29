# Resultados de la corrida real · Práctica 3 · Unidad 1

- **Alumno:** Ricardo Nuñez Hernandez
- **Número de control:** 23070505
- **Modelo:** `gemini-3.5-flash-lite`
- **Bitácoras:** `logs/corrida-20260928-2301*.jsonl` en adelante (los 18 turnos), más
  `logs/corrida-20260928-2215*.jsonl` y `2219`, que guardan el primer intento con
  `gemini-3.5-flash` y sus fallos por 503 y 429.

## Nota sobre el modelo

La práctica pide `gemini-3.5-flash`. El primer intento se hizo con ese modelo y sólo
`R01` alcanzó a responder: el servidor devolvió 503 UNAVAILABLE de forma repetida y,
como cada llamada agota sus reintentos, la cuota diaria de 20 peticiones se consumió
con una sola respuesta útil. Es exactamente el escenario que advierte la sección 3.1
del documento. `gemini-3.8-flash` devolvió el mismo 503 y `gemini-2.5-flash-lite`
devolvió 404 («no longer available to new users», con recomendación explícita de usar
`gemini-3.5-flash-lite`). La corrida completa se hizo entonces con
**`gemini-3.5-flash-lite`**, y `R01` se repitió con él para que los 18 turnos sean
comparables entre sí.

Dato útil: los tokens de entrada son prácticamente idénticos entre `gemini-3.5-flash`
(6,533 en `R01`) y `gemini-3.5-flash-lite` (6,533 en el mismo `R01`). El tokenizador es
el mismo, así que el costo de entrada no depende del modelo sino del Reglamento que se
envía. Lo que sí cambia es la salida: 816 tokens contra 53 para la misma pregunta,
porque el modelo `lite` «piensa» mucho menos antes de responder.

## 1. Los 18 turnos

| id | Cita esperada | Citas obtenidas | Citas inválidas | ¿Correcta? | Tokens de entrada |
|----|---------------|-----------------|-----------------|------------|-------------------|
| R01 | Art. 7, fracc. XV | 7.XV | — | sí | 6533 |
| R02 | Art. 8, fracc. VIII; Art. 9 | 8.VIII, 9, 12 | — | sí | 6535 |
| R03 | Art. 9, fracc. II | 9.II | — | sí | 6536 |
| R04 | Art. 15 | 15 | — | sí | 6538 |
| R05 | Art. 12 | 12 | — | sí | 6531 |
| R06 | Art. 2, fracc. XIII; Art. 3 | 2.XIII, 3 | — | sí | 6534 |
| R07 | Art. 19, fracc. III | 19.III | — | sí | 6538 |
| R08 | no consta | (ninguna) · `no_consta: true` | — | sí | 6535 |
| R09 | no consta | (ninguna) · `no_consta: true` | — | sí | 6531 |
| R10 | fuera de alcance / no consta | (ninguna) · `no_consta: true` | — | sí | 6530 |
| R11 | Art. 8, fracc. VI; Art. 7, fracc. XVIII; Art. 13 | 6.XVI, 6.XVII, 7.XVIII, 8.VI, 13, 14 | — | sí | 6539 |
| R12 | Art. 7, fracc. XX; Art. 8, fracc. XVII | 7.XX | — | **parcial** | 6541 |
| C1-1 | Art. 9 | 9.I, 9.II, 9.III, 9.IV, 9.V | — | sí | 6526 |
| C1-2 | Art. 9, fracc. V | 9.V | — | sí | 6630 |
| C1-3 | Art. 15; Art. 17 | 15 | — | **parcial** | 6679 |
| C2-1 | Art. 8, fracc. II | 8.II | — | sí | 6531 |
| C2-2 | Art. 8, fracc. II | 8.II | — | sí | 6583 |
| C2-3 | Art. 10 | 10, 10.I, 10.II, 10.III, 10.IV, 10.V | — | sí | 6646 |

Criterio: se cuenta **correcta** si cita lo esperado sin citas inválidas, o si dice
«no consta» / «fuera de alcance» cuando debía. **Parcial** si cita una parte del
fundamento esperado y omite otra, sin inventar nada.

## 2. Totales

| | |
|---|---|
| Correctas | **16** de 18 |
| Parciales | **2** (R12 y C1-3) |
| Incorrectas | **0** |
| **Citas inválidas** | **0** en los 18 turnos |

Cero citas inválidas es el resultado central de la práctica: en 18 respuestas, el
modelo no escribió ni un artículo ni una fracción que no existiera en el Reglamento.
El aviso de `validar_citas` nunca tuvo que dispararse. Conviene no confundir eso con
suerte: el modelo simulado sí produce `Art. 31, fracc. II` y la verificación lo marca,
así que sabemos que el mecanismo funciona y que simplemente no hubo nada que marcar.

Las tres preguntas cuyo tema no está en el Reglamento (R08 faltas, R09 exámenes
extraordinarios, R10 horario de cafetería) se resolvieron las tres con
`no_consta: true` y sin ninguna cita. El asistente no inventó un porcentaje de
asistencia ni un horario, que es justo lo que esas preguntas venían a probar.

Las cuatro preguntas que sólo se entienden con memoria funcionaron: `C1-2` («¿y cuál
es la más grave?») citó `9.V` recibiendo 3 mensajes, y `C2-2` («¿y si tengo un permiso
por escrito?») citó `8.II` recibiendo 3. Sin el recorte enviado, ninguna de las dos
tendría antecedente.

## 3. Tokens

| | |
|---|---|
| Tokens de entrada, promedio por llamada | **6,556** |
| Tokens de entrada, total de la corrida | **118,016** |
| Tokens de salida, promedio | 61 |
| Tokens de salida, total | 1,105 |
| **Total de la corrida** | **119,121** |
| Rango de entrada | 6,526 (C1-1) a 6,679 (C1-3) |
| Segundos por llamada, promedio | 10.4 |

Los tokens de entrada son casi constantes porque **el 99 % de cada llamada es el
Reglamento**: el prompt de sistema con el documento sustituido ocupa 27,204 caracteres,
y la pregunta del usuario son unas pocas decenas. La variación de 153 tokens entre el
turno más barato y el más caro es, entera, la memoria corta acumulada dentro de las
conversaciones.

**Proporción medida: 4.169 caracteres por token** (27,204 caracteres → 6,526 tokens en
el turno con la memoria más corta).

## 4. Estimación para el Manual de Lineamientos

El Manual de Lineamientos Académico-Administrativos tiene unos **334,000 caracteres**.
Con la proporción medida arriba:

```
334,000 caracteres ÷ 4.169 caracteres/token ≈ 80,124 tokens
```

Agregarlo al prompt llevaría cada pregunta de **~6,526 a ~86,650 tokens de entrada**,
es decir **13.3 veces más caro**. Los 18 turnos del banco pasarían de 118,016 tokens a
aproximadamente **1,559,694**.

**Dos problemas que aparecerían:**

1. **El costo y la cuota se vuelven prohibitivos.** Una sola pregunta consumiría más
   tokens de entrada que los 18 turnos actuales juntos. En la capa gratuita, donde ya
   fue difícil completar 18 llamadas por saturación, la corrida sería directamente
   imposible; en una capa de pago, cada pregunta costaría trece veces más y tardaría
   bastante más en responder, porque el modelo tiene que leer el prompt completo antes
   de empezar a escribir.

2. **La precisión de las citas se degradaría.** Hoy el modelo tiene 126 citas posibles
   a la vista, en un documento corto y bien estructurado, y acertó 16 de 18 sin inventar
   nada. Con 361,000 caracteres, el artículo relevante queda enterrado entre cientos de
   páginas que hablan de otra cosa, y aparece un riesgo nuevo: **confundir de qué
   documento viene cada regla**. El asistente podría citar un artículo del Reglamento
   para responder algo que en realidad regula el Manual, o al revés. Mi verificación
   no lo detectaría, porque el número de artículo existiría.

**La alternativa de diseño que los evita:** dejar de mandar todo el documento y
**recuperar sólo lo pertinente**. Se indexan los dos documentos por artículo o por
sección, y ante cada pregunta se buscan primero los fragmentos relevantes —por
palabras clave o por similitud semántica— y se envían únicamente ésos, con la etiqueta
del documento del que salieron. El prompt vuelve a pesar unos pocos miles de tokens,
la cita queda anclada a su fuente, y el índice de validación puede cubrir los dos
documentos por separado. El costo es que ahora hay que acertar en la búsqueda: si el
recuperador no trae el artículo correcto, el modelo no puede citarlo aunque exista.
Es el diseño que el proyecto de la unidad exige con los 22,900 negocios del DENUE,
que no caben en ningún prompt.

## 5. La respuesta más débil de la corrida

**R12** — *«Copié un programa de internet para una tarea sin decir de dónde era. ¿El
reglamento dice algo?»*. Citó `Art. 7, fracc. XX`, que es la obligación de evitar el
plagio, pero **omitió `Art. 8, fracc. XVII`**, que convierte el quebrantamiento de los
derechos de propiedad intelectual en conducta prohibida, y por tanto sancionable. La
respuesta es cierta pero se queda corta en lo que más le importa a quien pregunta: no
sólo estás incumpliendo una obligación, estás incurriendo en una conducta que tiene
sanción prevista.

**¿De quién fue el problema?**

- **Del código, no.** `extraer_citas` reconoce el formato y habría extraído `8.XVII`
  si el modelo lo hubiera escrito; `validar_citas` no marcó nada porque no había nada
  falso que marcar. El código hizo su trabajo: verificar. No es su trabajo completar.
- **Del prompt, en parte.** La regla 2 pide citar toda afirmación normativa, pero no
  pide explícitamente **conectar la obligación con la conducta prohibida y la sanción**
  cuando la pregunta es sobre las consecuencias de un acto. Una regla que dijera «si la
  pregunta es sobre una falta, cita la obligación, la conducta prohibida y la sanción
  aplicable» probablemente lo habría arreglado.
- **Del modelo, sobre todo.** Y se sabe porque en `R02` —«¿qué pasa si alguien entra
  con un arma?»— **sí** hizo la cadena completa: `8.VIII` (conducta prohibida), `9`
  (sanciones) y `12` (quién las emite). El modelo es capaz de encadenar; en R12
  simplemente se conformó con el primer artículo pertinente que encontró. Sus 53 tokens
  de salida frente a los 76 de R02 apuntan en la misma dirección: menos elaboración.

El mismo diagnóstico aplica a la otra parcial, **C1-3**, que citó `Art. 15` (el plazo
de diez días para el recurso de revisión) pero no `Art. 17` (que el fallo llega en
máximo treinta días y es irrevocable). Contestó la pregunta literal —«¿se puede
apelar?»— y no el contexto útil que la rodea.

## 6. Qué garantiza el código y qué sólo le pide el prompt al modelo

El código **garantiza** que toda cita que aparezca en una respuesta se compare contra
un índice de 126 claves construido desde el JSON, y que cualquier artículo o fracción
inexistente se muestre con un aviso visible y quede registrado en la bitácora. Garantiza
también qué ve el modelo en cada llamada: el Reglamento completo y a lo más
`MAX_MENSAJES` mensajes de historia, empezando siempre por el usuario. Y garantiza que
una llamada fallida no envenene la memoria ni pase inadvertida.

El prompt sólo **pide**: que el modelo cite con el formato exacto, que no invente
números, que responda «no consta» cuando el tema no está, que no juzgue casos personales
y que use los tres renglones. Nada de eso está garantizado —R12 y C1-3 muestran que el
formato se cumple pero la exhaustividad no—, y el hueco que se ve en la traza E.2 con
el texto T6 lo confirma: una cita mal formateada pero verdadera se escapa de las dos
redes, porque el prompt no la impidió y el código no tiene nada falso que marcar.
