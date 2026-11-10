// Algoritmo de prueba 1 — Paúl Rodríguez (AndreewCore)
//
// Programa Go con la mayoría de tokens del subconjunto de GoTutor, usado
// como entrada para validar el analizador. Para generar el log léxico:
//   cd backend && python probar_lexico.py ../algoritmos/algoritmo1.go -u AndreewCore

package main

import "fmt"

func valorInventario(precios map[string]float64, stock map[string]int) float64 {

	var total float64 = 0.0
	for nombre, precio := range precios {
		total += precio * float64(stock[nombre])
	}
	return total

}

func main() {

	precios := map[string]float64{"lapiz": 0.5, "cuaderno": 2.75}

	stock := map[string]int{"lapiz": 40, "cuaderno": 3}

	minimos := [2]int{10, 5}

	nombres := []string{"lapiz", "cuaderno"}

	const LIMITE = 100
	var reponer string
	var llegada int

	fmt.Println("Unidades de lápiz que llegaron:")
	fmt.Scan(&llegada)
	stock["lapiz"] += llegada /* comentario de prueba */

	for i := 0; i < len(nombres); i++ {
		if stock[nombres[i]] < minimos[i] {
			reponer = reponer + nombres[i] + " "
		}
	}

	total := valorInventario(precios, stock); // ';' explícito de prueba
	if total > LIMITE {
		fmt.Printf("Inventario alto: %.2f\n", total)
	} else {
		fmt.Println("Inventario: %.2f\n", total)
	}

	switch len(reponer) {
	case 0:
		fmt.Println("Nada que reponer")
	default:
		fmt.Println("Reponer:", reponer)
	}
}