"""Fase 2 — Análisis sintáctico de Go con PLY (ply.yacc).

>>> A CARGO DEL GRUPO <<<

La API solo llama a `analizar_sintactico(codigo)`.

Contrato (ver modelos.py):
    analizar_sintactico(codigo: str) -> tuple[Nodo | None, list[ErrorAnalisis]]

El árbol que devuelvas es el que se dibuja en la interfaz y el que recibe
semantico.py. Construye objetos `Nodo`, no tuplas:

    def p_sentencia_if(p):
        'sentencia_if : IF expresion bloque'
        p[0] = Nodo("IfStmt", "", p.lineno(1), [p[2], p[3]])

La gramática es la de la sección 4 del documento del proyecto
(Proyecto_LP_Parcial1_LosGogos_G3.pdf). Qué reglas le tocan a cada uno sale
de la Tabla 11 (Asignación de reglas) más el reparto del avance 2. Lo que
queda fuera está en "Casos fuera de la gramática", al final de este
encabezado.

Cómo se reparte este archivo
----------------------------
Igual que en lexico.py: cada integrante escribe SOLO dentro de su bloque
INICIO/FIN. La "Estructura común" ya está hecha y compila sola, así que cada
uno puede probar su parte sin esperar a los demás.

PLY junta todas las funciones p_ que definen el mismo no terminal. Por eso
cada integrante agrega sus alternativas a `sentencia`, `expresion` y `tipo`
desde su propio bloque, con su propia función:

    def p_sentencia_AndreewCore(p):
        '''sentencia : declaracion_var
                     | for_condicional'''
        p[0] = p[1]

Cuando dos integrantes aportan formas de la misma construcción (for y
funciones), cada uno usa su propio no terminal (`for_condicional`,
`for_clasico`, `func_con_retorno`...) en lugar de `sentencia_for` o
`declaracion_func`: si dos escribieran `sentencia : sentencia_for`, PLY se
detiene con "Duplicate rule". El árbol usa el mismo `Nodo` para todas
(p. ej. "ForStmt", "FuncDecl"), así el semántico no ve la diferencia.

Un no terminal que se usa pero nadie define rompe la construcción del parser
("Symbol 'x' used, but not defined"): no dejen reglas a medias fuera de los
comentarios.

Para ver los conflictos shift/reduce de la gramática, desde backend/:
    GOTUTOR_DEBUG_YACC=1 python probar_sintactico.py ../algoritmos/algoritmo1.go
deja analizador/parser.out (ignorado por git) con los estados y conflictos.

Casos fuera de la gramática (pendientes / limitaciones para la sustentación)
--------------------------------------------------------------------------
El alcance es la Tabla 11 del documento más el reparto del avance 2 (ver
CONTRIBUTING.md). Lo de la sección 4 que nadie tiene asignado no se
implementa; se anota aquí para explicarlo en la sustentación.

  Se implementan aunque no estén en la sección 4 (el documento los necesita):
  - Programa, `package` e `import`: el documento no define la regla inicial.
    Resuelto en la estructura común (solo `import "x"`, no `import ( ... )`).
  - Tipos compuestos en parámetros (`notas []float64`, `m map[string]int`):
    la Tabla 9 los usa como tipos. Cada dueño de una estructura de datos
    agrega su forma a `tipo`.
  - Structs y métodos: la entrega pide clases, propiedades y métodos y el
    documento no los define (AndreewCore).

  Fuera del alcance (están en la sección 4 o en los algoritmos, pero no en
  la Tabla 11 ni en el reparto):
  - `var total = 10` (var sin tipo): solo se asignó la variable con tipo.
  - Conversión explícita `float64(x)`. algoritmo1.go (L15) y algoritmo2.go
    (L23) la usan: hay que reescribir esas líneas o fallarán.
  - Asignar a un índice: `stock["lapiz"] += llegada` (algoritmo1.go L37).
    `asignacion` solo admite un ID a la izquierda.
  - Declaración múltiple: `suma, promedio, perfecta := estadisticas(notas)`
    (algoritmo2.go L38). Sin ella, el resultado de una función con varios
    retornos solo se puede devolver, no guardar.

  Limitaciones aceptadas:
  - Sin inserción automática de ';': los saltos de línea se ignoran y ';' es
    opcional (`sentencia : PUNTO_COMA`). Se acepta `x := 1 y := 2` en una
    misma línea, que Go rechaza.
  - Sin coma final en literales de varias líneas (`lista_valores`).
  - Por lo mismo, `return` sin valor seguido de una línea que empieza con
    un ID se lee como `return x` (conflicto shift/reduce esperado).
  - `range` solo sobre un ID; `case` debe tener al menos una sentencia.
  - Las funciones son sentencias (así lo define el documento), así que el
    parser acepta funciones dentro de funciones; Go no.
  - Sin `if x := f(); x > 0`, `import ( ... )`, literales de struct dentro de
    la condición de if/for/switch, punteros, interfaces ni goroutines.
"""

