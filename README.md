# GoTutor

Tutor web para aprender cómo un compilador analiza Go: el alumno escribe código
y ve, fase por fase, los tokens, el árbol sintáctico, la tabla de símbolos y
los errores, con explicaciones de cada fase.

Proyecto de Lenguajes de Programación (ESPOL), grupo 3. Las normas de trabajo
del grupo están en [CONTRIBUTING.md](CONTRIBUTING.md).

```
GoTutor/
├── algoritmos/               algoritmoN.go (válido) y sus versiones con errores de cada fase
│                             (_errorM léxico, _errorsynM sintáctico, _errorsemM semántico)
├── backend/                  Python 3.11+ · Flask · PLY
│   ├── analizador/
│   │   ├── lexico.py         análisis léxico (ply.lex)
│   │   ├── sintactico.py     análisis sintáctico + AST (ply.yacc)
│   │   ├── semantico.py      análisis semántico + tabla de símbolos
│   │   └── modelos.py        contrato de datos con la interfaz (no cambiar campos)
│   ├── servicio.py           ejecuta las 3 fases en orden y arma el JSON
│   ├── bitacora.py           escribe los logs de cada fase en logs/
│   ├── app.py                API Flask (POST /api/analizar)
│   ├── probar_lexico.py      corre solo el léxico sobre un .go y deja su log
│   ├── probar_sintactico.py  corre el sintáctico sobre un .go y deja su log
│   ├── probar_semantico.py   corre el semántico sobre un .go y deja su log
│   ├── logs/                 logs generados en cada análisis
│   └── tests/                pruebas de la integración
└── frontend/                 Vite + JavaScript sin framework (pnpm)
    └── src/
        ├── vistas/           Ejemplos, Análisis libre, Guardados, Cuaderno
        ├── datos/            ejemplos, textos del tutor y almacenamiento de guardados
        ├── nube/firebase.js  esqueleto de login con Google (pendiente)
        └── …
```

## Cómo correrlo

Se necesitan dos terminales.

**Backend** (puerto 8000):

