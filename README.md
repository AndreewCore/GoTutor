# GoTutor

Tutor web para aprender cómo un compilador analiza Go: el alumno escribe código
y ve, fase por fase, los tokens, el árbol sintáctico, la tabla de símbolos y
los errores, con explicaciones de cada fase.

```
GoTutor/
├── algoritmos/               algoritmoN.go (válido) y algoritmoN_errorM.go (con errores) de cada integrante
├── backend/                  Python 3.11+ · Flask · PLY
│   ├── analizador/
│   │   ├── lexico.py         ← GRUPO: análisis léxico (ply.lex)
│   │   ├── sintactico.py     ← GRUPO: análisis sintáctico + AST (ply.yacc)
│   │   ├── semantico.py      ← GRUPO: análisis semántico + tabla de símbolos
│   │   └── modelos.py        contrato de datos con la interfaz (no cambiar campos)
│   ├── servicio.py           ejecuta las 3 fases en orden y arma el JSON
│   ├── bitacora.py           escribe los logs de cada fase en logs/
│   ├── app.py                API Flask (POST /api/analizar)
│   ├── probar_lexico.py      corre solo el léxico sobre un .go y deja su log
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

## Para el grupo: avance 1 (analizador léxico)

Entrega: link del repositorio hasta el **08/11/2026 23h55**. Quien no tenga
commits en el historial no recibe nota.

**Estado: completo.** Las reglas léxicas de los tres integrantes están en
`feature/lexico`, y cada uno tiene su algoritmo válido, dos versiones con
errores léxicos y los logs de esas pruebas en `backend/logs/`. El sintáctico y
el semántico quedan para los siguientes avances, así que en la interfaz salen
como "Función no implementada".

| Integrante | Usuario | Reglas léxicas | Algoritmos |
|---|---|---|---|
| Paúl Rodríguez | `AndreewCore` | Delimitadores, Comentarios | `algoritmo1.go`, `algoritmo1_error1.go`, `algoritmo1_error2.go` |
| Danilo García | `Danilogb18` | Variables, Tipos de datos | `algoritmo2.go`, `algoritmo2_error1.go`, `algoritmo2_error2.go` |
| Samuel Echeverría | `SamuelEcheverria` | Operadores, Palabras reservadas | `algoritmo3.go`, `algoritmo3_error1.go`, `algoritmo3_error2.go` |

Los nombres de los tokens son los del documento del proyecto (`ENTERO`,
`ASIGNA_CORTA`, `LLAVE_IZQ`…).

**1. Rama.** Cada uno trabaja en su rama, que sale de `feature/lexico`, y abre
el PR hacia `feature/lexico` (no hacia `dev`):

```bash
git fetch
git switch -c feature/lexico-<usuario> origin/feature/lexico
```

Cuando los tres aportes estén en `feature/lexico`, esa rama se integra a `dev`
con un PR. La CI solo corre en los PR hacia `dev`, `staging` y `main`, porque
`test_ejemplos.py` necesita los tokens de los tres para pasar.

**2. Código.** En `backend/analizador/lexico.py` cada integrante escribe solo
dentro de su bloque `INICIO aporte` / `FIN aporte`. Sus tokens van en su lista
`tokens_<usuario>` y sus palabras reservadas en `reservadas_<usuario>`; al final
del archivo se juntan solos en `tokens` y `reservadas`. Así nadie edita las
mismas líneas y los merges no chocan.

**3. Algoritmo.** Escribir en su `algoritmos/algoritmoN.go` un programa Go con la
mayoría de tokens del subconjunto.

**4. Log.** Probar el lexer con su algoritmo; cada prueba genera un log en
`backend/logs/` con todos los tokens y errores:

```bash
cd backend
python probar_lexico.py ../algoritmos/algoritmo2.go -u Danilogb18
# -> logs/lexico-Danilogb18-06-11-2026-14h32.txt
```

Usen `-u` con su usuario de GitHub: sin esa opción el nombre del log se toma
de `git config user.name`, que suele ser el nombre completo.

**5. Commit.** Incluir los logs en el commit (`git add backend/logs/`): deben
quedar en el historial.

## Para el grupo: qué hay que implementar

Solo se editan los tres archivos de `backend/analizador/`. Cada uno trae
`TODO(grupo)` con ejemplos. Mientras una fase no esté implementada, la interfaz
la muestra como **"Función no implementada"**, así que pueden avanzar una por una.

| Archivo | Función que llama la API | Devuelve | Se considera "no implementado" mientras… |
|---|---|---|---|
| `lexico.py` | `analizar_lexico(codigo)` | `(list[Token], list[ErrorAnalisis])` | la lista `tokens` esté vacía |
| `sintactico.py` | `analizar_sintactico(codigo)` | `(Nodo \| None, list[ErrorAnalisis])` | no exista ninguna regla `p_xxx` |
| `semantico.py` | `analizar_semantico(ast, codigo)` | `(list[Simbolo], list[ErrorAnalisis])` | lance `NotImplementedError` |

Reglas:

- Los errores **no se imprimen**: se agregan a la lista (`t.lexer.errores` en el
  léxico y `_errores` en el sintáctico). Si no, no aparecen en la interfaz.
- Las líneas y columnas empiezan en 1. Para la columna usen
  `columna(codigo, t.lexpos)` de `modelos.py`: un tabulador cuenta como una
  columna (como en Go) y la cuenta coincide con la del editor de la interfaz,
  incluso con emojis.
- El parser construye objetos `Nodo(tipo, dato, linea, hijos)`, no tuplas. Si un
  nodo tiene un error, márquenlo con `error="syn"` o `error="sem"` para que salga
  en rojo.
- El semántico solo corre si el léxico y el sintáctico terminan sin errores.
- `mensaje` dice qué está mal y `sugerencia` cómo arreglarlo. La interfaz es para
  estudiantes, así que conviene escribirlos claros y en español.
- Si su código lanza una excepción, la API no se cae: la fase sale como
  **"Fallo del analizador"** con el mensaje, y el traceback aparece en la consola
  de Flask.
- Para probar sin la interfaz:
  `python -c "import servicio, json; print(json.dumps(servicio.analizar(open('x.go').read()), indent=2, ensure_ascii=False))"`
  desde `backend/`.

### Logs

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
`-u MiUsuario` en `probar_lexico.py`.

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
