# Traza a mano · Práctica 3

- **Alumno:** Ricardo Nuñez Hernandez
- **Número de control:** 23070505

> **Nota de honestidad académica.** La plantilla original indica que esta parte no
> se hace con un asistente de IA. El docente autorizó expresamente, para esta
> entrega, que la práctica completa se desarrollara con asistencia de IA, y así se
> declara también en el README. El contenido de abajo se obtuvo leyendo el código
> de `app/memoria.py` y `app/citas.py` y se comprobó ejecutándolo.

## E.1 La memoria (`max_mensajes = 4`)

Mensajes que se agregan: `u1`, `m1`, `u2`, `m2`, `u3`, `m3`, `u4` y `m4`.

El orden que sigue el asistente en cada turno es: **agregar la pregunta → recortar →
llamar al modelo → agregar la respuesta**. Por eso, en el momento de la llamada `N`,
la respuesta `mN` todavía no existe: el historial siempre tiene un número impar de
mensajes justo antes de llamar.

| Llamada | Lista que recibe el modelo (predicción) | Cantidad | Lo que dio el programa | ¿Coincide? |
|---|---|---|---|---|
| 1 | `[u1]` | 1 | `[u1]` | sí |
| 2 | `[u1, m1, u2]` | 3 | `[u1, m1, u2]` | sí |
| 3 | `[u2, m2, u3]` | 3 | `[u2, m2, u3]` | sí |
| 4 | `[u3, m3, u4]` | 3 | `[u3, m3, u4]` | sí |

Detalle de cada recorte:

- **Llamada 1.** Historial: `[u1]`. Tiene menos de 4 mensajes, así que `historial[-4:]`
  devuelve la lista completa. El primero es del usuario, no se descarta nada.
- **Llamada 2.** Historial: `[u1, m1, u2]`. Sigue teniendo menos de 4, se envía completo.
  El primero es `u1`, del usuario: la regla no actúa.
- **Llamada 3.** Historial: `[u1, m1, u2, m2, u3]`, cinco mensajes. Los últimos cuatro son
  `[m1, u2, m2, u3]` y el primero es del modelo, así que **cae `m1`** y se envían tres.
- **Llamada 4.** Historial: `[u1, m1, u2, m2, u3, m3, u4]`, siete mensajes. Los últimos
  cuatro son `[m2, u3, m3, u4]` y el primero vuelve a ser del modelo: **cae `m2`**.

**Mensajes del historial completo al terminar:** 8 (`u1, m1, u2, m2, u3, m3, u4, m4`).
`recortar` devuelve una lista nueva y nunca borra del historial original, así que el
programa conserva la conversación entera aunque al modelo sólo le lleguen tres mensajes.

**¿Qué recortes cambian por la regla «si el primero es del modelo, se descarta»? ¿Qué habría recibido el modelo sin ella?**

Cambian las llamadas 3 y 4. Las dos primeras no, porque el historial todavía era más
corto que `max_mensajes` y empezaba con `u1`. Sin la regla, la llamada 3 habría recibido
`[m1, u2, m2, u3]` y la 4 `[m2, u3, m3, u4]`: cuatro mensajes cada una, pero empezando
con un mensaje del modelo. Eso es una conversación mal formada — el modelo vería que
«él» habló primero, sin que nadie le hubiera preguntado nada — y la API de Gemini espera
que el primer `Content` enviado tenga el rol `user`. El precio de la regla es enviar un
mensaje menos; la ganancia es que el recorte siempre es una conversación válida.

**En el turno 4, «¿y eso a quién aplica?» se refiere a `u1`. ¿Lo puede entender el modelo? ¿Por qué?**

No. La llamada 4 le envía exactamente `[u3, m3, u4]`, y `u1` no está en esa lista: se
quedó fuera del recorte desde la llamada 3. Para el modelo, esa conversación empieza en
`u3`, así que el «eso» de `u4` no tiene a qué referirse — va a inventar un antecedente o
va a pedir que se lo aclaren. El historial completo sí conserva `u1`, pero eso le sirve
al programa, no al modelo: **lo que no se envía, no existe para el modelo.** Es la
primera de las cuatro ideas de la sección 4 del documento, y aquí se ve el costo exacto
de recortar: memoria más barata a cambio de olvidar lo viejo.

## E.2 Las citas

Datos del Reglamento que hacen falta para juzgar cada cita: el artículo 7 tiene **23**
fracciones (I a XXIII), el 8 tiene **21**, el 9 tiene **5** (I a V), el 14 tiene **4**
numerados con dígitos, y el último artículo del Reglamento es el **22**.

