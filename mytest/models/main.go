package main

import (
	"encoding/json"
	"fmt"
)

type Test struct {
	ID          int64      `json:"id"`
	Title       string     `json:"title"`
	Description string     `json:"description"`
	Questions   []Question `json:"questions"`
}

type Question struct {
	ID      int64    `json:"id"`
	Text    string   `json:"text"`
	Answers []Answer `json:"answers"`
	Correct int      `json:"correct"` // Индекс правильного ответа в массиве Answers
}

type Answer struct {
	ID   int64  `json:"id"`
	Text string `json:"text"`
}

func ExampleTest() Test {
	return Test{
		ID:          1,
		Title:       "Пример теста: Общие знания",
		Description: "Этот тест проверяет общие знания.",
		Questions: []Question{
			{
				ID:   1,
				Text: "Какой язык программирования используется для разработки Android-приложений?",
				Answers: []Answer{
					{ID: 1, Text: "Java"},
					{ID: 2, Text: "C#"},
					{ID: 3, Text: "Python"},
				},
				Correct: 0, // Верный ответ - "Java" (индекс 0)
			},
			{
				ID:   2,
				Text: "Какой элемент таблицы Менделеева обозначается символом 'H'?",
				Answers: []Answer{
					{ID: 1, Text: "Гелий"},
					{ID: 2, Text: "Водород"},
					{ID: 3, Text: "Кислород"},
				},
				Correct: 1, // Верный ответ - "Водород" (индекс 1)
			},
			{
				ID:   3,
				Text: "Кто написал 'Войну и мир'?",
				Answers: []Answer{
					{ID: 1, Text: "Чехов"},
					{ID: 2, Text: "Толстой"},
					{ID: 3, Text: "Достоевский"},
				},
				Correct: 1, // Верный ответ - "Толстой" (индекс 1)
			},
		},
	}
}

func main() {
	test := ExampleTest()
	testJSON, _ := json.MarshalIndent(test, "", "  ")
	fmt.Println(string(testJSON))
}
