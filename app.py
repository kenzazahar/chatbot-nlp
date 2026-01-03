from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from models.chatbot_model import ChatbotNLP
import sqlite3
import uuid
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'secret_key_chatbot_nlp'
CORS(app)

# Initialisation du Chatbot
chatbot = ChatbotNLP()

# Base de données
DATABASE = 'database.db'

def init_db():
    """Initialise la base de données avec toutes les colonnes nécessaires"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Table principale avec toutes les colonnes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            user_msg TEXT,
            bot_resp TEXT,
            intent TEXT,
            confidence REAL,
            emotion TEXT DEFAULT 'neutral',
            rating INTEGER,
            language TEXT DEFAULT 'fr',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Base de données initialisée")

def detect_language(text):
    """Détection simple de la langue basée sur des caractères"""
    # Détection Arabe
    if any('\u0600' <= char <= '\u06FF' for char in text):
        return 'ar'
    
    # Détection Anglais (Mots clés simples)
    common_en = ['the', 'is', 'my', 'where', 'how', 'what', 'hello', 'hi']
    if any(word in text.lower().split() for word in common_en):
        return 'en'
        
    return 'fr'

@app.route('/')
def home():
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    session_id = session.get('user_id', 'default')
    
    if not user_message:
        return jsonify({'error': 'Message vide'})
    
    # 1. Détecter la langue
    lang = detect_language(user_message)
    
    # 2. Obtenir la réponse
    result = chatbot.chat(user_message, session_id, lang=lang)
    
    # 3. Sauvegarder en base
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO conversations 
            (session_id, user_msg, bot_resp, intent, confidence, emotion, language) 
            VALUES (?,?,?,?,?,?,?)
        ''', (
            session_id, 
            user_message, 
            result['response'], 
            result['intent'], 
            result['confidence'],
            result['emotion'],
            lang
        ))
        
        # Récupérer l'ID de la conversation insérée
        conversation_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        # Ajouter l'ID à la réponse
        result['conversation_id'] = conversation_id
        result['language'] = lang
        
    except Exception as e:
        print(f"❌ Erreur DB: {e}")
        result['conversation_id'] = None
    
    return jsonify(result)

@app.route('/chat/feedback', methods=['POST'])
def feedback():
    """Enregistre le feedback utilisateur"""
    data = request.get_json()
    conversation_id = data.get('conversation_id')
    rating = data.get('rating', 3)  # 1-5
    
    if not conversation_id:
        return jsonify({'error': 'ID manquant'}), 400
    
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE conversations SET rating = ? WHERE id = ?',
            (rating, conversation_id)
        )
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        print(f"❌ Erreur feedback: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/stats')
def stats():
    """Stats pour le panneau latéral"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM conversations')
    total = cursor.fetchone()[0]
    
    cursor.execute('SELECT AVG(confidence) FROM conversations WHERE intent != "unknown"')
    avg = cursor.fetchone()[0] or 0
    
    cursor.execute('''
        SELECT intent, COUNT(*) as cnt 
        FROM conversations 
        WHERE intent != "unknown"
        GROUP BY intent 
        ORDER BY cnt DESC 
        LIMIT 5
    ''')
    top_intents = [{'intent': row[0], 'count': row[1]} for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({
        'total_conversations': total,
        'avg_confidence': avg,
        'top_intents': top_intents
    })

@app.route('/admin')
def admin():
    """Page dashboard administrateur"""
    return render_template('admin.html')

@app.route('/api/admin/stats')
def admin_stats():
    """Stats complètes pour le dashboard admin"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Total conversations
    cursor.execute('SELECT COUNT(*) FROM conversations')
    total = cursor.fetchone()[0]
    
    # Confiance moyenne
    cursor.execute('SELECT AVG(confidence) FROM conversations WHERE intent != "unknown"')
    avg_conf = cursor.fetchone()[0] or 0
    
    # Utilisateurs satisfaits (rating >= 4)
    cursor.execute('SELECT COUNT(*) FROM conversations WHERE rating >= 4')
    happy_users = cursor.fetchone()[0]
    
    # Conversations aujourd'hui
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute(
        'SELECT COUNT(*) FROM conversations WHERE DATE(timestamp) = ?', 
        (today,)
    )
    today_conv = cursor.fetchone()[0]
    
    # Top intentions
    cursor.execute('''
        SELECT intent, COUNT(*) as cnt 
        FROM conversations 
        WHERE intent != "unknown"
        GROUP BY intent 
        ORDER BY cnt DESC 
        LIMIT 5
    ''')
    top_intents = [{'intent': row[0], 'count': row[1]} for row in cursor.fetchall()]
    
    # Distribution des émotions
    cursor.execute('SELECT emotion, COUNT(*) FROM conversations GROUP BY emotion')
    emotions_data = dict(cursor.fetchall())
    emotions = {
        'happy': emotions_data.get('happy', 0),
        'neutral': emotions_data.get('neutral', 0),
        'frustrated': emotions_data.get('frustrated', 0)
    }
    
    # Timeline (7 derniers jours)
    timeline_labels = []
    timeline_data = []
    
    for i in range(6, -1, -1):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        timeline_labels.append(date)
        
        cursor.execute(
            'SELECT COUNT(*) FROM conversations WHERE DATE(timestamp) = ?',
            (date,)
        )
        count = cursor.fetchone()[0]
        timeline_data.append(count)
    
    conn.close()
    
    return jsonify({
        'total_conversations': total,
        'avg_confidence': avg_conf,
        'happy_users': happy_users,
        'today_conversations': today_conv,
        'top_intents': top_intents,
        'emotions': emotions,
        'timeline': {
            'labels': timeline_labels,
            'data': timeline_data
        }
    })

@app.route('/api/admin/conversations')
def get_conversations():
    """Liste des dernières conversations pour le tableau"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, timestamp, user_msg, bot_resp, intent, confidence, emotion 
        FROM conversations 
        ORDER BY id DESC 
        LIMIT 100
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    
    conversations = []
    for row in rows:
        conversations.append({
            'id': row[0],
            'timestamp': row[1],
            'user_message': row[2],
            'bot_response': row[3],
            'intent': row[4],
            'confidence': row[5],
            'emotion': row[6] or 'neutral'
        })
    
    return jsonify(conversations)

if __name__ == '__main__':
    init_db()
    print("\n🚀 Chatbot NLP démarré sur http://localhost:5000")
    print(" Dashboard admin : http://localhost:5000/admin\n")
    app.run(debug=True)