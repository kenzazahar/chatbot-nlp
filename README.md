# 🤖 Chatbot NLP - Service Client Intelligent

Un chatbot de service client utilisant le NLP (Natural Language Processing) avec une interface web moderne.

## 🎯 Fonctionnalités

- ✅ Compréhension du langage naturel en français
- ✅ Réponses intelligentes basées sur les intentions
- ✅ Interface web moderne et responsive
- ✅ Base de données SQLite pour historique
- ✅ Statistiques en temps réel
- ✅ Suggestions de questions rapides
- ✅ Animation de "typing indicator"

## 📋 Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- 2 GB d'espace disque (pour les modèles NLP)

## 🚀 Installation Rapide

### 1. Cloner ou télécharger le projet

```bash
git clone <votre-repo>
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

⏱️ **Temps d'installation : 5-10 minutes**

### 4. Lancer l'application

```bash
python app.py
```

🌐 Ouvrir dans le navigateur : **http://localhost:5000**

## 📁 Structure du Projet

```
chatbot-nlp/
├── app.py                      # Application Flask principale
├── requirements.txt            # Dépendances Python
├── database.db                 # Base de données SQLite (créée automatiquement)
│
├── data/
│   └── intents.json           # Intentions et réponses du chatbot
│
├── models/
│   └── chatbot_model.py       # Logique NLP du chatbot
│
├── templates/
│   └── index.html             # Interface web
│
└── static/
    ├── style.css              # Styles CSS
    └── script.js              # JavaScript frontend
```



## 📊 API Endpoints

### POST /chat
Envoyer un message au chatbot

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
  "confidence": 0.92
}
```

### GET /stats
Obtenir les statistiques

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


## 📈 Améliorations Futures

- [ ] Authentification utilisateur
- [ ] Support multilingue
- [ ] Intégration avec des APIs externes
- [ ] Apprentissage automatique des nouvelles réponses
- [ ] Export des conversations en CSV
- [ ] Dashboard d'administration


