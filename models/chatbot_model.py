import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import random
from collections import deque
import os

class ChatbotNLP:
    def __init__(self, intents_file='data/intents.json'):
        """Initialise le chatbot avec le modèle NLP"""
        print(" Chargement du modèle NLP (cela peut prendre quelques secondes)...")
        
        # Modèle léger et rapide
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Charger les intents
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_path, intents_file)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.intents = data['intents']
        
        # Préparer les patterns en gérant le format multilingue
        self.patterns = []
        self.pattern_to_intent = {}
        
        for intent in self.intents:
            patterns_data = intent['patterns']
            
            # Liste temporaire pour stocker toutes les phrases de cet intent
            current_intent_patterns = []
            
            # Si le format est un dictionnaire {"fr": [], "en": []}
            if isinstance(patterns_data, dict):
                for lang in patterns_data:
                    current_intent_patterns.extend(patterns_data[lang])
            
            # Si le format est une liste simple ["text", "text"]
            elif isinstance(patterns_data, list):
                current_intent_patterns = patterns_data
            
            # On enregistre les patterns
            for pattern in current_intent_patterns:
                self.patterns.append(pattern)
                self.pattern_to_intent[pattern] = intent['tag']
        
        # Calculer les embeddings une seule fois au démarrage
        self.pattern_embeddings = self.model.encode(self.patterns)
        
        # Initialiser l'historique
        self.conversation_history = {}
        
        print(f"✅ Modèle prêt ! {len(self.patterns)} phrases apprises.")
    
    def add_to_history(self, session_id, message, intent):
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = deque(maxlen=5)
        
        self.conversation_history[session_id].append({
            'message': message,
            'intent': intent
        })
    
    def get_context(self, session_id):
        if session_id in self.conversation_history:
            return list(self.conversation_history[session_id])
        return []

    def detect_emotion(self, message):
        """Détection basique d'émotion"""
        msg = message.lower()
        if any(w in msg for w in ['merci', 'super', 'génial', 'top', 'cool']):
            return 'happy'
        if any(w in msg for w in ['nul', 'mauvais', 'déçu', 'problème', 'erreur', 'pas content']):
            return 'frustrated'
        return 'neutral'
    
    def get_intent(self, user_message, session_id=None):
        """Détermine l'intention"""
        # Encoder le message utilisateur
        user_embedding = self.model.encode([user_message])
        
        # Calculer similarités
        similarities = cosine_similarity(user_embedding, self.pattern_embeddings)[0]
        
        # Trouver le meilleur match
        best_match_idx = np.argmax(similarities)
        best_similarity = similarities[best_match_idx]
        
        # Debug : afficher ce que le bot a compris dans la console
        best_pattern = self.patterns[best_match_idx]
        # print(f"DEBUG: Message='{user_message}' | Match='{best_pattern}' | Score={best_similarity:.2f}")
        
        # --- CORRECTION SEUIL ---
        # On baisse le seuil à 0.35 pour être plus tolérant
        if best_similarity < 0.35:
            return None, best_similarity
        
        intent_tag = self.pattern_to_intent[best_pattern]
        return intent_tag, best_similarity
    
    def get_response(self, intent_tag, emotion='neutral', lang='fr'):
        """Récupère une réponse"""
        for intent in self.intents:
            if intent['tag'] == intent_tag:
                # Gestion de la réponse selon la langue détectée (par défaut FR)
                responses_data = intent['responses']
                
                if isinstance(responses_data, dict):
                    possible_responses = responses_data.get(lang, responses_data.get('fr', []))
                else:
                    possible_responses = responses_data
                
                response = random.choice(possible_responses)
                
                # Adaptation émotionnelle simple (seulement en FR pour l'exemple)
                if lang == 'fr':
                    if emotion == 'frustrated':
                        response = "Je suis navré d'entendre ça. " + response
                    elif emotion == 'happy':
                        response = "Avec plaisir ! " + response
                
                return response
        
        return "Désolé, je n'ai pas de réponse pour ça."
    
    def chat(self, user_message, session_id='default', lang='fr'):
        emotion = self.detect_emotion(user_message)
        intent, confidence = self.get_intent(user_message, session_id)
        
        if intent:
            self.add_to_history(session_id, user_message, intent)
            response = self.get_response(intent, emotion, lang)
        else:
            # Messages d'erreur par langue
            error_msgs = {
                'fr': "Je ne suis pas sûr de comprendre. Pouvez-vous reformuler ?",
                'en': "I'm not sure I understand. Can you rephrase?",
                'ar': "لست متأكدا أنني أفهم. هل يمكنك إعادة الصياغة؟"
            }
            response = error_msgs.get(lang, error_msgs['fr'])
        
        return {
            'response': response,
            'intent': intent or 'unknown',
            'confidence': float(confidence),
            'emotion': emotion
        }