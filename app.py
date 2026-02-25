"""
Flask Backend - Language Learning App
Doly sapaklar, maşklar we AI integration bilen
"""

from flask import Flask, request, jsonify,render_template
from flask_cors import CORS
from datetime import datetime, timedelta
import jwt
import json
import os

app = Flask(__name__)
CORS(app)

# Secret key for JWT
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'

# ====== IN-MEMORY DATABASE ======
# Hakyky database üçin SQLite, PostgreSQL, ýa-da MongoDB ulanyp bilersiňiz

users = []
languages = []
enrollments = []
lessons = []
exercises = []
vocabulary_words = []
progress_data = []
user_id_counter = 1
enrollment_id_counter = 1
lesson_id_counter = 1
exercise_id_counter = 1
vocab_id_counter = 1

@app.route('/')
def index():
    return render_template('index.html')
# ====== INITIALIZE DATA ======

def initialize_data():
    """Başlangyç maglumatlary ýükle"""
    global languages, lessons, exercises, lesson_id_counter, exercise_id_counter
    
    # DILLER
    languages.extend([
        {
            "id": 1,
            "name": "Ispança",
            "code": "es",
            "flag": "🇪🇸",
            "description": "Dünýäde 500+ million adam gürleýän dil"
        },
        {
            "id": 2,
            "name": "Fransuzça",
            "code": "fr",
            "flag": "🇫🇷",
            "description": "Romance diller maşgalasynyň agzasy"
        },
        {
            "id": 3,
            "name": "Nemesçe",
            "code": "de",
            "flag": "🇩🇪",
            "description": "Europanyň merkezi dillerinden"
        },
        {
            "id": 4,
            "name": "Italýança",
            "code": "it",
            "flag": "🇮🇹",
            "description": "Sungat we medeniýet dili"
        },
        {
            "id": 5,
            "name": "Ýaponça",
            "code": "ja",
            "flag": "🇯🇵",
            "description": "Aziýanyň möhüm dillerinden"
        },
        {
            "id": 6,
            "name": "Hytaýça",
            "code": "zh",
            "flag": "🇨🇳",
            "description": "Iň köp adam gürleýän dil"
        }
    ])
    
    # ISPANÇA SAPAKLAR WE MAŞKLAR
    create_spanish_lessons()
    
    # FRANSUZÇA SAPAKLAR
    create_french_lessons()
    
    # NEMESÇE SAPAKLAR
    create_german_lessons()