import os
import sys
from functools import cache

import ply.yacc as yacc

from .lexico import construir_lexer, tokens  # noqa: F401 (yacc lee `tokens` de este módulo)
from .modelos import ErrorAnalisis, Nodo, columna

# Los errores de la ejecución actual. analizar_sintactico los reinicia; es
# seguro ser global porque servicio.py atiende un análisis a la vez.
_errores: list[ErrorAnalisis] = []

# Sin esto PLY toma como símbolo inicial la primera regla del archivo, y el
# orden de los bloques no debería importar.
start = "programa"


# ===========================================================================
# Estructura común (preparada antes del reparto; compila sin los aportes)
# ===========================================================================
# Reglas que usan los tres bloques: programa, bloque, sentencias, tipos
# primitivos, operandos simples, llamadas, parámetros, return y errores.

def p_programa(p):
    """programa : PACKAGE ID importaciones sentencias
                | PACKAGE ID importaciones"""
    hijos = [Nodo("PackageClause", p[2], p.lineno(1)), *p[3]]
    if len(p) == 5:
        hijos += p[4]
    p[0] = Nodo("Program", "", p.lineno(1), hijos)


def p_importaciones(p):
    """importaciones : importaciones IMPORT CADENA
                     | empty"""
    if len(p) == 2:
        p[0] = []
    else:
        p[0] = p[1] + [Nodo("ImportDecl", p[3], p.lineno(2))]


def p_sentencias(p):
    """sentencias : sentencia
                  | sentencias sentencia"""
    # Las sentencias vacías (un ';' suelto) llegan como None y no van al árbol.
    previas = [] if len(p) == 2 else p[1]
    p[0] = previas + ([p[len(p) - 1]] if p[len(p) - 1] is not None else [])


def p_sentencia_comun(p):
    """sentencia : BREAK
                 | CONTINUE
                 | llamada
                 | sentencia_return"""
    if p.slice[1].type in ("BREAK", "CONTINUE"):
        p[0] = Nodo("BranchStmt", p[1], p.lineno(1))
    else:
        p[0] = p[1]


def p_sentencia_vacia(p):
    """sentencia : PUNTO_COMA"""
    # ';' es opcional en GoTutor (no hay inserción automática): un ';' escrito
    # a mano es una sentencia vacía, y así ninguna regla tiene que pedirlo.
    p[0] = None


def p_sentencia_error(p):
    """sentencia : error"""
    # Permite seguir analizando tras un error y reportar más de uno; p_error
    # ya registró el mensaje.
    p[0] = Nodo("Error", "", p.lineno(1), error="syn")


def p_bloque(p):
    """bloque : LLAVE_IZQ sentencias LLAVE_DER
              | LLAVE_IZQ LLAVE_DER"""
    p[0] = Nodo("Block", "", p.lineno(1), p[2] if len(p) == 4 else [])


def p_tipo_primitivo(p):
    """tipo : TIPO_INT
            | TIPO_FLOAT
            | TIPO_STRING
            | TIPO_BOOL"""
    p[0] = Nodo("Type", p[1], p.lineno(1))


def p_expresion_literal(p):
    """expresion : ENTERO
                 | DECIMAL
                 | CADENA
                 | TRUE
                 | FALSE"""
    p[0] = Nodo("BasicLit", p[1], p.lineno(1))


def p_expresion_id(p):
    """expresion : ID"""
    p[0] = Nodo("Ident", p[1], p.lineno(1))


