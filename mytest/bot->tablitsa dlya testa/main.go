package main

import (
	"bufio"
	"database/sql"
	"fmt"
	"log"
	"os"
	"strings"

	_ "github.com/lib/pq" // драйвер PostgreSQL
)

type Test struct {
	Question      string
	VariantOtveta string // Для хранения вариантов как строки
	PravilnOtveta string
}

// Функция для создания таблицы с заданным именем
func createTable(db *sql.DB, tableName string) error {
	createTableSQL := fmt.Sprintf(`
    CREATE TABLE IF NOT EXISTS %s (
        number SERIAL PRIMARY KEY,
        question TEXT NOT NULL,
        variant_otveta TEXT NOT NULL,
        praviln_otvet TEXT NOT NULL
    );`, tableName)

	_, err := db.Exec(createTableSQL)
	if err != nil {
		return fmt.Errorf("ошибка при создании таблицы %s: %v", tableName, err)
	}

	fmt.Printf("Таблица %s успешно создана\n", tableName)
	return nil
}

// Функция для вставки нового теста в таблицу
func insertTest(db *sql.DB, tableName string, test Test) error {
	insertSQL := fmt.Sprintf(`
    INSERT INTO %s (question, variant_otveta, praviln_otvet)
    VALUES ($1, $2, $3) RETURNING number;`, tableName)

	var id int
	err := db.QueryRow(insertSQL, test.Question, test.VariantOtveta, test.PravilnOtveta).Scan(&id)
	if err != nil {
		return fmt.Errorf("ошибка при вставке теста в таблицу %s: %v", tableName, err)
	}
	fmt.Printf("Тест добавлен в таблицу %s с ID: %d\n", tableName, id)
	return nil
}

// Функция для чтения ввода от пользователя
func readInput(prompt string) string {
	fmt.Print(prompt)
	scanner := bufio.NewScanner(os.Stdin)
	scanner.Scan()
	return scanner.Text()
}

func main() {
	// Строка подключения к базе данных
	connStr := "user=postgres password=1 dbname=tests sslmode=disable"
	db, err := sql.Open("postgres", connStr)
	if err != nil {
		log.Fatal("Ошибка подключения к базе данных:", err)
	}
	defer db.Close()

	// Ввод имени таблицы пользователем
	tableName := readInput("Введите имя для таблицы: ")

	// Создаем таблицу с заданным именем
	if err := createTable(db, tableName); err != nil {
		log.Fatal(err)
	}

	// Бесконечный цикл для ввода тестов
	for {
		question := readInput("Введите вопрос (или введите 'exit' для выхода): ")
		if question == "exit" {
			break
		}

		variantOtveta := readInput("Введите варианты ответа, разделенные запятой: ")
		// Заменяем запятые на специальный набор символов
		variantOtvetaWithDelimiter := strings.ReplaceAll(variantOtveta, ",", " *$*#* ")

		pravilnOtveta := readInput("Введите правильный ответ: ")

		test := Test{
			Question:      question,
			VariantOtveta: variantOtvetaWithDelimiter, // Сохраняем вариант с разделителем
			PravilnOtveta: pravilnOtveta,
		}

		if err := insertTest(db, tableName, test); err != nil {
			log.Fatal(err)
		}
	}
}
