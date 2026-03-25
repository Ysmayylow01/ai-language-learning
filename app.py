"""
Flask Backend - Language Learning App
SQLite database bilen doly işleýär
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime, timedelta
import jwt
import sqlite3
import os

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
DATABASE = 'language_app.db'

# ====== DATABASE HELPERS ======

def get_db():
    """Database birikdirmesi"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def query_db(query, args=(), one=False):
    """SELECT sorgusy"""
    conn = get_db()
    cur = conn.execute(query, args)
    rv = cur.fetchall()
    conn.close()
    rows = [dict(r) for r in rv]
    return rows[0] if (one and rows) else (None if (one and not rows) else rows)

def execute_db(query, args=()):
    """INSERT/UPDATE/DELETE sorgusy"""
    conn = get_db()
    cur = conn.execute(query, args)
    conn.commit()
    last_id = cur.lastrowid
    conn.close()
    return last_id

# ====== DATABASE INIT ======

def init_db():
    """Tablolary döret"""
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            native_language TEXT DEFAULT 'Turkmen',
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS languages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT NOT NULL UNIQUE,
            flag TEXT,
            description TEXT
        );

        CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            language_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            level TEXT DEFAULT 'beginner',
            order_num INTEGER DEFAULT 1,
            content TEXT,
            FOREIGN KEY (language_id) REFERENCES languages(id)
        );

        CREATE TABLE IF NOT EXISTS exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lesson_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            type TEXT NOT NULL,
            difficulty INTEGER DEFAULT 1,
            points INTEGER DEFAULT 10,
            content TEXT,
            FOREIGN KEY (lesson_id) REFERENCES lessons(id)
        );

        CREATE TABLE IF NOT EXISTS enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            language_id INTEGER NOT NULL,
            level TEXT DEFAULT 'beginner',
            total_points INTEGER DEFAULT 0,
            streak_days INTEGER DEFAULT 0,
            last_activity TEXT DEFAULT (datetime('now')),
            enrolled_at TEXT DEFAULT (datetime('now')),
            UNIQUE(user_id, language_id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (language_id) REFERENCES languages(id)
        );

        CREATE TABLE IF NOT EXISTS exercise_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            exercise_id INTEGER NOT NULL,
            lesson_id INTEGER NOT NULL,
            is_correct INTEGER NOT NULL,
            points_earned INTEGER DEFAULT 0,
            answered_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (exercise_id) REFERENCES exercises(id)
        );

        CREATE TABLE IF NOT EXISTS vocabulary_words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            language_id INTEGER NOT NULL,
            word TEXT NOT NULL,
            translation TEXT NOT NULL,
            example TEXT,
            mastery_level INTEGER DEFAULT 0,
            times_practiced INTEGER DEFAULT 0,
            last_practiced TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (language_id) REFERENCES languages(id)
        );
    """)
    conn.commit()
    conn.close()

def seed_data():
    """Başlangyç maglumatlary goş (diňe bir gezek)"""
    existing = query_db("SELECT COUNT(*) as cnt FROM languages", one=True)
    if existing and existing['cnt'] > 0:
        return  # Eýýäm ýüklenipdir

    import json

    # DILLER
    languages_data = [
        ("Ispança", "es", "🇪🇸", "Dünýäde 500+ million adam gürleýän dil"),
        ("Fransuzça", "fr", "🇫🇷", "Romance diller maşgalasynyň agzasy"),
        ("Nemesçe", "de", "🇩🇪", "Europanyň merkezi dillerinden"),
        ("Italýança", "it", "🇮🇹", "Sungat we medeniýet dili"),
        ("Ýaponça", "ja", "🇯🇵", "Aziýanyň möhüm dillerinden"),
        ("Hytaýça", "zh", "🇨🇳", "Iň köp adam gürleýän dil"),
    ]
    conn = get_db()
    conn.executemany(
        "INSERT INTO languages (name, code, flag, description) VALUES (?, ?, ?, ?)",
        languages_data
    )

    # ISPANÇA SAPAKLAR
    es_lessons = [
        (1, "Salamlaşma we tanyşma", "Esasy salamlaşma sözleri we özüňi tanyşdyrmak", "beginner", 1,
         json.dumps({"sections": [
             {"type": "text", "content": "Ispança salamlaşmak üçin: Hola (Salam), Buenos días (Ertiriňiz haýyrly), Adiós (Hoş gal), Gracias (Sag bol), Por favor (Haýyş edýärin)."},
             {"type": "vocabulary", "words": [
                 {"word": "Hola", "translation": "Salam", "example": "¡Hola! ¿Cómo estás?"},
                 {"word": "Buenos días", "translation": "Ertiriňiz haýyrly", "example": "Buenos días, señora."},
                 {"word": "Adiós", "translation": "Hoş gal", "example": "Adiós, hasta mañana."},
                 {"word": "Gracias", "translation": "Sag bol", "example": "Muchas gracias."},
                 {"word": "Por favor", "translation": "Haýyş edýärin", "example": "Por favor, ayúdame."}
             ]}
         ]})),
        (1, "Sanlar (0-20)", "Esasy sanlary öwrenmek", "beginner", 2,
         json.dumps({"sections": [
             {"type": "text", "content": "Ispança sanlar: 0 (cero), 1 (uno), 2 (dos), 3 (tres), 4 (cuatro), 5 (cinco), 6 (seis), 7 (siete), 8 (ocho), 9 (nueve), 10 (diez)."},
             {"type": "vocabulary", "words": [
                 {"word": "uno", "translation": "bir", "example": "Tengo uno."},
                 {"word": "dos", "translation": "iki", "example": "Dos más dos son cuatro."},
                 {"word": "diez", "translation": "on", "example": "Son las diez."},
                 {"word": "veinte", "translation": "ýigrimi", "example": "Veinte años."}
             ]}
         ]})),
        (1, "Maşgala agzalary", "Ene, ata, dogan-garyndaş sözleri", "beginner", 3,
         json.dumps({"sections": [
             {"type": "text", "content": "Maşgala: padre (kakam), madre (ejem), hermano (dogam), hermana (uýam), abuelo (babam), hijo (ogul), hija (gyz)."},
             {"type": "vocabulary", "words": [
                 {"word": "padre", "translation": "kakam", "example": "Mi padre trabaja."},
                 {"word": "madre", "translation": "ejem", "example": "Mi madre cocina."},
                 {"word": "hermano", "translation": "dogam", "example": "Tengo un hermano."},
                 {"word": "familia", "translation": "maşgala", "example": "Mi familia es grande."}
             ]}
         ]})),
        (1, "Reňkler", "Esasy reňkleri öwrenmek", "intermediate", 4,
         json.dumps({"sections": [
             {"type": "text", "content": "Reňkler: rojo (gyzyl), azul (gök), verde (ýaşyl), amarillo (sary), negro (gara), blanco (ak)."},
             {"type": "vocabulary", "words": [
                 {"word": "rojo", "translation": "gyzyl", "example": "El coche es rojo."},
                 {"word": "azul", "translation": "gök", "example": "El cielo es azul."},
                 {"word": "verde", "translation": "ýaşyl", "example": "Las plantas son verdes."}
             ]}
         ]})),
        (1, "Iýmit we içmek", "Restoranda sargyt etmek", "intermediate", 5,
         json.dumps({"sections": [
             {"type": "text", "content": "Restoran sözleri: comida (iýmit), bebida (içgi), desayuno (ertirlik), almuerzo (nahar), cena (agşamlyk). Iýmitler: pan (çörek), carne (et), pescado (balyk), arroz (tüwi)."},
             {"type": "vocabulary", "words": [
                 {"word": "agua", "translation": "suw", "example": "Quiero agua, por favor."},
                 {"word": "pan", "translation": "çörek", "example": "El pan está caliente."},
                 {"word": "pollo", "translation": "towuk", "example": "Pollo con arroz."}
             ]}
         ]})),
    ]
    conn.executemany(
        "INSERT INTO lessons (language_id, title, description, level, order_num, content) VALUES (?, ?, ?, ?, ?, ?)",
        es_lessons
    )

    # Sapak ID-lerini al
    conn.commit()
    s1 = conn.execute("SELECT id FROM lessons WHERE language_id=1 AND order_num=1").fetchone()['id']
    s2 = conn.execute("SELECT id FROM lessons WHERE language_id=1 AND order_num=2").fetchone()['id']
    s3 = conn.execute("SELECT id FROM lessons WHERE language_id=1 AND order_num=3").fetchone()['id']

    # MAŞKLAR
    exercises_data = [
        # Sapak 1
        (s1, '"Hola" näme diýmek?', "multiple_choice", 1, 10,
         json.dumps({"question": '"Hola" näme diýmek?', "options": ["Salam", "Hoş gal", "Sag bol", "Ertiriňiz haýyrly"], "correct_answer": "Salam", "hint": "Iň umumy salamlaşma sözi"})),
        (s1, '"Gracias" terjime et', "translation", 1, 15,
         json.dumps({"question": '"Gracias" sözüni terjime et', "correct_answer": "Sag bol", "hint": "Minnetdarlyk bildirýär"})),
        (s1, "Salamlaşmany tamamla", "fill_blank", 2, 10,
         json.dumps({"question": "_____ días! (Ertiriňiz haýyrly)", "correct_answer": "Buenos", "hint": "'Gowy' diýmek"})),
        # Sapak 2
        (s2, '"Cinco" näçe?', "multiple_choice", 1, 10,
         json.dumps({"question": '"Cinco" näçe?', "options": ["3", "5", "7", "9"], "correct_answer": "5", "hint": "Ellerinde näçe barmak bar?"})),
        (s2, "10-y ýaz", "translation", 2, 15,
         json.dumps({"question": "10 sanyny ispança ýaz", "correct_answer": "diez", "hint": "D bilen başlaýar"})),
        # Sapak 3
        (s3, "Maşgala sözleri", "multiple_choice", 2, 10,
         json.dumps({"question": '"Madre" näme diýmek?', "options": ["Kakam", "Ejem", "Dogam", "Uýam"], "correct_answer": "Ejem", "hint": "Zenan maşgala agzasy"})),
    ]
    conn.executemany(
        "INSERT INTO exercises (lesson_id, title, type, difficulty, points, content) VALUES (?, ?, ?, ?, ?, ?)",
        exercises_data
    )

    # FRANSUZÇA SAPAK
    conn.execute(
        "INSERT INTO lessons (language_id, title, description, level, order_num, content) VALUES (?, ?, ?, ?, ?, ?)",
        (2, "Salamlaşma - Bonjour!", "Fransuzça esasy salamlaşma", "beginner", 1,
         json.dumps({"sections": [
             {"type": "text", "content": "Fransuzça: Bonjour (Salam), Bonsoir (Agşamyňyz haýyrly), Au revoir (Hoş gal), Merci (Sag bol), S'il vous plaît (Haýyş edýärin)."},
             {"type": "vocabulary", "words": [
                 {"word": "Bonjour", "translation": "Salam", "example": "Bonjour, madame!"},
                 {"word": "Merci", "translation": "Sag bol", "example": "Merci beaucoup!"},
                 {"word": "Au revoir", "translation": "Hoş gal", "example": "Au revoir, à demain!"}
             ]}
         ]}))
    )
    conn.commit()
    fr_lesson = conn.execute("SELECT id FROM lessons WHERE language_id=2 AND order_num=1").fetchone()['id']
    conn.execute(
        "INSERT INTO exercises (lesson_id, title, type, difficulty, points, content) VALUES (?, ?, ?, ?, ?, ?)",
        (fr_lesson, "Bonjour näme diýmek?", "multiple_choice", 1, 10,
         json.dumps({"question": '"Bonjour" näme diýmek?', "options": ["Salam", "Hoş gal", "Sag bol", "Haýyş edýärin"], "correct_answer": "Salam", "hint": "Gündiz salamlaşma sözi"}))
    )

    # NEMESÇE SAPAK
    conn.execute(
        "INSERT INTO lessons (language_id, title, description, level, order_num, content) VALUES (?, ?, ?, ?, ?, ?)",
        (3, "Guten Tag!", "Nemesçe salamlaşma we özüňi tanyşdyrmak", "beginner", 1,
         json.dumps({"sections": [
             {"type": "text", "content": "Nemesçe: Guten Tag (Salam), Guten Morgen (Ertiriňiz haýyrly), Auf Wiedersehen (Hoş gal), Danke (Sag bol), Bitte (Haýyş edýärin)."},
             {"type": "vocabulary", "words": [
                 {"word": "Hallo", "translation": "Salam", "example": "Hallo! Wie geht's?"},
                 {"word": "Danke", "translation": "Sag bol", "example": "Danke schön!"},
                 {"word": "Tschüss", "translation": "Hoş gal", "example": "Tschüss, bis später!"}
             ]}
         ]}))
    )
    conn.commit()
    conn.close()
    print("✅ Başlangyç maglumatlar ýüklendi")

# ====== AUTH HELPERS ======

def generate_token(user_id):
    payload = {'user_id': user_id, 'exp': datetime.utcnow() + timedelta(days=30)}
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['user_id']
    except:
        return None

def get_current_user():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    try:
        token = auth_header.split(' ')[1]
        user_id = verify_token(token)
        if user_id:
            return query_db("SELECT * FROM users WHERE id = ?", (user_id,), one=True)
    except:
        pass
    return None

# ====== ROUTES ======

@app.route('/')
def index():
    return render_template('index.html')

# --- AUTH ---

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    native_language = data.get('native_language', 'Turkmen')

    if not username or not email or not password:
        return jsonify({"error": "Ähli meýdanlary dolduryň"}), 400

    if query_db("SELECT id FROM users WHERE username = ?", (username,), one=True):
        return jsonify({"error": "Bu username eýýäm ulanylypdyr"}), 400

    if query_db("SELECT id FROM users WHERE email = ?", (email,), one=True):
        return jsonify({"error": "Bu email eýýäm ulanylypdyr"}), 400

    user_id = execute_db(
        "INSERT INTO users (username, email, password, native_language) VALUES (?, ?, ?, ?)",
        (username, email, password, native_language)
    )
    token = generate_token(user_id)
    user = query_db("SELECT id, username, email, native_language, created_at FROM users WHERE id = ?", (user_id,), one=True)
    return jsonify({"token": token, "user": user}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({"error": "Username we password gerek"}), 400

    user = query_db("SELECT * FROM users WHERE username = ? AND password = ?", (username, password), one=True)
    if not user:
        return jsonify({"error": "Username ýa-da password ýalňyş"}), 401

    token = generate_token(user['id'])
    user_data = {k: v for k, v in user.items() if k != 'password'}
    return jsonify({"token": token, "user": user_data})

@app.route('/api/auth/me', methods=['GET'])
def get_me():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    user_data = {k: v for k, v in user.items() if k != 'password'}
    return jsonify(user_data)

# --- LANGUAGES ---

@app.route('/api/languages', methods=['GET'])
def get_languages():
    return jsonify(query_db("SELECT * FROM languages ORDER BY id"))

@app.route('/api/languages/<int:language_id>', methods=['GET'])
def get_language(language_id):
    lang = query_db("SELECT * FROM languages WHERE id = ?", (language_id,), one=True)
    if not lang:
        return jsonify({"error": "Dil tapylmady"}), 404
    return jsonify(lang)

# --- ENROLLMENTS ---

@app.route('/api/enrollments', methods=['GET'])
def get_enrollments():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    rows = query_db("""
        SELECT e.*, l.name as language_name, l.code, l.flag, l.description
        FROM enrollments e
        JOIN languages l ON l.id = e.language_id
        WHERE e.user_id = ?
        ORDER BY e.enrolled_at DESC
    """, (user['id'],))

    for row in rows:
        row['language'] = {
            'id': row['language_id'],
            'name': row['language_name'],
            'code': row['code'],
            'flag': row['flag'],
            'description': row['description']
        }
    return jsonify(rows)

@app.route('/api/enrollments', methods=['POST'])
def create_enrollment():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    language_id = request.json.get('language_id')
    if not language_id:
        return jsonify({"error": "language_id gerek"}), 400

    lang = query_db("SELECT * FROM languages WHERE id = ?", (language_id,), one=True)
    if not lang:
        return jsonify({"error": "Dil tapylmady"}), 404

    existing = query_db("SELECT id FROM enrollments WHERE user_id = ? AND language_id = ?",
                        (user['id'], language_id), one=True)
    if existing:
        return jsonify({"error": "Bu dile eýýäm ýazylandyňyz"}), 400

    eid = execute_db(
        "INSERT INTO enrollments (user_id, language_id) VALUES (?, ?)",
        (user['id'], language_id)
    )
    enrollment = query_db("SELECT * FROM enrollments WHERE id = ?", (eid,), one=True)
    enrollment['language'] = lang
    return jsonify(enrollment), 201

@app.route('/api/enrollments/<int:enrollment_id>', methods=['DELETE'])
def delete_enrollment(enrollment_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    row = query_db("SELECT * FROM enrollments WHERE id = ? AND user_id = ?", (enrollment_id, user['id']), one=True)
    if not row:
        return jsonify({"error": "Enrollment tapylmady"}), 404

    execute_db("DELETE FROM enrollments WHERE id = ?", (enrollment_id,))
    return jsonify({"message": "Ýazgydan çykdyňyz"})

# --- LESSONS ---

@app.route('/api/lessons', methods=['GET'])
def get_lessons():
    user = get_current_user()
    language_id = request.args.get('language_id', type=int)
    level = request.args.get('level')

    if not language_id:
        return jsonify({"error": "language_id gerek"}), 400

    query = "SELECT * FROM lessons WHERE language_id = ?"
    args = [language_id]
    if level:
        query += " AND level = ?"
        args.append(level)
    query += " ORDER BY order_num"

    rows = query_db(query, args)
    for row in rows:
        # Maşk sany
        ex_count = query_db("SELECT COUNT(*) as cnt FROM exercises WHERE lesson_id = ?", (row['id'],), one=True)
        row['exercises_count'] = ex_count['cnt'] if ex_count else 0
        row.pop('content', None)

        # Tamamlandy barla (ulanyjy giren bolsa)
        row['is_completed'] = False
        if user:
            ex_list = query_db("SELECT id FROM exercises WHERE lesson_id = ?", (row['id'],))
            if ex_list:
                ex_ids = [e['id'] for e in ex_list]
                completed = query_db(
                    f"SELECT COUNT(DISTINCT exercise_id) as cnt FROM exercise_results "
                    f"WHERE user_id = ? AND is_correct = 1 AND exercise_id IN ({','.join('?'*len(ex_ids))})",
                    [user['id']] + ex_ids, one=True
                )
                row['is_completed'] = completed and completed['cnt'] == len(ex_ids)

    return jsonify(rows)

@app.route('/api/lessons/<int:lesson_id>', methods=['GET'])
def get_lesson(lesson_id):
    import json
    lesson = query_db("SELECT * FROM lessons WHERE id = ?", (lesson_id,), one=True)
    if not lesson:
        return jsonify({"error": "Sapak tapylmady"}), 404

    # Content JSON parse
    if lesson.get('content'):
        try:
            lesson['content'] = json.loads(lesson['content'])
        except:
            pass

    exs = query_db("SELECT * FROM exercises WHERE lesson_id = ?", (lesson_id,))
    for ex in exs:
        if ex.get('content'):
            try:
                ex['content'] = json.loads(ex['content'])
            except:
                pass
    lesson['exercises'] = exs
    return jsonify(lesson)

# --- EXERCISES ---

@app.route('/api/exercises/<int:exercise_id>', methods=['GET'])
def get_exercise(exercise_id):
    import json
    ex = query_db("SELECT * FROM exercises WHERE id = ?", (exercise_id,), one=True)
    if not ex:
        return jsonify({"error": "Maşk tapylmady"}), 404
    if ex.get('content'):
        try:
            ex['content'] = json.loads(ex['content'])
        except:
            pass
    return jsonify(ex)

@app.route('/api/exercises/<int:exercise_id>/submit', methods=['POST'])
def submit_exercise(exercise_id):
    import json
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    ex = query_db("SELECT * FROM exercises WHERE id = ?", (exercise_id,), one=True)
    if not ex:
        return jsonify({"error": "Maşk tapylmady"}), 404

    content = json.loads(ex['content']) if isinstance(ex['content'], str) else ex['content']
    user_answer = request.json.get('answer', '').strip()
    correct_answer = content.get('correct_answer', '')
    is_correct = user_answer.lower() == correct_answer.lower()
    points_earned = ex['points'] if is_correct else 0

    # Netijäni sakla
    execute_db(
        "INSERT INTO exercise_results (user_id, exercise_id, lesson_id, is_correct, points_earned) VALUES (?, ?, ?, ?, ?)",
        (user['id'], exercise_id, ex['lesson_id'], 1 if is_correct else 0, points_earned)
    )

    # Enrollment total_points güncelle
    lesson = query_db("SELECT language_id FROM lessons WHERE id = ?", (ex['lesson_id'],), one=True)
    if lesson and points_earned > 0:
        execute_db(
            "UPDATE enrollments SET total_points = total_points + ?, last_activity = datetime('now') WHERE user_id = ? AND language_id = ?",
            (points_earned, user['id'], lesson['language_id'])
        )

    return jsonify({
        "score": 1.0 if is_correct else 0.0,
        "is_correct": is_correct,
        "correct_answer": correct_answer,
        "feedback": {
            "message": "Dogry! Gowy iş!" if is_correct else f"Ýalňyş. Dogry jogap: {correct_answer}",
            "suggestions": ["Sapak içerigi täzeden okaň"] if not is_correct else []
        },
        "points_earned": points_earned
    })

# --- VOCABULARY ---

@app.route('/api/vocabulary', methods=['GET'])
def get_vocabulary():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    language_id = request.args.get('language_id', type=int)
    if not language_id:
        return jsonify({"error": "language_id gerek"}), 400

    rows = query_db(
        "SELECT * FROM vocabulary_words WHERE user_id = ? AND language_id = ? ORDER BY created_at DESC",
        (user['id'], language_id)
    )
    return jsonify(rows)

@app.route('/api/vocabulary', methods=['POST'])
def add_vocabulary():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    word = data.get('word', '').strip()
    translation = data.get('translation', '').strip()
    language_id = data.get('language_id')
    example = data.get('example', '')

    if not word or not translation or not language_id:
        return jsonify({"error": "word, translation, language_id gerek"}), 400

    vid = execute_db(
        "INSERT INTO vocabulary_words (user_id, language_id, word, translation, example) VALUES (?, ?, ?, ?, ?)",
        (user['id'], language_id, word, translation, example)
    )
    new_word = query_db("SELECT * FROM vocabulary_words WHERE id = ?", (vid,), one=True)
    return jsonify(new_word), 201

@app.route('/api/vocabulary/<int:word_id>', methods=['DELETE'])
def delete_vocabulary(word_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    row = query_db("SELECT * FROM vocabulary_words WHERE id = ? AND user_id = ?", (word_id, user['id']), one=True)
    if not row:
        return jsonify({"error": "Söz tapylmady"}), 404

    execute_db("DELETE FROM vocabulary_words WHERE id = ?", (word_id,))
    return jsonify({"message": "Söz öçürildi"})

@app.route('/api/vocabulary/<int:word_id>/practice', methods=['POST'])
def practice_vocabulary(word_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    word = query_db("SELECT * FROM vocabulary_words WHERE id = ? AND user_id = ?", (word_id, user['id']), one=True)
    if not word:
        return jsonify({"error": "Söz tapylmady"}), 404

    correct = request.json.get('correct', False)
    new_mastery = min(5, word['mastery_level'] + 1) if correct else max(0, word['mastery_level'] - 1)

    execute_db(
        "UPDATE vocabulary_words SET mastery_level = ?, times_practiced = times_practiced + 1, last_practiced = datetime('now') WHERE id = ?",
        (new_mastery, word_id)
    )
    updated = query_db("SELECT * FROM vocabulary_words WHERE id = ?", (word_id,), one=True)
    return jsonify(updated)

# --- PROGRESS ---

@app.route('/api/progress', methods=['GET'])
def get_progress():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    language_id = request.args.get('language_id', type=int)
    if not language_id:
        return jsonify({"error": "language_id gerek"}), 400

    total_lessons = query_db("SELECT COUNT(*) as cnt FROM lessons WHERE language_id = ?", (language_id,), one=True)['cnt']
    total_exercises = query_db(
        "SELECT COUNT(*) as cnt FROM exercises e JOIN lessons l ON l.id = e.lesson_id WHERE l.language_id = ?",
        (language_id,), one=True
    )['cnt']

    # Tamamlanan sapaklar (ähli maşklar dogry jogaplanan)
    lesson_ids = [r['id'] for r in query_db("SELECT id FROM lessons WHERE language_id = ?", (language_id,))]
    completed_lessons = 0
    for lid in lesson_ids:
        ex_ids = [e['id'] for e in query_db("SELECT id FROM exercises WHERE lesson_id = ?", (lid,))]
        if not ex_ids:
            continue
        done = query_db(
            f"SELECT COUNT(DISTINCT exercise_id) as cnt FROM exercise_results "
            f"WHERE user_id = ? AND is_correct = 1 AND exercise_id IN ({','.join('?'*len(ex_ids))})",
            [user['id']] + ex_ids, one=True
        )
        if done and done['cnt'] == len(ex_ids):
            completed_lessons += 1

    # Tamamlanan maşklar (dogry)
    completed_exercises = query_db(
        "SELECT COUNT(DISTINCT er.exercise_id) as cnt FROM exercise_results er "
        "JOIN exercises e ON e.id = er.exercise_id "
        "JOIN lessons l ON l.id = e.lesson_id "
        "WHERE er.user_id = ? AND l.language_id = ? AND er.is_correct = 1",
        (user['id'], language_id), one=True
    )['cnt']

    # Jemi bal
    enrollment = query_db("SELECT total_points FROM enrollments WHERE user_id = ? AND language_id = ?",
                          (user['id'], language_id), one=True)
    total_points = enrollment['total_points'] if enrollment else 0

    # Ortaça bal (%)
    avg_score_row = query_db(
        "SELECT AVG(CAST(er.is_correct AS REAL)) as avg FROM exercise_results er "
        "JOIN exercises e ON e.id = er.exercise_id "
        "JOIN lessons l ON l.id = e.lesson_id "
        "WHERE er.user_id = ? AND l.language_id = ?",
        (user['id'], language_id), one=True
    )
    avg_score = round((avg_score_row['avg'] or 0) * 100, 1)

    return jsonify({
        "total_lessons": total_lessons,
        "completed_lessons": completed_lessons,
        "total_exercises": total_exercises,
        "completed_exercises": completed_exercises,
        "total_points": total_points,
        "completion_rate": round((completed_lessons / total_lessons * 100) if total_lessons else 0, 1),
        "average_score": avg_score
    })

# --- AI CONVERSATION ---

@app.route('/api/ai/conversation', methods=['POST'])
def ai_conversation():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    message = data.get('message', '').strip()
    language_id = data.get('language_id')

    if not message:
        return jsonify({"error": "message gerek"}), 400

    lang = query_db("SELECT * FROM languages WHERE id = ?", (language_id,), one=True)
    lang_name = lang['name'] if lang else "Unknown"

    responses = {
        1: "¡Hola! Estoy aquí para ayudarte con español. (Salam! Men saňa ispança kömek etmek üçin şu ýerdäm.)",
        2: "Bonjour! Je suis là pour vous aider avec le français. (Salam! Men size fransuzça kömek etmek üçin şu ýerdäm.)",
        3: "Guten Tag! Ich bin hier, um Ihnen mit Deutsch zu helfen. (Salam! Men size nemesçe kömek etmek üçin şu ýerdäm.)"
    }
    ai_response = responses.get(language_id, "Hello! I'm here to help you learn!")

    corrections = []
    if "gracias" in message.lower():
        corrections.append({"original": "gracias", "corrected": "gracias", "explanation": "Dogry! 'Gracias' - 'Sag bol' diýmek."})

    return jsonify({
        "message": ai_response,
        "suggestions": ["Täze sözleri öwreniň", "Sapak mazmunyny täzeden okaň", "Maşk ediň"],
        "corrections": corrections if corrections else None
    })

# --- STATS ---

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Umumy statistika (admin ýa-da debug üçin)"""
    return jsonify({
        "users": query_db("SELECT COUNT(*) as cnt FROM users", one=True)['cnt'],
        "languages": query_db("SELECT COUNT(*) as cnt FROM languages", one=True)['cnt'],
        "lessons": query_db("SELECT COUNT(*) as cnt FROM lessons", one=True)['cnt'],
        "exercises": query_db("SELECT COUNT(*) as cnt FROM exercises", one=True)['cnt'],
        "enrollments": query_db("SELECT COUNT(*) as cnt FROM enrollments", one=True)['cnt'],
        "exercise_results": query_db("SELECT COUNT(*) as cnt FROM exercise_results", one=True)['cnt'],
        "vocabulary_words": query_db("SELECT COUNT(*) as cnt FROM vocabulary_words", one=True)['cnt'],
    })

