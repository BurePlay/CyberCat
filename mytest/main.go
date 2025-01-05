package main

import (
	"bufio"
	"database/sql"
	"fmt"
	"log"
	"os"
	"strings"

	_ "github.com/lib/pq" // Импортируем драйвер PostgreSQL
)

func main() {
	// Укажите свои параметры подключения к базе данных
	connStr := "user=postgres password=1 dbname=tests sslmode=disable"     //dbname-название бд 
	db, err := sql.Open("postgres", connStr)
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Проверка подключения
	err = db.Ping()
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println("Успешно подключено к базе данных!")

	// Ввод данных от пользователя
	reader := bufio.NewReader(os.Stdin)
	fmt.Print("Введите вопрос: ")
	question, _ := reader.ReadString('\n')
	question = strings.TrimSpace(question) // Удаляем лишние пробелы и символы новой строки

	fmt.Print("Введите варианты ответа: ")
	variant_otveta, _ := reader.ReadString('\n')
	variant_otveta = strings.TrimSpace(variant_otveta)

	fmt.Print("Введите правильный ответ: ")
	praviln_otvet, _ := reader.ReadString('\n')
	praviln_otvet = strings.TrimSpace(praviln_otvet)

	// Подготовка SQL запроса на вставку данных
	insertQuery := `INSERT INTO test1 (question, variant_otveta, praviln_otvet) VALUES ($1, $2, $3)`    //здесь сначала заполняется имя теста (test1), потом название столбцов

	// Выполнение запроса для вставки данных
	_, err = db.Exec(insertQuery, question, variant_otveta, praviln_otvet)
	if err != nil {
		log.Fatalf("Ошибка вставки данных: %v", err) // Выводим ошибку, если она произошла
	}

	// Успешное сообщение
	fmt.Println("Данные успешно вставлены!")
}
