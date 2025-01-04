package api

import (
	"github.com/gorilla/mux"
)

func SetupRouter() *mux.Router {
	r := mux.NewRouter()

	r.HandleFunc("/api/auth", AuthHandler).Methods("POST")
	r.HandleFunc("/api/users", GetUsersHandler).Methods("GET")

	return r
}
