from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from models.chatbot_model import ChatbotNLP
import sqlite3
from datetime import datetime, timedelta
import os
import uuid
import json

app = Flask(__name__)
app.secret_key = 'votre-cle-secrete-super-securisee'
CORS(app)

# Initialiser le chatbot
chatbot = ChatbotNLP()

# Configuration de la base de données
DATABASE = 'database.db'

def init_db():
    """Initialise la base de données avec tables améliorées"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Table conversations avec colonnes supplémentaires
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            user_message TEXT NOT NULL,
            bot_response TEXT NOT NULL,
            intent TEXT,
            confidence REAL,
            emotion TEXT,
            language TEXT DEFAULT 'fr',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table utilisateurs (pour auth future)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table feedback
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER,
            rating INTEGER CHECK(rating >= 1 AND rating <= 5),
            comment TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Base de données initialisée avec succès")

def save_conversation(session_id, user_msg, bot_resp, intent, confidence, emotion, language='fr'):
    """Sauvegarde une conversation enrichie dans la DB"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO conversations 
        (session_id, user_message, bot_response, intent, confidence, emotion, language)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (session_id, user_msg, bot_resp, intent, confidence, emotion, language))
    
    conn.commit()
    conversation_id = cursor.lastrowid
    conn.close()
    
    return conversation_id

def detect_language(text):
    """Détection simple de la langue"""
    # Mots clés par langue
    fr_keywords = ['bonjour', 'merci', 'comment', 'pourquoi', 'ou', 'est']
    en_keywords = ['hello', 'thank', 'how', 'why', 'where', 'is']
    ar_keywords = ['مرحبا', 'شكرا', 'كيف', 'لماذا', 'أين']
    
    text_lower = text.lower()
    
    fr_count = sum(1 for kw in fr_keywords if kw in text_lower)
    en_count = sum(1 for kw in en_keywords if kw in text_lower)
    
    # Détection arabe par unicode
    ar_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
    
    if ar_chars > 3:
        return 'ar'
    elif en_count > fr_count:
        return 'en'
    else:
        return 'fr'

@app.route('/')
def home():
    """Page d'accueil"""
    # Générer un ID de session unique
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return render_template('index.html')

