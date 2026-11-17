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

from .modelos import ErrorAnalisis, Nodo, Simbolo, columna


# ===== INICIO aporte: Paúl Rodríguez (AndreewCore) =====
# Reglas (Tabla 11): Retorno de funciones, Asignación de tipo.
# Base: estado del análisis, visitar, reportar y el punto de entrada.
# Nodos (avance 2): VarDecl, FuncDecl, MethodDecl, ReturnStmt, CallExpr,
#   IndexExpr, SelectorExpr, MapLit.

class Analizador:
    """Estado del recorrido que comparten todas las funciones (`az`)."""

    def __init__(self, codigo: str):
        """Prepara el estado para analizar `codigo`."""
        self.codigo = codigo
        # reportar() busca la columna en la línea del error; se parte una sola vez.
        self.lineas = codigo.split("\n")
        self.errores: list[ErrorAnalisis] = []
        # (nombre, tipos de retorno) de la función que se está recorriendo:
        # Retorno de funciones compara cada `return` con esa firma.
        self.funcion: tuple[str, list[str]] | None = None
        # Tipos de retorno de cada función declarada, para el tipo de una llamada.
        self.firmas: dict[str, list[str]] = {}
        # Tabla de símbolos (SamuelEcheverria).
        self.ambito = Ambito("global")
        self.simbolos: list[Simbolo] = []


def analizar_semantico(ast: Nodo, codigo: str) -> tuple[list[Simbolo], list[ErrorAnalisis]]:
    """Revisa el significado del programa y devuelve la tabla de símbolos y los errores."""
    az = Analizador(codigo)
    for hijo in ast.hijos:
        visitar(az, hijo)
    return az.simbolos, az.errores


def visitar(az: Analizador, nodo: Nodo) -> str | None:
    """Llama a `sem_<nodo.tipo>(az, nodo)` y devuelve lo que devuelva; ERROR si no existe."""
    # Despacho por nombre: cada integrante agrega sus nodos desde su bloque sin
    # tocar esta función (igual que PLY junta las p_ de cada uno).
    funcion = globals().get(f"sem_{nodo.tipo}")
    # Sin función, el nodo no se modela (PackageClause, StructDecl...) o su
    # dueño aún no la escribe: ERROR hace que las reglas no lo revisen.
    return funcion(az, nodo) if funcion else ERROR


def reportar(az: Analizador, regla: str, nodo: Nodo, mensaje: str, sugerencia: str = "",
             texto: str | None = None) -> None:
    """Agrega un ErrorAnalisis("sem", ...) con el mensaje "[<regla>] ..." y marca `nodo.error = "sem"`.

    Los nodos solo guardan la línea: la columna es la de `texto` (por defecto
    `nodo.dato`) dentro de esa línea, calculada con `columna()` de modelos.py.
    """
    nodo.error = "sem"
    az.errores.append(ErrorAnalisis("sem", nodo.linea, _columna_de(az, nodo.linea, texto or nodo.dato),
                                    f"[{regla}] {mensaje}", sugerencia))


def _columna_de(az: Analizador, linea: int, texto: str) -> int:
    """Columna de la primera aparición de `texto` en `linea`, o 1 si no aparece."""
    if not 1 <= linea <= len(az.lineas):
        return 1
    inicio = sum(len(l) + 1 for l in az.lineas[:linea - 1])
    posicion = az.lineas[linea - 1].find(texto) if texto else -1
    return columna(az.codigo, inicio + max(posicion, 0))


def nombre_tipo(nodo: Nodo) -> str:
    """Texto de un nodo Type ("int", "[]float64") o MapType ("map[string]int", hijos [clave, valor])."""
    # MapType guarda solo "map" en `dato`: el texto completo se arma con sus hijos.
    if nodo.tipo == "MapType":
        return f"map[{nombre_tipo(nodo.hijos[0])}]{nombre_tipo(nodo.hijos[1])}"
    return nodo.dato


