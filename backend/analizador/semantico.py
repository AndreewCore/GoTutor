"""Fase 3 — Análisis semántico: recorre el AST, llena la tabla de símbolos y
aplica las reglas semánticas de la Tabla 11 del documento del proyecto.

La API llama a `analizar_semantico(ast, codigo)` solo si las fases léxica y
sintáctica terminaron sin errores. Mientras lance NotImplementedError, la
interfaz muestra "Función no implementada" en esta fase.

Contrato (ver modelos.py):
    analizar_semantico(ast: Nodo, codigo: str)
        -> tuple[list[Simbolo], list[ErrorAnalisis]]

Cómo se reparte este archivo
----------------------------
No hay estructura común: cada integrante escribe SOLO dentro de su bloque
INICIO/FIN. Cada uno tiene sus dos reglas de la Tabla 11, una parte de la base
del recorrido y el recorrido de los nodos que armó su gramática en el avance 2.

`visitar(az, nodo)` llama a la función `sem_<tipo del nodo>` (p. ej.
`sem_VarDecl`) y devuelve el tipo de la expresión (Tabla 9), o None si es una
sentencia. Un nodo sin función `sem_` se ignora, así que cada uno puede probar
lo suyo aunque los demás no hayan terminado, una vez que esté la base:
`Analizador`, `visitar` y `reportar` (AndreewCore), la tabla de símbolos
(SamuelEcheverria) y los tipos (Danilogb18).

Funciones que usan los demás (no cambien su firma):
    AndreewCore       visitar, reportar, asignar, nombre_tipo
    Danilogb18        ERROR, SIN_VALOR, tipo_literal, tupla, tipo_elemento,
                      tipo_clave, conversion, condicion
    SamuelEcheverria  abrir, cerrar, declarar, buscar, identificador

Tipo `error` (Tabla 9): lo que no se modela tiene ese tipo, y las reglas no
se aplican a una expresión de tipo `error`. Así no hay mensajes en cascada ni
errores falsos por lo que está fuera del alcance.

No considerado (fuera de la Tabla 11)
-------------------------------------
  - Conversión explícita `float64(x)` / `int(x)`: no está en la gramática y
    no se valida. La regla de Conversión solo detecta el int→float64 implícito.
  - Structs, campos y métodos: `ana.edad` y `ana.Nombre()` tienen tipo `error`.
  - Llamadas a paquetes (`fmt.Println`): tipo `error`, no se revisan.
  - Argumentos de una llamada contra los parámetros de la función.
  - Asignación compuesta (`+=`) e incremento (`x++`).
  - Variables declaradas y nunca usadas, constantes inmutables.
  - Funciones usadas antes de su declaración (Go lo permite; aquí no).
  - Literales sin tipo: `var x float64 = 0` es un error; se escribe `0.0`.
"""

from __future__ import annotations

from .modelos import ErrorAnalisis, Nodo, Simbolo, columna  # noqa: F401


# ===== INICIO aporte: Paúl Rodríguez (AndreewCore) =====
# Reglas (Tabla 11): Retorno de funciones, Asignación de tipo.
# Base: estado del análisis, visitar, reportar y el punto de entrada.
# Nodos (avance 2): VarDecl, FuncDecl, MethodDecl, ReturnStmt, CallExpr,
#   IndexExpr, SelectorExpr, MapLit.

class Analizador:
    """Estado del recorrido que comparten todas las funciones (`az`)."""

    def __init__(self, codigo: str):
        """Prepara el estado para analizar `codigo`."""
        # TODO(AndreewCore): guardar `codigo`, `errores` (list[ErrorAnalisis]),
        #   la función actual (nombre y tipos de retorno, para Retorno) y los
        #   tipos de retorno de cada función (para el tipo de una llamada).
        #   SamuelEcheverria necesita `ambito` (Ambito("global")) y `simbolos`.


def analizar_semantico(ast: Nodo, codigo: str) -> tuple[list[Simbolo], list[ErrorAnalisis]]:
    """Revisa el significado del programa y devuelve la tabla de símbolos y los errores."""
    # TODO(AndreewCore): crear el Analizador, visitar los hijos de `ast` (Program)
    #   y devolver (az.simbolos, az.errores).
    raise NotImplementedError("semantico.py aún no está implementado")


def visitar(az: Analizador, nodo: Nodo) -> str | None:
    """Llama a `sem_<nodo.tipo>(az, nodo)` y devuelve lo que devuelva; ERROR si no existe."""
    # TODO(AndreewCore): buscar la función con globals().get(f"sem_{nodo.tipo}").


