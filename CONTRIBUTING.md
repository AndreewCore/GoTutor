# Guía para integrantes

Cómo trabajamos en el repositorio. La descripción del proyecto, cómo correrlo y
el contrato de la API están en el [README](README.md).

## Ramas

Cada fase del analizador tiene su rama (`feature/lexico`, luego la del
sintáctico y la del semántico). Cada integrante trabaja en una rama que sale de
la rama de la fase y abre el PR hacia ella, no hacia `dev`:

```bash
git fetch
git switch -c feature/lexico-<usuario> origin/feature/lexico
```

Cuando los tres aportes están en la rama de la fase, esa rama se integra a `dev`
con un PR. La CI solo corre en los PR hacia `dev`, `staging` y `main`, porque
`test_ejemplos.py` necesita los aportes de los tres para pasar.

## Avance 1: analizador léxico

| Integrante | Usuario | Reglas léxicas |
|---|---|---|
| Paúl Rodríguez | `AndreewCore` | Delimitadores, Comentarios |
| Danilo García | `Danilogb18` | Variables, Tipos de datos |
| Samuel Echeverría | `SamuelEcheverria` | Operadores, Palabras reservadas |

Los nombres de los tokens son los del documento del proyecto (`ENTERO`,
`ASIGNA_CORTA`, `LLAVE_IZQ`…).

1. **Código.** En `backend/analizador/lexico.py` cada integrante escribe solo
   dentro de su bloque `INICIO aporte` / `FIN aporte`. Sus tokens van en su
   lista `tokens_<usuario>` y sus palabras reservadas en `reservadas_<usuario>`;
   al final del archivo se juntan solos en `tokens` y `reservadas`. Así nadie
   edita las mismas líneas y los merges no chocan.
2. **Algoritmos.** En `algoritmos/`, un programa válido (`algoritmoN.go`) con la
   mayoría de tokens del subconjunto y dos versiones con errores léxicos
   (`algoritmoN_error1.go`, `algoritmoN_error2.go`).
3. **Logs.** Probar el lexer con cada algoritmo; cada prueba genera un log en
   `backend/logs/`:

   ```bash
   cd backend
   python probar_lexico.py ../algoritmos/algoritmo2.go -u Danilogb18
   # -> logs/lexico-Danilogb18-06-11-2026-14h32.txt
   ```

   Usen `-u` con su usuario de GitHub: sin esa opción el nombre del log se toma
   de `git config user.name`, que suele ser el nombre completo.
4. **Commit.** Incluir los logs en el commit (`git add backend/logs/`): deben
   quedar en el historial. No suban los logs que genera la interfaz al probar.

## Avance 2: analizador sintáctico

La rama de la fase es `feature/sintactico`:

```bash
git fetch
git switch -c feature/sintactico-<usuario> origin/feature/sintactico
```

Las reglas salen de la Tabla 11 del documento (Asignación de reglas), más un
reparto extra del avance 2 con construcciones básicas que enriquecen los
algoritmos. Cada uno toma reglas parecidas a las suyas, para que su
sintáctico le sirva después en el semántico.

| Integrante | Usuario | Tabla 11 | Además (avance 2) |
|---|---|---|---|
| Paúl Rodríguez | `AndreewCore` | Variable con tipo, for condicional, map, funciones con retorno | `fmt` (impresión y lectura), acceso por índice, `for {}`, structs y métodos |
| Danilo García | `Danilogb18` | Asignación compuesta, slice, for range, funciones con múltiple retorno | Expresiones booleanas, `:=`, for clásico, `x++` / `x--` |
| Samuel Echeverría | `SamuelEcheverria` | Constante, arreglo, if, funciones sin retorno | Expresiones aritméticas, `switch` |

1. **Código.** En `backend/analizador/sintactico.py` cada integrante escribe
   solo dentro de su bloque `INICIO aporte` / `FIN aporte`, siguiendo sus
   `TODO(<usuario>)`. Las reglas vienen de la sección 4 del documento del
   proyecto. La "Estructura común" (programa, bloque, sentencias, tipos
   primitivos, llamadas, parámetros, `return` y `p_error`) ya está hecha y
   compila sola, así que cada uno puede probar su parte sin esperar a los demás.
   Las alternativas de `sentencia`, `expresion` y `tipo` se agregan con una
   función propia en el bloque de cada uno (PLY las junta). Comenten cada regla.
2. **Algoritmos.** El `algoritmoN.go` de cada uno debe pasar el sintáctico con
   sus reglas. Agreguen versiones con errores de sintaxis
   (`algoritmoN_errorsyn1.go`, `algoritmoN_errorsyn2.go`) y, quien tenga
   structs, un ejemplo con struct y método.
3. **Logs.** Cada prueba genera un log en `backend/logs/`:

   ```bash
   cd backend
   python probar_sintactico.py ../algoritmos/algoritmo2.go -u Danilogb18
   # -> logs/sintactico-Danilogb18-12-11-2026-14h32.txt
   ```

4. **Commit.** Incluir los logs (`git add backend/logs/`) y abrir el PR hacia
   `feature/sintactico`.

Lo que queda fuera del reparto y aparece en los algoritmos (`var x = 5` sin
tipo, `float64(x)`, asignar a un índice, declaración múltiple) está listado al
inicio de `sintactico.py`: hay que ajustar esos algoritmos o explicarlo como
limitación en la sustentación.

En `feature/sintactico`, `test_ejemplos.py` falla hasta que estén los tres
aportes, porque los ejemplos usan reglas de todos. Para ver los conflictos de
la gramática: `GOTUTOR_DEBUG_YACC=1 python probar_sintactico.py <archivo>`,
que deja `analizador/parser.out` (no se sube).

## Implementar las fases

Solo se editan los tres archivos de `backend/analizador/`. Cada uno trae
`TODO(grupo)` con ejemplos. Mientras una fase no esté implementada, la interfaz
la muestra como **"Función no implementada"**, así que se puede avanzar una por una.

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
- Si el código lanza una excepción, la API no se cae: la fase sale como
  **"Fallo del analizador"** con el mensaje, y el traceback aparece en la consola
  de Flask.
- Para probar sin la interfaz, desde `backend/`:
  `python -c "import servicio, json; print(json.dumps(servicio.analizar(open('x.go').read()), indent=2, ensure_ascii=False))"`

Antes de abrir un PR, corran `python -m unittest` en `backend/`. Los casos que
salen como *skipped* en `test_ejemplos.py` son las fases que faltan.
