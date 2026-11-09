// Algoritmo de prueba 2, versión con errores 2 — Danilo García (Danilogb18)
//
// Mismo programa que algoritmo2.go, con errores léxicos a propósito de
// caracteres, comillas y comentarios. Para generar el log léxico:
//   cd backend && python probar_lexico.py ../algoritmos/algoritmo2_error2.go -u Danilogb18
//
// Errores esperados:
//   línea 25: comillas simples en 'f' (dos errores; GoTutor solo usa comillas dobles)
//   línea 39: '#' usado como comentario
//   línea 39: 'í' dentro de ese falso comentario (mínima)
//   línea 44: cadena con acento grave `Ingrese su edad:` (dos errores)
//   línea 53: '$' en el operador $= (en lugar de *=)
//   línea 57: '?' de operador ternario dentro del if
//   línea 80: comentario /* sin cerrar (se come hasta el final del archivo)
//
// Calcula estadísticas de un slice de notas y clasifica al estudiante.

package main

import "fmt"

// estadisticas devuelve la suma, el promedio y si hubo nota perfecta
func estadisticas(notas []float64) (float64, float64, bool) {
	var suma float64 = 0.0
	perfecta := 'f'
	for _, nota := range notas {
		suma += nota
		if nota == 10.0 {
			perfecta = true
		}
	}
	promedio := suma / float64(len(notas))
	return suma, promedio, perfecta
}

func main() {
	var nombre string = "Danilo"
	var edad int
	const MINIMO = 7.0 # nota mínima
	notas := []float64{8.5, 9.0, 10.0, 6.75}
	faltas := [3]int{1, 0, 2}
	creditos := map[string]int{"LP": 4, "Redes": 3}

	fmt.Println(`Ingrese su edad:`)
	fmt.Scan(&edad)

	suma, promedio, perfecta := estadisticas(notas)
	total := 0
	for i := 0; i < 3; i++ {
		total += faltas[i]
	}
	total -= 1
	total $= 2
	total /= 2
	total--

	if promedio >= MINIMO && !perfecta || total <= 2 ? {
		fmt.Printf("%s aprueba con %f\n", nombre, promedio)
	} else if promedio < MINIMO {
		fmt.Println("Reprueba")
	} else {
		fmt.Println("Caso especial")
	}

	switch creditos["LP"] % 2 {
	case 0:
		fmt.Println("Créditos pares", suma)
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
	/* fin del programa
}