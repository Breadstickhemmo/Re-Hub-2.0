from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'qwertyuiop'

# Функция для подключения к базе данных
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    with conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')
    conn.close()

# Инициализируем базу данных при первом запуске
if not os.path.exists('users.db'):
    init_db()

# Главная страница
@app.route('/')
def index():
    return render_template('index.html')

# Регистрация
@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    # Хэшируем пароль
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256:600000')

    # Подключаемся к базе данных и добавляем пользователя
    conn = get_db_connection()
    try:
        with conn:
            conn.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                (username, email, hashed_password)
            )
        flash('Регистрация прошла успешно! Теперь вы можете войти.', 'success')
        return redirect(url_for('index'))
    except sqlite3.IntegrityError:
        flash('Имя пользователя или email уже существуют.', 'error')
        return redirect(url_for('index'))
    finally:
        conn.close()

# Вход
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # Подключаемся к базе данных и проверяем данные
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE username = ?',
        (username,)
    ).fetchone()
    conn.close()

    if user and check_password_hash(user['password'], password):
        # Успешный вход — сохраняем данные в сессии
        session['user_id'] = user['id']
        session['username'] = user['username']
        flash('Вы успешно вошли!', 'success')
        return redirect(url_for('index'))
    else:
        # Неправильные данные
        flash('Неверное имя пользователя или пароль.', 'error')
        return redirect(url_for('index'))

# Выход
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    flash('Вы вышли из системы.')
    return redirect(url_for('index'))

@app.route('/profile')
def profile():
    if 'username' in session:
        return render_template('profile.html')
    else:
        flash("Пожалуйста, войдите, чтобы получить доступ к профилю.", "error")
        return redirect(url_for('index'))

@app.route('/change_password', methods=['POST'])
def change_password():
    if 'username' in session:
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash("Новый пароль и подтверждение не совпадают.", "error")
            return redirect(url_for('profile'))

        # Подключение к базе данных и проверка текущего пароля
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (session['username'],)).fetchone()
        
        if not check_password_hash(user['password'], current_password):
            flash("Неверный текущий пароль.", "error")
            conn.close()
            return redirect(url_for('profile'))
        
        # Обновление пароля в базе данных
        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256:600000')
        conn.execute('UPDATE users SET password = ? WHERE username = ?', (hashed_password, session['username']))
        conn.commit()
        conn.close()

        flash("Пароль успешно изменен.", "success")
        return redirect(url_for('profile'))
    else:
        flash("Пожалуйста, войдите для выполнения этого действия.", "error")
        return redirect(url_for('index'))
    
@app.route('/tarot', methods=['POST'])
def tarot():
    if 'username' in session:
        return render_template('tarot.html')
    else:
        flash("Пожалуйста, войдите, чтобы получить доступ к раскладу.", "error")
        return redirect(url_for('index'))

@app.route('/cosmos', methods=['POST'])
def cosmos():
    if 'username' in session:
        return render_template('cosmos.html')
    else:
        flash("Пожалуйста, войдите, чтобы получить доступ к рассчёту.", "error")
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)