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

    def p_sentencia_<usuario>(p):
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
  - `var total = 10` (var sin tipo): la Tabla 11 solo asigna la variable con
    tipo, pero la sección 4 la incluye en `declaracion_var` (AndreewCore).

  Fuera del alcance (están en la sección 4 o en los algoritmos, pero no en
  la Tabla 11 ni en el reparto):
  - Conversión explícita `float64(x)`.
  - Asignar a un índice: `stock["lapiz"] += llegada`. `asignacion` solo
    admite un ID a la izquierda.
  - Declaración múltiple: `suma, promedio, perfecta := estadisticas(notas)`.
    Sin ella, el resultado de una función con varios retornos solo se puede
    devolver o pasar a otra función, no guardar. Por eso el ejemplo
    `ambitos` de la interfaz usa `var total float64 = dividir(8, 2)`.

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


_ultimo_token_error = None
def p_sentencia_error(p):
    """sentencia : error"""
    # Permite seguir analizando tras un error y reportar más de uno; p_error ya registró el mensaje.
    global _ultimo_token_error
    token = _memoria.actual if _memoria else None
    if token is not None and token is _ultimo_token_error:
        token.type = "PUNTO_COMA"
    _ultimo_token_error = token
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
#     (y sin tipo, `var total = 10`, porque la sección 4 la incluye)
#   - Sentencia for condicional: `for total < 100 { ... }`
#   - Estructura de datos: map  `map[string]int{"Ana": 20}`
#   - Funciones con retorno: `func suma(a int, b int) int { ... }`
# Además (reparto del avance 2):
#   - Impresión e ingreso de datos: `fmt.Println(...)`, `fmt.Scan(&x)`
#   - Acceso por índice: `numeros[0]`, `edades["Ana"]`
#   - for infinito: `for { ... }`
#   - Clases: struct (propiedades) y métodos con receptor

def p_sentencia_AndreewCore(p):
    """sentencia : declaracion_var
                 | for_condicional
                 | for_infinito
                 | func_con_retorno
                 | declaracion_struct
                 | declaracion_metodo"""
    p[0] = p[1]


# --- Paso 1: variable con tipo ---------------------------------------------

def p_declaracion_var(p):
    """declaracion_var : VAR ID tipo
                       | VAR ID tipo ASIGNA expresion
                       | VAR ID ASIGNA expresion"""
    # Sin valor, Go le da el valor cero del tipo: el nodo solo lleva el tipo.
    # Sin tipo, Go lo infiere del valor: el nodo solo lleva la expresión y el
    # semántico deduce el tipo.
    if p.slice[3].type == "ASIGNA":
        hijos = [p[4]]
    else:
        hijos = [p[3]] if len(p) == 4 else [p[3], p[5]]
    p[0] = Nodo("VarDecl", p[2], p.lineno(1), hijos)


def p_declaracion_var_struct(p):
    """declaracion_var : VAR ID ID
                       | VAR ID ID ASIGNA literal_struct"""
    # Regla aparte para `var a Persona`: agregar `tipo : ID` choca con la
    # llamada `f(x)`, y aquí el ID solo puede ser el nombre de un struct.
    tipo = Nodo("Type", p[3], p.lineno(3))
    hijos = [tipo] if len(p) == 4 else [tipo, p[5]]
    p[0] = Nodo("VarDecl", p[2], p.lineno(1), hijos)


# --- Paso 2: for condicional e infinito -------------------------------------

def p_for_condicional(p):
    """for_condicional : FOR expresion bloque"""
    p[0] = Nodo("ForStmt", "condicional", p.lineno(1), [p[2], p[3]])


def p_for_infinito(p):
    """for_infinito : FOR bloque"""
    p[0] = Nodo("ForStmt", "infinito", p.lineno(1), [p[2]])


# --- Paso 3: map ------------------------------------------------------------

def p_expresion_AndreewCore(p):
    """expresion : mapa
                 | acceso_indice
                 | selector"""
    p[0] = p[1]


def p_mapa(p):
    """mapa : MAP CORCHETE_IZQ tipo CORCHETE_DER tipo LLAVE_IZQ lista_pares LLAVE_DER
            | MAP CORCHETE_IZQ tipo CORCHETE_DER tipo LLAVE_IZQ LLAVE_DER"""
    pares = p[7] if len(p) == 9 else []
    p[0] = Nodo("MapLit", "", p.lineno(1), [p[3], p[5], *pares])


