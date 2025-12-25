import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import random
from collections import deque

class ChatbotNLP:
    def __init__(self, intents_file='data/intents.json'):
        """Initialise le chatbot avec le modèle NLP"""
        print("🚀 Chargement du modèle NLP avec contexte conversationnel...")
        
        # Modèle léger
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Charger les intents
        with open(intents_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.intents = data['intents']
        
        # Préparer les patterns
        self.patterns = []
        self.pattern_to_intent = {}
        
        for intent in self.intents:
            for pattern in intent['patterns']:
                self.patterns.append(pattern)
                self.pattern_to_intent[pattern] = intent['tag']
        
        # Calculer les embeddings
        self.pattern_embeddings = self.model.encode(self.patterns)
        
        # 🆕 CONTEXTE CONVERSATIONNEL
        self.conversation_history = {}  # {session_id: deque([messages])}
        self.context_references = {
            'ça': ['celui-ci', 'cela', 'ça'],
            'ma commande': ['commande', 'colis', 'livraison'],
            'le produit': ['produit', 'article', 'item'],
            'retour': ['retourner', 'renvoyer', 'rembourser']
        }
        
        print("✅ Modèle prêt avec mémoire contextuelle !")
    
    def add_to_history(self, session_id, message, intent):
        """Ajoute un message à l'historique de la conversation"""
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = deque(maxlen=5)
        
        self.conversation_history[session_id].append({
            'message': message,
            'intent': intent,
            'timestamp': self._get_timestamp()
        })
    
    def get_context(self, session_id):
        """Récupère le contexte de la conversation"""
        if session_id in self.conversation_history:
            return list(self.conversation_history[session_id])
        return []
    
    def resolve_references(self, message, session_id):
        """Résout les références contextuelles (ça, celui-là, etc.)"""
        context = self.get_context(session_id)
        
        if not context:
            return message
        
        # Dernière intention
        last_intent = context[-1]['intent'] if context else None
        
        # Remplacer les pronoms par le contexte
        message_lower = message.lower()
        
        # Si "ça" ou "celui-là" et on parle de commande
        if any(ref in message_lower for ref in ['ça', 'celui-là', 'cela', 'celui-ci']):
            if last_intent in ['statut_commande', 'livraison']:
                message = message_lower.replace('ça', 'ma commande')
                message = message.replace('celui-là', 'ma commande')
            elif last_intent == 'retour_produit':
                message = message_lower.replace('ça', 'le retour')
        
        # Si question de suivi ("et pour", "combien", etc.)
        follow_up_keywords = ['et pour', 'combien', 'quand', 'comment', 'pourquoi']
        if any(kw in message_lower for kw in follow_up_keywords):
            if last_intent:
                # Ajouter le contexte au message
                context_hint = f"{message} {last_intent}"
                return context_hint
        
        return message
    
    def detect_emotion(self, message):
        """🆕 Détecte l'émotion dans le message"""
        message_lower = message.lower()
        
        # Mots positifs
        positive_words = ['merci', 'super', 'génial', 'parfait', 'excellent', 'content', 'heureux']
        # Mots négatifs/frustration
        negative_words = ['nul', 'mauvais', 'déçu', 'frustré', 'énervé', 'pas content', 'problème', 'erreur']
        # Mots urgents
        urgent_words = ['urgent', 'vite', 'rapidement', 'immédiatement', 'maintenant']
        
        positive_count = sum(1 for word in positive_words if word in message_lower)
        negative_count = sum(1 for word in negative_words if word in message_lower)
        urgent_count = sum(1 for word in urgent_words if word in message_lower)
        
        if negative_count >= 2 or urgent_count >= 1:
            return 'frustrated'
        elif positive_count >= 1:
            return 'happy'
        elif negative_count == 1:
            return 'concerned'
        else:
            return 'neutral'
    
    def get_intent(self, user_message, session_id=None):
        """Détermine l'intention avec résolution de contexte"""
        # Résoudre les références si session_id fourni
        if session_id:
            resolved_message = self.resolve_references(user_message, session_id)
        else:
            resolved_message = user_message
        
        # Encoder le message
        user_embedding = self.model.encode([resolved_message])
        
        # Calculer similarités
        similarities = cosine_similarity(user_embedding, self.pattern_embeddings)[0]
        best_match_idx = np.argmax(similarities)
        best_similarity = similarities[best_match_idx]
        
        if best_similarity < 0.5:
            return None, best_similarity
        
        best_pattern = self.patterns[best_match_idx]
        intent_tag = self.pattern_to_intent[best_pattern]
        
        return intent_tag, best_similarity
    
    def get_response(self, intent_tag, emotion='neutral'):
        """Récupère une réponse adaptée à l'émotion"""
        for intent in self.intents:
            if intent['tag'] == intent_tag:
                response = random.choice(intent['responses'])
                
                # 🆕 Adapter selon l'émotion
                if emotion == 'frustrated':
                    response = "Je comprends votre frustration. " + response + " Je peux vous mettre en contact avec un conseiller si nécessaire."
                elif emotion == 'happy':
                    response = response + " 😊 Ravi de vous aider !"
                elif emotion == 'concerned':
                    response = "Je vais faire de mon mieux pour vous aider. " + response
                
                return response
        
        return "Je ne suis pas sûr de comprendre. Pouvez-vous reformuler ?"
    
    def chat(self, user_message, session_id='default'):
        """Fonction principale avec contexte"""
        # Détecter l'émotion
        emotion = self.detect_emotion(user_message)
        
        # Détecter l'intention avec contexte
        intent, confidence = self.get_intent(user_message, session_id)
        
        # Ajouter à l'historique
        if intent:
            self.add_to_history(session_id, user_message, intent)
        
        # Réponse adaptée
        if intent is None:
            response = "Je ne suis pas sûr de comprendre votre question. Pouvez-vous la reformuler ou contacter notre support ?"
        else:
            response = self.get_response(intent, emotion)
        
        return {
            'response': response,
            'intent': intent or 'unknown',
            'confidence': float(confidence),
            'emotion': emotion,
            'context': self.get_context(session_id)
        }
    
    def _get_timestamp(self):
        """Obtient le timestamp actuel"""
        from datetime import datetime
        return datetime.now().isoformat()