def p_expresion_paren(p):
    """expresion : PAREN_IZQ expresion PAREN_DER"""
    p[0] = Nodo("ParenExpr", "()", p.lineno(1), [p[2]])


def p_expresion_llamada(p):
    """expresion : llamada"""
    p[0] = p[1]


def p_llamada(p):
    """llamada : ID PAREN_IZQ argumentos PAREN_DER"""
    p[0] = Nodo("CallExpr", p[1], p.lineno(1), p[3])


def p_argumentos(p):
    """argumentos : lista_valores
                  | empty"""
    p[0] = p[1] or []


def p_lista_valores(p):
    """lista_valores : expresion
                     | lista_valores COMA expresion"""
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]


def p_parametros(p):
    """parametros : lista_parametros
                  | empty"""
    p[0] = p[1] or []


def p_lista_parametros(p):
    """lista_parametros : parametro
                        | lista_parametros COMA parametro"""
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]


def p_parametro(p):
    """parametro : ID tipo"""
    p[0] = Nodo("Param", p[1], p.lineno(1), [p[2]])


def p_sentencia_return(p):
    """sentencia_return : RETURN lista_valores
                        | RETURN"""
    # Común a las tres funciones (sin retorno, uno y varios); que la
    # cantidad coincida con la firma lo revisa el semántico.
    # Conflicto shift/reduce esperado: sin ';' automático, `return` seguido
    # de una línea que empieza con ID se lee como `return x`. PLY elige
    # shift, que es lo correcto; solo afecta a código muerto tras el return.
    p[0] = Nodo("ReturnStmt", "", p.lineno(1), p[2] if len(p) == 3 else [])


def p_empty(p):
    """empty :"""
    p[0] = None


class _LexerConMemoria:
    """Envuelve el lexer de PLY para recordar el token anterior al actual.

    p_error lo necesita para ubicar el error donde está de verdad: sin ';'
    automático, falta algo al final de una línea pero el token inesperado es
    el primero de la línea siguiente.
    """

    def __init__(self, lexer):
        """Guarda el lexer real; `anterior` y `actual` empiezan vacíos."""
        self.lexer = lexer
        self.anterior = None
        self.actual = None

    def __getattr__(self, nombre):
        """Delega el resto (lineno, lexpos...) al lexer real.

        PLY los lee al reducir una regla vacía con tracking=True.
        """
        return getattr(self.lexer, nombre)

    def input(self, codigo):
        """Pasa el código al lexer real."""
        self.lexer.input(codigo)

    def token(self):
        """Entrega el siguiente token al parser y recuerda el anterior."""
        self.anterior, self.actual = self.actual, self.lexer.token()
        return self.actual


# El lexer de la ejecución actual, para que p_error vea el token anterior.
_memoria: _LexerConMemoria | None = None


def p_error(p):
    """Registra el error en `_errores` para que salga en la interfaz y en el log."""
    anterior = _memoria.anterior if _memoria else None
    if p is None:
        # Al llegar al final, el último token leído quedó en `actual`.
        ultimo = _memoria.actual if _memoria and _memoria.actual else anterior
        _errores.append(ErrorAnalisis(
            fase="syn",
            linea=ultimo.lineno if ultimo else 1,
            columna=_fin_de(ultimo) if ultimo else 1,
            mensaje="Fin de archivo inesperado: el programa terminó antes de completar una instrucción.",
            sugerencia="Revisa que cada '{' tenga su '}' y cada '(' su ')'.",
        ))
        return

    codigo = p.lexer.lexdata
    # Una línea que termina en ';', '{' o '}' ya está cerrada: ahí el problema
    # sí es el token nuevo.
    if (anterior is not None and anterior.lineno < p.lineno
            and anterior.type not in ("PUNTO_COMA", "LLAVE_IZQ", "LLAVE_DER")):
        # El token es el primero de su línea: lo que falta está al final de
        # la línea anterior (p. ej. un ')' sin cerrar).
        _errores.append(ErrorAnalisis(
            fase="syn",
            linea=anterior.lineno,
            columna=_fin_de(anterior),
            mensaje=f"La línea {anterior.lineno} quedó incompleta: después de '{anterior.value}' "
                    f"no se esperaba '{p.value}' (línea {p.lineno}).",
            sugerencia="Revisa si falta cerrar un paréntesis ')' o completar la instrucción.",
        ))
        return

    _errores.append(ErrorAnalisis(
        fase="syn",
        linea=p.lineno,
        columna=columna(codigo, p.lexpos),
        mensaje=f"Token inesperado: '{p.value}'.",
        sugerencia="Revisa el orden de la instrucción: puede faltar un operador, una coma, "
                   "un ';' o una llave antes de este punto.",
    ))