def p_lista_pares(p):
    """lista_pares : par
                   | lista_pares COMA par"""
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]


def p_par(p):
    """par : expresion DOS_PUNTOS expresion"""
    p[0] = Nodo("KeyValue", ":", p.lineno(2), [p[1], p[3]])


def p_tipo_map(p):
    """tipo : MAP CORCHETE_IZQ tipo CORCHETE_DER tipo"""
    # Para parámetros como `m map[string]int` (Tabla 9).
    p[0] = Nodo("MapType", "map", p.lineno(1), [p[3], p[5]])


# --- Paso 4: función con un retorno -----------------------------------------

def p_func_con_retorno(p):
    """func_con_retorno : FUNC ID PAREN_IZQ parametros PAREN_DER tipo bloque"""
    # Mismo nodo que las funciones de los demás para que el semántico no
    # distinga la forma; el tipo de retorno va como hijo "Results".
    resultados = Nodo("Results", "", p.lineno(6), [p[6]])
    p[0] = Nodo("FuncDecl", p[2], p.lineno(1), [*p[4], resultados, p[7]])


# --- Paso 5: fmt (impresión y lectura) --------------------------------------

def p_llamada_selector(p):
    """llamada : ID PUNTO ID PAREN_IZQ argumentos PAREN_DER"""
    # Cubre fmt.Println(...) y también la llamada a un método: p.Saludar().
    p[0] = Nodo("CallExpr", f"{p[1]}.{p[3]}", p.lineno(1), p[5])


def p_expresion_direccion(p):
    """expresion : AMPERSAND ID"""
    # fmt.Scan necesita la dirección de la variable para poder escribir en ella.
    p[0] = Nodo("UnaryExpr", "&", p.lineno(1), [Nodo("Ident", p[2], p.lineno(2))])


# --- Paso 6: acceso por índice ----------------------------------------------

def p_acceso_indice(p):
    """acceso_indice : ID CORCHETE_IZQ expresion CORCHETE_DER"""
    p[0] = Nodo("IndexExpr", p[1], p.lineno(1), [p[3]])


# --- Paso 7: structs (propiedades) y métodos ---------------------------------

def p_declaracion_struct(p):
    """declaracion_struct : TYPE ID STRUCT LLAVE_IZQ campos LLAVE_DER"""
    p[0] = Nodo("StructDecl", p[2], p.lineno(1), p[5])


def p_campos(p):
    """campos : campo
              | campos campo"""
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]


def p_campo(p):
    """campo : ID tipo"""
    p[0] = Nodo("Field", p[1], p.lineno(1), [p[2]])


def p_declaracion_metodo(p):
    """declaracion_metodo : FUNC PAREN_IZQ ID ID PAREN_DER ID PAREN_IZQ parametros PAREN_DER bloque
                          | FUNC PAREN_IZQ ID ID PAREN_DER ID PAREN_IZQ parametros PAREN_DER tipo bloque"""
    # El receptor `(e Estudiante)` es lo que ata el método al struct.
    receptor = Nodo("Receiver", p[3], p.lineno(3), [Nodo("Type", p[4], p.lineno(4))])
    hijos = [receptor, *p[8]]
    if len(p) == 12:
        hijos.append(Nodo("Results", "", p.lineno(10), [p[10]]))
    hijos.append(p[len(p) - 1])
    p[0] = Nodo("MethodDecl", p[6], p.lineno(1), hijos)


def p_selector(p):
    """selector : ID PUNTO ID"""
    # Leer una propiedad: e.nombre.
    p[0] = Nodo("SelectorExpr", f"{p[1]}.{p[3]}", p.lineno(1))


def p_literal_struct(p):
    """literal_struct : ID LLAVE_IZQ lista_pares LLAVE_DER
                      | ID LLAVE_IZQ LLAVE_DER"""
    # Solo se usa tras `var x T =`; como expresión general chocaría con `for x {`.
    pares = p[3] if len(p) == 5 else []
    p[0] = Nodo("CompositeLit", p[1], p.lineno(1), pares)


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

