const chatForm = document.getElementById('chatForm');
const userInput = document.getElementById('userInput');
const chatMessages = document.getElementById('chatMessages');
const sendBtn = document.getElementById('sendBtn');

let lastConversationId = null;
let typingTimeout = null;

// 🆕 Auto-complétion et suggestions
userInput.addEventListener('input', async (e) => {
    clearTimeout(typingTimeout);
    
    const message = e.target.value;
    
    if (message.length >= 3) {
        typingTimeout = setTimeout(async () => {
            await fetchSuggestions(message);
        }, 300);
    } else {
        hideSuggestions();
    }
});

async function fetchSuggestions(message) {
    try {
        const response = await fetch('/chat/suggestions', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });
        
        const data = await response.json();
        
        if (data.suggestions && data.suggestions.length > 0) {
            showSuggestions(data.suggestions);
        }
    } catch (error) {
        console.error('Erreur suggestions:', error);
    }
}

function showSuggestions(suggestions) {
    let suggestionsDiv = document.getElementById('autoSuggestions');
    
    if (!suggestionsDiv) {
        suggestionsDiv = document.createElement('div');
        suggestionsDiv.id = 'autoSuggestions';
        suggestionsDiv.style.cssText = `
            position: absolute;
            bottom: 100%;
            left: 0;
            right: 0;
            background: white;
            border-radius: 15px 15px 0 0;
            box-shadow: 0 -5px 15px rgba(0,0,0,0.1);
            max-height: 200px;
            overflow-y: auto;
            z-index: 100;
        `;
        document.querySelector('.chat-input-container').appendChild(suggestionsDiv);
    }
    
    suggestionsDiv.innerHTML = suggestions.map(s => `
        <div class="suggestion-item" onclick="applySuggestion('${s.replace(/'/g, "\\'")}')">
            💡 ${s}
        </div>
    `).join('');
    
    // Ajouter les styles
    if (!document.getElementById('suggestionStyles')) {
        const style = document.createElement('style');
        style.id = 'suggestionStyles';
        style.textContent = `
            .suggestion-item {
                padding: 12px 20px;
                cursor: pointer;
                transition: background 0.2s;
                border-bottom: 1px solid #f0f0f0;
            }
            .suggestion-item:hover {
                background: #f8f9fa;
            }
            .suggestion-item:last-child {
                border-bottom: none;
            }
        `;
        document.head.appendChild(style);
    }
}

function hideSuggestions() {
    const suggestionsDiv = document.getElementById('autoSuggestions');
    if (suggestionsDiv) {
        suggestionsDiv.remove();
    }
}

function applySuggestion(text) {
    userInput.value = text;
    hideSuggestions();
    userInput.focus();
}

// Fonction pour envoyer un message avec émotions
async function sendMessage(message) {
    sendBtn.disabled = true;
    hideSuggestions();
    
    addMessage(message, 'user');
    userInput.value = '';
    
    showTypingIndicator();
    
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });
        
        const data = await response.json();
        
        removeTypingIndicator();
        
        // Afficher la réponse avec émotion
        addMessage(data.response, 'bot', data.emotion);
        
        // Sauvegarder l'ID pour le feedback
        lastConversationId = data.conversation_id;
        
        // Afficher le bouton de feedback
        showFeedbackButton();
        
        // Afficher l'indicateur de langue si différent du français
        if (data.language && data.language !== 'fr') {
            showLanguageIndicator(data.language);
        }
        
        // 🆕 Afficher le contexte (debug mode)
        if (data.context && data.context.length > 0) {
            console.log('📝 Contexte conversationnel:', data.context);
        }
        
        updateStats();
        
    } catch (error) {
        removeTypingIndicator();
        addMessage('Désolé, une erreur est survenue. Veuillez réessayer.', 'bot');
        console.error('Erreur:', error);
    }
    
    sendBtn.disabled = false;
    userInput.focus();
}

