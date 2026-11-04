"""Los ejemplos de la interfaz como casos de prueba del analizador del grupo.

Se leen de frontend/src/datos/ejemplos.js (con Node) para que la vista
Ejemplos y estas pruebas no se desincronicen. Cada ejemplo declara la fase y
la línea del error que enseña; la prueba exige que las fases anteriores
terminen en "ok" y que esa fase reporte un error en esa línea.

Mientras una fase necesaria siga sin implementar, su caso se marca como
omitido (skipped): la lista de omitidos es el avance pendiente del grupo.
"""

import json
import shutil
import subprocess
import unittest
from pathlib import Path

import servicio

EJEMPLOS_JS = Path(__file__).resolve().parents[2] / "frontend" / "src" / "datos" / "ejemplos.js"

_LECTOR = """
const m = await import(process.argv[1]);
console.log(JSON.stringify({inicial: m.STARTER, ejemplos: m.EXAMPLES}));
"""


def _cargar():
    """Importa ejemplos.js con Node y devuelve (programa inicial, ejemplos)."""
    salida = subprocess.run(
        ["node", "--input-type=module", "-e", _LECTOR, EJEMPLOS_JS.as_uri()],
        capture_output=True, text=True, check=True, timeout=30,
    ).stdout
    datos = json.loads(salida)
    return datos["inicial"], datos["ejemplos"]


@unittest.skipUnless(shutil.which("node"), "se necesita Node para leer ejemplos.js")
class PruebasEjemplos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inicial, cls.ejemplos = _cargar()

    def analizar(self, codigo, hasta):
        """Analiza `codigo` y omite el caso si alguna fase hasta `hasta` no está lista."""
        r = servicio.analizar(codigo, "main.go", escribir_logs=False)
        for fase in servicio.FASES[: servicio.FASES.index(hasta) + 1]:
            estado = r["fases"][fase]["estado"]
            if estado == "no_impl":
                self.skipTest(f"fase {fase} sin implementar")
            if estado == "fallo":
                self.fail(r["fases"][fase]["errores"][0]["mensaje"])
        return r

    def test_se_leyeron_los_ejemplos(self):
        self.assertGreater(len(self.ejemplos), 0)
        for ej in self.ejemplos:
            self.assertIn(ej["fase"], servicio.FASES, ej["id"])

    def test_programa_inicial_sin_errores(self):
        r = self.analizar(self.inicial, "sem")
        for fase, datos in r["fases"].items():
            self.assertEqual(datos["estado"], "ok", f"{fase}: {datos['errores']}")

    def test_cada_ejemplo_falla_donde_dice(self):
        for ej in self.ejemplos:
            with self.subTest(ejemplo=ej["id"]):
                r = self.analizar(ej["code"], ej["fase"])
                anteriores = servicio.FASES[: servicio.FASES.index(ej["fase"])]
                for fase in anteriores:
                    self.assertEqual(r["fases"][fase]["estado"], "ok",
                                     f"{fase}: {r['fases'][fase]['errores']}")
                fase = r["fases"][ej["fase"]]
                self.assertEqual(fase["estado"], "error")
                self.assertIn(ej["linea"], [e["linea"] for e in fase["errores"]], fase["errores"])
                for e in fase["errores"]:
                    self.assertTrue(e["mensaje"].strip(), "todo error necesita un mensaje")


if __name__ == "__main__":
    unittest.main()
