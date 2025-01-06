from pymongo import MongoClient

# Подключение к MongoDB Atlas (замени строку подключения на свою)
uri = "mongodb+srv://BurePlay:123@users.tgbfe.mongodb.net/"
client = MongoClient(uri)

# Выбор базы данных и коллекции
db = client['Users']
collection = db['users']

# Функция для входа пользователя
def login():
    print("Введите данные для входа:")
    email = input("Почта: ").replace(" ", "")  # Удаляем пробелы из почты
    password = input("Пароль: ")

    # Ищем пользователя с указанной почтой
    user = collection.find_one({"email": email})

    if user:
        # Проверяем пароль
        if user['password'] == password:
            print("Вход успешен!")
        else:
            print("Неправильный пароль.")
    else:
        print("Пользователь с такой почтой еще не зарегистрирован.")

# Запуск функции для входа
login()
