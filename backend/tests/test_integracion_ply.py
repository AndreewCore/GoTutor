"""Integración del esqueleto con PLY real, sin mocks del analizador.

Copia `analizador/` a una carpeta temporal, le agrega una gramática mínima
(`package main` + `func main() {}`) y la pasa por servicio.analizar. Así se
comprueba que construir_lexer, el conteo de líneas, columna(), _tiene_reglas y
la detección de errores funcionan con PLY y no solo con dobles de prueba.

Solo corre mientras lexico.py y sintactico.py sigan siendo plantillas: en
cuanto el grupo escriba sus reglas, las de aquí chocarían con las suyas, y las
pruebas de test_ejemplos.py pasan a cubrir la integración real.
"""

import importlib
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import bitacora
import servicio
from analizador import lexico, sintactico

ANALIZADOR = Path(__file__).resolve().parent.parent / "analizador"
PAQUETE = "analizador_mini"

LEXICO_MINI = '''

reservadas = {"package": "PACKAGE", "func": "FUNC"}
tokens = ["ID", "LPAREN", "RPAREN", "LBRACE", "RBRACE"] + list(reservadas.values())
t_LPAREN = r"\\("
t_RPAREN = r"\\)"
t_LBRACE = r"\\{"
t_RBRACE = r"\\}"
t_ignore = " \\t"


def t_ID(t):
    r"[A-Za-z_]\\w*"
    t.type = reservadas.get(t.value, "ID")
    return t


def t_newline(t):
    r"\\n+"
    t.lexer.lineno += len(t.value)


def t_error(t):
    t.lexer.errores.append(ErrorAnalisis(
        "lex", t.lineno, columna(t.lexer.lexdata, t.lexpos), f"Carácter no reconocido: '{t.value[0]}'."))
    t.lexer.skip(1)
'''

SINTACTICO_MINI = '''

def p_programa(p):
    "programa : PACKAGE ID funcion"
    p[0] = Nodo("Program", "", 1, [Nodo("PackageClause", p[2], p.lineno(1)), p[3]])


def p_funcion(p):
    "funcion : FUNC ID LPAREN RPAREN LBRACE RBRACE"
    p[0] = Nodo("FuncDecl", p[2], p.lineno(1))


def p_error(p):
    if p is None:
        _errores.append(ErrorAnalisis("syn", 1, 1, "Fin de archivo inesperado."))
        return
    _errores.append(ErrorAnalisis(
        "syn", p.lineno, columna(p.lexer.lexdata, p.lexpos), f"Token inesperado: '{p.value}'."))
'''

VALIDO = "package main\n\nfunc main() {\n}\n"


def _es_plantilla() -> bool:
    """Indica si el grupo aún no escribió reglas en lexico.py ni sintactico.py."""
    return not lexico.tokens and not sintactico._tiene_reglas()


@unittest.skipUnless(_es_plantilla(), "lexico.py/sintactico.py ya tienen reglas; ver test_ejemplos.py")
class PruebasIntegracionPly(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Arma el paquete temporal con la gramática mínima y lo importa."""
        cls.carpeta = Path(tempfile.mkdtemp())
        destino = cls.carpeta / PAQUETE
        shutil.copytree(ANALIZADOR, destino, ignore=shutil.ignore_patterns("__pycache__", "parsetab.py"))
        with open(destino / "lexico.py", "a", encoding="utf-8") as f:
            f.write(LEXICO_MINI)
        with open(destino / "sintactico.py", "a", encoding="utf-8") as f:
            f.write(SINTACTICO_MINI)
        sys.path.insert(0, str(cls.carpeta))
        cls.lexico = importlib.import_module(f"{PAQUETE}.lexico")
        cls.sintactico = importlib.import_module(f"{PAQUETE}.sintactico")

    @classmethod
    def tearDownClass(cls):
        """Quita el paquete temporal para no contaminar otras pruebas."""
        sys.path.remove(str(cls.carpeta))
        for nombre in [m for m in sys.modules if m == PAQUETE or m.startswith(PAQUETE + ".")]:
            del sys.modules[nombre]
        shutil.rmtree(cls.carpeta)

    def analizar(self, codigo, escribir_logs=False):
        """Corre el servicio real con el léxico y sintáctico mínimos."""
        with mock.patch.object(servicio, "analizar_lexico", self.lexico.analizar_lexico), \
             mock.patch.object(servicio, "analizar_sintactico", self.sintactico.analizar_sintactico):
            return servicio.analizar(codigo, "main.go", escribir_logs=escribir_logs)

    def estados(self, r):
        """Estados de las tres fases, en orden."""
        return [r["fases"][f]["estado"] for f in servicio.FASES]

    def test_programa_valido(self):
        r = self.analizar(VALIDO)
        self.assertEqual(self.estados(r), ["ok", "ok", "no_impl"])
        self.assertEqual([t["tipo"] for t in r["tokens"]],
                         ["PACKAGE", "ID", "FUNC", "ID", "LPAREN", "RPAREN", "LBRACE", "RBRACE"])
        self.assertEqual(r["tokens"][-1], {"tipo": "RBRACE", "valor": "}", "linea": 4, "columna": 1})
        self.assertEqual(r["ast"]["hijos"][1], {"tipo": "FuncDecl", "dato": "main", "linea": 3,
                                                "hijos": [], "error": None})

    def test_error_lexico_con_posicion(self):
        r = self.analizar("package main\n  @\n")
        self.assertEqual(self.estados(r), ["error", "pendiente", "pendiente"])
        err = r["fases"]["lex"]["errores"][0]
        self.assertEqual((err["linea"], err["columna"]), (2, 3))

    def test_error_sintactico_con_posicion(self):
        r = self.analizar("package main\n\nfunc main( {\n}\n")
        self.assertEqual(self.estados(r), ["ok", "error", "pendiente"])
        err = r["fases"]["syn"]["errores"][0]
        self.assertEqual((err["linea"], err["columna"]), (3, 12))

    def test_fin_de_archivo(self):
        r = self.analizar("package main\nfunc main(")
        self.assertEqual(r["fases"]["syn"]["errores"][0]["mensaje"], "Fin de archivo inesperado.")

    def test_los_errores_no_se_arrastran_entre_analisis(self):
        self.analizar("package main\nfunc main(")
        r = self.analizar(VALIDO)
        self.assertEqual(r["fases"]["syn"], {"estado": "ok", "errores": []})

    def test_no_genera_tablas_en_el_repo(self):
        self.analizar(VALIDO)
        destino = self.carpeta / PAQUETE
        self.assertFalse((destino / "parsetab.py").exists())
        self.assertFalse((destino / "parser.out").exists())

    def test_logs_de_las_fases_ejecutadas(self):
        with tempfile.TemporaryDirectory() as logs, \
             mock.patch.object(bitacora, "CARPETA", Path(logs)), \
             mock.patch.object(bitacora, "usuario_git", return_value="prueba"):
            r = self.analizar(VALIDO, escribir_logs=True)
            self.assertEqual(len(r["logs"]), 2)
            self.assertTrue(r["logs"][0].startswith("logs/lexico-prueba-"))
            texto = (Path(logs) / r["logs"][1].removeprefix("logs/")).read_text(encoding="utf-8")
        self.assertIn("FuncDecl main  (L3)", texto)
        self.assertIn("Sin errores.", texto)


if __name__ == "__main__":
    unittest.main()
