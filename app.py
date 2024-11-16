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
                password TEXT NOT NULL,
                email TEXT UNIQUE,
                first_name TEXT,
                last_name TEXT,
                father_name TEXT,
                bday INTEGER,
                bmonth INTEGER,
                byear INTEGER,
                phone TEXT,
                company_info TEXT,
                jobpos TEXT,
                personal_traits TEXT,
                professional_traits TEXT
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS businesses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                business_name TEXT NOT NULL,
                job_positions TEXT,
                recruiter_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tarot (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
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
    user = None
    if 'username' in session:
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (session['username'],)).fetchone()
        conn.close()
    return render_template('index.html', user=user)

# Минимальная и максимальная длина пароля
MIN_PASSWORD_LENGTH = 4
MAX_PASSWORD_LENGTH = 128

# Регистрация
@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']

    if len(password) < MIN_PASSWORD_LENGTH or len(password) > MAX_PASSWORD_LENGTH:
        flash(f'Пароль должен содержать от {MIN_PASSWORD_LENGTH} до {MAX_PASSWORD_LENGTH} символов.', 'error')
        return redirect(url_for('index'))

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256:600000')

    conn = get_db_connection()
    try:
        with conn:
            conn.execute(
                'INSERT INTO users (username, password) VALUES (?, ?)',
                (username, hashed_password)
            )
        flash('Регистрация прошла успешно! Теперь вы можете войти.', 'success')
        return redirect(url_for('index'))
    except sqlite3.IntegrityError:
        flash('Имя пользователя уже существует.', 'error')
        return redirect(url_for('index'))
    finally:
        conn.close()

# Вход
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE username = ?',
        (username,)
    ).fetchone()
    conn.close()

    if user and check_password_hash(user['password'], password):
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['jobpos'] = user['jobpos']  # Сохраняем должность в сессии
        flash('Вы успешно вошли!', 'success')
        return redirect(url_for('index'))
    else:
        flash('Неверное имя пользователя или пароль.', 'error')
        return redirect(url_for('index'))

# Выход
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    flash('Вы вышли из системы.')
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' in session:
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (session['username'],)).fetchone()
        business = conn.execute('SELECT business_name, job_positions FROM businesses WHERE user_id = ?', (user['id'],)).fetchone()
        conn.close()
        
        # Сохраняем business_name и job_positions в сессии, если они существуют
        if business:
            session['business_name'] = business['business_name']
            session['job_positions'] = business['job_positions']  # Сохраняем должности в сессии
        else:
            session['business_name'] = None
            session['job_positions'] = None
            
        return render_template('profile.html', user=user, user_business=business)
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

@app.route('/confirm_email', methods=['POST'])
def confirm_email():
    if 'username' in session:
        email = request.form['email']
        flash('Письмо с подтверждением отправлено на ваш email.', 'success')
        return redirect(url_for('profile'))
    else:
        flash("Пожалуйста, войдите, чтобы подтвердить почту.", "error")
        return redirect(url_for('index'))

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'username' in session:
        last_name = request.form['last_name']
        first_name = request.form['first_name']
        father_name = request.form['father_name']
        birth_day = request.form['birth_day']
        birth_month = request.form['birth_month']
        birth_year = request.form['birth_year']
        phone = request.form['phone']
        email = request.form['email']

        conn = get_db_connection()
        conn.execute('UPDATE users SET last_name = ?, first_name = ?, father_name = ?, phone = ?, email = ?, bday = ?, bmonth = ?, byear = ? WHERE username = ?',
                     (last_name, first_name, father_name, phone, email, birth_day, birth_month, birth_year, session['username']))
        conn.commit()
        conn.close()

        flash("Данные успешно обновлены.", "success")
        return redirect(url_for('profile'))
    else:
        flash("Пожалуйста, войдите для выполнения этого действия.", "error")
        return redirect(url_for('index'))

@app.route('/update_traits', methods=['POST'])
def update_traits():
    if 'username' in session:
        personal_traits = request.form.get('personal_traits')
        professional_traits = request.form.get('professional_traits')

        conn = get_db_connection()
        conn.execute(
            'UPDATE users SET personal_traits = ?, professional_traits = ? WHERE username = ?',
            (personal_traits, professional_traits, session['username'])
        )
        conn.commit()
        conn.close()

        flash("Информация успешно обновлена.", "success")
        return redirect(url_for('profile'))
    else:
        flash("Пожалуйста, войдите для выполнения этого действия.", "error")
        return redirect(url_for('index'))

@app.route('/manage_business', methods=['POST'])
def manage_business():
    if 'user_id' in session:
        business_name = request.form['business_name']
        user_id = session['user_id']

        conn = get_db_connection()
        try:
            # Проверяем, существует ли уже бизнес для этого пользователя
            existing_business = conn.execute('SELECT * FROM businesses WHERE user_id = ?', (user_id,)).fetchone()
            if existing_business:
                # Обновляем существующий бизнес
                conn.execute('UPDATE businesses SET business_name = ? WHERE user_id = ?',
                             (business_name, user_id))
            else:
                # Вставляем новый бизнес
                conn.execute('INSERT INTO businesses (user_id, business_name) VALUES (?, ?)',
                             (user_id, business_name))  # Рекрутер - это текущий пользователь
            conn.commit()
            flash("Информация о бизнесе успешно обновлена.", "success")
        except Exception as e:
            flash(f'Произошла ошибка: {e}', 'error')
        finally:
            conn.close()
        
        return redirect(url_for('profile'))
    else:
        flash("Пожалуйста, войдите для выполнения этого действия.", "error")
        return redirect(url_for('index'))

