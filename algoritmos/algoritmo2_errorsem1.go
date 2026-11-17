// Algoritmo de prueba 2, versión con errores semánticos 1 — Danilo García (Danilogb18)
//
// Mismo programa que algoritmo2.go, con errores a propósito de la regla
// semántica Conversión: Go no convierte int y float64 de forma implícita.
// Todos usan variables (no literales), así que también son errores para el compilador real de Go. El archivo es sintácticamente válido, porque el
// semántico solo corre si el léxico y el sintáctico terminan sin errores.
// Para generar el log:
//   cd backend && python probar_semantico.py ../algoritmos/algoritmo2_errorsem1.go -u Danilogb18
//
// Errores esperados (regla Conversión):
//   línea 34: suma (float64) dividida para cantidad, que ahora es un contador int
//   línea 54: la variable int bono dentro de un slice []float64
//   línea 72: total (int) multiplicado por factor (float64)
//   línea 73: total (int) guardado en una variable float64

package main

import "fmt"

const MINIMO = 7.0

// estadisticas devuelve la suma, el promedio y si hubo nota perfecta
func estadisticas(notas []float64) (float64, float64, bool) {
	var suma float64 = 0.0
	cantidad := 0
	perfecta := false
	for _, nota := range notas {
		suma += nota
		cantidad++
		if nota == 10.0 {
			perfecta = true
		}
	}
	promedio := suma / cantidad
	return suma, promedio, perfecta
}

// reportar recibe los tres resultados de estadisticas y clasifica al estudiante
func reportar(suma float64, promedio float64, perfecta bool) {
	fmt.Println("Suma de notas:", suma)
	if promedio >= MINIMO && !perfecta || promedio == 10.0 {
		fmt.Printf("Aprueba con %f\n", promedio)
	} else if promedio < MINIMO {
		fmt.Println("Reprueba")
	} else {
		fmt.Println("Caso especial")
	}
}

func main() {
	var nombre string = "Danilo"
	var edad int
	bono := 1
	notas := []float64{8.5, 9.0, 10.0, bono}
	faltas := [3]int{1, 0, 2}
	creditos := map[string]int{"LP": 4, "Redes": 3}

	fmt.Println("Estudiante:", nombre)
	fmt.Println("Ingrese su edad:")
	fmt.Scan(&edad)

	reportar(estadisticas(notas))
	total := 0
	for i := 0; i < 3; i++ {
		total += faltas[i]
	}
	total -= 1
	total *= 2
	total /= 2
	total--
	factor := 1.5
	total = total * factor
	var promedioFaltas float64 = total
	fmt.Println(promedioFaltas)

	switch creditos["LP"] % 2 {
	case 0:
		fmt.Println("Créditos pares, faltas:", total)
	default:
		fmt.Println("Créditos impares", -edad, edad != 0, edad > 18)
	}

	for total > 0 {
		total = total - 1 + 2*0
		if total == 1 {
			continue
		}
		break
	}
	edad++
}