def asignar(az: Analizador, nodo: Nodo, nombre: str, esperado: str, recibido: str) -> None:
    """Revisa que `recibido` se pueda guardar en `nombre` de tipo `esperado`.

    Se salta si alguno es ERROR. Primero `conversion` (para que int→float64
    dé un solo mensaje, el de Conversión) y, si no reportó, Asignación de tipo.
    """
    # Un ERROR ya se reportó o no se modela: revisarlo daría un mensaje en cascada.
    if ERROR in (esperado, recibido):
        return
    if conversion(az, nodo, esperado, recibido):
        return
    # Regla semántica (Tabla 11) — Asignación de tipo: el tipo del valor debe
    # coincidir exactamente con el de la variable.
    if esperado != recibido:
        reportar(az, "Asignación de tipo", nodo,
                 f"No se puede asignar un valor de tipo '{recibido}' a la variable "
                 f"'{nombre}' de tipo '{esperado}'.",
                 f"Asigna un valor de tipo '{esperado}' o declara '{nombre}' con otro tipo.",
                 texto=nombre)


def sem_VarDecl(az: Analizador, n: Nodo) -> None:
    """`var x T`, `var x T = v` o `var x = v`; dato = nombre, hijos [tipo], [tipo, valor] o [valor].

    El tipo es un nodo Type o MapType. Con tipo y valor, llama a `asignar`.
    """
    tiene_tipo = n.hijos[0].tipo in ("Type", "MapType")
    esperado = nombre_tipo(n.hijos[0]) if tiene_tipo else None
    valor = n.hijos[-1] if not tiene_tipo or len(n.hijos) == 2 else None
    # El valor se revisa antes de declarar: en `var x = x` la x de la derecha es la de afuera.
    recibido = visitar(az, valor) if valor else None
    if esperado and recibido:
        asignar(az, n, n.dato, esperado, recibido)
    # Sin tipo, Go lo deduce del valor.
    declarar(az, n.dato, esperado or recibido, "Variable", n.linea)


def _parametros(n: Nodo) -> list[Nodo]:
    """Los Param de una función o método, estén sueltos o dentro de un nodo Params."""
    return [p for h in n.hijos for p in (h.hijos if h.tipo == "Params" else [h]) if p.tipo == "Param"]


def _resultados(n: Nodo) -> list[str]:
    """Los tipos de retorno (hijo Results); [] si la función no devuelve nada."""
    return next(([nombre_tipo(t) for t in h.hijos] for h in n.hijos if h.tipo == "Results"), [])


def _recorrer_funcion(az: Analizador, n: Nodo, resultados: list[str]) -> None:
    """Revisa el cuerpo de una función o método en su ámbito, con sus parámetros declarados."""
    anterior = az.funcion
    az.funcion = (n.dato, resultados)
    abrir(az, n.dato)
    for h in n.hijos:
        if h.tipo == "Receiver":
            declarar(az, h.dato, h.hijos[0].dato, "Parámetro", h.linea)
    for p in _parametros(n):
        declarar(az, p.dato, nombre_tipo(p.hijos[0]), "Parámetro", p.linea)
    # El cuerpo comparte el ámbito con los parámetros, como en Go.
    for sentencia in n.hijos[-1].hijos:
        visitar(az, sentencia)
    cerrar(az)
    # Se restaura por las funciones anidadas, que la gramática acepta.
    az.funcion = anterior


def sem_FuncDecl(az: Analizador, n: Nodo) -> None:
    """Declara la función y revisa su cuerpo con sus parámetros en un ámbito nuevo.

    dato = nombre. hijos: los Param (sueltos o dentro de un nodo Params), un
    Results opcional con los tipos de retorno y el Block del cuerpo al final.
    """
    resultados = _resultados(n)
    firma = f"func({', '.join(nombre_tipo(p.hijos[0]) for p in _parametros(n))})"
    if resultados:
        firma += " " + tupla(resultados)
    # Se declara antes del cuerpo para que la función pueda llamarse a sí misma.
    declarar(az, n.dato, firma, "Función", n.linea)
    az.firmas[n.dato] = resultados
    _recorrer_funcion(az, n, resultados)


