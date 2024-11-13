from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'qwertyuiop'

def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_tarot_db_connection():
    conn = sqlite3.connect('tarot_cards_new.db')
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
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tarot (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                bday INTEGER,
                bmonth INTEGER,
                byear INTEGER,
                jobpos TEXT,
                card_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (id)
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
        user_id = session['user_id']

        conn = get_db_connection()
        existing_entry = conn.execute(
            'SELECT bday, bmonth, byear, jobpos FROM tarot WHERE user_id = ?',
            (user_id,)
        ).fetchone()
        conn.close()

        if existing_entry:
            return render_template('tarot.html', 
                                   bday=existing_entry['bday'], 
                                   bmonth=existing_entry['bmonth'], 
                                   byear=existing_entry['byear'], 
                                   jobpos=existing_entry['jobpos'])
        else:
            return render_template('tarot.html')
    else:
        flash("Пожалуйста, войдите, чтобы получить доступ к раскладу.", "error")
        return redirect(url_for('index'))

def calculate_date_value(day, month, year):
    digits_sum = sum(int(digit) for digit in f"{day}{month}{year}")
    
    while digits_sum > 22:
        digits_sum -= 22
    
    return digits_sum

@app.route('/tarot_result', methods=['POST'])
def tarot_result():
    if 'user_id' in session:
        user_id = session['user_id']
        bday = request.form['birth_day']
        bmonth = request.form['birth_month']
        byear = request.form['birth_year']
        jobpos = request.form['position']
        jobpos_filter = request.form.get('jobpos_filter')

        card_id = calculate_date_value(bday, bmonth, byear)

        conn = get_db_connection()
        try:
            with conn:
                tarot_conn = get_tarot_db_connection()
                card = tarot_conn.execute(
                    'SELECT name, description FROM tarot_cards_new WHERE id = ?',
                    (card_id,)
                ).fetchone()
                tarot_conn.close()

                if not card:
                    flash('Карта не найдена.', 'error')
                    return redirect(url_for('index'))

                existing_entry = conn.execute(
                    'SELECT * FROM tarot WHERE user_id = ?',
                    (user_id,)
                ).fetchone()

                if existing_entry:
                    conn.execute(
                        'UPDATE tarot SET bday = ?, bmonth = ?, byear = ?, jobpos = ?, card_id = ? WHERE user_id = ?',
                        (bday, bmonth, byear, jobpos, card_id, user_id)
                    )
                    flash('Данные успешно обновлены!', 'success')
                else:
                    conn.execute(
                        'INSERT INTO tarot (user_id, bday, bmonth, byear, jobpos, card_id) VALUES (?, ?, ?, ?, ?, ?)',
                        (user_id, bday, bmonth, byear, jobpos, card_id)
                    )
                    flash('Данные успешно сохранены!', 'success')

                page = request.args.get('page', 1, type=int)
                per_page = 10
                offset = (page - 1) * per_page

                query = 'SELECT u.username, t.jobpos FROM users u LEFT JOIN tarot t ON u.id = t.user_id'
                if jobpos_filter:
                    query += ' WHERE t.jobpos = ?'
                    users = conn.execute(query, (jobpos_filter,)).fetchall()
                else:
                    users = conn.execute(query).fetchall()

                total_users = len(users)
                users = users[offset:offset + per_page]

                total_pages = (total_users + per_page - 1) // per_page

                job_positions = conn.execute('SELECT DISTINCT jobpos FROM tarot').fetchall()

            return render_template('tarot_result.html',
                                   user_id=user_id,
                                   bday=bday,
                                   bmonth=bmonth,
                                   byear=byear,
                                   jobpos=jobpos,
                                   card_name=card['name'],
                                   card_description=card['description'],
                                   users=users,
                                   total_pages=total_pages,
                                   current_page=page,
                                   jobpos_filter=jobpos_filter,
                                   job_positions=job_positions)  # Передаем уникальные должности
        except Exception as e:
            flash(f'Произошла ошибка при сохранении данных: {e}', 'error')
            return redirect(url_for('index'))
        finally:
            conn.close()
    else:
        flash("Пожалуйста, войдите, чтобы сохранить данные.", "error")
        return redirect(url_for('index'))

@app.route('/check_user', methods=['POST'])
def check_user():
    if 'user_id' in session:
        selected_username = request.form['username']

        conn = get_db_connection()
        tarot_entries = conn.execute('SELECT * FROM tarot WHERE user_id IN (SELECT id FROM users WHERE username IN (?, ?))', 
                                      (session['username'], selected_username)).fetchall()
        conn.close()

        results = []

        if len(tarot_entries) >= 2:
            day1, month1, year1 = tarot_entries[0]['bday'], tarot_entries[0]['bmonth'], tarot_entries[0]['byear']
            day2, month2, year2 = tarot_entries[1]['bday'], tarot_entries[1]['bmonth'], tarot_entries[1]['byear']

            value1 = calculate_date_value(day1, month1, year1)
            value2 = calculate_date_value(day2, month2, year2)

            total_sum = value1 + value2

            while total_sum > 22:
                total_sum -= 22

            final_value1 = (total_sum + value1) % 22 or 22
            final_value2 = (total_sum + value2) % 22 or 22

            # Получаем названия и описания карт из базы данных
            tarot_conn = get_tarot_db_connection()
            card1 = tarot_conn.execute('SELECT name, description FROM tarot_cards_new WHERE id = ?', (final_value1,)).fetchone()
            card2 = tarot_conn.execute('SELECT name, description FROM tarot_cards_new WHERE id = ?', (final_value2,)).fetchone()
            total_card = tarot_conn.execute('SELECT name, description FROM tarot_cards_new WHERE id = ?', (total_sum,)).fetchone()
            tarot_conn.close()

            results = {
                'value1': value1,
                'value2': value2,
                'total_sum': total_sum,
                'card_name1': card1['name'] if card1 else 'Неизвестная карта',
                'card_description1': card1['description'] if card1 else 'Нет описания',
                'card_name2': card2['name'] if card2 else 'Неизвестная карта',
                'card_description2': card2['description'] if card2 else 'Нет описания',
                'total_card_name': total_card['name'] if total_card else 'Неизвестная карта',
                'total_card_description': total_card['description'] if total_card else 'Нет описания',
            }

        return render_template('taro_sov.html', results=results, selected_username=selected_username)

    else:
        flash("Пожалуйста, войдите для выполнения этого действия.", "error")
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