def create_spanish_lessons():
    """Ispança sapaklar we maşklar"""
    global lessons, exercises, lesson_id_counter, exercise_id_counter
    
    # SAPAK 1: Salamlaşma
    lesson1_id = lesson_id_counter
    lessons.append({
        "id": lesson1_id,
        "language_id": 1,
        "title": "Salamlaşma we tanyşma",
        "description": "Esasy salamlaşma sözleri we özüňi tanyşdyrmak",
        "level": "beginner",
        "order": 1,
        "content": {
            "sections": [
                {
                    "type": "text",
                    "content": "Ispança salamlaşmak üçin köp görnüşli sözler bar. Iň umumy sözler: Hola (Salam), Buenos días (Ertiriňiz haýyrly), Buenas tardes (Günortan haýyrly), Buenas noches (Agşamyňyz haýyrly)."
                },
                {
                    "type": "vocabulary",
                    "words": [
                        {"word": "Hola", "translation": "Salam", "example": "¡Hola! ¿Cómo estás?"},
                        {"word": "Buenos días", "translation": "Ertiriňiz haýyrly", "example": "Buenos días, señora."},
                        {"word": "Adiós", "translation": "Hoş gal", "example": "Adiós, hasta mañana."},
                        {"word": "Gracias", "translation": "Sag bol", "example": "Muchas gracias."},
                        {"word": "Por favor", "translation": "Haýyş edýärin", "example": "Por favor, ayúdame."}
                    ]
                }
            ]
        }
    })
    lesson_id_counter += 1
    
    # Sapak 1 üçin maşklar
    exercises.extend([
        {
            "id": exercise_id_counter,
            "lesson_id": lesson1_id,
            "title": "\"Hola\" näme diýmek?",
            "type": "multiple_choice",
            "difficulty": 1,
            "points": 10,
            "content": {
                "question": "\"Hola\" näme diýmek?",
                "options": ["Salam", "Hoş gal", "Sag bol", "Ertiriňiz haýyrly"],
                "correct_answer": "Salam",
                "hint": "Bu iň umumy salamlaşma sözi"
            }
        },
        {
            "id": exercise_id_counter + 1,
            "lesson_id": lesson1_id,
            "title": "\"Gracias\" terjime et",
            "type": "translation",
            "difficulty": 1,
            "points": 15,
            "content": {
                "question": "\"Gracias\" sözüni terjime et",
                "correct_answer": "Sag bol",
                "hint": "Bu minnetdarlyk bildirýär"
            }
        },
        {
            "id": exercise_id_counter + 2,
            "lesson_id": lesson1_id,
            "title": "Salamlaşmany tamamla",
            "type": "fill_blank",
            "difficulty": 2,
            "points": 10,
            "content": {
                "question": "_____ días! (Ertiriňiz haýyrly)",
                "correct_answer": "Buenos",
                "hint": "Bu söz 'gowy' diýmek"
            }
        }
    ])
    exercise_id_counter += 3
    
    # SAPAK 2: Sanlar
    lesson2_id = lesson_id_counter
    lessons.append({
        "id": lesson2_id,
        "language_id": 1,
        "title": "Sanlar (0-20)",
        "description": "Esasy sanlary öwrenmek",
        "level": "beginner",
        "order": 2,
        "content": {
            "sections": [
                {
                    "type": "text",
                    "content": "Ispança sanlar: 0 (cero), 1 (uno), 2 (dos), 3 (tres), 4 (cuatro), 5 (cinco), 6 (seis), 7 (siete), 8 (ocho), 9 (nueve), 10 (diez)."
                },
                {
                    "type": "vocabulary",
                    "words": [
                        {"word": "uno", "translation": "bir", "example": "Tengo uno."},
                        {"word": "dos", "translation": "iki", "example": "Dos más dos son cuatro."},
                        {"word": "tres", "translation": "üç", "example": "Tres amigos."},
                        {"word": "diez", "translation": "on", "example": "Son las diez."},
                        {"word": "veinte", "translation": "ýigrimi", "example": "Veinte años."}
                    ]
                }
            ]
        }
    })
    lesson_id_counter += 1
    
    exercises.extend([
        {
            "id": exercise_id_counter,
            "lesson_id": lesson2_id,
            "title": "\"Cinco\" näçe?",
            "type": "multiple_choice",
            "difficulty": 1,
            "points": 10,
            "content": {
                "question": "\"Cinco\" näçe?",
                "options": ["3", "5", "7", "9"],
                "correct_answer": "5",
                "hint": "Ellerinde näçe barmak bar?"
            }
        },
        {
            "id": exercise_id_counter + 1,
            "lesson_id": lesson2_id,
            "title": "10-y ýaz",
            "type": "translation",
            "difficulty": 2,
            "points": 15,
            "content": {
                "question": "10 sanyny ispança ýaz",
                "correct_answer": "diez",
                "hint": "D bilen başlaýar"
            }
        }
    ])
    exercise_id_counter += 2
    
    # SAPAK 3: Maşgala
    lesson3_id = lesson_id_counter
    lessons.append({
        "id": lesson3_id,
        "language_id": 1,
        "title": "Maşgala agzalary",
        "description": "Ene, ata, dogan-garyndaş sözleri",
        "level": "beginner",
        "order": 3,
        "content": {
            "sections": [
                {
                    "type": "text",
                    "content": "Maşgala agzalary: padre (kakam), madre (ejem), hermano (dogam), hermana (uýam), abuelo (mamam/babam), hijo (ogul), hija (gyz)."
                },
                {
                    "type": "vocabulary",
                    "words": [
                        {"word": "padre", "translation": "kakam", "example": "Mi padre trabaja."},
                        {"word": "madre", "translation": "ejem", "example": "Mi madre cocina."},
                        {"word": "hermano", "translation": "dogam", "example": "Tengo un hermano."},
                        {"word": "familia", "translation": "maşgala", "example": "Mi familia es grande."}
                    ]
                }
            ]
        }
    })
    lesson_id_counter += 1
    
    exercises.extend([
        {
            "id": exercise_id_counter,
            "lesson_id": lesson3_id,
            "title": "Maşgala sözleri",
            "type": "multiple_choice",
            "difficulty": 2,
            "points": 10,
            "content": {
                "question": "\"Madre\" näme diýmek?",
                "options": ["Kakam", "Ejem", "Dogam", "Uýam"],
                "correct_answer": "Ejem",
                "hint": "Zenan maşgala agzasy"
            }
        }
    ])
    exercise_id_counter += 1
    
    # SAPAK 4: Reňkler (Orta dereje)
    lesson4_id = lesson_id_counter
    lessons.append({
        "id": lesson4_id,
        "language_id": 1,
        "title": "Reňkler",
        "description": "Esasy reňkleri öwrenmek",
        "level": "intermediate",
        "order": 4,
        "content": {
            "sections": [
                {
                    "type": "text",
                    "content": "Ispança reňkler: rojo (gyzyl), azul (gök), verde (ýaşyl), amarillo (sary), negro (gara), blanco (ak)."
                },
                {
                    "type": "vocabulary",
                    "words": [
                        {"word": "rojo", "translation": "gyzyl", "example": "El coche es rojo."},
                        {"word": "azul", "translation": "gök", "example": "El cielo es azul."},
                        {"word": "verde", "translation": "ýaşyl", "example": "Las plantas son verdes."}
                    ]
                }
            ]
        }
    })
    lesson_id_counter += 1
    
    # SAPAK 5: Iýmit (Orta dereje)
    lesson5_id = lesson_id_counter
    lessons.append({
        "id": lesson5_id,
        "language_id": 1,
        "title": "Iýmit we içmek",
        "description": "Restoranda sargyt etmek",
        "level": "intermediate",
        "order": 5,
        "content": {
            "sections": [
                {
                    "type": "text",
                    "content": "Restoran sözleri: comida (iýmit), bebida (içgi), desayuno (ertirlik), almuerzo (nahar), cena (agşamlyk). Iýmitler: pan (çörek), carne (et), pescado (balyk), arroz (tüwi), ensalada (salat)."
                },
                {
                    "type": "vocabulary",
                    "words": [
                        {"word": "agua", "translation": "suw", "example": "Quiero agua, por favor."},
                        {"word": "pan", "translation": "çörek", "example": "El pan está caliente."},
                        {"word": "pollo", "translation": "towuk", "example": "Pollo con arroz."}
                    ]
                }
            ]
        }
    })
    lesson_id_counter += 1