def sem_MethodDecl(az: Analizador, n: Nodo) -> None:
    """Como FuncDecl, con hijos [Receiver, Param..., Results?, Block]; Receiver(dato = nombre, [Type])."""
    # El método no va a la tabla: `ana.Mostrar()` no se revisa (structs no considerados).
    _recorrer_funcion(az, n, _resultados(n))


def sem_ReturnStmt(az: Analizador, n: Nodo) -> None:
    """`return v1, v2`; hijos = valores. Regla Retorno de funciones."""
    recibidos = [visitar(az, h) for h in n.hijos]
    if az.funcion is None or ERROR in recibidos:
        return
    nombre, esperados = az.funcion
    # `return g()` con g de varios retornos llega como una sola tupla "(T1, T2)".
    if recibidos == esperados or (len(recibidos) == 1 and recibidos[0] == tupla(esperados)):
        return
    # Regla semántica (Tabla 11) — Retorno de funciones: el return debe coincidir
    # con la firma; en una función sin tipo de retorno no lleva valores.
    if not esperados:
        mensaje = f"La función '{nombre}' no tiene tipo de retorno; el return no debe llevar valores."
        sugerencia = "Quita los valores del return o agrega el tipo de retorno a la firma."
    else:
        mensaje = (f"Tipo de retorno inválido en la función '{nombre}'; se esperaba "
                   f"'{tupla(esperados)}' pero se retornó '{tupla(recibidos)}'.")
        sugerencia = f"Devuelve un valor de tipo '{tupla(esperados)}' o cambia la firma de '{nombre}'."
    reportar(az, "Retorno de funciones", n, mensaje, sugerencia, texto="return")


def sem_CallExpr(az: Analizador, n: Nodo) -> str:
    """`f(args)` o `pkg.f(args)`; dato = "f" o "x.f", hijos = argumentos.

    Devuelve el tipo de retorno de f: T, una tupla "(T1, T2)" o SIN_VALOR.
    Con prefijo (fmt.Println, ana.Mostrar) devuelve ERROR.
    """
    # Los argumentos se visitan para revisar lo que usan, no contra los parámetros.
    for argumento in n.hijos:
        visitar(az, argumento)
    if "." in n.dato:
        identificador(az, n.dato.split(".")[0], n)
        return ERROR
    if identificador(az, n.dato, n) is None or n.dato not in az.firmas:
        return ERROR
    return tupla(az.firmas[n.dato])


def sem_IndexExpr(az: Analizador, n: Nodo) -> str:
    """`c[i]`; dato = nombre de la colección, hijos [índice]. Devuelve el tipo del elemento."""
    coleccion = identificador(az, n.dato, n)
    visitar(az, n.hijos[0])
    return tipo_elemento(coleccion.tipo) if coleccion else ERROR


def sem_SelectorExpr(az: Analizador, n: Nodo) -> str:
    """`x.campo`; dato = "x.campo". Revisa que x exista; devuelve ERROR (structs no considerados)."""
    identificador(az, n.dato.split(".")[0], n)
    return ERROR


def sem_MapLit(az: Analizador, n: Nodo) -> str:
    """`map[K]V{k: v}`; hijos [tipo K, tipo V, KeyValue([k, v])...]. Devuelve "map[K]V"."""
    for par in n.hijos[2:]:
        visitar(az, par.hijos[0])
        visitar(az, par.hijos[1])
    return f"map[{nombre_tipo(n.hijos[0])}]{nombre_tipo(n.hijos[1])}"

# ===== FIN aporte: Paúl Rodríguez (AndreewCore) =====


# ===== INICIO aporte: Danilo García (Danilogb18) =====
# Reglas (Tabla 11): Conversión, Estructuras de control.
# Base: los tipos de la Tabla 9.
# Nodos (avance 2): AssignStmt, ShortVarDecl, IncDecStmt, ForStmt,
#   CompositeLit, UnaryExpr, BasicLit.


ERROR = "error"
SIN_VALOR = "sin valor"  # llamada a una función sin retorno

