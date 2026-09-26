# Asistente del Reglamento de Estudiantes del TecNM

- **Alumno:** Ricardo Nuñez Hernandez
- **Número de control:** 23070505
- **Asignatura:** Desarrollo de Agentes Inteligentes (ACD-2504), grupo 850P-A
- **Docente:** D. C. C. Alejandro Estrada Padilla
- **Trabajo:** Práctica 3 · Unidad 1
- **Entrega:** 30 de septiembre de 2026

## Qué hace

Responde dudas de estudiantes sobre el Reglamento de Estudiantes del Tecnológico
Nacional de México —si hay que traer la credencial, qué sanciones existen, cuánto
tiempo hay para inconformarse— citando el artículo y la fracción exactos, y dice
«No consta en el Reglamento de Estudiantes» cuando el tema no está ahí. Su única
fuente es `data/reglamento_estudiantes_tecnm.json`, que el programa convierte en
texto y mete completo dentro de las instrucciones de sistema de cada llamada a
Gemini: no hay búsqueda ni herramientas.

Lo que lo distingue de pegar el PDF en un chat es que **el código verifica lo que
el modelo responde**. El prompt le pide al modelo que cite con un formato exacto,
pero pedir no es garantizar: `app/citas.py` extrae con expresiones regulares cada
cita de la respuesta, la convierte a una clave (`9`, `9.II`, `14.3`) y la compara
contra un índice de 126 claves construido desde el JSON. Si el modelo inventa un
artículo, la respuesta se muestra igual pero con un aviso agregado por el programa
—`[Aviso] Estas citas no existen en el Reglamento: 31.II`— y la cita falsa queda
registrada en la bitácora. También es el código, y no el modelo, el que decide qué
se recuerda: la memoria corta se recorta a los últimos `MAX_MENSAJES` mensajes antes
de cada llamada.

## Arquitectura

```
Tú> ¿y cuál es la más grave?
 |
 v
memoria.agregar(historial, "usuario", pregunta)
memoria.recortar(historial, MAX_MENSAJES)      <- sólo los últimos mensajes;
 |                                                si el primero es del modelo, se descarta
 v
modelo.llamar_modelo(enviados, sistema)        <- UNA llamada, sin herramientas
 |   sistema = prompts/sistema.md con {REGLAMENTO} sustituido
 |             por reglamento.texto_para_prompt()  (~25,200 caracteres)
 v
memoria.agregar(historial, "modelo", texto)    <- el texto crudo, sin el aviso
 |
 v
citas.extraer_citas(texto) -> citas.validar_citas(citas, indice_citas)
 |   si hay citas inválidas, el código agrega un aviso visible
 v
respuesta en pantalla + una línea JSON en logs/corrida-AAAAMMDD-HHMMSS.jsonl
```

Los tres canales —terminal, lote y Telegram— llaman al mismo `Asistente.responder`.
Ninguno arma prompts, recorta memoria ni extrae citas por su cuenta. Y un solo
archivo, `app/modelo.py`, importa `google.genai`: cambiar de proveedor sería
reescribir ese archivo y nada más.

## Requisitos e instalación

