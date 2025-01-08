from flask import Flask, render_template, request, redirect, url_for
from flask_mail import Mail, Message
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from itsdangerous import URLSafeTimedSerializer
import hashlib

app = Flask(__name__)

# Подключение к MongoDB
uri = "mongodb+srv://BurePlay:123@users.tgbfe.mongodb.net/"
client = MongoClient(uri)
db = client['Users']
collection = db['users']

# Настройки для отправки email
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'igor.romanyuk.2007@gmail.com'  # Ваш email
app.config['MAIL_PASSWORD'] = 'bxzv hzku lyyi mjqn'   # Ваш пароль
mail = Mail(app)

# Секретный ключ для токенов
app.config['SECRET_KEY'] = 'your_secret_key'
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# Создаем уникальный индекс для email (выполняется один раз)
try:
    collection.create_index([('email', 1)], unique=True)
except Exception as e:
    print("Индекс уже существует:", e)

# Главная страница
@app.route('/')
def home():
    return redirect(url_for('register'))  # Перенаправление на регистрацию

# Маршрут для регистрации
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nickname = request.form['nickname']
        email = request.form['email'].replace(" ", "").lower()
        password = request.form['password']

        # Хэшируем пароль
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Проверяем, существует ли уже пользователь с таким email
        try:
            # Временно сохраняем пользователя без подтверждения
            user_data = {
                "nickname": nickname,
                "email": email,
                "password": hashed_password,
                "confirmed": False
            }
            collection.insert_one(user_data)

            # Отправляем письмо для подтверждения
            token = serializer.dumps(email, salt='email-confirmation')
            confirm_url = url_for('confirm_email', token=token, _external=True)

            msg = Message('Подтверждение регистрации', sender=app.config['MAIL_USERNAME'], recipients=[email])
            msg.body = f'Здравствуйте, {nickname}!\n\nПерейдите по ссылке, чтобы подтвердить ваш email: {confirm_url}'
            mail.send(msg)

            return "На вашу почту отправлено письмо для подтверждения."
        except DuplicateKeyError:
            return "Пользователь с таким email уже существует."
    return render_template('register.html')

# Подтверждение email
@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = serializer.loads(token, salt='email-confirmation', max_age=3600)  # Токен действует 1 час
    except Exception:
        return "Ссылка для подтверждения недействительна или истекла."

    # Обновляем статус пользователя
    user = collection.find_one({"email": email})
    if user and not user.get("confirmed", False):
        collection.update_one({"email": email}, {"$set": {"confirmed": True}})
        return "Ваш email успешно подтвержден!"
    elif user and user.get("confirmed", False):
        return "Ваш email уже подтвержден."
    else:
        return "Пользователь не найден."

# Маршрут для входа
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].replace(" ", "").lower()
        password = request.form['password']

        # Хэшируем введенный пароль
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Проверяем пользователя
        user = collection.find_one({"email": email})
        if user:
            if not user.get("confirmed", False):
                return "Подтвердите вашу почту перед входом."
            if user['password'] == hashed_password:
                return redirect(url_for('quiz'))
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