NUMERICOS = ("int", "float64")


# --- Base: tipos de la Tabla 9 

def tipo_literal(lexema: str) -> str:
    """Tipo de un literal según su lexema: "int", "float64", "string" o "bool"."""
    # El lexer deja el lexema tal cual (ENTERO y DECIMAL no se convierten a número), así que basta mirar su forma: comillas, true/false o un punto.
    if lexema.startswith('"'):
        return "string"
    if lexema in ("true", "false"):
        return "bool"
    if "." in lexema:
        return "float64"
    return "int"


def tupla(tipos: list[str]) -> str:
    """Tipo de lo que devuelve una función: T, "(T1, T2)" o SIN_VALOR si no devuelve nada."""
    # Un solo tipo no lleva paréntesis: `func f() int` devuelve "int", que se compara directo con el tipo de una variable.
    if not tipos:
        return SIN_VALOR
    if len(tipos) == 1:
        return tipos[0]
    return "(" + ", ".join(tipos) + ")"


def _partes_map(tipo: str) -> tuple[str, str] | None:
    """Separa "map[K]V" en (K, V); None si `tipo` no es un map.
    Se busca el ']' que cierra la clave contando corchetes, porque la clave o el valor pueden tener corchetes propios: "map[string][]int" -> ("string", "[]int").
    """
    if not tipo.startswith("map["):
        return None
    nivel = 0
    for i in range(3, len(tipo)):
        if tipo[i] == "[":
            nivel += 1
        elif tipo[i] == "]":
            nivel -= 1
            if nivel == 0:
                return tipo[4:i], tipo[i + 1:]
    return None


def _es_arreglo(tipo: str) -> bool:
    """True para "[N]T" (arreglo con tamaño); "[]T" es slice."""
    cierre = tipo.find("]")
    return tipo.startswith("[") and cierre > 1 and tipo[1:cierre].isdigit()


def tipo_elemento(tipo: str) -> str:
    """Tipo de `c[i]` o del valor en `range c`: T en "[]T" y "[N]T", V en "map[K]V"; si no, ERROR."""
    if tipo.startswith("[]"):
        return tipo[2:]
    if _es_arreglo(tipo):
        return tipo[tipo.find("]") + 1:]
    partes = _partes_map(tipo)
    return partes[1] if partes else ERROR


def tipo_clave(tipo: str) -> str:
    """Tipo de la clave en `range c`: "int" en arreglos y slices, K en "map[K]V"; si no, ERROR."""
    if tipo.startswith("[]") or _es_arreglo(tipo):
        return "int"  # la posición
    partes = _partes_map(tipo)
    return partes[0] if partes else ERROR


# --- Regla Conversión 

def conversion(az: Analizador, nodo: Nodo, esperado: str, recibido: str) -> bool:
    """Regla Conversión: int y float64 mezclados sin conversión explícita.

    La llaman `asignar` (`esperado` es el tipo de la variable) y las operaciones
    aritméticas (los dos operandos). Devuelve True si reportó, para que no se
    reporte además Asignación u Operaciones.
    """
    # Solo se dispara con la pareja int/float64. Con cualquier otro par (int y string, por ejemplo) devuelve False y decide la regla de quien llamó: Asignación de tipo u Operaciones permitidas. Si uno es ERROR, el error ya se reportó antes y no se repite.
    if {esperado, recibido} != set(NUMERICOS):
        return False

    # La sugerencia no propone `float64(x)`: la conversión explícita no está en la gramática así que el analizador rechazaría justo lo que se le sugiere al alumno.
    if nodo.tipo == "BinaryExpr":
        mensaje = (f"No existe conversión implícita entre 'int' y 'float64': la operación "
                   f"'{nodo.dato}' mezcla un operando de tipo '{esperado}' con uno de tipo '{recibido}'.")
        sugerencia = ("Go no convierte números automáticamente: usa operandos del mismo tipo "
                      "(por ejemplo, escribe 2.0 en vez de 2 si el otro operando es float64).")
    else:
        mensaje = f"No existe conversión implícita del tipo '{recibido}' al tipo '{esperado}'."
        if esperado == "float64":
            sugerencia = ("Usa un valor de tipo float64: escribe el literal con decimales "
                          "(5.0 en vez de 5) o una variable declarada como float64.")
        else:
            sugerencia = ("Un int no puede guardar decimales: usa un valor entero "
                          "o declara la variable como float64.")
    reportar(az, "Conversión", nodo, mensaje, sugerencia)
    return True


