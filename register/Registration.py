from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError  # Импортируем ошибку DuplicateKeyError

uri = "mongodb+srv://BurePlay:123@users.tgbfe.mongodb.net/"
client = MongoClient(uri)

# Выбор базы данных и коллекции
db = client['Users']
collection = db['users']

# Убедимся, что индекс на поле email уникален
collection.create_index("email", unique=True)

# Функция для добавления пользователя
def add_user():
    print("Введите данные пользователя:")
    nickname = input("Никнейм: ")
    email = input("Почта: ").replace(" ", "")  # Удаляем все пробелы из почты
    password = input("Пароль: ")

    # Формируем документ для вставки
    user_data = {
        "nickname": nickname,
        "email": email,
        "password": password
    }

    try:
        # Вставляем данные в коллекцию
        result = collection.insert_one(user_data)
        print(f"Пользователь добавлен с ID: {result.inserted_id}")
    except DuplicateKeyError:
        print("Пользователь с такой почтой уже зарегистрирован.")

# Запуск функции для добавления пользователя
add_user()
