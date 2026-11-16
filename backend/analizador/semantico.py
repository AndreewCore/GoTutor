"""Fase 3 — Análisis semántico: recorre el AST, llena la tabla de símbolos y
aplica las reglas semánticas de la Tabla 11 del documento del proyecto.

La API llama a `analizar_semantico(ast, codigo)` solo si las fases léxica y
sintáctica terminaron sin errores.

Contrato (ver modelos.py):
    analizar_semantico(ast: Nodo, codigo: str)
        -> tuple[list[Simbolo], list[ErrorAnalisis]]

Cómo se reparte este archivo
----------------------------
Igual que en lexico.py y sintactico.py: cada integrante escribe SOLO dentro
de su bloque INICIO/FIN, en las dos funciones de sus reglas. La "Estructura
común" las llama en el punto del recorrido donde aplican.

La estructura común es lo que piden las Tablas 9 y 10 del documento, sin lo
cual ninguna regla puede funcionar: la tabla de símbolos con sus ámbitos y el
tipo de cada expresión. No reporta errores; eso lo hacen las reglas.

Tipo `error` (Tabla 9): lo que el semántico no modela tiene ese tipo, y las
reglas no se aplican a una expresión de tipo `error`. Así no hay mensajes en
cascada ni errores falsos por lo que está fuera del alcance.

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

# Tipos internos de la Tabla 9.
ERROR = "error"
SIN_VALOR = "sin valor"

COMPARACIONES = {"==", "!=", "<", ">", "<=", ">="}
LOGICOS = {"&&", "||"}


# ===== Estructura común =====

class Ambito:
    """Un nivel de la tabla de símbolos: global, función o bloque."""

    def __init__(self, nombre: str, padre: Ambito | None = None):
        """Crea el ámbito; su ruta ("main › for") es la que sale en la tabla."""
        self.padre = padre
        self.simbolos: dict[str, Simbolo] = {}
        es_hijo_de_global = padre is not None and padre.padre is None
        self.ruta = nombre if padre is None or es_hijo_de_global else f"{padre.ruta} › {nombre}"


class Analizador:
    """Recorre el AST guardando el ámbito y la función actuales, los símbolos y los errores."""

    def __init__(self, codigo: str):
        """Empieza en el ámbito global, sin símbolos ni errores."""
        self.codigo = codigo
        self.lineas = codigo.split("\n")
        self.ambito = Ambito("global")
        self.simbolos: list[Simbolo] = []
        self.errores: list[ErrorAnalisis] = []
        self.firmas: dict[str, list[str]] = {}  # función -> tipos de retorno
        self.funcion: tuple[str, list[str]] | None = None  # (nombre, tipos de retorno)

    # --- Tabla de símbolos ---------------------------------------------------

    def abrir(self, nombre: str) -> None:
        """Entra a un ámbito nuevo dentro del actual."""
        self.ambito = Ambito(nombre, self.ambito)

    def cerrar(self) -> None:
        """Vuelve al ámbito padre."""
        self.ambito = self.ambito.padre

    def declarar(self, nombre: str, tipo: str, categoria: str, linea: int) -> Simbolo:
        """Agrega `nombre` al ámbito actual y a la tabla que se muestra en la interfaz."""
        simbolo = Simbolo(nombre, tipo, categoria, self.ambito.ruta, linea)
        self.ambito.simbolos[nombre] = simbolo
        self.simbolos.append(simbolo)
        return simbolo

    def buscar(self, nombre: str) -> Simbolo | None:
        """Busca `nombre` del ámbito actual hacia el global; None si no está declarado."""
        ambito = self.ambito
        while ambito is not None:
            if nombre in ambito.simbolos:
                return ambito.simbolos[nombre]
            ambito = ambito.padre
        return None

    def reportar(self, regla: str, nodo: Nodo, mensaje: str, sugerencia: str = "",
                 texto: str | None = None) -> None:
        """Registra un error semántico y marca `nodo` en rojo en el árbol.

        `texto` es lo que se busca en la línea para la columna (por defecto,
        `nodo.dato`): los nodos solo guardan la línea.
        """
        nodo.error = "sem"
        self.errores.append(ErrorAnalisis("sem", nodo.linea, self._columna(nodo.linea, texto or nodo.dato),
                                          f"[{regla}] {mensaje}", sugerencia))

    def _columna(self, linea: int, texto: str) -> int:
        """Columna de la primera aparición de `texto` en la línea, o 1 si no aparece."""
        if not 1 <= linea <= len(self.lineas):
            return 1
        inicio = sum(len(l) + 1 for l in self.lineas[:linea - 1])
        posicion = self.lineas[linea - 1].find(texto) if texto else -1
        return columna(self.codigo, inicio + max(posicion, 0))

    # --- Sentencias -------------------------------------------------------------

    def sentencias(self, nodos: list[Nodo]) -> None:
        """Revisa una lista de sentencias en orden."""
        for nodo in nodos:
            self.sentencia(nodo)

    def sentencia(self, n: Nodo) -> None:
        """Declara lo que `n` declara y revisa lo que usa."""
        t = n.tipo
        if t == "ImportDecl":
            self.declarar(n.dato.strip('"').split("/")[-1], "paquete", "Paquete", n.linea)
        elif t == "VarDecl":
            self._var(n)
        elif t == "ConstDecl":
            self.declarar(n.dato, self.expresion(n.hijos[0]), "Constante", n.linea)
        elif t == "ShortVarDecl":
            # El valor se revisa antes de declarar: en `x := x` la x de la derecha es la de afuera.
            tipo = self.expresion(n.hijos[1])
            self.declarar(n.hijos[0].dato, tipo, "Variable", n.linea)
        elif t == "AssignStmt":
            self._asignacion(n)
        elif t == "IncDecStmt":
            self.expresion(n.hijos[0])
        elif t in ("FuncDecl", "MethodDecl"):
            self._funcion(n)
        elif t == "ReturnStmt":
            self._retorno(n)
        elif t == "IfStmt":
            self._if(n)
        elif t == "ForStmt":
            self._for(n)
        elif t == "SwitchStmt":
            self._switch(n)
        elif t == "Block":
            self._bloque(n, "bloque")
        elif t == "CallExpr":
            self.expresion(n)
        # PackageClause, StructDecl y BranchStmt no declaran ni usan nada que revisen las reglas.

    def _bloque(self, bloque: Nodo, nombre: str) -> None:
        """Revisa `bloque` en un ámbito propio."""
        self.abrir(nombre)
        self.sentencias(bloque.hijos)
        self.cerrar()

    def _var(self, n: Nodo) -> None:
        """`var x T`, `var x T = v` o `var x = v`."""
        tiene_tipo = n.hijos[0].tipo in ("Type", "MapType")
        declarado = nombre_tipo(n.hijos[0]) if tiene_tipo else None
        valor = n.hijos[-1] if not tiene_tipo or len(n.hijos) == 2 else None
        recibido = self.expresion(valor) if valor else None
        if declarado and recibido:
            self._asignar(n, n.dato, declarado, recibido)
        self.declarar(n.dato, declarado or recibido, "Variable", n.linea)

    def _asignacion(self, n: Nodo) -> None:
        """`x = v`; la asignación compuesta (`+=`) solo revisa que x exista."""
        destino, valor = n.hijos
        simbolo = self.identificador(destino.dato, destino, usar=False)
        recibido = self.expresion(valor)
        if n.dato == "=" and simbolo:
            self._asignar(n, destino.dato, simbolo.tipo, recibido)

    def _asignar(self, n: Nodo, nombre: str, esperado: str, recibido: str) -> None:
        """Aplica Conversión y, si no reportó, Asignación de tipo.

        Conversión va primero para que int→float64 dé un solo mensaje, el suyo.
        """
        if ERROR in (esperado, recibido):
            return
        if conversion_Danilogb18(self, n, esperado, recibido):
            return
        asignacion_AndreewCore(self, n, nombre, esperado, recibido)

    def _funcion(self, n: Nodo) -> None:
        """Declara la función (no los métodos) y revisa su cuerpo con sus parámetros."""
        # Según la regla, los parámetros llegan sueltos o dentro de un nodo "Params".
        params = [p for h in n.hijos for p in (h.hijos if h.tipo == "Params" else [h]) if p.tipo == "Param"]
        resultados = next(([nombre_tipo(t) for t in h.hijos] for h in n.hijos if h.tipo == "Results"), [])
        if n.tipo == "FuncDecl":
            firma = f"func({', '.join(nombre_tipo(p.hijos[0]) for p in params)})"
            if resultados:
                firma += " " + tupla(resultados)
            self.declarar(n.dato, firma, "Función", n.linea)
            self.firmas[n.dato] = resultados

        anterior, self.funcion = self.funcion, (n.dato, resultados)
        self.abrir(n.dato)
        for h in n.hijos:
            if h.tipo == "Receiver":
                self.declarar(h.dato, h.hijos[0].dato, "Parámetro", h.linea)
        for p in params:
            self.declarar(p.dato, nombre_tipo(p.hijos[0]), "Parámetro", p.linea)
        # El cuerpo comparte el ámbito con los parámetros, como en Go.
        self.sentencias(n.hijos[-1].hijos)
        self.cerrar()
        self.funcion = anterior

    def _retorno(self, n: Nodo) -> None:
        """Calcula los tipos devueltos y aplica Retorno de funciones."""
        recibidos = [self.expresion(h) for h in n.hijos]
        if self.funcion is None or ERROR in recibidos:
            return
        nombre, esperados = self.funcion
        retorno_AndreewCore(self, n, nombre, esperados, recibidos)

    def _condicion(self, cond: Nodo, estructura: str) -> None:
        """Calcula el tipo de la condición y aplica Estructuras de control."""
        tipo = self.expresion(cond)
        if tipo != ERROR:
            condicion_Danilogb18(self, cond, tipo, estructura)

    def _if(self, n: Nodo) -> None:
        """`if c {} [else {} | else if ...]`."""
        cond, entonces, *sino = n.hijos
        self._condicion(cond, "if")
        self._bloque(entonces, "if")
        for rama in sino:
            if rama.tipo == "Block":
                self._bloque(rama, "else")
            else:
                self.sentencia(rama)

    def _for(self, n: Nodo) -> None:
        """Las cuatro formas de for; lo que declara el for vive en su ámbito."""
        self.abrir("for")
        if n.dato == "condicional":
            self._condicion(n.hijos[0], "for")
        elif n.dato == "clásico":
            inicio, cond, post, _ = n.hijos
            self.sentencia(inicio)
            self._condicion(cond, "for")
            self.sentencia(post)
        elif n.dato == "range":
            clave, valor, coleccion, _ = n.hijos
            tipo = self.expresion(coleccion)
            for ident, tipo_var in ((clave, tipo_clave(tipo)), (valor, tipo_elemento(tipo))):
                if ident.dato != "_":
                    self.declarar(ident.dato, tipo_var, "Variable", ident.linea)
        self.sentencias(n.hijos[-1].hijos)
        self.cerrar()

    def _switch(self, n: Nodo) -> None:
        """`switch v { case ...: ... default: ... }`; cada caso es un ámbito."""
        self.expresion(n.hijos[0])
        for caso in n.hijos[1:]:
            self.abrir(caso.dato)
            cuerpo = caso.hijos
            if caso.dato == "case":
                self.expresion(cuerpo[0])
                cuerpo = cuerpo[1:]
            self.sentencias(cuerpo)
            self.cerrar()

    # --- Expresiones ------------------------------------------------------------

    def identificador(self, nombre: str, nodo: Nodo, usar: bool = True) -> Simbolo | None:
        """Busca `nombre`; si no está declarado aplica Identificadores.

        `usar` cuenta la lectura en `usos` (asignarle a x no es leerla).
        """
        simbolo = self.buscar(nombre)
        if simbolo is None:
            identificador_SamuelEcheverria(self, nodo, nombre)
        elif usar:
            simbolo.usos += 1
        return simbolo

    def expresion(self, n: Nodo) -> str:
        """Devuelve el tipo de la expresión `n` (Tabla 9) revisando lo que usa."""
        t = n.tipo
        if t == "BasicLit":
            return tipo_literal(n.dato)
        if t == "Ident":
            simbolo = self.identificador(n.dato, n)
            return simbolo.tipo if simbolo else ERROR
        if t == "ParenExpr":
            return self.expresion(n.hijos[0])
        if t == "UnaryExpr":
            tipo = self.expresion(n.hijos[0])
            # `&x` (fmt.Scan) es un puntero: fuera de la Tabla 9.
            return {"!": "bool", "-": tipo}.get(n.dato, ERROR)
        if t == "BinaryExpr":
            izq, der = (self.expresion(h) for h in n.hijos)
            if n.dato in COMPARACIONES or n.dato in LOGICOS:
                return "bool"
            if ERROR in (izq, der) or conversion_Danilogb18(self, n, izq, der):
                return ERROR
            return operacion_SamuelEcheverria(self, n, izq, der)
        if t == "CallExpr":
            return self._llamada(n)
        if t == "SelectorExpr":
            self.identificador(n.dato.split(".")[0], n)
            return ERROR
        if t == "IndexExpr":
            coleccion = self.identificador(n.dato, n)
            self.expresion(n.hijos[0])
            return tipo_elemento(coleccion.tipo) if coleccion else ERROR
        if t == "MapLit":
            for par in n.hijos[2:]:
                self.expresion(par.hijos[0])
                self.expresion(par.hijos[1])
            return f"map[{nombre_tipo(n.hijos[0])}]{nombre_tipo(n.hijos[1])}"
        if t == "ArrayLit":
            for valor in n.hijos[1:]:
                self.expresion(valor)
            return n.dato
        if t == "CompositeLit":
            # En un struct, la clave de `nombre: "Ana"` es un campo, no una variable.
            for h in n.hijos:
                self.expresion(h.hijos[1] if h.tipo == "KeyValue" else h)
            return n.dato
        return ERROR

    def _llamada(self, n: Nodo) -> str:
        """Tipo de `f(...)`: su retorno, una tupla si son varios, o "sin valor"."""
        for argumento in n.hijos:
            self.expresion(argumento)
        if "." in n.dato:  # fmt.Println(...) o ana.Mostrar()
            self.identificador(n.dato.split(".")[0], n)
            return ERROR
        if self.identificador(n.dato, n) is None or n.dato not in self.firmas:
            return ERROR
        return tupla(self.firmas[n.dato])


def nombre_tipo(nodo: Nodo) -> str:
    """Texto del tipo de un nodo Type o MapType: "int", "[]float64", "map[string]int"."""
    if nodo.tipo == "MapType":
        return f"map[{nombre_tipo(nodo.hijos[0])}]{nombre_tipo(nodo.hijos[1])}"
    return nodo.dato


def tupla(tipos: list[str]) -> str:
    """Tipo de lo que devuelve una función: T, "(T1, T2)" o "sin valor"."""
    if not tipos:
        return SIN_VALOR
    return tipos[0] if len(tipos) == 1 else f"({', '.join(tipos)})"


def tipo_literal(lexema: str) -> str:
    """Tipo de un literal según su lexema."""
    if lexema.startswith('"'):
        return "string"
    if lexema in ("true", "false"):
        return "bool"
    return "float64" if "." in lexema else "int"


def _partes_map(tipo: str) -> tuple[str, str]:
    """Separa "map[K]V" en (K, V) respetando corchetes anidados."""
    nivel = 0
    for i, c in enumerate(tipo[3:], start=3):
        nivel += {"[": 1, "]": -1}.get(c, 0)
        if nivel == 0:
            return tipo[4:i], tipo[i + 1:]
    return ERROR, ERROR


def tipo_elemento(tipo: str) -> str:
    """Tipo de `c[i]` o del valor en `range c`: T en []T y [N]T, V en map[K]V."""
    if tipo.startswith("map["):
        return _partes_map(tipo)[1]
    if tipo.startswith("["):
        return tipo[tipo.index("]") + 1:]
    return ERROR


def tipo_clave(tipo: str) -> str:
    """Tipo de la clave en `range c`: int en arreglos y slices, K en map[K]V."""
    if tipo.startswith("map["):
        return _partes_map(tipo)[0]
    return "int" if tipo.startswith("[") else ERROR


def analizar_semantico(ast: Nodo, codigo: str) -> tuple[list[Simbolo], list[ErrorAnalisis]]:
    """Revisa el significado del programa y devuelve la tabla de símbolos y los errores."""
    analizador = Analizador(codigo)
    analizador.sentencias(ast.hijos)
    return analizador.simbolos, analizador.errores


# ===== INICIO aporte: Paúl Rodríguez (AndreewCore) =====
# Reglas semánticas (Tabla 11): Retorno de funciones, Asignación de tipo.

def retorno_AndreewCore(az: Analizador, nodo: Nodo, funcion: str,
                        esperados: list[str], recibidos: list[str]) -> None:
    """[Retorno de funciones] `return` de `funcion` con valores de tipo `recibidos`.

    `esperados` son los tipos de la firma ([] si no tiene retorno). Una llamada
    con varios retornos llega como un solo tipo "(T1, T2)".
    """
    # TODO(AndreewCore): comparar con la firma y reportar, p. ej.:
    #   az.reportar("Retorno de funciones", nodo,
    #               f"Tipo de retorno inválido en la función '{funcion}'; se esperaba "
    #               f"'float64' pero se retornó 'int'.", "...", texto="return")


def asignacion_AndreewCore(az: Analizador, nodo: Nodo, nombre: str, esperado: str, recibido: str) -> None:
    """[Asignación de tipo] `nombre = valor` o `var nombre T = valor`.

    `esperado` es el tipo de la variable y `recibido` el del valor. Conversión
    (int→float64) ya se revisó antes.
    """
    # TODO(AndreewCore): si no coinciden, reportar, p. ej.:
    #   az.reportar("Asignación de tipo", nodo,
    #               f"No se puede asignar un valor de tipo '{recibido}' a la variable "
    #               f"'{nombre}' de tipo '{esperado}'.", "...", texto=nombre)

# ===== FIN aporte: Paúl Rodríguez (AndreewCore) =====


# ===== INICIO aporte: Danilo García (Danilogb18) =====
# Reglas semánticas (Tabla 11): Conversión, Estructuras de control.

def conversion_Danilogb18(az: Analizador, nodo: Nodo, esperado: str, recibido: str) -> bool:
    """[Conversión] int y float64 mezclados sin conversión explícita.

    Se llama en asignaciones (`esperado` es el tipo de la variable) y en
    operaciones aritméticas (`esperado` y `recibido` son los dos operandos;
    `nodo.tipo == "BinaryExpr"`). Devuelve True si reportó, para que no se
    reporte además Asignación u Operaciones.
    """
    # TODO(Danilogb18): reportar, p. ej.:
    #   az.reportar("Conversión", nodo,
    #               "No existe conversión implícita del tipo 'int' al tipo 'float64'.", "...")
    #   return True
    return False


def condicion_Danilogb18(az: Analizador, nodo: Nodo, tipo: str, estructura: str) -> None:
    """[Estructuras de control] Condición de un if o for (`estructura`) con tipo `tipo`."""
    # TODO(Danilogb18): si no es bool, reportar, p. ej.:
    #   az.reportar("Estructuras de control", nodo,
    #               f"La condición de la estructura '{estructura}' debe ser de tipo 'bool', "
    #               f"pero se recibió '{tipo}'.", "...")

# ===== FIN aporte: Danilo García (Danilogb18) =====


# ===== INICIO aporte: Samuel Echeverría (SamuelEcheverria) =====
# Reglas semánticas (Tabla 11): Identificadores, Operaciones permitidas.

def identificador_SamuelEcheverria(az: Analizador, nodo: Nodo, nombre: str) -> None:
    """[Identificadores] `nombre` se usa en `nodo` sin estar declarado en el ámbito actual ni en uno superior."""
    # TODO(SamuelEcheverria): reportar y agregar una fila "Sin declarar" a la tabla, p. ej.:
    #   az.reportar("Identificadores", nodo,
    #               f"El identificador '{nombre}' no ha sido declarado en este ámbito.", "...", texto=nombre)
    #   az.simbolos.append(Simbolo(nombre, ERROR, "Sin declarar", az.ambito.ruta, nodo.linea, error=True))


def operacion_SamuelEcheverria(az: Analizador, nodo: Nodo, izq: str, der: str) -> str:
    """[Operaciones permitidas] Devuelve el tipo de `izq <nodo.dato> der` (+ - * / %).

    Conversión (int con float64) ya se revisó antes.
    """
    # TODO(SamuelEcheverria): - * / % solo entre numéricos del mismo tipo; + también
    #   entre dos string. Si no se permite, reportar y devolver ERROR, p. ej.:
    #   az.reportar("Operaciones permitidas", nodo,
    #               f"Operación '{nodo.dato}' inválida entre operandos de tipo '{izq}' y '{der}'.", "...")
    return izq if izq == der else ERROR

# ===== FIN aporte: Samuel Echeverría (SamuelEcheverria) =====