# --- Regla Estructuras de control 

def condicion(az: Analizador, nodo: Nodo, estructura: str) -> None:
    """Regla Estructuras de control: visita la condición de un if o for y exige que sea bool."""
    tipo = visitar(az, nodo)
    # ERROR: la condición ya tuvo un error (p. ej. variable sin declarar) o usa algo no considerado; reportarla otra vez sería un mensaje en cascada.
    if tipo in ("bool", ERROR, None):
        return
    # Go no trata los números como verdadero/falso como C o Python, la sugerencia muestra la comparación que el usuario probablemente quería.
    if tipo in NUMERICOS:
        sugerencia = "Compara el valor para obtener un bool, por ejemplo: x != 0 o x > 0."
    elif tipo == "string":
        sugerencia = 'Compara el texto para obtener un bool, por ejemplo: s != "".'
    else:
        sugerencia = "Usa una comparación (==, <, >...) o una variable de tipo bool."
    reportar(az, "Estructuras de control", nodo,
             f"La condición de la estructura '{estructura}' debe ser de tipo 'bool', "
             f"pero se recibió '{tipo}'.", sugerencia)


# --- Nodos de la gramática de Danilogb18 

def sem_AssignStmt(az: Analizador, n: Nodo) -> None:
    """`x = v` o `x += v`; dato = operador, hijos [Ident, valor]. Con "=", llama a `asignar`."""
    ident, valor = n.hijos
    recibido = visitar(az, valor)
    simbolo = identificador(az, ident.dato, ident, usar=n.dato != "=")
    if simbolo is None:
        return
    if n.dato == "=":
        asignar(az, n, ident.dato, simbolo.tipo, recibido)


def sem_ShortVarDecl(az: Analizador, n: Nodo) -> None:
    """`x := v`; hijos [Ident, valor]. Declara x con el tipo del valor (visitado antes de declarar)."""
    ident, valor = n.hijos
    # Se visita antes de declarar para que `x := x + 1` busque la x de afuera y no la nueva, que todavía no existe (igual que en Go).
    tipo = visitar(az, valor)
    # `:=` es la única forma de declarar sin escribir el tipo: el tipo de x es
    # el del valor. Si el valor es ERROR, x queda con tipo ERROR y las reglas
    # no se aplican a sus usos (sin errores en cascada).
    declarar(az, ident.dato, tipo or ERROR, "Variable", n.linea)


def sem_IncDecStmt(az: Analizador, n: Nodo) -> None:
    """`x++` / `x--`; hijos [Ident]. Solo revisa que x exista."""
    ident = n.hijos[0]
    # x++ lee x para sumarle 1, así que cuenta como uso.
    identificador(az, ident.dato, ident)


def sem_ForStmt(az: Analizador, n: Nodo) -> None:
    """Las cuatro formas de for, en un ámbito propio. Según dato:

    "condicional" [cond, Block], "infinito" [Block],
    "clásico" [ShortVarDecl, cond, post, Block],
    "range" [Ident clave, Ident valor, Ident colección, Block] (clave "_" no se declara).
    """
    abrir(az, "for")
    if n.dato == "condicional":
        cond, cuerpo = n.hijos
        condicion(az, cond, "for")
    elif n.dato == "clásico":
        inicio, cond, paso, cuerpo = n.hijos
        visitar(az, inicio)  # declara i antes de usarla en la condición
        condicion(az, cond, "for")
        visitar(az, paso)
    elif n.dato == "range":
        clave, valor, coleccion, cuerpo = n.hijos
        simbolo = identificador(az, coleccion.dato, coleccion)
        tipo = simbolo.tipo if simbolo else ERROR
        # Arreglos y slices dan (posición int, elemento); maps, (clave, valor). Otro tipo (int, string) queda en ERROR, no está en el alcance
        for var, tipo_var in ((clave, tipo_clave(tipo)), (valor, tipo_elemento(tipo))):
            if var.dato != "_":  # el identificador vacío descarta el valor
                declarar(az, var.dato, tipo_var, "Variable", var.linea)
    else:  # "infinito"
        cuerpo = n.hijos[0]
    visitar(az, cuerpo)
    cerrar(az)