def _fin_de(tok) -> int:
    """Columna justo después del token `tok`, donde debería ir lo que falta."""
    # Los LexToken de PLY no guardan el código fuente; el lexer sí.
    return columna(_memoria.lexer.lexdata, tok.lexpos + len(str(tok.value)))


# ===== INICIO aporte: Paúl Rodríguez (AndreewCore) =====
# Reglas asignadas (Tabla 11 del documento):
#   - Variable con tipo: `var edad int`, `var nombre string = "Ana"`
#   - Sentencia for condicional: `for total < 100 { ... }`
#   - Estructura de datos: map  `map[string]int{"Ana": 20}`
#   - Funciones con retorno: `func suma(a int, b int) int { ... }`
# Además (reparto del avance 2):
#   - Impresión e ingreso de datos: `fmt.Println(...)`, `fmt.Scan(&x)`
#   - Acceso por índice: `numeros[0]`, `edades["Ana"]`
#   - for infinito: `for { ... }`
#   - Clases: struct (propiedades) y métodos con receptor
#
# TODO(AndreewCore): sección 4, "Declaración de Variables" (con tipo).
#   sentencia       : declaracion_var
#   declaracion_var : VAR ID tipo
#                   | VAR ID tipo ASIGNA expresion
#
# TODO(AndreewCore): sección 4, "Estructuras de Control" (for condicional e infinito).
#   sentencia       : for_condicional | for_infinito
#   for_condicional : FOR expresion bloque
#   for_infinito    : FOR bloque
#
# TODO(AndreewCore): sección 4, "Estructuras de Datos" (map).
#   expresion   : mapa
#   mapa        : MAP CORCHETE_IZQ tipo CORCHETE_DER tipo LLAVE_IZQ lista_pares LLAVE_DER
#   lista_pares : par | lista_pares COMA par
#   par         : expresion DOS_PUNTOS expresion
#   tipo        : MAP CORCHETE_IZQ tipo CORCHETE_DER tipo      (para parámetros, Tabla 9)
#
# TODO(AndreewCore): sección 4, "Declaraciones de Funciones" (con un retorno).
#   sentencia        : func_con_retorno
#   func_con_retorno : FUNC ID PAREN_IZQ parametros PAREN_DER tipo bloque
#   (`return` ya está en la estructura común.)
#
# TODO(AndreewCore): sección 4, "Impresión y solicitud de datos".
#   llamada   : ID PUNTO ID PAREN_IZQ argumentos PAREN_DER
#   expresion : AMPERSAND ID
#
# TODO(AndreewCore): sección 4, "Estructuras de Datos" (acceso por índice).
#   expresion     : acceso_indice
#   acceso_indice : ID CORCHETE_IZQ expresion CORCHETE_DER
#   (Sirve para los arreglos de SamuelEcheverria, los slices de Danilogb18 y los maps.)
#
# TODO(AndreewCore): clases (no están en el documento; las pide la entrega).
#   sentencia          : declaracion_struct | declaracion_metodo
#   declaracion_struct : TYPE ID STRUCT LLAVE_IZQ campos LLAVE_DER
#   campos             : campo | campos campo
#   campo              : ID tipo
#   declaracion_metodo : FUNC PAREN_IZQ ID ID PAREN_DER ID PAREN_IZQ parametros PAREN_DER bloque
#                      | FUNC PAREN_IZQ ID ID PAREN_DER ID PAREN_IZQ parametros PAREN_DER tipo bloque
#   expresion          : ID PUNTO ID                                   (leer una propiedad)
#   (La llamada `p.metodo()` ya queda cubierta por la llamada con prefijo de fmt.)
#   Cuidado: `tipo : ID` (para `var p Persona`) choca con la llamada `f(x)`,
#   y un literal `Persona{...}` como expresión general choca con `for x {`.
#   Si se agregan, que sea con reglas propias, p. ej.
#   `declaracion_corta : ID ASIGNA_CORTA ID LLAVE_IZQ ... LLAVE_DER`.

