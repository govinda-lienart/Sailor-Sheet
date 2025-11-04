# Chatbot Practice with DeepSeek AI 🤖

A standalone practice version of the chatbot widget with AI-powered responses using DeepSeek API.

## 🎯 Features

- **AI-Powered Responses**: Uses DeepSeek AI model for intelligent conversations
- **Context-Aware**: Reads information about Sailor Sheet from a text file
- **Fallback System**: Falls back to basic responses if API fails
- **Typing Indicator**: Shows animated typing dots while AI is thinking
- **Responsive Design**: Beautiful gradient blue background
- **Interactive Robot**: Bouncing robot animation with Lottie
- **Click to Chat**: Floating chatbot widget in bottom right corner

## 📁 Files

- `index.html` - Main HTML file with blue gradient background
- `chatbot.js` - Chatbot logic with AI integration
- `chatbot.css` - Chatbot styling and animations
- `app.py` - Flask backend with DeepSeek integration
- `context.txt` - Information about Sailor Sheet for AI context
- `requirements.txt` - Python dependencies
- `README.md` - This file

## 🚀 Setup Instructions

### 1. Create Environment File (Optional)

Create a `.env` file in the `chatbot_practice` directory (optional, API key has a fallback):

```bash
# Create .env file
echo "DEEPSEEK_API_KEY=sk-your-api-key-here" > .env
```

Or use the default API key that's built into the code.

### 2. Install Python Dependencies

```bash
# Make sure you're in the chatbot_practice directory
cd Practice/prototypes/chatbot_practice

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the Application

```bash
# Start the Flask server
python app.py

# Server will start on http://localhost:5000
```

### 3. Open in Browser

Visit: **http://localhost:5000**

## 🎨 How It Works

1. **User sends message** → Frontend (chatbot.js)
2. **Message goes to backend** → Flask server (app.py)
3. **Backend calls DeepSeek API** → Direct API call with context
4. **AI reads context** → Information from context.txt
5. **AI generates response** → Based on context and question
6. **Response sent back** → Displayed in chatbot
7. **Fallback if error** → Basic responses from chatbot.js

## 💬 Try These Questions

- "What is Sailor Sheet?"
- "How does Sailor Sheet work?"
- "What features does Sailor Sheet have?"
- "Tell me about the technology"
- "What countries are supported?"
- "How do I create a transaction?"
- "What is the future of Sailor Sheet?"

## 🔧 Customization

### Update AI Context

Edit `context.txt` to change what the AI knows about Sailor Sheet:

```bash
nano context.txt
# or
code context.txt
```

### Modify AI Behavior

Edit `app.py` to change:
- Temperature (creativity): Line 21
- Max tokens (response length): Line 22
- System prompt: Line 54
- Response template: Lines 59-67

### Change Styling

Edit `chatbot.css` to modify:
- Colors
- Sizes
- Animations
- Layout

### Update Fallback Responses

Edit `chatbot.js` in the `getBotResponse()` function around line 87.

## 🐛 Troubleshooting

### API Key Issues

If you see errors, make sure the DeepSeek API key is valid in `app.py` (line 15).

### Port Already in Use

If port 5000 is busy, change it in `app.py` line 122:

```python
app.run(debug=True, port=8000, host='0.0.0.0')  # Use port 8000 instead
```

### Module Not Found

Make sure you installed all dependencies:

```bash
pip install -r requirements.txt
```

### CORS Issues

Flask-CORS should handle this automatically. If not, check line 15 in `app.py`.

## 📊 Technology Stack

- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **Backend**: Python Flask
- **AI**: DeepSeek API via LangChain
- **Animation**: Lottie (via CDN)
- **Dependencies**: flask, flask-cors, requests, langchain

## 🎓 Learning Points

This practice project demonstrates:
- Integration of AI APIs with LangChain
- Custom LLM wrapper for DeepSeek
- LangChain chains and prompt templates
- Flask backend with REST API
- Frontend-backend communication with fetch()
- Error handling and fallback systems
- Context injection for AI responses
- Real-time UI updates

## 📝 Notes

- This is a practice/demo version
- The DeepSeek API key is included for testing
- No sensitive data is stored
- All responses are generated on-the-fly
- Context loads from a simple text file
- Perfect for experimenting with AI chatbots

## 🚧 Future Enhancements

Ideas for improvement:
- Add conversation memory/history
- Support multiple contexts
- Add user authentication
- Store chat history in database
- Add more AI models to compare
- Implement streaming responses
- Add voice input/output

Enjoy experimenting with AI chatbots! 🎉