def p_sentencia_Danilogb18(p):
    """sentencia : asignacion
                 | declaracion_corta
                 | incremento
                 | for_clasico
                 | for_range
                 | func_varios_retornos"""
    # Agrega mis construcciones a la lista de sentencias válidas. Cada una ya construye su propio Nodo, así que solo se pasa hacia arriba.
    p[0] = p[1]


# Declaración de variables: asignación simple/compuesta y declaración corta

def p_asignacion(p):
    """asignacion : ID ASIGNA expresion
                  | ID MAS_ASIGNA expresion
                  | ID MENOS_ASIGNA expresion
                  | ID POR_ASIGNA expresion
                  | ID DIV_ASIGNA expresion"""
    p[0] = Nodo("AssignStmt", p[2], p.lineno(1),[Nodo("Ident", p[1], p.lineno(1)), p[3]])


def p_declaracion_corta(p):
    """declaracion_corta : ID ASIGNA_CORTA expresion"""
    # Declaración corta `x := 5`: declara la variable y deduce su tipo del
    # valor. Es un no terminal propio (no va dentro de `asignacion`) porque el for clásico la usa como inicialización y el semántico la trata distinto: 
    # aquí se declara un símbolo nuevo, en `=` se usa uno existente.
    p[0] = Nodo("ShortVarDecl", ":=", p.lineno(1), [Nodo("Ident", p[1], p.lineno(1)), p[3]])


# Expresiones booleanas: comparaciones y conectores lógicos

def p_expresion_booleana(p):
    """expresion : expresion IGUAL expresion
                 | expresion DISTINTO expresion
                 | expresion MENOR expresion
                 | expresion MAYOR expresion
                 | expresion MENOR_IGUAL expresion
                 | expresion MAYOR_IGUAL expresion
                 | expresion AND expresion
                 | expresion OR expresion"""
    # la tabla `precedence` del final resuelve el orden: || < && < comparaciones.
    p[0] = Nodo("BinaryExpr", p[2], p.lineno(2), [p[1], p[3]])


def p_expresion_not(p):
    """expresion : NOT expresion"""
    # Negación lógica `!activo`. NOT ya está en la precedencia con asociatividad
    p[0] = Nodo("UnaryExpr", "!", p.lineno(1), [p[2]])


# Estructura de datos: slice

def p_expresion_slice(p):
    """expresion : slice"""
    # Un literal de slice puede ir donde vaya cualquier valor: `l := []int{1, 2}`.
    p[0] = p[1]


def p_slice(p):
    """slice : CORCHETE_IZQ CORCHETE_DER tipo LLAVE_IZQ lista_valores LLAVE_DER"""
    # Literal de slice `[]float64{8.5, 9.0}`. A diferencia del arreglo, los corchetes van vacíos (sin tamaño). `lista_valores` es de la estructura común.
    p[0] = Nodo("CompositeLit", "[]" + p[3].dato, p.lineno(1), p[5])


def p_tipo_slice(p):
    """tipo : CORCHETE_IZQ CORCHETE_DER tipo"""
    # Tipo slice para parámetros y declaraciones: `func f(notas []float64)`.
    # Es recursivo (`tipo` dentro de `tipo`), así también vale `[][]int`.
    # El dato guarda el tipo completo como texto para que el semántico lo compare.
    p[0] = Nodo("Type", "[]" + p[3].dato, p.lineno(1))


# Estructuras de control: incremento, for clásico y for range

def p_incremento(p):
    """incremento : ID INCREMENTO
                  | ID DECREMENTO"""
    # `x++` y `x--`. En Go son sentencias, no expresiones (no existe `y = x++`),
    # por eso van en `sentencia` y no en `expresion`.
    p[0] = Nodo("IncDecStmt", p[2], p.lineno(1), [Nodo("Ident", p[1], p.lineno(1))])


def p_for_clasico(p):
    """for_clasico : FOR declaracion_corta PUNTO_COMA expresion PUNTO_COMA post_for bloque"""
    # for de tres partes: `for i := 0; i < 10; i++ { ... }`.
    # Hijos: inicialización, condición, paso y cuerpo, en ese orden.
    # Los ';' aquí son obligatorios (separan las tres partes), a diferencia
    # del ';' opcional al final de una sentencia.
    p[0] = Nodo("ForStmt", "clásico", p.lineno(1), [p[2], p[4], p[6], p[7]])