| Texto | `extraer_citas` (predicción) | Inválidas (predicción) | Lo que dio el programa | ¿Coincide? |
|---|---|---|---|---|
| T1 | `['9.II']` | ninguna | `['9.II']`, inválidas `[]` | sí |
| T2 | `['15', '8.VIII']` | ninguna | `['15', '8.VIII']`, inválidas `[]` | sí |
| T3 | `['7.XXV', '23']` | `7.XXV` y `23` | `['7.XXV', '23']`, inválidas `['7.XXV', '23']` | sí |
| T4 | `[]` | ninguna | `[]`, inválidas `[]` | sí |
| T5 | `['14.3']` | ninguna | `['14.3']`, inválidas `[]` | sí |
| T6 | `['7']` | ninguna | `['7']`, inválidas `[]` | sí |

Comentario por texto:

- **T1** es el caso simple: un artículo con fracción, en el formato exacto del prompt.
- **T2** mezcla dos formatos en una frase, «artículo 15» en minúsculas y sin punto, y
  «Art. 8 fracción VIII» sin coma. La expresión regular reconoce los dos y respeta el
  orden de aparición.
- **T3** es el caso que justifica toda la Parte D: las dos citas están bien escritas y
  las dos son falsas. El artículo 7 sólo llega a la fracción XXIII, así que `7.XXV` no
  existe; y el Reglamento termina en el artículo 22, así que `23` tampoco. La regex las
  extrae sin quejarse — a propósito — y es el índice de 126 claves el que las rechaza.
- **T4** no tiene ninguna cita, y el resultado es una lista vacía, no un error.
- **T5** repite la misma cita dos veces, con distinta capitalización. Se devuelve una
  sola vez, porque `extraer_citas` entrega las citas sin repetir. También comprueba que
  el formato `numeral` del artículo 14 se convierte a la clave `14.3`.

**¿Qué hace su código con T6? ¿Su verificación detecta el problema? ¿Qué parte del sistema debería evitar que el modelo escriba así?**

Con T6 (`Art. 7, fracciones XVIII y XXI`) el código devuelve `['7']`: reconoce el
artículo y **pierde las dos fracciones**. Es el comportamiento buscado, no un accidente.
La tabla de la sección 8.1 define tres formatos —`Art. N`, `Art. N, fracc. R` y
`Art. N, numeral R`— y ninguno contempla el plural con varias romanas unidas por «y».
Hay además una trampa técnica: `fracc` es prefijo de `fracciones`, así que una expresión
regular escrita como `fracc\.?\s*([IVXLCDM]+)` mordería la `i` de `iones` y devolvería
una fracción `I` que nadie escribió. Por eso el patrón exige o el punto (`fracc\.`) o
una frontera de palabra (`fracc\b`), y sobre T6 el grupo de la fracción simplemente no
casa.

**Mi verificación no detecta el problema**, y ése es el punto incómodo: `7` existe en el
índice, así que `validar_citas` lo da por bueno y no marca nada. El resultado no es una
cita falsa, es una cita **incompleta**: el estudiante ve «Art. 7» cuando el modelo quiso
decir dos fracciones concretas. Si esas fracciones no existieran, el aviso nunca
aparecería. Es un falso negativo silencioso, y lo dejo documentado en lugar de taparlo.

Lo que debería evitar que el modelo escriba así es **el prompt de sistema**, no el código.
La regla 2 de `prompts/sistema.md` ya lo pide explícitamente: una cita por cada fracción,
separadas por punto y coma, es decir `Art. 7, fracc. XVIII; Art. 7, fracc. XXI`. El
reparto de responsabilidades es el de siempre: el prompt pide el formato y el código
verifica que lo citado exista. Cuando el modelo desobedece el formato sin inventar nada,
se cae entre las dos redes. La alternativa sería ampliar la expresión regular al plural,
pero eso se aleja del contrato escrito y sólo tapa el síntoma; prefiero dejar constancia
del hueco.

## E.3 Los tokens de la conversación C1

| Turno | Mensajes enviados | Tokens de entrada | Tokens de salida |
|---|---|---|---|
| C1-1 | (escriba aquí) | | |
| C1-2 | (escriba aquí) | | |
| C1-3 | (escriba aquí) | | |

**¿Por qué crecen los tokens de entrada? ¿Qué parte de ellos es el Reglamento?**

(escriba aquí)

**¿Qué pasaría en el turno 10 de una conversación larga si `recortar` no existiera?**

(escriba aquí)