@app.route('/health', methods=['GET'])
def health():
    stats = query_db("""
        SELECT
            (SELECT COUNT(*) FROM users) as users,
            (SELECT COUNT(*) FROM languages) as languages,
            (SELECT COUNT(*) FROM lessons) as lessons,
            (SELECT COUNT(*) FROM exercises) as exercises
    """, one=True)
    return jsonify({"status": "ok", **stats})

# ====== ADMIN ENDPOINTS ======

# --- LANGUAGES CRUD ---

@app.route('/api/languages', methods=['POST'])
def create_language():
    """Täze dil goş"""
    data = request.json or {}
    name        = data.get('name', '').strip()
    code        = data.get('code', '').strip().lower()
    flag        = data.get('flag', '').strip()
    description = data.get('description', '').strip()

    if not name or not code:
        return jsonify({"error": "name we code gerek"}), 400
    if query_db("SELECT id FROM languages WHERE code = ?", (code,), one=True):
        return jsonify({"error": "Bu kod eýýäm ulanylypdyr"}), 400

    lid = execute_db(
        "INSERT INTO languages (name, code, flag, description) VALUES (?, ?, ?, ?)",
        (name, code, flag, description)
    )
    return jsonify(query_db("SELECT * FROM languages WHERE id = ?", (lid,), one=True)), 201

