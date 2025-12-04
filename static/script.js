const chatForm = document.getElementById('chatForm');
const userInput = document.getElementById('userInput');
const chatMessages = document.getElementById('chatMessages');
const sendBtn = document.getElementById('sendBtn');

// Fonction pour envoyer un message
async function sendMessage(message) {
    // Désactiver le bouton pendant l'envoi
    sendBtn.disabled = true;
    
    // Afficher le message de l'utilisateur
    addMessage(message, 'user');
    
    // Vider l'input
    userInput.value = '';
    
    // Afficher l'indicateur de saisie
    showTypingIndicator();
    
    try {
        // Envoyer au backend
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });
        
        const data = await response.json();
        
        // Retirer l'indicateur de saisie
        removeTypingIndicator();
        
        // Afficher la réponse du bot
        addMessage(data.response, 'bot');
        
        // Mettre à jour les stats
        updateStats();
        
    } catch (error) {
        removeTypingIndicator();
        addMessage('Désolé, une erreur est survenue. Veuillez réessayer.', 'bot');
        console.error('Erreur:', error);
    }
    
    // Réactiver le bouton
    sendBtn.disabled = false;
    userInput.focus();
}

// Ajouter un message au chat
function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = sender === 'bot' ? '🤖' : '👤';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    
    const paragraph = document.createElement('p');
    paragraph.textContent = text;
    
    const time = document.createElement('span');
    time.className = 'message-time';
    time.textContent = getCurrentTime();
    
    content.appendChild(paragraph);
    content.appendChild(time);
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Afficher l'indicateur de saisie
function showTypingIndicator() {
    const indicator = document.createElement('div');
    indicator.className = 'message bot-message';
    indicator.id = 'typingIndicator';
    indicator.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-content">
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>
    `;
    chatMessages.appendChild(indicator);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Retirer l'indicateur de saisie
function removeTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
        indicator.remove();
    }
}

// Obtenir l'heure actuelle
function getCurrentTime() {
    const now = new Date();
    return now.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
}

// Envoyer une suggestion
function sendSuggestion(message) {
    userInput.value = message;
    sendMessage(message);
}

// Mettre à jour les statistiques
async function updateStats() {
    try {
        const response = await fetch('/stats');
        const data = await response.json();
        
        document.getElementById('totalConv').textContent = data.total_conversations;
        document.getElementById('avgConf').textContent = (data.avg_confidence * 100).toFixed(0) + '%';
        
        const topIntents = document.getElementById('topIntents');
        topIntents.innerHTML = '<h4 style="margin: 15px 0 10px 0; font-size: 14px; color: #333;">Top Intentions</h4>';
        
        data.top_intents.forEach((item, index) => {
            const intentDiv = document.createElement('div');
            intentDiv.className = 'intent-item';
            intentDiv.innerHTML = `
                <span>${index + 1}. ${item.intent}</span>
                <span style="color: #667eea; font-weight: bold;">${item.count}</span>
            `;
            topIntents.appendChild(intentDiv);
        });
        
    } catch (error) {
        console.error('Erreur lors de la récupération des stats:', error);
    }
}

// Gestionnaire d'événement pour le formulaire
chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const message = userInput.value.trim();
    if (message) {
        sendMessage(message);
    }
});

// Permettre l'envoi avec Enter
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        chatForm.dispatchEvent(new Event('submit'));
    }
});

// Charger les stats au démarrage
updateStats();

// Mettre à jour les stats toutes les 30 secondes
setInterval(updateStats, 30000);