def reportar(az: Analizador, regla: str, nodo: Nodo, mensaje: str, sugerencia: str = "",
             texto: str | None = None) -> None:
    """Agrega un ErrorAnalisis("sem", ...) con el mensaje "[<regla>] ..." y marca `nodo.error = "sem"`.

    Los nodos solo guardan la línea: la columna es la de `texto` (por defecto
    `nodo.dato`) dentro de esa línea, calculada con `columna()` de modelos.py.
    """
    # TODO(AndreewCore)


def nombre_tipo(nodo: Nodo) -> str:
    """Texto de un nodo Type ("int", "[]float64") o MapType ("map[string]int", hijos [clave, valor])."""
    # TODO(AndreewCore)


def asignar(az: Analizador, nodo: Nodo, nombre: str, esperado: str, recibido: str) -> None:
    """Revisa que `recibido` se pueda guardar en `nombre` de tipo `esperado`.

    Se salta si alguno es ERROR. Primero `conversion` (para que int→float64
    dé un solo mensaje, el de Conversión) y, si no reportó, Asignación de tipo.
    """
    # TODO(AndreewCore): regla Asignación de tipo, p. ej.:
    #   reportar(az, "Asignación de tipo", nodo, f"No se puede asignar un valor de tipo "
    #            f"'{recibido}' a la variable '{nombre}' de tipo '{esperado}'.", "...", texto=nombre)


def sem_VarDecl(az: Analizador, n: Nodo) -> None:
    """`var x T`, `var x T = v` o `var x = v`; dato = nombre, hijos [tipo], [tipo, valor] o [valor].

    El tipo es un nodo Type o MapType. Con tipo y valor, llama a `asignar`.
    """
    # TODO(AndreewCore)


def sem_FuncDecl(az: Analizador, n: Nodo) -> None:
    """Declara la función y revisa su cuerpo con sus parámetros en un ámbito nuevo.

    dato = nombre. hijos: los Param (sueltos o dentro de un nodo Params), un
    Results opcional con los tipos de retorno y el Block del cuerpo al final.
    """
    # TODO(AndreewCore)


def sem_MethodDecl(az: Analizador, n: Nodo) -> None:
    """Como FuncDecl, con hijos [Receiver, Param..., Results?, Block]; Receiver(dato = nombre, [Type])."""
    # TODO(AndreewCore)


def sem_ReturnStmt(az: Analizador, n: Nodo) -> None:
    """`return v1, v2`; hijos = valores. Regla Retorno de funciones."""
    # TODO(AndreewCore): comparar con los tipos de retorno de la función actual, p. ej.:
    #   reportar(az, "Retorno de funciones", n, f"Tipo de retorno inválido en la función "
    #            f"'{funcion}'; se esperaba 'float64' pero se retornó 'int'.", "...", texto="return")


def sem_CallExpr(az: Analizador, n: Nodo) -> str:
    """`f(args)` o `pkg.f(args)`; dato = "f" o "x.f", hijos = argumentos.

    Devuelve el tipo de retorno de f: T, una tupla "(T1, T2)" o SIN_VALOR.
    Con prefijo (fmt.Println, ana.Mostrar) devuelve ERROR.
    """
    # TODO(AndreewCore)
    return ERROR


def sem_IndexExpr(az: Analizador, n: Nodo) -> str:
    """`c[i]`; dato = nombre de la colección, hijos [índice]. Devuelve el tipo del elemento."""
    # TODO(AndreewCore)
    return ERROR


def sem_SelectorExpr(az: Analizador, n: Nodo) -> str:
    """`x.campo`; dato = "x.campo". Revisa que x exista; devuelve ERROR (structs no considerados)."""
    # TODO(AndreewCore)
    return ERROR


def sem_MapLit(az: Analizador, n: Nodo) -> str:
    """`map[K]V{k: v}`; hijos [tipo K, tipo V, KeyValue([k, v])...]. Devuelve "map[K]V"."""
    # TODO(AndreewCore)
    return ERROR

# ===== FIN aporte: Paúl Rodríguez (AndreewCore) =====


# ===== INICIO aporte: Danilo García (Danilogb18) =====
# Reglas (Tabla 11): Conversión, Estructuras de control.
# Base: los tipos de la Tabla 9.
# Nodos (avance 2): AssignStmt, ShortVarDecl, IncDecStmt, ForStmt,
#   CompositeLit, UnaryExpr, BasicLit.