@app.route('/api/languages/<int:language_id>', methods=['PUT'])
def update_language(language_id):
    """Dili üýtget"""
    lang = query_db("SELECT * FROM languages WHERE id = ?", (language_id,), one=True)
    if not lang:
        return jsonify({"error": "Dil tapylmady"}), 404

    data = request.json or {}
    name        = data.get('name',        lang['name']).strip()
    code        = data.get('code',        lang['code']).strip().lower()
    flag        = data.get('flag',        lang['flag'] or '').strip()
    description = data.get('description', lang['description'] or '').strip()

    dup = query_db("SELECT id FROM languages WHERE code = ? AND id != ?", (code, language_id), one=True)
    if dup:
        return jsonify({"error": "Bu kod başga dilde ulanylypdyr"}), 400

    execute_db(
        "UPDATE languages SET name=?, code=?, flag=?, description=? WHERE id=?",
        (name, code, flag, description, language_id)
    )
    return jsonify(query_db("SELECT * FROM languages WHERE id = ?", (language_id,), one=True))

@app.route('/api/languages/<int:language_id>', methods=['DELETE'])
def delete_language(language_id):
    """Dili öçür"""
    if not query_db("SELECT id FROM languages WHERE id = ?", (language_id,), one=True):
        return jsonify({"error": "Dil tapylmady"}), 404
    execute_db("DELETE FROM languages WHERE id = ?", (language_id,))
    return jsonify({"message": "Dil öçürildi"})

