from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient

app = Flask(__name__)

# Подключение к MongoDB
uri = "mongodb+srv://BurePlay:123@users.tgbfe.mongodb.net/"
client = MongoClient(uri)
db = client['Users']
collection = db['users']

# Главная страница, которая перенаправляет на страницу регистрации
@app.route('/')
def home():
    return redirect(url_for('register'))  # Перенаправление на страницу регистрации

# Маршрут для регистрации
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nickname = request.form['nickname']
        email = request.form['email'].replace(" ", "")  # Убираем пробелы
        password = request.form['password']

        # Проверяем, существует ли уже пользователь с таким email
        existing_user = collection.find_one({"email": email})
        if existing_user:
            return "Пользователь с таким email уже существует."

        # Добавляем нового пользователя в базу данных
        user_data = {
            "nickname": nickname,
            "email": email,
            "password": password
        }
        collection.insert_one(user_data)

        return redirect(url_for('login'))  # Перенаправляем на страницу входа после успешной регистрации
    return render_template('register.html')

# Маршрут для входа
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].replace(" ", "")  # Убираем пробелы
        password = request.form['password']

        # Ищем пользователя в базе данных
        user = collection.find_one({"email": email})

        if user:
            if user['password'] == password:
                return redirect(url_for('quiz'))  # Перенаправляем на страницу теста
            else:
                return "Неправильный пароль. Попробуйте снова."
        else:
            return "Пользователь с такой почтой не зарегистрирован."
    return render_template('Login.html')

# Маршрут для страницы с тестом
@app.route('/quiz')
def quiz():
    return render_template('quiz.html')

if __name__ == '__main__':
    app.run(debug=True)