function addMessage(text, sender, emotion = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    // Animation d'entrée
    messageDiv.style.opacity = '0';
    messageDiv.style.transform = 'translateY(10px)';
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    
    // Avatar avec émotion pour le bot
    if (sender === 'bot' && emotion) {
        const emotionIcons = {
            'happy': '🤖😊',
            'neutral': '🤖',
            'frustrated': '🤖😟',
            'concerned': '🤖🤔'
        };
        avatar.textContent = emotionIcons[emotion] || '🤖';
    } else {
        avatar.textContent = sender === 'bot' ? '🤖' : '👤';
    }
    
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
    
    // Animation
    setTimeout(() => {
        messageDiv.style.transition = 'all 0.3s ease';
        messageDiv.style.opacity = '1';
        messageDiv.style.transform = 'translateY(0)';
    }, 10);
    
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

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

function removeTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
        indicator.remove();
    }
}

function getCurrentTime() {
    const now = new Date();
    return now.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
}

function sendSuggestion(message) {
    userInput.value = message;
    sendMessage(message);
}

// 🆕 Système de feedback
function showFeedbackButton() {
    // Supprimer l'ancien bouton s'il existe
    const oldFeedback = document.getElementById('feedbackContainer');
    if (oldFeedback) oldFeedback.remove();
    
    const feedbackDiv = document.createElement('div');
    feedbackDiv.id = 'feedbackContainer';
    feedbackDiv.style.cssText = `
        padding: 15px;
        margin: 10px 20px;
        background: #f8f9fa;
        border-radius: 15px;
        text-align: center;
    `;
    
    feedbackDiv.innerHTML = `
        <p style="margin-bottom: 10px; color: #666; font-size: 14px;">
            Cette réponse vous a-t-elle aidé ?
        </p>
        <div style="display: flex; gap: 10px; justify-content: center;">
            <button onclick="submitFeedback(5)" class="feedback-btn">👍 Oui</button>
            <button onclick="submitFeedback(1)" class="feedback-btn">👎 Non</button>
        </div>
    `;
    
    chatMessages.appendChild(feedbackDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Ajouter les styles
    if (!document.getElementById('feedbackStyles')) {
        const style = document.createElement('style');
        style.id = 'feedbackStyles';
        style.textContent = `
            .feedback-btn {
                padding: 8px 20px;
                border: 2px solid #667eea;
                border-radius: 20px;
                background: white;
                color: #667eea;
                cursor: pointer;
                font-size: 14px;
                transition: all 0.3s;
            }
            .feedback-btn:hover {
                background: #667eea;
                color: white;
                transform: scale(1.05);
            }
        `;
        document.head.appendChild(style);
    }
}

async function submitFeedback(rating) {
    try {
        await fetch('/chat/feedback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                conversation_id: lastConversationId,
                rating: rating
            })
        });
        
        const feedbackDiv = document.getElementById('feedbackContainer');
        if (feedbackDiv) {
            feedbackDiv.innerHTML = `
                <p style="color: #4caf50; font-weight: bold;">
                    ✓ Merci pour votre retour !
                </p>
            `;
            setTimeout(() => feedbackDiv.remove(), 2000);
        }
    } catch (error) {
        console.error('Erreur feedback:', error);
    }
}

function showLanguageIndicator(language) {
    const languages = {
        'en': '🇬🇧 English',
        'ar': '🇸🇦 العربية',
        'fr': '🇫🇷 Français'
    };
    
    const indicator = document.createElement('div');
    indicator.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: white;
        padding: 10px 15px;
        border-radius: 25px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        font-size: 14px;
        z-index: 1000;
    `;
    indicator.textContent = languages[language] || language;
    
    document.body.appendChild(indicator);
    
    setTimeout(() => {
        indicator.style.transition = 'opacity 0.5s';
        indicator.style.opacity = '0';
        setTimeout(() => indicator.remove(), 500);
    }, 3000);
}

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
        console.error('Erreur stats:', error);
    }
}

// Gestionnaire de formulaire
chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const message = userInput.value.trim();
    if (message) {
        sendMessage(message);
    }
});

// Enter pour envoyer
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        chatForm.dispatchEvent(new Event('submit'));
    }
});

// Charger les stats au démarrage
updateStats();
setInterval(updateStats, 30000);

// 🆕 Notification de bienvenue avec animation
setTimeout(() => {
    addMessage(
        "Bonjour ! Je suis votre assistant virtuel intelligent. Je peux vous aider en français, anglais ou arabe. N'hésitez pas à poser vos questions ! 🌍",
        'bot',
        'happy'
    );
}, 500);