# --- LESSONS CRUD ---

@app.route('/api/lessons', methods=['POST'])
def create_lesson():
    """Täze sapak goş"""
    import json as _json
    data = request.json or {}
    language_id = data.get('language_id')
    title       = data.get('title', '').strip()
    description = data.get('description', '').strip()
    level       = data.get('level', 'beginner')
    order_num   = int(data.get('order_num', 1))
    content     = data.get('content', {})

    if not language_id or not title:
        return jsonify({"error": "language_id we title gerek"}), 400
    if not query_db("SELECT id FROM languages WHERE id = ?", (language_id,), one=True):
        return jsonify({"error": "Dil tapylmady"}), 404

    lid = execute_db(
        "INSERT INTO lessons (language_id, title, description, level, order_num, content) VALUES (?, ?, ?, ?, ?, ?)",
        (language_id, title, description, level, order_num, _json.dumps(content))
    )
    lesson = query_db("SELECT * FROM lessons WHERE id = ?", (lid,), one=True)
    lesson['content'] = content
    return jsonify(lesson), 201

@app.route('/api/lessons/<int:lesson_id>', methods=['PUT'])
def update_lesson(lesson_id):
    """Sapak üýtget"""
    import json as _json
    lesson = query_db("SELECT * FROM lessons WHERE id = ?", (lesson_id,), one=True)
    if not lesson:
        return jsonify({"error": "Sapak tapylmady"}), 404

    data        = request.json or {}
    title       = data.get('title',       lesson['title']).strip()
    description = data.get('description', lesson['description'] or '').strip()
    level       = data.get('level',       lesson['level'])
    order_num   = int(data.get('order_num', lesson['order_num']))
    language_id = int(data.get('language_id', lesson['language_id']))
    content     = data.get('content',     {})

    execute_db(
        "UPDATE lessons SET language_id=?, title=?, description=?, level=?, order_num=?, content=? WHERE id=?",
        (language_id, title, description, level, order_num, _json.dumps(content), lesson_id)
    )
    updated = query_db("SELECT * FROM lessons WHERE id = ?", (lesson_id,), one=True)
    updated['content'] = content
    return jsonify(updated)

