from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

app = Flask(__name__)

app.config['SERVER_NAME'] = 'https://922b-93-171-156-92.ngrok-free.app'

# Подключение к MongoDB
uri = "mongodb+srv://BurePlay:123@users.tgbfe.mongodb.net/"
client = MongoClient(uri)
db = client['Users']
collection = db['users']

# Убедимся, что индекс на поле email уникален
collection.create_index("email", unique=True)

@app.route('/')
def register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_user():
    nickname = request.form.get('nickname')
    email = request.form.get('email')
    password = request.form.get('password')

    # Формируем документ для вставки
    user_data = {
        "nickname": nickname,
        "email": email,
        "password": password
    }

    try:
        # Вставляем данные в коллекцию
        collection.insert_one(user_data)
        return redirect(url_for('quiz'))
    except DuplicateKeyError:
        return "Пользователь с такой почтой уже зарегистрирован."

@app.route('/quiz')
def quiz():
    return render_template('quiz.html')  # Страница, куда перенаправляется пользователь после регистрации

if __name__ == '__main__':
    app.run(debug=True)
