//с помощью этого кода можно выводить информацию из таблицы


package main

import (
	"database/sql"
	"fmt"
	"log"

	_ "github.com/lib/pq" // импортируем драйвер PostgreSQL
)

func main() {
	// Строка подключения к базе данных
	connStr := "user=postgres password=1 dbname=tests sslmode=disable"

	// Подключение к базе данных
	db, err := sql.Open("postgres", connStr)
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Проверка соединения
	err = db.Ping()
	if err != nil {
		log.Fatal(err)
	}

	fmt.Println("Успешно подключено к базе данных!")

	// Запрос ID от пользователя
	fmt.Print("Введите номер строки: ")
	var number int
	_, err = fmt.Scanf("%d", &number)
	if err != nil {
		log.Fatalf("Ошибка ввода: %v", err)
	}

	// Запрос к базе данных для получения данных по ID
	var question string
	var variant_otveta string
	var praviln_otvet string

	row := db.QueryRow("SELECT question, variant_otveta, praviln_otvet FROM test1 WHERE number = $1", number)
	err = row.Scan(&question, &variant_otveta, &praviln_otvet)

	if err == sql.ErrNoRows {
		fmt.Printf("Номер строки %d не найден.\n", number)
	} else if err != nil {
		log.Fatal(err)
	} else {
		// Вывод данных о пользователе
		fmt.Printf("номер: %d, вопрос: %s, вариант ответа: %s, правильный ответ: %s\n", number, question, variant_otveta, praviln_otvet)
	}
}
