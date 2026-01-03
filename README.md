# Chatbot NLP - Service Client Intelligent

Un système de chatbot intelligent basé sur le traitement du langage naturel (NLP) pour automatiser le support client. Le projet utilise des modèles de transformation de phrases pour comprendre les intentions des utilisateurs et fournir des réponses contextuelles appropriées.

## Table des matières

- [Caractéristiques](#caractéristiques)
- [Architecture](#architecture)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Structure du projet](#structure-du-projet)
- [API Documentation](#api-documentation)
- [Base de données](#base-de-données)
- [Personnalisation](#personnalisation)
- [Dashboard administrateur](#dashboard-administrateur)
- [Support multilingue](#support-multilingue)
- [Déploiement](#déploiement)
- [Maintenance](#maintenance)
- [Contribution](#contribution)
- [Licence](#licence)

## Caractéristiques

### Fonctionnalités principales

- **Compréhension du langage naturel** : Utilise le modèle SentenceTransformer pour analyser et comprendre les messages des utilisateurs
- **Détection d'intention** : Classification automatique des requêtes utilisateur en intentions prédéfinies
- **Analyse émotionnelle** : Détection basique des émotions (heureux, neutre, frustré)
- **Support multilingue** : Gestion du français, anglais et arabe
- **Mémoire conversationnelle** : Maintien du contexte sur les 5 derniers messages
- **Système de feedback** : Collecte des évaluations utilisateur sur la qualité des réponses
- **Auto-complétion** : Suggestions intelligentes pendant la frappe
- **Dashboard administrateur** : Interface complète de monitoring et d'analyse

### Interface utilisateur

- Design moderne et responsive
- Animations fluides et indicateurs de saisie
- Suggestions de questions rapides
- Retour visuel sur la langue détectée
- Interface épurée centrée sur la conversation

### Analytics et monitoring

- Statistiques en temps réel
- Graphiques de distribution des intentions
- Analyse des émotions utilisateur
- Timeline des conversations
- Export des données (CSV, JSON)
- Filtres et recherche avancée

## Architecture

Le système est construit sur une architecture Flask moderne avec les composants suivants :

```
Frontend (HTML/CSS/JS)
         ↓
    Flask Server
         ↓
    NLP Engine (SentenceTransformer)
         ↓
    SQLite Database
```

### Technologies utilisées

**Backend**
- Python 3.8+
- Flask (framework web)
- Flask-CORS (gestion des requêtes cross-origin)
- SentenceTransformers (modèle NLP)
- scikit-learn (calcul de similarité)
- SQLite (base de données)

**Frontend**
- HTML5
- CSS3 (avec animations)
- JavaScript vanilla
- Chart.js (visualisations)

**Modèle NLP**
- all-MiniLM-L6-v2 (384 dimensions)
- Similarité cosinus pour le matching d'intentions

## Prérequis

### Système

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- 2 GB d'espace disque libre (pour les modèles NLP)
- 4 GB de RAM minimum recommandé

### Connaissances

- Bases en Python
- Compréhension des API REST
- Notions de NLP (optionnel)

## Installation

### 1. Cloner le projet

```bash
git clone https://github.com/kenzazahar/chatbot-nlp.git
cd chatbot-nlp
```

### 2. Créer un environnement virtuel

**Windows**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

Temps estimé : 5-10 minutes selon votre connexion internet.

### 4. Initialiser la base de données

La base de données sera créée automatiquement au premier lancement.

```bash
python app.py
```

## Configuration

### Fichier de configuration principal

Le fichier `app.py` contient les paramètres principaux :

```python
app.secret_key = 'votre_clé_secrète'  # Changez cette valeur en production
DATABASE = 'database.db'
```

### Configuration des intentions

Le fichier `data/intents.json` définit les intentions reconnues par le chatbot :

```json
{
  "intents": [
    {
      "tag": "nom_intention",
      "patterns": {
        "fr": ["phrase1", "phrase2"],
        "en": ["phrase1", "phrase2"],
        "ar": ["phrase1", "phrase2"]
      },
      "responses": {
        "fr": ["réponse1", "réponse2"],
        "en": ["response1", "response2"],
        "ar": ["réponse1", "réponse2"]
      }
    }
  ]
}
```

### Paramètres du modèle NLP

Dans `models/chatbot_model.py` :

```python
# Seuil de confiance minimum
CONFIDENCE_THRESHOLD = 0.35

# Taille de l'historique conversationnel
HISTORY_SIZE = 5

# Modèle SentenceTransformer
MODEL_NAME = 'all-MiniLM-L6-v2'
```

## Utilisation

### Démarrage du serveur

```bash
python app.py
```

Le serveur démarre sur `http://localhost:5000`

### Accès aux interfaces

**Interface utilisateur**
```
http://localhost:5000
```

**Dashboard administrateur**
```
http://localhost:5000/admin
```

### Utilisation de l'interface chat

1. Tapez votre message dans la zone de saisie
2. Appuyez sur Entrée ou cliquez sur le bouton d'envoi
3. Le chatbot analyse votre message et répond
4. Évaluez la réponse avec les boutons de feedback

### Utilisation du dashboard

1. Accédez à `/admin`
2. Consultez les statistiques en temps réel
3. Filtrez les conversations par intention ou émotion
4. Exportez les données en CSV ou JSON
5. Analysez les graphiques de performance

## Structure du projet

```
chatbot-nlp/
│
├── app.py                          # Application Flask principale
├── requirements.txt                # Dépendances Python
├── database.db                     # Base de données SQLite
├── README.md                       # Documentation
│
├── data/
│   └── intents.json               # Définitions des intentions
│
├── models/
│   └── chatbot_model.py           # Logique NLP et traitement
│
├── templates/
│   ├── index.html                 # Interface utilisateur
│   └── admin.html                 # Dashboard administrateur
│
└── static/
    ├── style.css                  # Styles CSS (si séparés)
    └── script.js                  # JavaScript frontend (si séparé)
```

## API Documentation

### POST /chat

Envoie un message au chatbot.

**Request**
```json
{
  "message": "Où est ma commande ?"
}
```

**Response**
```json
{
  "response": "Pour vérifier le statut, j'ai besoin de votre numéro de commande.",
  "intent": "statut_commande",
  "confidence": 0.89,
  "emotion": "neutral",
  "language": "fr",
  "conversation_id": 123
}
```

### POST /chat/feedback

Enregistre l'évaluation d'une réponse.

**Request**
```json
{
  "conversation_id": 123,
  "rating": 5
}
```

**Response**
```json
{
  "success": true
}
```

### GET /stats

Récupère les statistiques globales.

**Response**
```json
{
  "total_conversations": 250,
  "avg_confidence": 0.87,
  "top_intents": [
    {"intent": "statut_commande", "count": 45},
    {"intent": "livraison", "count": 32}
  ]
}
```

### GET /api/admin/stats

Statistiques détaillées pour le dashboard.

**Response**
```json
{
  "total_conversations": 250,
  "avg_confidence": 0.87,
  "happy_users": 180,
  "today_conversations": 25,
  "top_intents": [...],
  "emotions": {
    "happy": 120,
    "neutral": 100,
    "frustrated": 30
  },
  "timeline": {
    "labels": ["2025-01-01", "2025-01-02", ...],
    "data": [15, 22, 18, ...]
  }
}
```

### GET /api/admin/conversations

Liste des conversations récentes.

**Response**
```json
[
  {
    "id": 123,
    "timestamp": "2025-01-03 14:30:00",
    "user_message": "Bonjour",
    "bot_response": "Bonjour ! Comment puis-je vous aider ?",
    "intent": "salutation",
    "confidence": 0.95,
    "emotion": "happy"
  }
]
```

## Base de données

### Schéma de la table `conversations`

```sql
CREATE TABLE conversations (
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
);
```

### Requêtes utiles

**Conversations du jour**
```sql
SELECT * FROM conversations 
WHERE DATE(timestamp) = DATE('now');
```

**Intentions les plus fréquentes**
```sql
SELECT intent, COUNT(*) as count 
FROM conversations 
GROUP BY intent 
ORDER BY count DESC;
```

**Taux de satisfaction**
```sql
SELECT 
    COUNT(CASE WHEN rating >= 4 THEN 1 END) * 100.0 / COUNT(*) as satisfaction_rate
FROM conversations 
WHERE rating IS NOT NULL;
```

## Personnalisation

### Ajouter de nouvelles intentions

1. Ouvrir `data/intents.json`
2. Ajouter une nouvelle entrée :

```json
{
  "tag": "nouvelle_intention",
  "patterns": {
    "fr": ["phrase exemple 1", "phrase exemple 2"],
    "en": ["example phrase 1", "example phrase 2"],
    "ar": ["مثال عبارة 1", "مثال عبارة 2"]
  },
  "responses": {
    "fr": ["Réponse en français"],
    "en": ["Response in English"],
    "ar": ["الرد بالعربية"]
  }
}
```

3. Redémarrer le serveur pour charger les nouvelles intentions

### Modifier le seuil de confiance

Dans `models/chatbot_model.py`, ligne 73 :

```python
if best_similarity < 0.35:  # Augmenter pour être plus strict
    return None, best_similarity
```

### Personnaliser l'interface

**Couleurs principales** (dans `templates/index.html`) :
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

**Messages de bienvenue** (dans le JavaScript) :
```javascript
addMessage(
    "Votre message personnalisé ici",
    'bot',
    'happy'
);
```

## Dashboard administrateur

### Fonctionnalités

**Statistiques en temps réel**
- Total des conversations
- Confiance moyenne du modèle
- Utilisateurs satisfaits (rating >= 4)
- Conversations du jour

**Visualisations**
- Graphique circulaire des intentions
- Distribution des émotions
- Timeline des 7 derniers jours

**Gestion des conversations**
- Table complète des conversations
- Recherche par mot-clé
- Filtres par intention et émotion
- Export CSV et JSON

### Rafraîchissement automatique

Le dashboard se met à jour automatiquement toutes les 30 secondes.

## Support multilingue

### Langues supportées

- Français (fr)
- Anglais (en)
- Arabe (ar)

### Détection automatique

La langue est détectée automatiquement en fonction :
- Des caractères utilisés (arabe)
- Des mots-clés communs (anglais)
- Par défaut : français

### Ajouter une nouvelle langue

1. Ajouter les patterns dans `intents.json`
2. Ajouter les réponses correspondantes
3. Mettre à jour la fonction `detect_language()` dans `app.py`


## Maintenance

### Sauvegarde de la base de données

```bash
# Copie simple
cp database.db database_backup_$(date +%Y%m%d).db

# Avec compression
tar -czf database_backup_$(date +%Y%m%d).tar.gz database.db
```

### Nettoyage des anciennes conversations

```python
# Script Python pour nettoyer les données anciennes
import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Supprimer les conversations de plus de 90 jours
cutoff_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
cursor.execute('DELETE FROM conversations WHERE timestamp < ?', (cutoff_date,))

conn.commit()
conn.close()
```

### Mise à jour du modèle

Pour changer le modèle NLP :

```python
# Dans models/chatbot_model.py
self.model = SentenceTransformer('nouveau-modele-name')
```

Modèles recommandés :
- `all-MiniLM-L6-v2` : Léger et rapide (384 dim)
- `paraphrase-multilingual-MiniLM-L12-v2` : Meilleur multilingue
- `all-mpnet-base-v2` : Plus précis mais plus lourd (768 dim)



## Crédits

Développé avec :
- SentenceTransformers par UKPLab
- Flask par Pallets
- Chart.js pour les visualisations

---

Version : 3.0.0  
Dernière mise à jour : 03 Janvier 2026