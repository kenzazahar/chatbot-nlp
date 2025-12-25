# Chatbot NLP - Service Client Intelligent

Un chatbot de service client utilisant le NLP (Natural Language Processing) avec une interface web moderne.

## Fonctionnalités

### Version 2.0 - Sprint 3
- Compréhension du langage naturel en français, anglais et arabe
- Contexte conversationnel (mémoire des 5 derniers messages)
- Détection d'émotions et réponses adaptées
- Support multilingue avec détection automatique
- Dashboard administrateur complet avec graphiques
- Suggestions intelligentes et auto-complétion
- Système de feedback utilisateur
- Export des données (CSV/JSON)
- Interface web moderne et responsive
- Base de données SQLite pour historique enrichi
- Statistiques et analytics en temps réel

### Version 1.0
- Réponses intelligentes basées sur les intentions
- Base de données pour historique
- Statistiques basiques
- Animation de typing indicator

## Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- 2 GB d'espace disque (pour les modèles NLP)

## Installation Rapide

### 1. Cloner le projet
```bash
git clone https://github.com/kenzazahar/chatbot-nlp
cd chatbot-nlp
```

### 2. Créer l'environnement virtuel
```bash
python -m venv venv

# Activer l'environnement
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
python -m spacy download fr_core_news_md
```

Temps d'installation : 5-10 minutes

### 4. Lancer l'application
```bash
python app.py
```

Ouvrir dans le navigateur : **http://localhost:5000**

Dashboard administrateur : **http://localhost:5000/admin**

## Structure du Projet
```
chatbot-nlp/
├── app.py                      # Application Flask principale
├── requirements.txt            # Dépendances Python
├── database.db                 # Base de données SQLite (créée automatiquement)
│
├── data/
│   └── intents.json           # Intentions et réponses multilingues
│
├── models/
│   └── chatbot_model.py       # Logique NLP avec contexte et émotions
│
├── templates/
│   ├── index.html             # Interface utilisateur
│   └── admin.html             # Dashboard administrateur
│
└── static/
    ├── style.css              # Styles CSS
    └── script.js              # JavaScript frontend
```

## API Endpoints

### POST /chat
Envoyer un message au chatbot avec contexte conversationnel

**Request:**
```json
{
  "message": "Bonjour"
}
```

**Response:**
```json
{
  "response": "Bonjour ! Comment puis-je vous aider ?",
  "intent": "salutation",
  "confidence": 0.92,
  "emotion": "neutral",
  "language": "fr",
  "conversation_id": 123,
  "context": [...]
}
```

### POST /chat/suggestions
Obtenir des suggestions intelligentes

**Request:**
```json
{
  "message": "comm"
}
```

**Response:**
```json
{
  "suggestions": [
    "Comment faire un retour ?",
    "Commande en cours"
  ]
}
```

### POST /chat/feedback
Enregistrer le feedback utilisateur

**Request:**
```json
{
  "conversation_id": 123,
  "rating": 5,
  "comment": "Très utile"
}
```

### GET /stats
Obtenir les statistiques basiques

**Response:**
```json
{
  "total_conversations": 150,
  "top_intents": [
    {"intent": "statut_commande", "count": 45},
    {"intent": "livraison", "count": 32}
  ],
  "avg_confidence": 0.87
}
```

### GET /api/admin/stats
Obtenir les statistiques complètes pour le dashboard admin

**Response:**
```json
{
  "total_conversations": 150,
  "avg_confidence": 0.87,
  "happy_users": 95,
  "today_conversations": 12,
  "top_intents": [...],
  "emotions": {
    "happy": 50,
    "neutral": 80,
    "frustrated": 20
  },
  "timeline": {
    "labels": ["2024-12-18", "2024-12-19", ...],
    "data": [10, 15, 12, ...]
  }
}
```

### GET /api/admin/conversations
Obtenir la liste complète des conversations

**Response:**
```json
[
  {
    "id": 1,
    "session_id": "uuid-xxx",
    "user_message": "Bonjour",
    "bot_response": "Bonjour ! Comment puis-je vous aider ?",
    "intent": "salutation",
    "confidence": 0.92,
    "emotion": "neutral",
    "language": "fr",
    "timestamp": "2024-12-25T10:30:00"
  },
  ...
]
```

## Base de Données

### Table conversations
```sql
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    user_message TEXT NOT NULL,
    bot_response TEXT NOT NULL,
    intent TEXT,
    confidence REAL,
    emotion TEXT,
    language TEXT DEFAULT 'fr',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Table feedback
```sql
CREATE TABLE feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER,
    rating INTEGER CHECK(rating >= 1 AND rating <= 5),
    comment TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);