def sem_CompositeLit(az: Analizador, n: Nodo) -> str:
    """Slice `[]T{...}` (dato "[]T", hijos = valores) o struct `P{campo: v}` (dato "P", hijos KeyValue).

    En un struct, la clave es un campo, no una variable: solo se visita el valor.
    Devuelve dato.
    """
    if n.dato.startswith("[]"):
        elemento = tipo_elemento(n.dato)
        for valor in n.hijos:
            # Cada valor se guarda en un elemento de tipo T: un 8 dentro de []float64 es el mismo int→float64 implícito que en `var x float64 = 8`.
            conversion(az, valor, elemento, visitar(az, valor))
        return n.dato
    for par in n.hijos:
        visitar(az, par.hijos[1])
    return ERROR  # structs no considerados, sus usos no se revisan


def sem_UnaryExpr(az: Analizador, n: Nodo) -> str:
    """`!x` (bool), `-x` (tipo de x) o `&x` (ERROR: punteros no considerados); hijos [x]."""
    tipo = visitar(az, n.hijos[0])  # también cuenta el uso de x en `&x`
    if n.dato == "&" or tipo == ERROR:
        return ERROR
    return "bool" if n.dato == "!" else tipo


def sem_BasicLit(az: Analizador, n: Nodo) -> str:
    """Literal; dato = lexema tal como se escribió."""
    return tipo_literal(n.dato)


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
        self.nombre = nombre
        self.padre = padre
        self.simbolos: dict[str, Simbolo] = {}
        # Si el padre es None o es "global", la ruta es el nombre directo (ej. "global", "main").
        # Si estamos dentro de una función o bloque anidado, se encadena (ej. "main › if").
        if padre is None or padre.ruta == "global":
            self.ruta = nombre
        else:
            self.ruta = f"{padre.ruta} › {nombre}"


def abrir(az: Analizador, nombre: str) -> None:
    """Entra a un ámbito nuevo dentro del actual."""
    az.ambito = Ambito(nombre, az.ambito)


def cerrar(az: Analizador) -> None:
    """Vuelve al ámbito padre."""
    if az.ambito.padre is not None:
        az.ambito = az.ambito.padre


def declarar(az: Analizador, nombre: str, tipo: str, categoria: str, linea: int) -> Simbolo:
    """Agrega `nombre` al ámbito actual y a `az.simbolos`, la tabla que muestra la interfaz.

    categoria: "Variable", "Constante", "Parámetro", "Función" o "Paquete".
    """
    sim = Simbolo(
        nombre=nombre,
        tipo=tipo,
        categoria=categoria,
        ambito=az.ambito.ruta,
        linea=linea,
    )
    az.ambito.simbolos[nombre] = sim
    az.simbolos.append(sim)
    return sim


def buscar(az: Analizador, nombre: str) -> Simbolo | None:
    """Busca `nombre` del ámbito actual hacia el global; None si no está declarado."""
    actual: Ambito | None = az.ambito
    while actual is not None:
        if nombre in actual.simbolos:
            return actual.simbolos[nombre]
        actual = actual.padre
    return None