@app.route('/api/lessons/<int:lesson_id>', methods=['DELETE'])
def delete_lesson(lesson_id):
    """Sapak öçür"""
    if not query_db("SELECT id FROM lessons WHERE id = ?", (lesson_id,), one=True):
        return jsonify({"error": "Sapak tapylmady"}), 404
    execute_db("DELETE FROM exercises WHERE lesson_id = ?", (lesson_id,))
    execute_db("DELETE FROM lessons WHERE id = ?", (lesson_id,))
    return jsonify({"message": "Sapak öçürildi"})

# --- EXERCISES CRUD ---

@app.route('/api/exercises', methods=['POST'])
def create_exercise():
    """Täze maşk goş"""
    import json as _json
    data       = request.json or {}
    lesson_id  = data.get('lesson_id')
    title      = data.get('title', '').strip()
    ex_type    = data.get('type', 'multiple_choice')
    difficulty = int(data.get('difficulty', 1))
    points     = int(data.get('points', 10))
    content    = data.get('content', {})

    if not lesson_id or not title:
        return jsonify({"error": "lesson_id we title gerek"}), 400
    if not query_db("SELECT id FROM lessons WHERE id = ?", (lesson_id,), one=True):
        return jsonify({"error": "Sapak tapylmady"}), 404

    eid = execute_db(
        "INSERT INTO exercises (lesson_id, title, type, difficulty, points, content) VALUES (?, ?, ?, ?, ?, ?)",
        (lesson_id, title, ex_type, difficulty, points, _json.dumps(content))
    )
    ex = query_db("SELECT * FROM exercises WHERE id = ?", (eid,), one=True)
    ex['content'] = content
    return jsonify(ex), 201

