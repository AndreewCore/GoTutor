
package main

import "fmt"

func main() {
	var cajero string = "Samuel"
	var turno int
	const IMPUESTO = 0.15

	fmt.Println("Ingrese el número de turno:")
	fmt.Scan(&turno)

	if turno == 1 {
		turno = ~turno 
		fmt.Printf("Turno invertido\n")
	} else {
		fmt.Println("Turno normal")
	}
}