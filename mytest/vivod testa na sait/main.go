package main

import (
	"database/sql"
	"encoding/json"
	"log"
	"net/http"

	_ "github.com/lib/pq"
)

type Question struct {
	Question string `json:"question"`
	Variants string `json:"variants"`
}

func main() {
	connStr := "user=postgres password=1 dbname=tests sslmode=disable"
	db, err := sql.Open("postgres", connStr)
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	err = db.Ping()
	if err != nil {
		log.Fatal(err)
	}
	log.Println("Успешно подключено к базе данных!")

	http.HandleFunc("/questions", func(w http.ResponseWriter, r *http.Request) {
		rows, err := db.Query("SELECT question, variant_otveta FROM test2")
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		defer rows.Close()

		var questions []Question
		for rows.Next() {
			var q Question
			var variants string
			err := rows.Scan(&q.Question, &variants)
			if err != nil {
				http.Error(w, err.Error(), http.StatusInternalServerError)
				return
			}
			q.Variants = variants
			questions = append(questions, q)
		}

		if err = rows.Err(); err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(questions)
	})

	// Обслуживание статических файлов
	http.Handle("/", http.FileServer(http.Dir("."))) // Убедитесь, что вы находите се в том же каталоге, что и q.html

	log.Println("Сервер запускает на http://localhost:8084")
	log.Fatal(http.ListenAndServe(":8084", nil))
}