@app.route('/admin')
def admin():
    """Page admin"""
    return render_template('admin.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Endpoint pour le chat avec contexte"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'Message vide'}), 400
        
        # Obtenir ou créer session_id
        session_id = session.get('session_id', str(uuid.uuid4()))
        session['session_id'] = session_id
        
        # Détecter la langue
        language = detect_language(user_message)
        
        # Obtenir la réponse du chatbot avec contexte
        result = chatbot.chat(user_message, session_id)
        
        # Sauvegarder dans la DB
        conversation_id = save_conversation(
            session_id,
            user_message,
            result['response'],
            result['intent'],
            result['confidence'],
            result['emotion'],
            language
        )
        
        result['conversation_id'] = conversation_id
        result['language'] = language
        
        return jsonify(result)
    
    except Exception as e:
        print(f"Erreur: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/chat/suggestions', methods=['POST'])
def get_suggestions():
    """🆕 Obtenir des suggestions de questions"""
    try:
        data = request.get_json()
        current_message = data.get('message', '')
        
        # Suggestions basées sur les intentions populaires
        suggestions = []
        
        if len(current_message) < 3:
            # Suggestions générales
            suggestions = [
                "Où est ma commande ?",
                "Comment faire un retour ?",
                "Modes de paiement",
                "Délai de livraison"
            ]
        else:
            # Recherche dans les patterns
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT DISTINCT user_message 
                FROM conversations 
                WHERE user_message LIKE ? 
                LIMIT 5
            ''', (f'%{current_message}%',))
            
            results = cursor.fetchall()
            suggestions = [r[0] for r in results]
            conn.close()
        
        return jsonify({'suggestions': suggestions})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat/feedback', methods=['POST'])
def submit_feedback():
    """🆕 Enregistrer le feedback utilisateur"""
    try:
        data = request.get_json()
        conversation_id = data.get('conversation_id')
        rating = data.get('rating')
        comment = data.get('comment', '')
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO feedback (conversation_id, rating, comment)
            VALUES (?, ?, ?)
        ''', (conversation_id, rating, comment))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stats')
def stats():
    """Statistiques basiques"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Total conversations
    cursor.execute('SELECT COUNT(*) FROM conversations')
    total = cursor.fetchone()[0]
    
    # Intentions populaires
    cursor.execute('''
        SELECT intent, COUNT(*) as count 
        FROM conversations 
        WHERE intent != 'unknown'
        GROUP BY intent 
        ORDER BY count DESC 
        LIMIT 5
    ''')
    top_intents = cursor.fetchall()
    
    # Confiance moyenne
    cursor.execute('SELECT AVG(confidence) FROM conversations WHERE intent != "unknown"')
    avg_confidence = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return jsonify({
        'total_conversations': total,
        'top_intents': [{'intent': i[0], 'count': i[1]} for i in top_intents],
        'avg_confidence': round(avg_confidence, 2)
    })

@app.route('/api/admin/stats')
def admin_stats():
    """🆕 Stats complètes pour le dashboard admin"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Stats générales
    cursor.execute('SELECT COUNT(*) FROM conversations')
    total = cursor.fetchone()[0]
    
    cursor.execute('SELECT AVG(confidence) FROM conversations WHERE intent != "unknown"')
    avg_confidence = cursor.fetchone()[0] or 0
    
    # Utilisateurs satisfaits (émotions happy)
    cursor.execute('SELECT COUNT(*) FROM conversations WHERE emotion = "happy"')
    happy_users = cursor.fetchone()[0]
    
    # Conversations aujourd'hui
    today = datetime.now().date()
    cursor.execute('SELECT COUNT(*) FROM conversations WHERE DATE(timestamp) = ?', (today,))
    today_conv = cursor.fetchone()[0]
    
    # Top intentions
    cursor.execute('''
        SELECT intent, COUNT(*) as count 
        FROM conversations 
        WHERE intent != 'unknown'
        GROUP BY intent 
        ORDER BY count DESC 
        LIMIT 5
    ''')
    top_intents = [{'intent': i[0], 'count': i[1]} for i in cursor.fetchall()]
    
    # Distribution des émotions
    cursor.execute('''
        SELECT emotion, COUNT(*) as count 
        FROM conversations 
        GROUP BY emotion
    ''')
    emotions_data = cursor.fetchall()
    emotions = {
        'happy': 0,
        'neutral': 0,
        'frustrated': 0,
        'concerned': 0
    }
    for emotion, count in emotions_data:
        if emotion in emotions:
            emotions[emotion] = count
    
    # Timeline (7 derniers jours)
    cursor.execute('''
        SELECT DATE(timestamp) as day, COUNT(*) as count
        FROM conversations
        WHERE timestamp >= datetime('now', '-7 days')
        GROUP BY DATE(timestamp)
        ORDER BY day
    ''')
    timeline_data = cursor.fetchall()
    timeline = {
        'labels': [row[0] for row in timeline_data],
        'data': [row[1] for row in timeline_data]
    }
    
    conn.close()
    
    return jsonify({
        'total_conversations': total,
        'avg_confidence': avg_confidence,
        'happy_users': happy_users,
        'today_conversations': today_conv,
        'top_intents': top_intents,
        'emotions': emotions,
        'timeline': timeline
    })

@app.route('/api/admin/conversations')
def admin_conversations():
    """🆕 Liste complète des conversations pour admin"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            id, session_id, user_message, bot_response, 
            intent, confidence, emotion, language, timestamp
        FROM conversations
        ORDER BY timestamp DESC
        LIMIT 100
    ''')
    
    conversations = []
    for row in cursor.fetchall():
        conversations.append({
            'id': row[0],
            'session_id': row[1],
            'user_message': row[2],
            'bot_response': row[3],
            'intent': row[4],
            'confidence': row[5],
            'emotion': row[6],
            'language': row[7],
            'timestamp': row[8]
        })
    
    conn.close()
    return jsonify(conversations)

if __name__ == '__main__':
    # Initialiser la DB
    init_db()
    
    print("\n" + "="*60)
    print("🤖 CHATBOT NLP - VERSION AMÉLIORÉE")
    print("="*60)
    print("✨ Nouvelles fonctionnalités:")
    print("   • Contexte conversationnel")
    print("   • Détection d'émotions")
    print("   • Support multilingue (FR/EN/AR)")
    print("   • Dashboard admin complet")
    print("   • Suggestions intelligentes")
    print("="*60)
    print("📍 Interface utilisateur: http://localhost:5000")
    print("📊 Dashboard admin: http://localhost:5000/admin")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5000)