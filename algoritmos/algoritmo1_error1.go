// Algoritmo de prueba 4 (con errores léxicos) — Paúl Rodríguez (AndreewCore)
//
// Registro de asistencia de un curso. Tiene errores léxicos a propósito para
// comprobar que el analizador los reporta todos, con línea, columna y
// sugerencia, sin detenerse en el primero. Para generar el log léxico:
//   cd backend && python probar_lexico.py ../algoritmos/algoritmo4.go -u AndreewCore
//
// Errores esperados:
//   línea 25: 'ñ' en el identificador año        (letra fuera del patrón de ID)
//   línea 26: '$' en el nombre de una variable
//   línea 27: número mal formado 3clases
//   línea 32: '#' usado como comentario
//   línea 37: '@' en lugar de '*'
//   línea 42: comillas simples en 'P' (dos errores)
//   línea 48: 'ñ' otra vez, al usar año
//   línea 49: cadena sin cerrar

package main

import "fmt"

func main() {
	asistencias := map[string]int{"Ana": 18, "Luis": 12, "Marta": 20}
	estudiantes := []string{"Ana", "Luis", "Marta"}
	año := 2026
	var $minimo int = 15
	total := 3clases
	var promedio float64

	/* Cuenta cuántos estudiantes
	   alcanzan el mínimo de asistencias. */
	# recorrer la lista de estudiantes
	aprobados := 0
	for i := 0; i < len(estudiantes); i++ {
		nombre := estudiantes[i]
		if asistencias[nombre] >= minimo {
			aprobados = aprobados @ 1
		}
	}

	promedio = float64(aprobados) / float64(len(estudiantes))
	estado := 'P'
	if promedio > 0.5 && total != 0 {
		fmt.Println("Curso con buena asistencia")
	} else {
		fmt.Println("Curso con baja asistencia")
	}
	fmt.Println("Año:", año, "Estado:", estado)
	fmt.Println("Fin del registro)
}