ERROR = "error"  # Tabla 9: expresión que no se modela o que ya falló
SIN_VALOR = "sin valor"  # Tabla 9: llamada a una función sin retorno


def tipo_literal(lexema: str) -> str:
    """Tipo de un literal según su lexema: "int", "float64", "string" o "bool"."""
    # TODO(Danilogb18)


def tupla(tipos: list[str]) -> str:
    """Tipo de lo que devuelve una función: T, "(T1, T2)" o SIN_VALOR si no devuelve nada."""
    # TODO(Danilogb18)


def tipo_elemento(tipo: str) -> str:
    """Tipo de `c[i]` o del valor en `range c`: T en "[]T" y "[N]T", V en "map[K]V"; si no, ERROR."""
    # TODO(Danilogb18)


def tipo_clave(tipo: str) -> str:
    """Tipo de la clave en `range c`: "int" en arreglos y slices, K en "map[K]V"; si no, ERROR."""
    # TODO(Danilogb18)


def conversion(az: Analizador, nodo: Nodo, esperado: str, recibido: str) -> bool:
    """Regla Conversión: int y float64 mezclados sin conversión explícita.

    La llaman `asignar` (`esperado` es el tipo de la variable) y las operaciones
    aritméticas (los dos operandos). Devuelve True si reportó, para que no se
    reporte además Asignación u Operaciones.
    """
    # TODO(Danilogb18), p. ej.:
    #   reportar(az, "Conversión", nodo, "No existe conversión implícita del tipo 'int' "
    #            "al tipo 'float64'.", "...")
    return False


def condicion(az: Analizador, nodo: Nodo, estructura: str) -> None:
    """Regla Estructuras de control: visita la condición de un if o for y exige que sea bool."""
    # TODO(Danilogb18), p. ej.:
    #   reportar(az, "Estructuras de control", nodo, f"La condición de la estructura "
    #            f"'{estructura}' debe ser de tipo 'bool', pero se recibió '{tipo}'.", "...")


def sem_AssignStmt(az: Analizador, n: Nodo) -> None:
    """`x = v` o `x += v`; dato = operador, hijos [Ident, valor]. Con "=", llama a `asignar`."""
    # TODO(Danilogb18)


def sem_ShortVarDecl(az: Analizador, n: Nodo) -> None:
    """`x := v`; hijos [Ident, valor]. Declara x con el tipo del valor (visitado antes de declarar)."""
    # TODO(Danilogb18)


def sem_IncDecStmt(az: Analizador, n: Nodo) -> None:
    """`x++` / `x--`; hijos [Ident]. Solo revisa que x exista."""
    # TODO(Danilogb18)


def sem_ForStmt(az: Analizador, n: Nodo) -> None:
    """Las cuatro formas de for, en un ámbito propio. Según dato:

    "condicional" [cond, Block], "infinito" [Block],
    "clásico" [ShortVarDecl, cond, post, Block],
    "range" [Ident clave, Ident valor, Ident colección, Block] (clave "_" no se declara).
    """
    # TODO(Danilogb18)


def sem_CompositeLit(az: Analizador, n: Nodo) -> str:
    """Slice `[]T{...}` (dato "[]T", hijos = valores) o struct `P{campo: v}` (dato "P", hijos KeyValue).

    En un struct, la clave es un campo, no una variable: solo se visita el valor.
    Devuelve dato.
    """
    # TODO(Danilogb18)
    return ERROR


def sem_UnaryExpr(az: Analizador, n: Nodo) -> str:
    """`!x` (bool), `-x` (tipo de x) o `&x` (ERROR: punteros no considerados); hijos [x]."""
    # TODO(Danilogb18)
    return ERROR


def sem_BasicLit(az: Analizador, n: Nodo) -> str:
    """Literal; dato = lexema tal como se escribió."""
    # TODO(Danilogb18)
    return ERROR

# ===== FIN aporte: Danilo García (Danilogb18) =====


# ===== INICIO aporte: Samuel Echeverría (SamuelEcheverria) =====
# Reglas (Tabla 11): Identificadores, Operaciones permitidas.
# Base: la tabla de símbolos con ámbitos (Tabla 10).
# Nodos (avance 2): ImportDecl, Ident, ParenExpr, ConstDecl, ArrayLit,
#   IfStmt, SwitchStmt, Block, BinaryExpr.