def p_post_for(p):
    """post_for : incremento
                | asignacion"""
    # Lo que se ejecuta al final de cada vuelta: `i++` o `i += 2`.
    p[0] = p[1]


def p_for_range(p):
    """for_range : FOR ID COMA ID ASIGNA_CORTA RANGE ID bloque"""
    p[0] = Nodo("ForStmt", "range", p.lineno(1), [
        Nodo("Ident", p[2], p.lineno(2)),
        Nodo("Ident", p[4], p.lineno(4)),
        Nodo("Ident", p[7], p.lineno(7)),
        p[8],
    ])


# Funciones con múltiple retorno

def p_func_varios_retornos(p):
    """func_varios_retornos : FUNC ID PAREN_IZQ parametros PAREN_DER PAREN_IZQ lista_tipos PAREN_DER bloque"""
    p[0] = Nodo("FuncDecl", p[2], p.lineno(1), [
        Nodo("Params", "", p.lineno(3), p[4]),
        Nodo("Results", "", p.lineno(6), p[7]),
        p[9],
    ])


def p_lista_tipos(p):
    """lista_tipos : tipo
                   | lista_tipos COMA tipo"""
    # Tipos de retorno separados por coma: `(float64, float64, bool)`. Recursiva por la izquierda, igual que lista_valores de la estructura común.
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]

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
precedencia_SamuelEcheverria: list[str] = ["UMINUS"]


def p_sentencia_SamuelEcheverria(p):
    """sentencia : declaracion_const
                 | sentencia_if
                 | func_sin_retorno
                 | sentencia_switch"""
    p[0] = p[1]


def p_expresion_SamuelEcheverria(p):
    """expresion : arreglo
                 | expresion MAS expresion
                 | expresion MENOS expresion
                 | expresion POR expresion
                 | expresion DIVIDIDO expresion
                 | expresion MODULO expresion
                 | MENOS expresion %prec UMINUS"""
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3:
        p[0] = Nodo("UnaryExpr", p[1], p.lineno(1), [p[2]])
    else:
        p[0] = Nodo("BinaryExpr", p[2], p.lineno(2), [p[1], p[3]])


def p_tipo_SamuelEcheverria(p):
    """tipo : CORCHETE_IZQ ENTERO CORCHETE_DER tipo"""
    p[0] = Nodo("Type", f"[{p[2]}]{p[4].dato}", p.lineno(1), [p[4]])


def p_declaracion_const(p):
    """declaracion_const : CONST ID ASIGNA expresion"""
    p[0] = Nodo("ConstDecl", p[2], p.lineno(1), [p[4]])


def p_arreglo(p):
    """arreglo : CORCHETE_IZQ ENTERO CORCHETE_DER tipo LLAVE_IZQ lista_valores LLAVE_DER"""
    p[0] = Nodo("ArrayLit", f"[{p[2]}]{p[4].dato}", p.lineno(1), [p[4], *p[6]])


def p_if_SamuelEcheverria(p):
    """sentencia_if : IF expresion bloque
                    | IF expresion bloque ELSE bloque
                    | IF expresion bloque ELSE sentencia_if"""
    hijos = [p[2], p[3]] if len(p) == 4 else [p[2], p[3], p[5]]
    p[0] = Nodo("IfStmt", "", p.lineno(1), hijos)


def p_func_sin_retorno(p):
    """func_sin_retorno : FUNC ID PAREN_IZQ parametros PAREN_DER bloque"""
    p[0] = Nodo("FuncDecl", p[2], p.lineno(1), [*p[4], p[6]])


def p_sentencia_switch(p):
    """sentencia_switch : SWITCH expresion LLAVE_IZQ casos LLAVE_DER"""
    p[0] = Nodo("SwitchStmt", "", p.lineno(1), [p[2], *p[4]])


def p_casos(p):
    """casos : caso
             | casos caso"""
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]


def p_caso(p):
    """caso : CASE expresion DOS_PUNTOS sentencias
            | DEFAULT DOS_PUNTOS sentencias"""
    if p.slice[1].type == "CASE":
        p[0] = Nodo("CaseClause", "case", p.lineno(1), [p[2], *p[4]])
    else:
        p[0] = Nodo("CaseClause", "default", p.lineno(1), p[3])

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
