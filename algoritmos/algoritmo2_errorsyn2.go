// Algoritmo de prueba 2, versión con errores sintácticos 2 — Danilo García (Danilogb18)
//
// Mismo programa que algoritmo2.go, con errores de sintaxis a propósito en
// las reglas de Danilo: múltiple retorno, expresiones booleanas y slice. Para generar el log sintáctico:
//   cd backend && python probar_sintactico.py ../algoritmos/algoritmo2_errorsyn2.go -u Danilogb18
//
// Errores esperados:
//   línea 21: tipos de retorno múltiples sin paréntesis (float64, float64, bool)
//   línea 39: operador '>=' sin operando derecho (promedio >= && !perfecta)
//   línea 51: slice sin tipo de elemento ([]{8.5, ...})
//   Los demás errores del log son en cascada: tras un error, PLY descarta
//   tokens hasta poder seguir, y una '}' o un 'else' quedan sin pareja.

package main

import "fmt"

const MINIMO = 7.0

// estadisticas devuelve la suma, el promedio y si hubo nota perfecta
func estadisticas(notas []float64) float64, float64, bool {
	var suma float64 = 0.0
	cantidad := 0.0
	perfecta := false
	for _, nota := range notas {
		suma += nota
		cantidad += 1.0
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
	if promedio >= && !perfecta || promedio == 10.0 {
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
	notas := []{8.5, 9.0, 10.0, 6.75}
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