@app.route('/api/exercises/<int:exercise_id>', methods=['PUT'])
def update_exercise(exercise_id):
    """Maşk üýtget"""
    import json as _json
    ex = query_db("SELECT * FROM exercises WHERE id = ?", (exercise_id,), one=True)
    if not ex:
        return jsonify({"error": "Maşk tapylmady"}), 404

    data       = request.json or {}
    lesson_id  = int(data.get('lesson_id',  ex['lesson_id']))
    title      = data.get('title',      ex['title']).strip()
    ex_type    = data.get('type',        ex['type'])
    difficulty = int(data.get('difficulty', ex['difficulty']))
    points     = int(data.get('points',     ex['points']))
    content    = data.get('content',    {})

    execute_db(
        "UPDATE exercises SET lesson_id=?, title=?, type=?, difficulty=?, points=?, content=? WHERE id=?",
        (lesson_id, title, ex_type, difficulty, points, _json.dumps(content), exercise_id)
    )
    updated = query_db("SELECT * FROM exercises WHERE id = ?", (exercise_id,), one=True)
    updated['content'] = content
    return jsonify(updated)

@app.route('/api/exercises/<int:exercise_id>', methods=['DELETE'])
def delete_exercise(exercise_id):
    """Maşk öçür"""
    if not query_db("SELECT id FROM exercises WHERE id = ?", (exercise_id,), one=True):
        return jsonify({"error": "Maşk tapylmady"}), 404
    execute_db("DELETE FROM exercise_results WHERE exercise_id = ?", (exercise_id,))
    execute_db("DELETE FROM exercises WHERE id = ?", (exercise_id,))
    return jsonify({"message": "Maşk öçürildi"})

