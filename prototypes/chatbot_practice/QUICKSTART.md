# Quick Start Guide 🚀

## Run the Chatbot with DeepSeek AI

### Step 1: Navigate to the folder
```bash
cd Practice/prototypes/chatbot_practice
```

### Step 2: Install dependencies (if not already done)
```bash
pip3 install -r requirements.txt
```

### Step 3: Start the Flask server
```bash
python3 app.py
```

### Step 4: Open in browser
Visit: **http://localhost:9000**

### Step 5: Test the chatbot!
Click the bouncing robot in the bottom-right corner and try asking:
- "What is Sailor Sheet?"
- "How does it work?"
- "What countries are supported?"

---

## Troubleshooting

**Port 9000 already in use?**
- Change line 197 in `app.py`: `app.run(debug=True, port=9000, host='0.0.0.0')`

**Module not found?**
```bash
pip3 install flask flask-cors requests
```

**API not working?**
- Check that DeepSeek API key is valid in `app.py` (line 18)
- Check your internet connection
- Try again - sometimes it needs a moment

---

## What This Demonstrates

✅ Direct AI API integration  
✅ Flask backend for chat  
✅ Context-aware responses  
✅ Error handling & fallbacks  
✅ Real-time UI updates  
✅ Typing indicators  

Enjoy experimenting! 🎉

