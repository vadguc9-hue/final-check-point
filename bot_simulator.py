#!/usr/bin/env python3
"""
Web-based Telegram bot simulator for testing payments
"""

from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# HTML template for the bot interface
BOT_INTERFACE = """
<!DOCTYPE html>
<html>
<head>
    <title>Payment Bot Simulator</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
        .chat-container { border: 2px solid #0088cc; border-radius: 10px; height: 400px; overflow-y: auto; padding: 20px; background: #f9f9f9; }
        .message { margin: 10px 0; padding: 10px; border-radius: 5px; max-width: 80%; }
        .user { background: #dcf8c6; margin-left: auto; }
        .bot { background: #e1f5fe; }
        .input-area { display: flex; margin-top: 20px; }
        input { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        button { padding: 10px 20px; background: #0088cc; color: white; border: none; border-radius: 5px; margin-left: 10px; cursor: pointer; }
        button:hover { background: #0077b3; }
        .header { text-align: center; margin-bottom: 20px; color: #0088cc; }
        .status { text-align: center; padding: 10px; margin: 10px 0; border-radius: 5px; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 Payment Bot Simulator</h1>
        <p>Test your payment system without Telegram connection issues</p>
    </div>
    
    <div class="chat-container" id="chat">
        <div class="message bot">
            <strong>🤖 Payment Bot:</strong> Welcome to Payment Bot! 🪙<br><br>
            Send 'PAY [amount]' to add funds:<br>
            • PAY 5 - Add 5 tokens<br>
            • PAY 10.5 - Add 10.5 tokens<br><br>
            Make sure your Telegram account is linked to your marketplace account!
        </div>
    </div>
    
    <div class="input-area">
        <input type="text" id="messageInput" placeholder="Type your message (e.g., PAY 5)" onkeypress="if(event.key==='Enter') sendMessage()">
        <button onclick="sendMessage()">Send</button>
    </div>
    
    <div id="status"></div>
    
    <script>
    function addMessage(text, isUser) {
        const chat = document.getElementById('chat');
        const message = document.createElement('div');
        message.className = `message ${isUser ? 'user' : 'bot'}`;
        message.innerHTML = text;
        chat.appendChild(message);
        chat.scrollTop = chat.scrollHeight;
    }
    
    function showStatus(text, isSuccess) {
        const status = document.getElementById('status');
        status.className = `status ${isSuccess ? 'success' : 'error'}`;
        status.innerHTML = text;
        status.style.display = 'block';
        setTimeout(() => status.style.display = 'none', 5000);
    }
    
    async function sendMessage() {
        const input = document.getElementById('messageInput');
        const message = input.value.trim();
        
        if (!message) return;
        
        // Add user message
        addMessage(`<strong>You:</strong> ${message}`, true);
        input.value = '';
        
        // Show typing indicator
        addMessage(`<strong>🤖 Payment Bot:</strong> 🔄 Processing...`, false);
        
        try {
            const response = await fetch('/api/payment/telegram', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    telegram_id: '123456789',
                    username: 'test_user', // Change this to your actual username
                    amount: parseFloat(message.match(/\\d+(?:\\.\\d+)?/)?.[0] || 0),
                    message: message
                })
            });
            
            const result = await response.json();
            
            // Remove typing indicator
            const messages = document.querySelectorAll('.message');
            messages[messages.length - 1].remove();
            
            if (response.ok) {
                addMessage(`<strong>🤖 Payment Bot:</strong> ✅ Payment successful!<br><br>
                    Amount: ${result.amount} tokens<br>
                    New balance: ${result.new_balance} tokens<br>
                    Transaction ID: ${result.payment_id}`, false);
                showStatus('Payment processed successfully!', true);
            } else {
                addMessage(`<strong>🤖 Payment Bot:</strong> ❌ Payment failed: ${result.error}`, false);
                showStatus(`Payment failed: ${result.error}`, false);
            }
            
        } catch (error) {
            // Remove typing indicator
            const messages = document.querySelectorAll('.message');
            messages[messages.length - 1].remove();
            
            addMessage(`<strong>🤖 Payment Bot:</strong> ❌ Connection error: ${error.message}`, false);
            showStatus(`Connection error: ${error.message}`, false);
        }
    }
    </script>
</body>
</html>
"""

@app.route('/')
def bot_simulator():
    return BOT_INTERFACE

@app.route('/api/payment/telegram', methods=['POST'])
def telegram_payment_web():
    """Web version of Telegram payment endpoint"""
    try:
        data = request.get_json()
        
        telegram_id = data.get('telegram_id')
        username = data.get('username')
        amount = data.get('amount')
        message_text = data.get('message', '')
        
        if not telegram_id or not amount or amount <= 0:
            return jsonify({'error': 'Invalid telegram_id or amount'}), 400
        
        # Import here to avoid circular imports
        import sys
        sys.path.append('.')
        from app import telegram_payment
        
        # Call the original payment function
        return telegram_payment()
        
    except Exception as e:
        return jsonify({'error': f'Web simulator error: {str(e)}'}), 500

if __name__ == '__main__':
    print("🤖 Payment Bot Simulator Starting...")
    print("Open: http://localhost:5001")
    print("This simulates the Telegram bot without connection issues!")
    app.run(port=5001, debug=True)