class Ambito:
    """Un nivel de la tabla de símbolos: global, función o bloque."""

    def __init__(self, nombre: str, padre: Ambito | None = None):
        """Crea el ámbito dentro de `padre`."""
        # TODO(SamuelEcheverria): guardar el padre, un dict nombre -> Simbolo y
        #   la ruta que sale en la tabla ("global", "main", "main › for").


def abrir(az: Analizador, nombre: str) -> None:
    """Entra a un ámbito nuevo dentro del actual."""
    # TODO(SamuelEcheverria)


def cerrar(az: Analizador) -> None:
    """Vuelve al ámbito padre."""
    # TODO(SamuelEcheverria)


def declarar(az: Analizador, nombre: str, tipo: str, categoria: str, linea: int) -> Simbolo:
    """Agrega `nombre` al ámbito actual y a `az.simbolos`, la tabla que muestra la interfaz.

    categoria: "Variable", "Constante", "Parámetro", "Función" o "Paquete".
    """
    # TODO(SamuelEcheverria)


def buscar(az: Analizador, nombre: str) -> Simbolo | None:
    """Busca `nombre` del ámbito actual hacia el global; None si no está declarado."""
    # TODO(SamuelEcheverria)


def identificador(az: Analizador, nombre: str, nodo: Nodo, usar: bool = True) -> Simbolo | None:
    """Regla Identificadores: busca `nombre` y, si no está declarado, lo reporta.

    Con `usar` suma 1 a `usos` (asignarle a x no cuenta como leerla).
    """
    # TODO(SamuelEcheverria): reportar y agregar una fila "Sin declarar" a la tabla, p. ej.:
    #   reportar(az, "Identificadores", nodo, f"El identificador '{nombre}' no ha sido "
    #            f"declarado en este ámbito.", "...", texto=nombre)
    #   az.simbolos.append(Simbolo(nombre, ERROR, "Sin declarar", ..., nodo.linea, error=True))


def sem_ImportDecl(az: Analizador, n: Nodo) -> None:
    """`import "fmt"`; dato = '"fmt"'. Declara el paquete para que `fmt.Println` no dé error."""
    # TODO(SamuelEcheverria)


def sem_Ident(az: Analizador, n: Nodo) -> str:
    """Uso de una variable; dato = nombre. Devuelve su tipo, o ERROR si no está declarada."""
    # TODO(SamuelEcheverria)
    return ERROR


def sem_ParenExpr(az: Analizador, n: Nodo) -> str:
    """`(x)`; hijos [x]. Devuelve el tipo de x."""
    # TODO(SamuelEcheverria)
    return ERROR


def sem_ConstDecl(az: Analizador, n: Nodo) -> None:
    """`const X = v`; dato = nombre, hijos [valor]."""
    # TODO(SamuelEcheverria)


def sem_ArrayLit(az: Analizador, n: Nodo) -> str:
    """`[N]T{...}`; dato = "[N]T", hijos [Type, valores...]. Devuelve dato."""
    # TODO(SamuelEcheverria)
    return ERROR


def sem_IfStmt(az: Analizador, n: Nodo) -> None:
    """`if c {} else ...`; hijos [cond, Block, (Block | IfStmt)?]. La condición va a `condicion`."""
    # TODO(SamuelEcheverria)


def sem_SwitchStmt(az: Analizador, n: Nodo) -> None:
    """`switch v {...}`; hijos [v, CaseClause...].

    CaseClause: dato "case" con hijos [valor, sentencias...] o "default" con
    hijos = sentencias. Cada caso es un ámbito.
    """
    # TODO(SamuelEcheverria)


def sem_Block(az: Analizador, n: Nodo) -> None:
    """`{ ... }`; hijos = sentencias, en un ámbito propio."""
    # TODO(SamuelEcheverria)


def sem_BinaryExpr(az: Analizador, n: Nodo) -> str:
    """`a op b`; dato = operador, hijos [a, b].

    Comparaciones y `&&`/`||` dan "bool" (Tabla 9). En + - * / % se aplica
    `conversion` y, si no reportó, la regla Operaciones permitidas.
    """
    # TODO(SamuelEcheverria): - * / % solo entre numéricos del mismo tipo; + también
    #   entre dos string. Si no se permite, reportar y devolver ERROR, p. ej.:
    #   reportar(az, "Operaciones permitidas", n, f"Operación '{n.dato}' inválida entre "
    #            f"operandos de tipo '{izq}' y '{der}' (tipos incompatibles).", "...")
    return ERROR

# ===== FIN aporte: Samuel Echeverría (SamuelEcheverria) =====
