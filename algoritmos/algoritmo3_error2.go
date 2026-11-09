
package main

import "fmt"

func main() {
	var cajero string = "Samuel"
	var turno int
	const IMPUESTO = 0.15

	fmt.Println("Ingrese el número de turno:")
	fmt.Scan(&turno)

	if turno >= 1 | turno <= 3 {
		fmt.Printf("Turno válido\n")
	} else {
		fmt.Println("Turno inválido")
	}
}