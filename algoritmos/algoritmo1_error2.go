// Algoritmo de prueba 5 (con errores léxicos) — Paúl Rodríguez (AndreewCore)
//
// Conversor de temperaturas de una semana. Tiene errores léxicos a propósito,
// sobre todo de delimitadores y comentarios. Para generar el log léxico:
//   cd backend && python probar_lexico.py ../algoritmos/algoritmo5.go -u AndreewCore
//
// Errores esperados:
//   línea 26: 'í' en el identificador límite
//   línea 27: número mal formado 12.5grados
//   línea 33: '?' de operador ternario
//   línea 37: cadena con acento grave `C` (dos errores)
//   línea 44: comentario /* sin cerrar (se come hasta el final del archivo)

package main

import "fmt"

/* Convierte grados Celsius a Fahrenheit. */
func aFahrenheit(c float64) float64 {
	return c*9/5 + 32
}

func main() {
	temperaturas := [7]float64{18.5, 21.0, 25.3, 30.1, 27.8, 19.4, 22.6}
	var suma float64 = 0.0
	límite := 28.0
	ajuste := 12.5grados

	for i := 0; i < len(temperaturas); i++ {
		suma += temperaturas[i]
	}
	promedio := suma / 7.0
	mensaje := promedio > 25.0 ? "semana calurosa" : "semana templada"

	switch {
	case promedio > 25.0:
		fmt.Println("Promedio alto en", `C`)
	default:
		fmt.Println("Promedio normal")
	}

	fmt.Printf("Promedio: %.2f F\n", aFahrenheit(promedio)); // ';' explícito
	fmt.Println(mensaje, ajuste)
	/* Pendiente: avisar cuando una temperatura supere el límite
	fmt.Println("Días sobre el límite:", límite)
}