# ===== FIN aporte: Paúl Rodríguez (AndreewCore) =====


# ===== INICIO aporte: Danilo García (Danilogb18) =====
# Reglas asignadas (Tabla 11 del documento):
#   - Variable de asignación compuesta: `x += 2` (y la asignación simple `x = 8`)
#   - Estructura de datos: slice  `[]int{4, 5, 6}`
#   - Sentencia for range: `for i, v := range numeros { ... }`
#   - Funciones con múltiple retorno: `func dividir(...) (float64, bool) { ... }`
# Además (reparto del avance 2):
#   - Expresiones booleanas
#   - Declaración corta `x := 5`
#   - for clásico: `for i := 0; i < 10; i++ { ... }`
#   - Incremento y decremento: `x++`, `x--`
#
# TODO(Danilogb18): sección 4, "Declaración de Variables" (asignación y forma corta).
#   sentencia         : asignacion | declaracion_corta
#   asignacion        : ID ASIGNA expresion
#                     | ID MAS_ASIGNA expresion | ID MENOS_ASIGNA expresion
#                     | ID POR_ASIGNA expresion | ID DIV_ASIGNA expresion
#   declaracion_corta : ID ASIGNA_CORTA expresion
#
# TODO(Danilogb18): sección 4, "Expresiones Booleanas". TRUE y FALSE ya están
# en la estructura común; la precedencia ya incluye estos operadores.
#   expresion : expresion IGUAL expresion | expresion DISTINTO expresion
#             | expresion MENOR expresion | expresion MAYOR expresion
#             | expresion MENOR_IGUAL expresion | expresion MAYOR_IGUAL expresion
#             | expresion AND expresion | expresion OR expresion
#             | NOT expresion
#
# TODO(Danilogb18): sección 4, "Estructuras de Datos" (slice).
#   expresion : slice
#   slice     : CORCHETE_IZQ CORCHETE_DER tipo LLAVE_IZQ lista_valores LLAVE_DER
#   tipo      : CORCHETE_IZQ CORCHETE_DER tipo      (para parámetros, Tabla 9)
#
# TODO(Danilogb18): sección 4, "Estructuras de Control" (for clásico y for range).
#   sentencia   : for_clasico | for_range | incremento
#   for_clasico : FOR declaracion_corta PUNTO_COMA expresion PUNTO_COMA post_for bloque
#   for_range   : FOR ID COMA ID ASIGNA_CORTA RANGE ID bloque
#   post_for    : incremento | asignacion
#   incremento  : ID INCREMENTO | ID DECREMENTO
#
# TODO(Danilogb18): sección 4, "Declaraciones de Funciones" (múltiple retorno).
#   sentencia            : func_varios_retornos
#   func_varios_retornos : FUNC ID PAREN_IZQ parametros PAREN_DER PAREN_IZQ lista_tipos PAREN_DER bloque
#   lista_tipos          : tipo | lista_tipos COMA tipo

# ===== FIN aporte: Danilo García (Danilogb18) =====


# ===== INICIO aporte: Samuel Echeverría (SamuelEcheverria) =====
# Reglas asignadas (Tabla 11 del documento):
#   - Variable declaración de constante: `const PI = 3.14`
#   - Estructura de datos: arreglo  `[3]int{1, 2, 3}`
#   - Sentencia if / else if / else
#   - Funciones sin retorno: `func saludar() { ... }`
# Además (reparto del avance 2):
#   - Expresiones aritméticas
#   - switch / case / default
#
# Tokens que usan `%prec` en sus reglas (p. ej. "UMINUS" para el '-' unario).
# Se agregan a la precedencia al final del archivo; PLY no construye el
# parser si un nombre está en la precedencia y ninguna regla lo usa, por eso
# la lista empieza vacía.
precedencia_SamuelEcheverria: list[str] = []

