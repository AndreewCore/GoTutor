// Algoritmo de prueba 2, versión con errores semánticos 2 — Danilo García (Danilogb18)
//
// Mismo programa que algoritmo2.go, con errores a propósito de la regla
// semántica Estructuras de control: la condición de un if o de un for debe
// ser de tipo bool (Go no trata los números ni el texto como verdadero/falso).
// El archivo es sintácticamente válido, porque el semántico solo corre si el
// léxico y el sintáctico terminan sin errores. Para generar el log:
//   cd backend && python probar_semantico.py ../algoritmos/algoritmo2_errorsem2.go -u Danilogb18
//
// Errores esperados (regla Estructuras de control):
//   línea 30: if con condición float64 (if nota)
//   línea 57: if con condición string (if nombre)
//   línea 65: for clásico con condición int (i < 3 escrito como 3)
//   línea 80: for condicional con condición int (for total)

package main

import "fmt"

const MINIMO = 7.0

// estadisticas devuelve la suma, el promedio y si hubo nota perfecta
func estadisticas(notas []float64) (float64, float64, bool) {
	var suma float64 = 0.0
	cantidad := 0.0
	perfecta := false
	for _, nota := range notas {
		suma += nota
		cantidad += 1.0
		if nota {
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
	notas := []float64{8.5, 9.0, 10.0, 6.75}
	faltas := [3]int{1, 0, 2}
	creditos := map[string]int{"LP": 4, "Redes": 3}

	if nombre {
		fmt.Println("Estudiante:", nombre)
	}
	fmt.Println("Ingrese su edad:")
	fmt.Scan(&edad)

	reportar(estadisticas(notas))
	total := 0
	for i := 0; 3; i++ {
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

	for total {
		total = total - 1 + 2*0
		if total == 1 {
			continue
		}
		break
	}
	edad++
}