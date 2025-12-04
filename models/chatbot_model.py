import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import random

class ChatbotNLP:
    def __init__(self, intents_file='data/intents.json'):
        """Initialise le chatbot avec le modèle NLP"""
        print("🚀 Chargement du modèle NLP (version légère)...")
        
        # MODÈLE PLUS LÉGER : all-MiniLM-L6-v2 (seulement 80MB au lieu de 470MB)
        # Parfait pour le français aussi !
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            print("✅ Modèle all-MiniLM-L6-v2 chargé (80MB)")
        except Exception as e:
            print(f"⚠️ Erreur de téléchargement : {e}")
            print("🔄 Tentative avec un modèle encore plus léger...")
            # Fallback vers un modèle minimaliste
            self.model = SentenceTransformer('paraphrase-MiniLM-L3-v2')
            print("✅ Modèle paraphrase-MiniLM-L3-v2 chargé (61MB)")
        
        # Charger les intents
        with open(intents_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.intents = data['intents']
        
        # Préparer les patterns et leurs embeddings
        self.patterns = []
        self.pattern_to_intent = {}
        
        for intent in self.intents:
            for pattern in intent['patterns']:
                self.patterns.append(pattern)
                self.pattern_to_intent[pattern] = intent['tag']
        
        # Calculer les embeddings de tous les patterns
        print("📊 Calcul des embeddings...")
        self.pattern_embeddings = self.model.encode(self.patterns)
        print("✅ Modèle prêt !")
    
    def get_intent(self, user_message):
        """Détermine l'intention de l'utilisateur"""
        # Encoder le message de l'utilisateur
        user_embedding = self.model.encode([user_message])
        
        # Calculer la similarité avec tous les patterns
        similarities = cosine_similarity(user_embedding, self.pattern_embeddings)[0]
        
        # Trouver le pattern le plus similaire
        best_match_idx = np.argmax(similarities)
        best_similarity = similarities[best_match_idx]
        
        # Seuil de confiance minimum
        if best_similarity < 0.5:
            return None, best_similarity
        
        # Retourner l'intent correspondant
        best_pattern = self.patterns[best_match_idx]
        intent_tag = self.pattern_to_intent[best_pattern]
        
        return intent_tag, best_similarity
    
    def get_response(self, intent_tag):
        """Récupère une réponse pour l'intent donné"""
        for intent in self.intents:
            if intent['tag'] == intent_tag:
                return random.choice(intent['responses'])
        
        return "Je ne suis pas sûr de comprendre. Pouvez-vous reformuler ?"
    
    def chat(self, user_message):
        """Fonction principale pour traiter un message"""
        # Détecter l'intention
        intent, confidence = self.get_intent(user_message)
        
        # Si pas d'intention claire
        if intent is None:
            return {
                'response': "Je ne suis pas sûr de comprendre votre question. Pouvez-vous la reformuler ou contacter notre support ?",
                'intent': 'unknown',
                'confidence': float(confidence)
            }
        
        # Obtenir la réponse
        response = self.get_response(intent)
        
        return {
            'response': response,
            'intent': intent,
            'confidence': float(confidence)
        }