def create_french_lessons():
    """Fransuzça sapaklar"""
    global lessons, exercises, lesson_id_counter, exercise_id_counter
    
    # Sapak 1: Bonjour!
    lesson_id = lesson_id_counter
    lessons.append({
        "id": lesson_id,
        "language_id": 2,
        "title": "Salamlaşma - Bonjour!",
        "description": "Fransuzça esasy salamlaşma",
        "level": "beginner",
        "order": 1,
        "content": {
            "sections": [
                {
                    "type": "text",
                    "content": "Fransuzça salamlaşmak: Bonjour (Salam/Ertiriňiz haýyrly), Bonsoir (Agşamyňyz haýyrly), Au revoir (Hoş gal), Merci (Sag bol), S'il vous plaît (Haýyş edýärin)."
                },
                {
                    "type": "vocabulary",
                    "words": [
                        {"word": "Bonjour", "translation": "Salam", "example": "Bonjour, madame!"},
                        {"word": "Merci", "translation": "Sag bol", "example": "Merci beaucoup!"},
                        {"word": "Au revoir", "translation": "Hoş gal", "example": "Au revoir, à demain!"}
                    ]
                }
            ]
        }
    })
    lesson_id_counter += 1
    
    exercises.append({
        "id": exercise_id_counter,
        "lesson_id": lesson_id,
        "title": "Bonjour näme diýmek?",
        "type": "multiple_choice",
        "difficulty": 1,
        "points": 10,
        "content": {
            "question": "\"Bonjour\" näme diýmek?",
            "options": ["Salam", "Hoş gal", "Sag bol", "Haýyş edýärin"],
            "correct_answer": "Salam"
        }
    })
    exercise_id_counter += 1

def create_german_lessons():
    """Nemesçe sapaklar"""
    global lessons, exercises, lesson_id_counter, exercise_id_counter
    
    lesson_id = lesson_id_counter
    lessons.append({
        "id": lesson_id,
        "language_id": 3,
        "title": "Guten Tag!",
        "description": "Nemesçe salamlaşma we özüňi tanyşdyrmak",
        "level": "beginner",
        "order": 1,
        "content": {
            "sections": [
                {
                    "type": "text",
                    "content": "Nemesçe salamlaşmak: Guten Tag (Salam), Guten Morgen (Ertiriňiz haýyrly), Auf Wiedersehen (Hoş gal), Danke (Sag bol), Bitte (Haýyş edýärin)."
                },
                {
                    "type": "vocabulary",
                    "words": [
                        {"word": "Hallo", "translation": "Salam", "example": "Hallo! Wie geht's?"},
                        {"word": "Danke", "translation": "Sag bol", "example": "Danke schön!"},
                        {"word": "Tschüss", "translation": "Hoş gal", "example": "Tschüss, bis später!"}
                    ]
                }
            ]
        }
    })
    lesson_id_counter += 1

