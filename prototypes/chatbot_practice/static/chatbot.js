// Chatbot Practice - Standalone Version
// Simple chatbot with basic interactions for practice

(function() {
    'use strict';
    
    let isOpen = false;

    function toggleChat() {
        const chatWindow = document.getElementById('chat-window');
        const chatToggle = document.getElementById('chat-toggle');
        
        isOpen = !isOpen;
        
        if (isOpen) {
            chatWindow.style.display = 'flex';
            chatToggle.style.transform = 'scale(0.9)';
            document.getElementById('chat-input').focus();
        } else {
            chatWindow.style.display = 'none';
            chatToggle.style.transform = 'scale(1)';
        }
    }

    function sendMessage() {
        const input = document.getElementById('chat-input');
        const message = input.value.trim();
        if (!message) return;

        // Add user message
        addMessage(message, 'user');
        input.value = '';

        // Show typing indicator
        const typingIndicator = addTypingIndicator();

        // Call AI backend API
        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            removeTypingIndicator(typingIndicator);
            addMessage(data.response, 'bot');
        })
        .catch(error => {
            console.error('Error:', error);
            removeTypingIndicator(typingIndicator);
            // Fallback to basic response
            const response = getBotResponse(message);
            addMessage(response, 'bot');
        });
    }

    function addMessage(text, sender) {
        const messagesContainer = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        
        messageDiv.className = `chat-message ${sender}-message`;
        messageDiv.textContent = text;
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function addTypingIndicator() {
        const messagesContainer = document.getElementById('chat-messages');
        const typingDiv = document.createElement('div');
        typingDiv.className = 'chat-message bot-message typing-indicator';
        typingDiv.innerHTML = '<span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span>';
        typingDiv.id = 'typing-indicator';
        messagesContainer.appendChild(typingDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        return typingDiv;
    }

    function removeTypingIndicator(indicator) {
        if (indicator && indicator.parentNode) {
            indicator.parentNode.removeChild(indicator);
        }
    }

    function getBotResponse(message) {
        const responses = {
            'hello': 'Hi there! How can I help you today?',
            'hi': 'Hello! Nice to meet you!',
            'help': 'I can help you with questions, have a conversation, or just chat!',
            'how are you': 'I\'m doing great, thanks for asking! How about you?',
            'goodbye': 'Goodbye! Feel free to come back anytime!',
            'bye': 'See you later!',
            'thanks': 'You\'re welcome! Happy to help!',
            'thank you': 'You\'re very welcome!',
            'what can you do': 'I can chat, answer questions, and have conversations with you! Try asking me anything!',
            'who are you': 'I\'m a friendly chatbot! I\'m here to chat and help you practice!',
            'tell me a joke': 'Why don\'t scientists trust atoms? Because they make up everything! 😄',
            'weather': 'I don\'t have access to weather data, but I hope it\'s a great day wherever you are!'
        };

        const lowerMessage = message.toLowerCase();
        
        for (const key in responses) {
            if (lowerMessage.includes(key)) {
                return responses[key];
            }
        }
        
        return "That's interesting! Can you tell me more?";
    }

    // Close chat when clicking outside
    document.addEventListener('click', function(e) {
        const widget = document.getElementById('chatbot-widget');
        if (isOpen && !widget.contains(e.target)) {
            toggleChat();
        }
    });

    // Expose toggleChat and sendMessage to global scope for HTML onclick handlers
    window.toggleChat = toggleChat;
    window.sendMessage = sendMessage;

    console.log('✅ Chatbot practice initialized');
})();