# --- ADMIN: USERS ---

@app.route('/api/admin/users', methods=['GET'])
def admin_get_users():
    """Ähli ulanyjylary al"""
    users = query_db(
        "SELECT id, username, email, native_language, created_at FROM users ORDER BY created_at DESC"
    )
    return jsonify(users)

@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
def admin_delete_user(user_id):
    """Ulanyjy öçür"""
    if not query_db("SELECT id FROM users WHERE id = ?", (user_id,), one=True):
        return jsonify({"error": "Ulanyjy tapylmady"}), 404
    execute_db("DELETE FROM enrollments WHERE user_id = ?", (user_id,))
    execute_db("DELETE FROM exercise_results WHERE user_id = ?", (user_id,))
    execute_db("DELETE FROM vocabulary_words WHERE user_id = ?", (user_id,))
    execute_db("DELETE FROM users WHERE id = ?", (user_id,))
    return jsonify({"message": "Ulanyjy öçürildi"})

# --- ADMIN: VOCABULARY ---

@app.route('/api/admin/vocabulary', methods=['GET'])
def admin_get_vocabulary():
    """Ähli söz depderini al"""
    words = query_db("""
        SELECT v.*, u.username
        FROM vocabulary_words v
        JOIN users u ON u.id = v.user_id
        ORDER BY v.created_at DESC
    """)
    return jsonify(words)

@app.route('/api/admin/vocabulary/<int:word_id>', methods=['DELETE'])
def admin_delete_vocabulary(word_id):
    """Söz öçür (admin)"""
    if not query_db("SELECT id FROM vocabulary_words WHERE id = ?", (word_id,), one=True):
        return jsonify({"error": "Söz tapylmady"}), 404
    execute_db("DELETE FROM vocabulary_words WHERE id = ?", (word_id,))
    return jsonify({"message": "Söz öçürildi"})

# ====== MAIN ======

if __name__ == '__main__':
    print("🚀 Backend başlaýar...")
    init_db()
    print("✅ Database tablolary taýýar")
    seed_data()
    print("\n🌐 Server: http://localhost:5070")
    print("📖 Health check: http://localhost:5070/health")
    app.run(debug=True, host='0.0.0.0', port=5070)