def identificador(az: Analizador, nombre: str, nodo: Nodo, usar: bool = True) -> Simbolo | None:
    """Regla Identificadores: busca `nombre` y, si no está declarado, lo reporta.

    Con `usar` suma 1 a `usos` (asignarle a x no cuenta como leerla).
    """
    if nombre == "_":
        return None

    sim = buscar(az, nombre)
    if sim is None:
        reportar(
            az,
            "Identificadores",
            nodo,
            f"El identificador '{nombre}' no ha sido declarado en este ámbito.",
            f"Declara '{nombre}' con 'var {nombre} <tipo>' o '{nombre} := <valor>' antes de usarlo.",
            texto=nombre,
        )
        az.simbolos.append(
            Simbolo(
                nombre=nombre,
                tipo=ERROR,
                categoria="Sin declarar",
                ambito=az.ambito.ruta,
                linea=nodo.linea,
                error=True,
            )
        )
        return None

    if usar:
        sim.usos += 1
    return sim


def sem_ImportDecl(az: Analizador, n: Nodo) -> None:
    """`import "fmt"`; dato = '"fmt"'. Declara el paquete para que `fmt.Println` no dé error."""
    nombre_paquete = n.dato.strip('"')
    if "/" in nombre_paquete:
        nombre_paquete = nombre_paquete.rsplit("/", 1)[-1]
    declarar(az, nombre_paquete, "paquete", "Paquete", n.linea)


def sem_Ident(az: Analizador, n: Nodo) -> str:
    """Uso de una variable; dato = nombre. Devuelve su tipo, o ERROR si no está declarada."""
    sim = identificador(az, n.dato, n, usar=True)
    if sim is None:
        return ERROR
    return sim.tipo


def sem_ParenExpr(az: Analizador, n: Nodo) -> str:
    """`(x)`; hijos [x]. Devuelve el tipo de x."""
    if not n.hijos:
        return ERROR
    return visitar(az, n.hijos[0])


def sem_ConstDecl(az: Analizador, n: Nodo) -> None:
    """`const X = v`; dato = nombre, hijos [valor]."""
    tipo_valor = visitar(az, n.hijos[0]) if n.hijos else ERROR
    declarar(az, n.dato, tipo_valor, "Constante", n.linea)


def sem_ArrayLit(az: Analizador, n: Nodo) -> str:
    """`[N]T{...}`; dato = "[N]T", hijos [Type, valores...]. Devuelve dato."""
    tipo_elem = nombre_tipo(n.hijos[0]) if n.hijos else ERROR
    for elem in n.hijos[1:]:
        tipo_item = visitar(az, elem)
        if tipo_item != ERROR and tipo_elem != ERROR:
            asignar(az, tipo_elem, tipo_item, elem, f"elemento de arreglo '{n.dato}'")
    return n.dato


def sem_IfStmt(az: Analizador, n: Nodo) -> None:
    """`if c {} else ...`; hijos [cond, Block, (Block | IfStmt)?]. La condición va a `condicion`."""
    if len(n.hijos) < 2:
        return

    condicion(az, n.hijos[0], "if")

    abrir(az, "if")
    for sentencia in n.hijos[1].hijos:
        visitar(az, sentencia)
    cerrar(az)

    if len(n.hijos) == 3:
        rama_else = n.hijos[2]
        if rama_else.tipo == "IfStmt":
            visitar(az, rama_else)
        else:
            abrir(az, "else")
            for sentencia in rama_else.hijos:
                visitar(az, sentencia)
            cerrar(az)


def sem_SwitchStmt(az: Analizador, n: Nodo) -> None:
    """`switch v {...}`; hijos [v, CaseClause...].

    CaseClause: dato "case" con hijos [valor, sentencias...] o "default" con
    hijos = sentencias. Cada caso es un ámbito.
    """
    if not n.hijos:
        return

    tipo_switch = visitar(az, n.hijos[0])

    for clausula in n.hijos[1:]:
        if clausula.dato == "case":
            tipo_caso = visitar(az, clausula.hijos[0])
            if tipo_switch != ERROR and tipo_caso != ERROR and tipo_switch != tipo_caso:
                reportar(
                    az,
                    "Operaciones permitidas",
                    clausula.hijos[0],
                    f"El valor del 'case' es de tipo '{tipo_caso}', pero la expresión del 'switch' es '{tipo_switch}'.",
                    f"Usa un valor de tipo '{tipo_switch}' en este caso.",
                )
            abrir(az, "case")
            for sentencia in clausula.hijos[1:]:
                visitar(az, sentencia)
            cerrar(az)
        else:
            abrir(az, "default")
            for sentencia in clausula.hijos:
                visitar(az, sentencia)
            cerrar(az)