```bash
cd backend
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

**Frontend** (puerto 5173, redirige `/api` al backend):

```bash
cd frontend
pnpm install
pnpm dev
```

Abre http://localhost:5173.

Para tener todo en un solo proceso (por ejemplo, en la presentación), ejecuta
`pnpm build` en `frontend/` y luego `python app.py`. Flask sirve el build en
http://localhost:8000.

Pruebas: `cd backend && python -m unittest -v`.

- `test_api.py`, `test_contrato.py`: API, orquestación y campos que lee la interfaz.
  `test_api.py` también comprueba que el léxico real tokenice un programa válido.
- `test_integracion_ply.py`: el esqueleto con PLY real y una gramática mínima.
  Se omite sola en cuanto `lexico.py`/`sintactico.py` tengan reglas.
- `test_ejemplos.py`: cada ejemplo de la vista Ejemplos debe fallar en la fase
  y línea que declara (necesita Node para leer `ejemplos.js`). Los casos cuya
  fase aún no está implementada salen como *skipped*: esa lista es lo que falta.

En el avance 1 (solo léxico) lo esperado es `OK (skipped=13)`: los 6 casos de
`test_ejemplos.py` necesitan el sintáctico y los 7 de `test_integracion_ply.py`
se desactivan porque `lexico.py` ya tiene reglas.

En el avance 2 lo esperado es `OK (skipped=11)`: los 4 casos de
`test_ejemplos.py` que llegan al semántico y los 7 de `test_integracion_ply.py`.

En el avance 3 las tres fases están implementadas y lo esperado es
`OK (skipped=7)`: todos los casos de `test_ejemplos.py` pasan y solo se omiten
los 7 de `test_integracion_ply.py`.

## Avance 1: analizador léxico

**Estado: completo.** El analizador léxico (`backend/analizador/lexico.py`,
con PLY) reconoce el subconjunto de Go del proyecto.

| Integrante | Usuario | Reglas léxicas | Algoritmos de prueba |
|---|---|---|---|
| Paúl Rodríguez | `AndreewCore` | Delimitadores, Comentarios | `algoritmo1.go`, `algoritmo1_error1.go`, `algoritmo1_error2.go` |
| Danilo García | `Danilogb18` | Variables, Tipos de datos | `algoritmo2.go`, `algoritmo2_error1.go`, `algoritmo2_error2.go` |
| Samuel Echeverría | `SamuelEcheverria` | Operadores, Palabras reservadas | `algoritmo3.go`, `algoritmo3_error1.go`, `algoritmo3_error2.go` |

Cada integrante aporta un programa válido con la mayoría de tokens del
subconjunto y dos versiones con errores léxicos. Los logs de esas pruebas están
en `backend/logs/`. Para reproducir uno:

```bash
cd backend
python probar_lexico.py ../algoritmos/algoritmo3_error1.go -u SamuelEcheverria
```

## Avance 2: analizador sintáctico

El analizador sintáctico (`backend/analizador/sintactico.py`, con `ply.yacc`)
construye el árbol que se dibuja en la interfaz y reporta cada error de
sintaxis con línea, columna, un mensaje en español y una sugerencia. Tras un
error sigue analizando, así que un programa puede mostrar varios errores.

Las reglas salen de la Tabla 11 del documento del proyecto más un reparto
extra del avance 2 (detalle en [CONTRIBUTING.md](CONTRIBUTING.md)):

| Integrante | Usuario | Reglas sintácticas | Algoritmos de prueba |
|---|---|---|---|
| Paúl Rodríguez | `AndreewCore` | Variable con tipo (y sin tipo), for condicional e infinito, map, funciones con retorno, `fmt` (impresión y lectura), acceso por índice, structs y métodos | `algoritmo1.go`, `algoritmo1_errorsyn1.go`, `algoritmo1_errorsyn2.go` |
| Danilo García | `Danilogb18` | Asignación (simple y compuesta), slice, for range, funciones con múltiple retorno, expresiones booleanas, `:=`, for clásico, `x++` / `x--` | `algoritmo2.go`, `algoritmo2_errorsyn1.go`, `algoritmo2_errorsyn2.go` |
| Samuel Echeverría | `SamuelEcheverria` | Constante, arreglo, if / else, funciones sin retorno, expresiones aritméticas, `switch` | `algoritmo3.go`, `algoritmo3_errorsyn1.go`, `algoritmo3_errorsyn2.go` |

Cada integrante aporta su programa válido, que pasa el sintáctico sin errores,
y dos versiones con errores de sintaxis. Cada archivo con errores lista en su
encabezado los errores esperados y su línea. Los logs están en `backend/logs/`
(`sintactico-<usuario>-<fecha>-<hora>.txt`). Para reproducir uno:

```bash
cd backend
python probar_sintactico.py ../algoritmos/algoritmo1_errorsyn1.go -u AndreewCore
```

Limitaciones (detalle al inicio de `sintactico.py`): no hay inserción
automática de `;` (el `;` es opcional y los saltos de línea se ignoran), y
quedan fuera la conversión explícita `float64(x)`, la asignación a un índice
(`m["a"] += 1`) y la declaración múltiple (`a, b := f()`).

## Avance 3: analizador semántico

**Estado: completo.** El analizador semántico (`backend/analizador/semantico.py`)
recorre el árbol del sintáctico, llena la tabla de símbolos con sus ámbitos
(global, función, `if`, `for`…) y aplica las seis reglas semánticas de la
Tabla 11 del documento. Solo corre si el léxico y el sintáctico terminaron sin
errores. Cada error dice la regla que lo detectó, por ejemplo
`[Asignación de tipo] No se puede asignar un valor de tipo 'int' a la variable 'curso' de tipo 'string'.`,
con línea, columna y una sugerencia, y el nodo del árbol queda marcado en rojo.

| Integrante | Usuario | Reglas semánticas | Algoritmos de prueba |
|---|---|---|---|
| Paúl Rodríguez | `AndreewCore` | Retorno de funciones, Asignación de tipo | `algoritmo1.go`, `algoritmo1_errorsem1.go`, `algoritmo1_errorsem2.go` |
| Danilo García | `Danilogb18` | Conversión, Estructuras de control | `algoritmo2.go`, `algoritmo2_errorsem1.go`, `algoritmo2_errorsem2.go` |
| Samuel Echeverría | `SamuelEcheverria` | Identificadores, Operaciones permitidas | `algoritmo3.go`, `algoritmo3_errorsem1.go`, `algoritmo3_errorsem2.go` |

Qué revisa cada regla:

- **Identificadores**: toda variable, constante o función que se usa está
  declarada en el ámbito actual o en uno que lo contiene.
- **Operaciones permitidas**: los operandos son de un tipo válido para el
  operador (`+` suma números del mismo tipo o concatena `string`, `%` solo con
  `int`, `&&` y `||` solo con `bool`), y el valor de cada `case` tiene el tipo
  del `switch`.
- **Conversión**: Go no convierte `int` a `float64` (ni al revés) de forma
  implícita, ni en una operación ni al asignar.
- **Estructuras de control**: la condición de un `if` o un `for` es `bool`.
- **Asignación de tipo**: el valor que se asigna tiene el mismo tipo que la
  variable.
- **Retorno de funciones**: cada `return` devuelve la cantidad y los tipos de
  la firma, y una función sin tipo de retorno no devuelve valores.

El programa válido de cada integrante pasa el semántico sin errores, y cada
versión con errores tiene uno o más errores de una de sus reglas. Los logs
están en `backend/logs/` (`semantico-<usuario>-<fecha>-<hora>.txt`), con la
tabla de símbolos y los errores. Para reproducir uno:

```bash
cd backend
python probar_semantico.py ../algoritmos/algoritmo2_errorsem2.go -u Danilogb18
```

Lo que no se considera está listado al inicio de `semantico.py`. Entre otras
cosas, no se revisan los structs y sus métodos, las llamadas a paquetes
(`fmt.Println`), los argumentos contra los parámetros de una función ni las
variables declaradas y nunca usadas. Para no dar errores en cascada, una
expresión que tuvo un error o que usa algo no considerado tiene el tipo
`error`, y las reglas no se aplican sobre ella.

## Logs

Cada análisis escribe en `backend/logs/` un archivo por cada fase que se ejecutó:

```
lexico-<usuarioGit>-<dd-mm-aaaa>-<HHhMM>.txt
sintactico-<usuarioGit>-<dd-mm-aaaa>-<HHhMM>.txt
semantico-<usuarioGit>-<dd-mm-aaaa>-<HHhMM>.txt
```

Si hay varios análisis en el mismo minuto, se agregan al final del mismo
archivo, separados por una línea de `=`, en vez de sobrescribirlo.

El usuario se toma de `git config user.name` (sin tildes ni espacios). Para
usar otro nombre: `GOTUTOR_USUARIO_GIT=MiUsuario python app.py`, o
`-u MiUsuario` en `probar_lexico.py`, `probar_sintactico.py` o
`probar_semantico.py`.

## Contrato de la API

`POST /api/analizar` con `{"codigo": "...", "archivo": "main.go"}`. Responde:

```jsonc
{
  "archivo": "main.go",
  "fases": {
    "lex": {"estado": "ok", "errores": []},
    "syn": {"estado": "error", "errores": [
      {"fase": "syn", "linea": 9, "columna": 2,
       "mensaje": "Se esperaba ')' antes de '}'.", "sugerencia": "…"}
    ]},
    "sem": {"estado": "pendiente", "errores": []}
  },
  "tokens":   [{"tipo": "PACKAGE", "valor": "package", "linea": 1, "columna": 1}],
  "ast":      {"tipo": "Program", "dato": "", "linea": 1, "hijos": [], "error": null},
  "simbolos": null,
  "logs":     ["logs/lexico-AndreewCore-02-11-2026-14h05.txt"]
}
```

Los estados posibles son `ok`, `error`, `pendiente` (una fase anterior falló),
`no_impl` y `fallo` (excepción de Python).

## Inicio de sesión y nube (pendiente)

Por ahora todos usan el perfil **Invitado**, y los programas guardados y las
notas viven en el `localStorage` del navegador. La estructura para Firebase ya
existe, pero no está conectada:

- `frontend/src/nube/firebase.js`: login con Google (Firebase Auth).
- `frontend/src/datos/almacen-firestore.js`: guardados por usuario en
  `usuarios/{uid}/guardados/{id}`. Trae las reglas de seguridad previstas.
- `frontend/src/datos/guardados.js`: las vistas solo hablan con este módulo;
  para cambiar a la nube basta con `usarAlmacen(almacenFirestore, uid)`.

Para conectarlo: `pnpm add firebase`, crear el proyecto en Firebase (plan Spark,
gratis), activar Google en Authentication y Cloud Firestore, copiar
`frontend/.env.example` a `frontend/.env.local` con la config, e implementar
las funciones marcadas como pendientes.

## Integración continua

GitHub Actions (`.github/workflows/ci.yml`) corre las pruebas del backend en
Python 3.11 y 3.14, y `pnpm build` del frontend, en cada PR y en cada push a
`dev`, `staging` y `main`. Los PR hacia ramas de fase como `feature/lexico`
no la corren. También falla si las pruebas dejan archivos sueltos
en el repo (logs, `parsetab.py`).