@app.route('/add_position', methods=['POST'])
def add_position():
    if 'user_id' in session:
        position = request.form['position']
        user_id = session['user_id']

        conn = get_db_connection()
        try:
            # Получаем текущие должности для пользователя
            existing_positions = conn.execute('SELECT job_positions FROM businesses WHERE user_id = ?', (user_id,)).fetchone()
            if existing_positions:
                # Обновляем должности, добавляя новую
                new_positions = existing_positions['job_positions']
                if new_positions:
                    new_positions += ',' + position
                else:
                    new_positions = position
                
                conn.execute('UPDATE businesses SET job_positions = ? WHERE user_id = ?', (new_positions, user_id))
            else:
                # Если нет должностей, создаем новую запись
                conn.execute('INSERT INTO businesses (user_id, job_positions) VALUES (?, ?)', (user_id, position))

            conn.commit()  # Подтверждаем изменения
            flash("Должность успешно добавлена.", "success")
        except Exception as e:
            flash(f'Произошла ошибка: {e}', 'error')
        finally:
            conn.close()

        return redirect(url_for('profile'))
    else:
        flash("Пожалуйста, войдите для выполнения этого действия.", "error")
        return redirect(url_for('index'))

@app.route('/remove_position', methods=['POST'])
def remove_position():
    if 'user_id' in session:
        position = request.form['position']
        user_id = session['user_id']

        conn = get_db_connection()
        try:
            # Получаем текущие должности для пользователя
            existing_positions = conn.execute('SELECT job_positions FROM businesses WHERE user_id = ?', (user_id,)).fetchone()
            if existing_positions:
                # Удаляем должность
                new_positions = existing_positions['job_positions'].split(',')
                new_positions = [pos for pos in new_positions if pos != position]  # Удаляем выбранную должность
                new_positions = ','.join(new_positions)  # Преобразуем обратно в строку

                conn.execute('UPDATE businesses SET job_positions = ? WHERE user_id = ?', (new_positions, user_id))
                conn.commit()
                flash("Должность успешно удалена.", "success")
            else:
                flash("Должности не найдены.", "error")
        except Exception as e:
            flash(f'Произошла ошибка: {e}', 'error')
        finally:
            conn.close()

        return redirect(url_for('profile'))
    else:
        flash("Пожалуйста, войдите для выполнения этого действия.", "error")
        return redirect(url_for('index'))

@app.route('/add_recruiter', methods=['POST'])
def add_recruiter():
    if 'user_id' in session:
        recruiter_username = request.form['recruiter_username']
        user_id = session['user_id']

        conn = get_db_connection()
        try:
            # Получаем ID рекрутера по логину
            recruiter = conn.execute('SELECT id FROM users WHERE username = ?', (recruiter_username,)).fetchone()
            if recruiter:
                conn.execute('UPDATE businesses SET recruiter_id = ? WHERE user_id = ?', (recruiter['id'], user_id))
                conn.commit()
                flash("Рекрутер успешно добавлен.", "success")
            else:
                flash("Рекрутер не найден.", "error")
        except Exception as e:
            flash(f'Произошла ошибка: {e}', 'error')
        finally:
            conn.close()

        return redirect(url_for('profile'))
    else:
        flash("Пожалуйста, войдите для выполнения этого действия.", "error")
        return redirect(url_for('index'))

def get_card_by_id(card_id):
    conn = get_tarot_db_connection()
    card = conn.execute(
        'SELECT name, description FROM tarot_cards_new WHERE id = ?',
        (card_id,)
    ).fetchone()
    conn.close()  # Закрываем соединение после запроса
    return card  # Возвращаем найденную карту или None, если не найдена

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

        # Вычисление card_id на основе даты рождения
        card_id = calculate_date_value(bday, bmonth, byear)

        conn = get_db_connection()
        try:
            # Проверяем, существует ли уже запись для пользователя
            existing_entry = conn.execute(
                'SELECT * FROM tarot WHERE user_id = ?',
                (user_id,)
            ).fetchone()

            if existing_entry:
                # Обновляем существующую запись
                conn.execute(
                    'UPDATE tarot SET card_id = ? WHERE user_id = ?',
                    (card_id, user_id)
                )
                flash('Данные успешно обновлены!', 'success')
            else:
                # Вставляем новую запись
                conn.execute(
                    'INSERT INTO tarot (user_id, card_id) VALUES (?, ?)',
                    (user_id, card_id)
                )
                flash('Данные успешно сохранены!', 'success')

            conn.commit()  # Подтверждаем изменения

            # Перенаправление на страницу результатов расклада с передачей card_id
            return render_template('tarot_result.html', card_id=card_id, get_card_by_id=get_card_by_id)

        except Exception as e:
            flash(f'Произошла ошибка: {e}', 'error')
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