// Chatbot Widget - Extracted from inline script
// This is a self-contained help chatbot for the accounting system

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

        // Generate bot response after a delay
        setTimeout(() => {
            const response = getBotResponse(message);
            addMessage(response, 'bot');
        }, 800);
    }

    function addMessage(text, sender) {
        const messagesContainer = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        
        messageDiv.className = `chat-message ${sender}-message`;
        messageDiv.textContent = text;
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function getBotResponse(message) {
        const responses = {
            'hello': 'Hi there! How can I help you with your accounting today?',
            'hi': 'Hello! What would you like to know about Sailor Sheet?',
            'help': 'I can help you with creating transactions, understanding categories, finding accounts, and general accounting questions.',
            'transaction': 'To create a transaction, fill out the form fields: date, description, amount, category, account, and fund. Then click Submit to Google Sheets.',
            'category': 'Categories help organize your transactions. You can select from the dropdown or add new ones.',
            'account': 'Accounts represent where the money comes from or goes to. Choose the appropriate account from the dropdown.',
            'fund': 'Funds help you track different sources of money or projects within your organization.',
            'sheet': 'This form submits data directly to your Google Sheets. Make sure you have the right sheet selected!',
            'how': 'I can guide you through the process. What specifically do you need help with?'
        };

        const lowerMessage = message.toLowerCase();
        
        for (const key in responses) {
            if (lowerMessage.includes(key)) {
                return responses[key];
            }
        }
        
        return "I'm here to help with your accounting questions! Try asking about transactions, categories, accounts, or funds.";
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

    console.log('✅ Chatbot initialized');
})();