def sem_Block(az: Analizador, n: Nodo) -> None:
    """`{ ... }`; hijos = sentencias, en un ámbito propio."""
    abrir(az, "bloque")
    for sentencia in n.hijos:
        visitar(az, sentencia)
    cerrar(az)


def sem_BinaryExpr(az: Analizador, n: Nodo) -> str:
    """`a op b`; dato = operador, hijos [a, b].

    Comparaciones y `&&`/`||` dan "bool" (Tabla 9). En + - * / % se aplica
    `conversion` y, si no reportó, la regla Operaciones permitidas.
    """
    izq = visitar(az, n.hijos[0])
    der = visitar(az, n.hijos[1])

    if izq == ERROR or der == ERROR:
        return ERROR

    op = n.dato

    # 1. Operadores lógicos: requieren bool en ambos lados y devuelven bool
    if op in ("&&", "||"):
        if izq != "bool" or der != "bool":
            reportar(
                az,
                "Operaciones permitidas",
                n,
                f"Operación lógica '{op}' inválida entre '{izq}' y '{der}'.",
                "Los operadores lógicos '&&' y '||' solo aceptan operandos de tipo 'bool'.",
            )
            return ERROR
        return "bool"

    # 2. Operadores relacionales: devuelven bool
    if op in ("==", "!=", "<", ">", "<=", ">="):
        if op in ("<", ">", "<=", ">="):
            if izq not in ("int", "float64", "string") or izq != der:
                if conversion(az, izq, der, n, f"comparación '{op}'"):
                    return ERROR
                reportar(
                    az,
                    "Operaciones permitidas",
                    n,
                    f"No se pueden comparar valores de tipo '{izq}' y '{der}' con '{op}'.",
                    "Compara valores del mismo tipo (int, float64 o string).",
                )
                return ERROR
        else:
            if izq != der:
                if conversion(az, izq, der, n, f"comparación '{op}'"):
                    return ERROR
                reportar(
                    az,
                    "Operaciones permitidas",
                    n,
                    f"Comparación '{op}' inválida entre '{izq}' y '{der}'.",
                    "Ambos lados de la comparación deben ser del mismo tipo.",
                )
                return ERROR
        return "bool"

    # 3. Operadores aritméticos (+, -, *, /, %)
    # Primero detectamos si es un intento de conversión implícita entre int y float64
    if conversion(az, izq, der, n, f"operación '{op}'"):
        return ERROR

    if op == "+":
        if izq in ("int", "float64", "string") and izq == der:
            return izq
        reportar(
            az,
            "Operaciones permitidas",
            n,
            f"Operación '+' inválida entre operandos de tipo '{izq}' y '{der}' (tipos incompatibles).",
            "El operador '+' solo suma números del mismo tipo (int o float64) o concatena dos 'string'.",
        )
        return ERROR

    if op in ("-", "*", "/", "%"):
        if op == "%" and (izq != "int" or der != "int"):
            reportar(
                az,
                "Operaciones permitidas",
                n,
                f"Operación '%' inválida entre operandos de tipo '{izq}' y '{der}'.",
                "El operador módulo '%' solo se aplica entre números enteros ('int').",
            )
            return ERROR
        if izq in ("int", "float64") and izq == der:
            return izq
        reportar(
            az,
            "Operaciones permitidas",
            n,
            f"Operación '{op}' inválida entre operandos de tipo '{izq}' y '{der}' (tipos incompatibles).",
            f"El operador '{op}' solo puede aplicarse entre números del mismo tipo exacto ('int' o 'float64').",
        )
        return ERROR

    return ERROR

# ===== FIN aporte: Samuel Echeverría (SamuelEcheverria) =====