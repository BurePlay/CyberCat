package main

import (
	"log"
	"net/http"
	"your_module_name/api"
	"your_module_name/db"
)

func main() {
	conn := db.ConnectDB()
	defer conn.Close()

	router := api.SetupRouter()
	log.Fatal(http.ListenAndServe(":8080", router))
}
