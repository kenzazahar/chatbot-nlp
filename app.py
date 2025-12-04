from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from models.chatbot_model import ChatbotNLP
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# Initialiser le chatbot
chatbot = ChatbotNLP()

# Configuration de la base de données
DATABASE = 'database.db'

def init_db():
    """Initialise la base de données"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT NOT NULL,
            bot_response TEXT NOT NULL,
            intent TEXT,
            confidence REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Base de données initialisée")

def save_conversation(user_msg, bot_resp, intent, confidence):
    """Sauvegarde une conversation dans la DB"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO conversations (user_message, bot_response, intent, confidence)
        VALUES (?, ?, ?, ?)
    ''', (user_msg, bot_resp, intent, confidence))
    
    conn.commit()
    conn.close()

@app.route('/')
def home():
    """Page d'accueil"""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Endpoint pour le chat"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'Message vide'}), 400
        
        # Obtenir la réponse du chatbot
        result = chatbot.chat(user_message)
        
        # Sauvegarder dans la DB
        save_conversation(
            user_message,
            result['response'],
            result['intent'],
            result['confidence']
        )
        
        return jsonify(result)
    
    except Exception as e:
        print(f"Erreur: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/stats')
def stats():
    """Statistiques des conversations"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Nombre total de conversations
    cursor.execute('SELECT COUNT(*) FROM conversations')
    total = cursor.fetchone()[0]
    
    # Intentions les plus fréquentes
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

if __name__ == '__main__':
    # Initialiser la DB au démarrage
    init_db()
    
    print("\n" + "="*50)
    print("🤖 CHATBOT NLP DÉMARRÉ")
    print("="*50)
    print("📍 URL: http://localhost:5000")
    print("="*50 + "\n")
    
    app.run(debug=True, port=5000)