Python 3.11 o superior y una clave de Google AI Studio (gratuita, se genera en
[aistudio.google.com](https://aistudio.google.com)).

```bash
git clone https://github.com/RicardoNunezHernandez/Asistente-reglamentario-23070505.git
cd Asistente-reglamentario-23070505
python -m venv .venv
```

Activar el entorno:

```powershell
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
source .venv/bin/activate
```

Si PowerShell responde `UnauthorizedAccess`, ejecute una sola vez
`Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` y vuelva a
activar. Debe aparecer `(.venv)` al inicio del prompt.

```bash
pip install -r requirements.txt
```

Después, copie el archivo de ejemplo y escriba su clave:

```powershell
copy .env.example .env      # Windows
cp .env.example .env        # macOS / Linux
```

Para comprobar la instalación sin gastar cuota:

```bash
python -m pruebas.prueba_citas                                   # debe imprimir OK
python -m app.lote data/preguntas_prueba.json --simulado         # 18 turnos simulados
```

## Variables de entorno

Van en `.env`, que **no se sube al repositorio**: está listado en `.gitignore` junto
con `.venv/` y `__pycache__/`. En el repositorio sólo viaja `.env.example`, con los
nombres y sin ningún valor.

| Variable | Para qué sirve |
|---|---|
| `GEMINI_API_KEY` | La clave de Google AI Studio. Sin ella funciona el modo `--simulado`, pero no el real. |
| `GEMINI_MODEL` | El identificador del modelo. Esta práctica se desarrolló con `gemini-3.5-flash`; si ese modelo dejara de existir, basta cambiar aquí el vigente de `ai.google.dev/gemini-api/docs/models`, sin tocar el código. |
| `MAX_MENSAJES` | Cuántos mensajes del historial se envían en cada llamada. Por omisión 6. |
| `TELEGRAM_BOT_TOKEN` | El token que entrega @BotFather. Quien lo tenga controla el bot. |
| `TELEGRAM_USUARIOS_PERMITIDOS` | Identificadores numéricos separados por comas. Con la lista vacía el bot no atiende a nadie. |

## Cómo usarlo

**El chat en la terminal.** Comandos dentro del chat: `/fuente` (qué documento se
consulta y su fecha de aprobación), `/reset` (borra la memoria) y `/salir`.

```bash
python -m app.cli --simulado     # modelo falso, no gasta cuota
python -m app.cli                # modelo real
```

**El lote del banco de pruebas.** Cada pregunta suelta empieza con la memoria vacía;
los turnos de una conversación la comparten. Entre llamadas reales espera 4 segundos.

```bash
python -m app.lote data/preguntas_prueba.json --simulado
python -m app.lote data/preguntas_prueba.json
python -m app.lote data/preguntas_prueba.json --solo R01,R02,R03
python -m app.lote data/preguntas_prueba.json --solo C1,C2
```

`--solo` acepta preguntas sueltas (`R01`…`R12`) y conversaciones completas (`C1`, `C2`).
Sirve para repartir la corrida en dos días y para repetir sólo lo que haya fallado.
Si un turno falla, el error queda en la bitácora y el lote sigue; si el que falla es
de una conversación, se omiten los turnos que le seguían.

**Las pruebas**, sin red y sin cuota:

```bash
python -m pruebas.prueba_citas
```

## Bot de Telegram

**Crear el bot.** En Telegram, abra una conversación con @BotFather (la cuenta
oficial, con palomita azul) y envíe `/newbot`. Elija un nombre visible y un nombre de
usuario terminado en `bot`. BotFather entrega un token con la forma `123456789:AA…`.

**Dónde va el token.** Únicamente en `TELEGRAM_BOT_TOKEN` de su archivo `.env`, que no
se sube. Nunca en el código, ni en este README, ni en una captura. Si se filtra, use
`/revoke` en BotFather y genere otro.

**Autorizar su identificador.** Arranque el bot y escríbale desde su celular: como
todavía no está en la lista, le contestará que es privado y le mostrará su propio
identificador numérico. Copie ese número a `TELEGRAM_USUARIOS_PERMITIDOS` (separados
por comas si son varios) y reinicie el bot. Con la lista vacía el bot no atiende a
nadie, y así un desconocido no puede agotarle la cuota diaria.

**Correrlo.** El bot responde sólo mientras el programa está abierto; se detiene con
`Ctrl+C`. Telegram acepta un solo programa por token, así que no lo abra dos veces.

```bash
python -m app.bot --simulado
python -m app.bot
```

**Comandos que atiende:** `/start` (qué hace, aviso de que no es autoridad del plantel
y aviso de privacidad), `/fuente` y `/reset`. Cualquier otro texto se responde con
`Asistente.responder`. La memoria es una por conversación (`chat.id`): dos personas no
comparten historial. Mientras el modelo responde, el bot muestra «escribiendo…» y no
se congela, porque la llamada bloqueante corre en otro hilo con `asyncio.to_thread`.
Las respuestas de más de 4,096 caracteres se parten, de preferencia en un salto de
línea.

En la bitácora, los turnos del bot llevan `"canal": "telegram"`, el identificador
`TG-1`, `TG-2`… y un campo `usuario` con los primeros 10 caracteres del SHA-256 del
identificador de Telegram. Nunca se guarda el identificador real ni el nombre.

La captura de una conversación real está en `evidencia/telegram.png`.

## Estructura del proyecto

```
asistente-reglamentario-23070505/
├─ README.md                    este archivo
├─ requirements.txt             google-genai, python-dotenv, python-telegram-bot
├─ .env.example                 nombres de las variables, sin valores
├─ .gitignore                   .env, .venv/ y __pycache__/
├─ verificar_entrega.py         del docente: revisa la forma de la entrega
├─ traza_manual.md              Parte E: la traza escrita a mano
├─ app/
│  ├─ __init__.py
│  ├─ reglamento.py             carga el JSON, lo vuelve texto para el prompt
│  │                            y construye el índice de 126 citas válidas
│  ├─ modelo.py                 la ÚNICA función que habla con Gemini
│  ├─ modelo_simulado.py        modelo falso con guion fijo de 3 respuestas
│  ├─ memoria.py                agregar, recortar y quitar el último mensaje
│  ├─ citas.py                  extrae las citas de una respuesta y las valida
│  ├─ asistente.py              une todo y escribe la bitácora
│  ├─ cli.py                    el chat en la terminal
│  ├─ lote.py                   corre el banco de pruebas
│  └─ bot.py                    el bot de Telegram: sólo recibe y entrega mensajes
├─ prompts/
│  └─ sistema.md                instrucciones de sistema con el marcador {REGLAMENTO}
├─ pruebas/
│  ├─ __init__.py
│  └─ prueba_citas.py           comprobaciones sin red, con assert
├─ data/                        del docente, sin modificar
│  ├─ reglamento_estudiantes_tecnm.json
│  ├─ Reglamento_de_Estudiantes_del_TecNM.pdf
│  └─ preguntas_prueba.json
├─ evaluacion/
│  ├─ esperadas.md              qué debería citar cada pregunta, escrito antes de correr
│  └─ resultados.md             qué citó de verdad, y el análisis
├─ logs/                        bitácoras corrida-AAAAMMDD-HHMMSS.jsonl
└─ evidencia/
   └─ telegram.png              captura de una conversación real con el bot
```

## Decisiones de diseño

**Una línea por cita posible.** `texto_para_prompt` recorre el JSON y escribe el
título en mayúsculas cuando cambia, una línea `Art. N.` con el encabezado, una línea
`Art. N, fracc. R.` por cada fracción —también para los incisos 1 a 4 del artículo 14,
que el original numera con dígitos— y, donde existe, una línea
`Art. N (párrafo final).`. El formato de esas líneas es el mismo con el que se le pide
al modelo que cite: copiar la cita del renglón donde leyó el dato hace mucho menos
probable que la invente.

**El formato de las citas, sin comillas.** El prompt pide `Art. 9` y `Art. 9, fracc. II`
con ejemplos concretos y sin comillas angulares, porque escribirlas en el prompt hace
que el modelo las copie en sus respuestas y rompan la extracción.

**`MAX_MENSAJES = 6`**, es decir tres turnos completos de ida y vuelta. Alcanza para
que una pregunta de seguimiento como «¿y cuál es la más grave?» tenga sentido, y evita
que cada llamada arrastre toda la conversación encima de los ~6,800 tokens que ya
cuesta el Reglamento. Además, si el primer mensaje del recorte es del modelo se
descarta, porque lo que se envía debe empezar con un mensaje del usuario.

**Cuando una cita es inválida**, el programa no oculta ni corrige la respuesta: la
muestra completa y le agrega `[Aviso] Estas citas no existen en el Reglamento: …`, y
registra las citas inválidas en la bitácora. El aviso sólo se muestra; al historial y
al campo `respuesta` de la bitácora va el texto crudo del modelo, para no devolverle
en el siguiente turno un texto que él no escribió.

**Cuando la llamada falla**, la pregunta sin responder se saca de la memoria, se
escribe una línea de bitácora con el campo `error` y `modelo: null`, y cada canal
muestra su propio mensaje comprensible en vez de un traceback. En el lote, el error
no detiene la corrida: se registra y se sigue con la siguiente pregunta.

## Resultados

COMPLETAR: cinco renglones con los números de `evaluacion/resultados.md`:

- respuestas correctas;
- citas inválidas;
- tokens por llamada;
- la estimación para el Manual de Lineamientos.

## Límites y ética

Este asistente es informativo y **no es autoridad del plantel**: no sustituye a la
Dirección, a Servicios Escolares ni al Comité Académico, y ninguna de sus respuestas
es una resolución. Su única fuente es el Reglamento de Estudiantes, así que todo lo
que viva en el Manual de Lineamientos Académico-Administrativos —faltas,
calificaciones, exámenes, bajas de materias, becas, residencias, titulación— queda
fuera y se responde «No consta en el Reglamento de Estudiantes».

Ante un caso personal o delicado explica la norma general con sus citas, no juzga el
caso ni declara culpables, y recomienda presentarlo por escrito ante la Dirección del
plantel; si hay riesgo para alguien, avisar de inmediato a las autoridades.

No guarda datos personales: en la bitácora, el usuario de Telegram se registra como
los primeros 10 caracteres del SHA-256 de su identificador, nunca el identificador
real ni el nombre. El aviso de `/start` pide expresamente no escribir datos personales,
porque los mensajes pasan por los servidores de Telegram y de Google. Aun así, el
modelo puede equivocarse: el aviso de citas inválidas atrapa los artículos inventados,
pero no garantiza que la interpretación de un artículo real sea la correcta. Ante una
duda que importe, hay que leer el Reglamento y preguntar en el plantel.

## Declaración de uso de IA

Usé **Claude (Claude Code)** como asistente de programación para el código de las
Partes A, B, C, D, F y H: `reglamento.py`, `modelo.py`, `modelo_simulado.py`,
`memoria.py`, `citas.py`, `asistente.py`, `cli.py`, `lote.py`, `bot.py`,
`pruebas/prueba_citas.py` y el borrador de `prompts/sistema.md` y de este README.
Trabajé de forma guiada: antes de cada módulo revisábamos las firmas del contrato y
yo decidía las ambigüedades (si el artículo 14 se cita con `fracc.` o con `numeral`,
si los transitorios entran al índice, si el descarte del recorte es un `if` o un
`while`, dónde vive la bitácora).

No usé IA para `traza_manual.md` (Parte E) ni para `evaluacion/esperadas.md`: la traza
la escribí a mano leyendo mi propio código, y las respuestas esperadas salen de mi
lectura del Reglamento, como pide la política del curso.

Cosas que hubo que corregir sobre la marcha: la lectura de argumentos de `lote.py`
salió enredada en el primer intento y se reescribió completa; al mover
`construir_asistente` de `cli.py` a `asistente.py` quedó la función vieja dentro de
`cli.py` y el chat dejó de arrancar con `NameError`; y una de las pruebas de
`partir_mensaje` estaba mal planteada —esperaba que el último trozo no terminara en
salto de línea— y falló contra código que sí era correcto. También hubo que cuidar dos
trampas del lenguaje que el asistente señaló pero que verifiqué yo: que `historial[-0:]`
devuelve la lista completa en vez de una vacía, y que `fracc` es prefijo de `fracciones`,
de modo que una expresión regular descuidada extrae una fracción `I` que nadie escribió.