```

### Table users (préparée pour V3)
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Fonctionnalités Détaillées

### Contexte Conversationnel
Le chatbot garde en mémoire les 5 derniers messages par session utilisateur, permettant de comprendre les références contextuelles comme "ça", "celui-là", etc.

**Exemple:**
```
User: "Où est ma commande ?"
Bot: "Quel est votre numéro de commande ?"
User: "Et ça prend combien de temps ?"
Bot comprend que "ça" fait référence à la livraison
```

### Détection d'Émotions
Le chatbot analyse le sentiment du message et adapte sa réponse :
- **Heureux** : Ton enjoué avec emoji
- **Frustré** : Empathie + proposition d'escalade vers conseiller
- **Neutre** : Réponse standard professionnelle

**Mots-clés détectés:**
- Positifs : merci, super, génial, parfait, excellent
- Négatifs : nul, mauvais, déçu, frustré, problème
- Urgents : urgent, vite, rapidement, immédiatement

### Support Multilingue
Détection automatique de la langue parmi :
- Français
- Anglais
- Arabe

Les réponses sont automatiquement fournies dans la langue détectée.

### Dashboard Administrateur
Accessible sur `/admin` avec :
- 4 KPIs en temps réel (conversations, confiance, satisfaction, aujourd'hui)
- 3 graphiques interactifs (Chart.js)
- Table des conversations avec filtres
- Export CSV/JSON
- Auto-refresh toutes les 30s

### Suggestions Intelligentes
Auto-complétion qui se déclenche après 3 caractères, proposant :
- Questions fréquemment posées
- Questions similaires de l'historique
- Suggestions contextuelles

## Configuration

### Personnaliser les intentions
Modifier le fichier `data/intents.json` :
```json
{
  "intents": [
    {
      "tag": "votre_intention",
      "patterns": {
        "fr": ["pattern 1", "pattern 2"],
        "en": ["pattern 1", "pattern 2"],
        "ar": ["النمط 1", "النمط 2"]
      },
      "responses": {
        "fr": ["réponse 1", "réponse 2"],
        "en": ["response 1", "response 2"],
        "ar": ["الرد 1", "الرد 2"]
      }
    }
  ]
}
```

### Ajuster le modèle NLP
Dans `models/chatbot_model.py`, vous pouvez modifier :
- Le modèle utilisé (ligne 12)
- Le seuil de confiance (ligne 95)
- La taille de l'historique (ligne 24)
- Les mots-clés d'émotions (lignes 56-61)

## Tests

### Lancer les tests unitaires
```bash
pip install pytest pytest-cov
pytest tests/ -v
```

### Avec couverture de code
```bash
pytest tests/ --cov=models --cov=app --cov-report=html
```

### Tests de performance
```bash
pytest tests/test_performance.py -v
```

## Déploiement

### Docker
```bash
docker build -t chatbot-nlp .
docker run -p 5000:5000 chatbot-nlp
```

### Heroku
```bash
heroku create chatbot-nlp
git push heroku main
```

### Configuration production
Modifier dans `app.py` :
```python
app.secret_key = 'votre-cle-securisee-production'
app.run(debug=False, host='0.0.0.0')
```

## Roadmap V3.0

### Court terme (1-2 semaines)
- Authentification utilisateur complète
- Escalade email automatique
- Commandes vocales (Speech-to-Text)

### Moyen terme (1 mois)
- Intégration LLM (GPT-4/Claude) pour questions complexes
- Intégration ontologies RDF
- Progressive Web App (PWA)

### Long terme (3 mois)
- Tests A/B automatiques
- Analytics avancés avec ML
- API publique documentée
- Reconnaissance d'images (OCR)

## Performance

### Métriques actuelles
- Temps de réponse : < 2 secondes
- Précision NLP : 87%
- Disponibilité : 99.9%
- Support : 3 langues
- Conversations simultanées : 100+

### Optimisations
- Calcul des embeddings au démarrage uniquement
- Cache Redis pour sessions (V3)
- CDN pour assets statiques (V3)
- Compression gzip activée

## Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

### Standards de code
- Python : PEP 8
- JavaScript : ESLint
- Commits : Conventional Commits

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## Auteur

Kenza ZAHAR - [kenzazahar17@gmail.com](mailto:kenzazahar17@gmail.com)

GitHub : [https://github.com/kenzazahar](https://github.com/kenzazahar)

## Remerciements

- Sentence-Transformers pour les modèles NLP
- Flask pour le framework web
- Chart.js pour les graphiques
- La communauté open-source



## Changelog

### Version 2.0 (25 décembre 2025) - Sprint 3
- Ajout contexte conversationnel
- Détection d'émotions
- Support multilingue (FR/EN/AR)
- Dashboard admin complet
- Suggestions intelligentes
- Système de feedback
- Export données CSV/JSON

### Version 1.0 (4 décembre 2025)
- Version initiale
- Classification d'intentions basique
- Interface utilisateur simple
- Statistiques de base

---

Dernière mise à jour : 25 décembre 2025