# TODO(SamuelEcheverria): sección 4, "Declaración de Variables" (constante).
#   sentencia         : declaracion_const
#   declaracion_const : CONST ID ASIGNA expresion
#
# TODO(SamuelEcheverria): sección 4, "Estructuras de Datos" (arreglo).
#   expresion : arreglo
#   arreglo   : CORCHETE_IZQ ENTERO CORCHETE_DER tipo LLAVE_IZQ lista_valores LLAVE_DER
#   tipo      : CORCHETE_IZQ ENTERO CORCHETE_DER tipo      (para parámetros, Tabla 9)
#
# TODO(SamuelEcheverria): sección 4, "Estructuras de Control" (if).
#   sentencia    : sentencia_if
#   sentencia_if : IF expresion bloque
#                | IF expresion bloque ELSE bloque
#                | IF expresion bloque ELSE sentencia_if
#
# TODO(SamuelEcheverria): sección 4, "Declaraciones de Funciones" (sin retorno).
#   sentencia        : func_sin_retorno
#   func_sin_retorno : FUNC ID PAREN_IZQ parametros PAREN_DER bloque
#
# TODO(SamuelEcheverria): sección 4, "Expresiones Aritméticas". Los operandos
# simples (ENTERO, DECIMAL, CADENA, ID, paréntesis) ya están en la estructura común.
#   expresion : expresion MAS expresion | expresion MENOS expresion
#             | expresion POR expresion | expresion DIVIDIDO expresion
#             | expresion MODULO expresion
#             | MENOS expresion %prec UMINUS      (y agregar "UMINUS" a precedencia_SamuelEcheverria)
#
# TODO(SamuelEcheverria): sección 4, "Estructuras de Control" (switch).
#   sentencia        : sentencia_switch
#   sentencia_switch : SWITCH expresion LLAVE_IZQ casos LLAVE_DER
#   casos            : caso | casos caso
#   caso             : CASE expresion DOS_PUNTOS sentencias
#                    | DEFAULT DOS_PUNTOS sentencias

# ===== FIN aporte: Samuel Echeverría (SamuelEcheverria) =====


# ---------------------------------------------------------------------------
# Precedencia de operadores (Tabla 8 del documento, de menor a mayor)
# ---------------------------------------------------------------------------
# PLY acepta en la precedencia tokens que aún ninguna regla usa, así que los
# operadores de todos van desde ya; solo los nombres inventados para %prec
# (como UMINUS) esperan a que exista su regla.
precedence = (
    ("left", "OR"),
    ("left", "AND"),
    ("left", "IGUAL", "DISTINTO", "MENOR", "MAYOR", "MENOR_IGUAL", "MAYOR_IGUAL"),
    ("left", "MAS", "MENOS"),
    ("left", "POR", "DIVIDIDO", "MODULO"),
    ("right", "NOT", *precedencia_SamuelEcheverria),
)


def _tiene_reglas() -> bool:
    """Indica si el grupo ya escribió alguna regla de gramática."""
    modulo = sys.modules[__name__]
    return any(nombre.startswith("p_") and nombre != "p_error" for nombre in vars(modulo))


def analizar_sintactico(codigo: str) -> tuple[Nodo | None, list[ErrorAnalisis]]:
    """Parsea `codigo` y devuelve el AST (o None si no se pudo) y los errores."""
    global _memoria
    if not _tiene_reglas():
        raise NotImplementedError("sintactico.py aún no define reglas")

    _errores.clear()
    _memoria = _LexerConMemoria(construir_lexer())
    ast = _parser().parse(codigo, lexer=_memoria, tracking=True)
    return ast, list(_errores)


@cache
def _parser():
    """Construye el parser una sola vez por proceso.

    Generar las tablas LALR de una gramática de Go tarda bastante más que
    parsear un programa, así que no conviene repetirlo en cada petición; el
    recargador de Flask reinicia el proceso cuando cambia este archivo.
    write_tables en False para que no aparezca parsetab.py en el repo; con
    GOTUTOR_DEBUG_YACC=1 se escribe parser.out (también ignorado por git).
    """
    depurar = os.environ.get("GOTUTOR_DEBUG_YACC") == "1"
    return yacc.yacc(module=sys.modules[__name__], write_tables=False, debug=depurar,
                     debugfile="parser.out", outputdir=os.path.dirname(__file__))
