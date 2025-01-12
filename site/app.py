import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mail import Mail, Message
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from itsdangerous import URLSafeTimedSerializer
import hashlib
from requests_oauthlib import OAuth2Session
from flask_dance.contrib.github import make_github_blueprint, github

app = Flask(__name__)

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Конфигурация OAuth для Яндекс
YANDEX_CLIENT_ID = "901bd33153ea435aab6d42127308774f"
YANDEX_CLIENT_SECRET = "6d43c53523914b4597dae838f0dd9d67"
YANDEX_REDIRECT_URI = "https://4f94-93-171-155-27.ngrok-free.app/yandex/authorized"




#Конфигурация OAuth для Github
CLIENT_ID = 'Ov23liJkzqD5GIAouD68' 
CLIENT_SECRET = '907a2c2067944aedfbc45485aa97cec44a80d249'
GITHUB_REDIRECT_URI = 'https://4f94-93-171-155-27.ngrok-free.app/github/callback'

# GitHub OAuth endpoints
AUTHORIZATION_BASE_URL = 'https://github.com/login/oauth/authorize'
TOKEN_URL = 'https://github.com/login/oauth/access_token'
API_BASE_URL = 'https://api.github.com/'



# Создаем сессию OAuth для Яндекса
oauth = OAuth2Session(YANDEX_CLIENT_ID, redirect_uri=YANDEX_REDIRECT_URI)

# Создаем сессию OAuth для Github
oauth_github = OAuth2Session(
    CLIENT_ID,
    redirect_uri=GITHUB_REDIRECT_URI,
    scope="read:user,user:email"
)

# Получаем URL для авторизации
authorization_url, state = oauth.authorization_url('https://oauth.yandex.ru/authorize')
print(f"Перейдите по следующему URL для авторизации: {authorization_url}")


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
    return render_template('home.html')

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

            return render_template('register.html', message = "На вашу почту отправлено письмо для подтверждения.")
        except DuplicateKeyError:
            return render_template('register.html', error = "Пользователь с таким email уже существует.") 
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
                return render_template('Login.html', message = "Подтвердите вашу почту перед входом.")
            if user['password'] == hashed_password:
                return redirect(url_for('quiz'))
            else:
                return render_template('Login.html', error = "Неправильный пароль. Попробуйте снова.")
        else:
            return render_template('Login.html', error = "Пользователь с такой почтой не зарегистрирован.")
    return render_template('Login.html')

# Маршрут для страницы с тестом
@app.route('/quiz')
def quiz():
    return render_template('quiz.html')

# OAuth для Яндекса
@app.route('/yandex/login')
def yandex_login():
    # Проверяем, авторизован ли пользователь через Яндекс
    if not oauth.authorized:
        return redirect(authorization_url)  # Перенаправляем на страницу авторизации

    # Получаем информацию о пользователе
    oauth.fetch_token('https://oauth.yandex.ru/token', client_secret=YANDEX_CLIENT_SECRET, authorization_response=request.url)
    response = oauth.get('https://login.yandex.ru/info')
    if response.ok:
        user_info = response.json()
        email = user_info.get("default_email")
        nickname = user_info.get("real_name") or email.split('@')[0]

        # Сразу подтверждаем email
        user = collection.find_one({"email": email})
        if not user:
            collection.insert_one({
                "nickname": nickname,
                "email": email,
                "confirmed": True
            })
        # Перенаправление на страницу quiz
        return redirect(url_for('quiz'))
    return "Ошибка авторизации через Яндекс"

# Обработка перенаправления от Яндекса после авторизации
@app.route('/yandex/authorized')
def yandex_authorized():
    # Получение токена доступа
    token = oauth.fetch_token(
        'https://oauth.yandex.ru/token',
        client_secret=YANDEX_CLIENT_SECRET,
        authorization_response=request.url
    )

    # Получение информации о пользователе
    response = oauth.get('https://login.yandex.ru/info')
    if response.ok:
        user_info = response.json()
        email = user_info.get("default_email")
        nickname = user_info.get("real_name") or email.split('@')[0]

        # Проверка, существует ли пользователь
        user = collection.find_one({"email": email})
        if not user:
            # Добавление пользователя в базу
            collection.insert_one({
                "nickname": nickname,
                "email": email,
                "confirmed": True
            })

        # Перенаправление на страницу quiz
        return redirect(url_for('quiz'))

    # Если произошла ошибка
    return "Ошибка авторизации через Яндекс"

# OAuth для GitHub
@app.route('/github/login')
def github_login():
    #Initiates the OAuth login process by redirecting to GitHub
    authorization_url, state = oauth_github.authorization_url(AUTHORIZATION_BASE_URL)
    session['oauth_state'] = state
    return redirect(authorization_url)



@app.route('/github/callback')
def github_callback():
    #GitHub will redirect here after the user logs in
    oauth_github.fetch_token(TOKEN_URL, client_secret=CLIENT_SECRET, authorization_response=request.url)
    resp = oauth_github.get(API_BASE_URL + 'user')  # Fetch user info from GitHub

    
    if resp.ok:
        user_info = resp.json()
        email = user_info.get("email") # Primary email, if public
        nickname = user_info.get("login")
        print(user_info)

        # If no email is available in the basic info, fetch emails explicitly
        if not email:
            email_resp = oauth_github.get(API_BASE_URL + 'user/emails')
            if email_resp.ok:
                emails = email_resp.json()  # List of email objects
                primary_email = next(
                    (e['email'] for e in emails if e.get('primary') and e.get('verified')),
                    None
                )
                email = primary_email


        if not email:
            return "Не удалось получить email пользователя с GitHub."

        print(f"User info: {user_info}")
        print(f"Email: {email}")


        user = collection.find_one({"email": email})
        if not user:
            collection.insert_one({
                "nickname": nickname,
                "email": email,
                "confirmed": True
            })

        return redirect(url_for('quiz'))

    return "Ошибка авторизации через GitHub."

    #return f'Hello, {user_info["login"]}!<br>Your GitHub email: {user_info.get("email", "No email found")}.'


# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)