# ====== HELPER FUNCTIONS ======

def generate_token(user_id):
    """JWT token döret"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=30)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    """JWT token barla"""
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['user_id']
    except:
        return None

def get_current_user():
    """Token-dan ulanyjyny al"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    
    try:
        token = auth_header.split(' ')[1]
        user_id = verify_token(token)
        if user_id:
            return next((u for u in users if u['id'] == user_id), None)
    except:
        pass
    return None

# ====== ROUTES ======

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Täze ulanyjy hasaba al"""
    global user_id_counter
    
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    native_language = data.get('native_language', 'Turkmen')
    
    # Validasiýa
    if not username or not email or not password:
        return jsonify({"error": "Ähli meýdanlary dolduryň"}), 400
    
    # Username bar bolsa
    if any(u['username'] == username for u in users):
        return jsonify({"error": "Bu username eýýäm ulanylypdyr"}), 400
    
    # Email bar bolsa
    if any(u['email'] == email for u in users):
        return jsonify({"error": "Bu email eýýäm ulanylypdyr"}), 400
    
    # Täze ulanyjy
    user = {
        "id": user_id_counter,
        "username": username,
        "email": email,
        "password": password,  # Production-da hash etmeli!
        "native_language": native_language,
        "created_at": datetime.now().isoformat()
    }
    users.append(user)
    user_id_counter += 1
    
    # Token döret
    token = generate_token(user['id'])
    
    # User maglumaty (password-syz)
    user_data = {k: v for k, v in user.items() if k != 'password'}
    
    return jsonify({
        "token": token,
        "user": user_data
    }), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Ulanyjy gir"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Username we password gerek"}), 400
    
    # Ulanyjyny tap
    user = next((u for u in users if u['username'] == username), None)
    
    if not user or user['password'] != password:
        return jsonify({"error": "Username ýa-da password ýalňyş"}), 401
    
    # Token döret
    token = generate_token(user['id'])
    
    user_data = {k: v for k, v in user.items() if k != 'password'}
    
    return jsonify({
        "token": token,
        "user": user_data
    })

@app.route('/api/auth/me', methods=['GET'])
def get_me():
    """Häzirki ulanyjy al"""
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    user_data = {k: v for k, v in user.items() if k != 'password'}
    return jsonify(user_data)

@app.route('/api/languages', methods=['GET'])
def get_languages():
    """Ähli dilleri al"""
    return jsonify(languages)

@app.route('/api/languages/<int:language_id>', methods=['GET'])
def get_language(language_id):
    """Bir dili al"""
    language = next((l for l in languages if l['id'] == language_id), None)
    if not language:
        return jsonify({"error": "Dil tapylmady"}), 404
    return jsonify(language)

@app.route('/api/enrollments', methods=['GET'])
def get_enrollments():
    """Ulanyjynyň ýazylan dillerini al"""
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    user_enrollments = [e for e in enrollments if e['user_id'] == user['id']]
    
    # Language maglumatyny goş
    for enrollment in user_enrollments:
        language = next((l for l in languages if l['id'] == enrollment['language_id']), None)
        enrollment['language'] = language
    
    return jsonify(user_enrollments)

@app.route('/api/enrollments', methods=['POST'])
def create_enrollment():
    """Täze dile ýazyl"""
    global enrollment_id_counter
    
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    language_id = data.get('language_id')
    
    if not language_id:
        return jsonify({"error": "language_id gerek"}), 400
    
    # Dil barmy?
    language = next((l for l in languages if l['id'] == language_id), None)
    if not language:
        return jsonify({"error": "Dil tapylmady"}), 404
    
    # Eýýäm ýazylanmy?
    existing = next((e for e in enrollments if e['user_id'] == user['id'] and e['language_id'] == language_id), None)
    if existing:
        return jsonify({"error": "Bu dile eýýäm ýazylandyňyz"}), 400
    
    # Täze enrollment
    enrollment = {
        "id": enrollment_id_counter,
        "user_id": user['id'],
        "language_id": language_id,
        "language": language,
        "level": "beginner",
        "total_points": 0,
        "streak_days": 0,
        "last_activity": datetime.now().isoformat(),
        "enrolled_at": datetime.now().isoformat()
    }
    enrollments.append(enrollment)
    enrollment_id_counter += 1
    
    return jsonify(enrollment), 201

@app.route('/api/lessons', methods=['GET'])
def get_lessons():
    """Sapaklar sanawы"""
    language_id = request.args.get('language_id', type=int)
    level = request.args.get('level')
    
    if not language_id:
        return jsonify({"error": "language_id gerek"}), 400
    
    # Filter sapaklar
    filtered_lessons = [l for l in lessons if l['language_id'] == language_id]
    
    if level:
        filtered_lessons = [l for l in filtered_lessons if l['level'] == level]
    
    # Ýönekeý wersiýa (content-syz)
    simple_lessons = []
    for lesson in filtered_lessons:
        simple_lesson = {k: v for k, v in lesson.items() if k != 'content'}
        
        # Maşk sany
        lesson_exercises = [e for e in exercises if e['lesson_id'] == lesson['id']]
        simple_lesson['exercises_count'] = len(lesson_exercises)
        simple_lesson['is_completed'] = False  # TODO: Progress-den al
        
        simple_lessons.append(simple_lesson)
    
    return jsonify(simple_lessons)

@app.route('/api/lessons/<int:lesson_id>', methods=['GET'])
def get_lesson(lesson_id):
    """Sapagyň jikme-jik maglumaty"""
    lesson = next((l for l in lessons if l['id'] == lesson_id), None)
    if not lesson:
        return jsonify({"error": "Sapak tapylmady"}), 404
    
    # Maşklary goş
    lesson_exercises = [e for e in exercises if e['lesson_id'] == lesson_id]
    
    lesson_detail = lesson.copy()
    lesson_detail['exercises'] = lesson_exercises
    
    return jsonify(lesson_detail)

@app.route('/api/exercises/<int:exercise_id>', methods=['GET'])
def get_exercise(exercise_id):
    """Maşk maglumatyny al"""
    exercise = next((e for e in exercises if e['id'] == exercise_id), None)
    if not exercise:
        return jsonify({"error": "Maşk tapylmady"}), 404
    
    return jsonify(exercise)

@app.route('/api/exercises/<int:exercise_id>/submit', methods=['POST'])
def submit_exercise(exercise_id):
    """Maşk jogabyny ibermek"""
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    exercise = next((e for e in exercises if e['id'] == exercise_id), None)
    if not exercise:
        return jsonify({"error": "Maşk tapylmady"}), 404
    
    data = request.json
    user_answer = data.get('answer', '').strip()
    correct_answer = exercise['content']['correct_answer']
    
    # Jogaby barla (case-insensitive)
    is_correct = user_answer.lower() == correct_answer.lower()
    score = 1.0 if is_correct else 0.0
    
    # Bal hasapla
    points_earned = exercise['points'] if is_correct else 0
    
    result = {
        "score": score,
        "is_correct": is_correct,
        "correct_answer": correct_answer,
        "feedback": {
            "message": "Dogry! Gowy iş!" if is_correct else f"Ýalňyş. Dogry jogap: {correct_answer}",
            "suggestions": ["Sapak içerigi täzeden okaň", "Beýleki mysallara seredň"] if not is_correct else []
        },
        "points_earned": points_earned
    }
    
    return jsonify(result)

@app.route('/api/vocabulary', methods=['GET'])
def get_vocabulary():
    """Täze sözler sanawы"""
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    language_id = request.args.get('language_id', type=int)
    if not language_id:
        return jsonify({"error": "language_id gerek"}), 400
    
    user_words = [w for w in vocabulary_words 
                  if w['user_id'] == user['id'] and w['language_id'] == language_id]
    
    return jsonify(user_words)

@app.route('/api/vocabulary', methods=['POST'])
def add_vocabulary():
    """Täze söz goş"""
    global vocab_id_counter
    
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    word = data.get('word')
    translation = data.get('translation')
    language_id = data.get('language_id')
    example = data.get('example')
    
    if not word or not translation or not language_id:
        return jsonify({"error": "word, translation, language_id gerek"}), 400
    
    new_word = {
        "id": vocab_id_counter,
        "user_id": user['id'],
        "word": word,
        "translation": translation,
        "language_id": language_id,
        "mastery_level": 0,
        "times_practiced": 0,
        "last_practiced": None,
        "example": example,
        "created_at": datetime.now().isoformat()
    }
    vocabulary_words.append(new_word)
    vocab_id_counter += 1
    
    return jsonify(new_word), 201

@app.route('/api/vocabulary/<int:word_id>/practice', methods=['POST'])
def practice_vocabulary(word_id):
    """Söz maşk et"""
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    word = next((w for w in vocabulary_words 
                 if w['id'] == word_id and w['user_id'] == user['id']), None)
    if not word:
        return jsonify({"error": "Söz tapylmady"}), 404
    
    data = request.json
    correct = data.get('correct', False)
    
    # Update mastery
    if correct:
        word['mastery_level'] = min(5, word['mastery_level'] + 1)
    else:
        word['mastery_level'] = max(0, word['mastery_level'] - 1)
    
    word['times_practiced'] += 1
    word['last_practiced'] = datetime.now().isoformat()
    
    return jsonify(word)

@app.route('/api/progress', methods=['GET'])
def get_progress():
    """Ösüş maglumatyny al"""
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    language_id = request.args.get('language_id', type=int)
    if not language_id:
        return jsonify({"error": "language_id gerek"}), 400
    
    # Sapaklar we maşklar sany
    language_lessons = [l for l in lessons if l['language_id'] == language_id]
    total_lessons = len(language_lessons)
    
    total_exercises = sum(len([e for e in exercises if e['lesson_id'] == l['id']]) 
                         for l in language_lessons)
    
    # TODO: Hakyky tamamlanan sapaklar we maşklar database-den almaly
    completed_lessons = 0
    completed_exercises = 0
    
    progress = {
        "total_lessons": total_lessons,
        "completed_lessons": completed_lessons,
        "total_exercises": total_exercises,
        "completed_exercises": completed_exercises,
        "total_points": 0,
        "completion_rate": 0.0,
        "average_score": 0.0
    }
    
    return jsonify(progress)

@app.route('/api/ai/conversation', methods=['POST'])
def ai_conversation():
    """AI söhbetdeşlik"""
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    message = data.get('message')
    language_id = data.get('language_id')
    
    if not message:
        return jsonify({"error": "message gerek"}), 400
    
    # Ýönekeý jogap (Real AI üçin Anthropic Claude API ulanyň)
    language = next((l for l in languages if l['id'] == language_id), None)
    language_name = language['name'] if language else "Unknown"
    
    responses = {
        1: f"¡Hola! Estoy aquí para ayudarte con español. (Salam! Men sana ispança kömek etmek üçin şu ýerdäm.)",
        2: f"Bonjour! Je suis là pour vous aider avec le français. (Salam! Men size fransuzça kömek etmek üçin şu ýerdäm.)",
        3: f"Guten Tag! Ich bin hier, um Ihnen mit Deutsch zu helfen. (Salam! Men size nemesçe kömek etmek üçin şu ýerdäm.)"
    }
    
    ai_response = responses.get(language_id, "Hello! I'm here to help you learn!")
    
    # Ýönekeý düzediş mysaly
    corrections = []
    if "gracias" in message.lower():
        corrections.append({
            "original": "gracias",
            "corrected": "gracias",
            "explanation": "Dogry! 'Gracias' - 'Sag bol' diýmek."
        })
    
    response = {
        "message": ai_response,
        "suggestions": [
            "Täze sözleri öwreniň",
            "Sapak mazmunyny täzeden okaň",
            "Maşk ediň"
        ],
        "corrections": corrections if corrections else None
    }
    
    return jsonify(response)

@app.route('/health', methods=['GET'])
def health():
    """Server işleýärmi barla"""
    return jsonify({
        "status": "ok",
        "users": len(users),
        "languages": len(languages),
        "lessons": len(lessons),
        "exercises": len(exercises)
    })

# ====== MAIN ======

if __name__ == '__main__':
    print("🚀 Backend başlaýar...")
    print("📚 Sapaklar we maşklar ýüklenýär...")
    initialize_data()
    print(f"✅ {len(languages)} dil ýüklendi")
    print(f"✅ {len(lessons)} sapak ýüklendi")
    print(f"✅ {len(exercises)} maşk ýüklendi")
    print("\n🌐 Server: http://localhost:5000")
    print("📖 Health check: http://localhost:5000/health")
    app.run(debug=True, host='0.0.0.0', port=5000)