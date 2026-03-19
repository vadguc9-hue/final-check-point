#!/usr/bin/env python3
"""
Telegram Bot for SMS-free payment processing
Install: pip install python-telegram-bot
"""

from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import re

# Your bot token from @BotFather
BOT_TOKEN = "8793242576:AAFHK7xffHGC8dslqWODNq3xcTkemzy84Ow"
WEBAPP_URL = "http://127.0.0.1:5000"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    await update.message.reply_text(
        "Welcome to Payment Bot! 🪙\n\n"
        "Send 'PAY [amount]' to add funds:\n"
        "• PAY 5 - Add 5 tokens\n"
        "• PAY 10.5 - Add 10.5 tokens\n\n"
        "Make sure your Telegram account is linked to your marketplace account!"
    )

async def handle_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle payment messages"""
    message_text = update.message.text.upper()
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    
    # Extract amount from message
    match = re.search(r'PAY\s+(\d+(?:\.\d+)?)', message_text)
    if not match:
        await update.message.reply_text(
            "❌ Invalid format. Use: PAY [amount]\n"
            "Example: PAY 5"
        )
        return
    
    amount = float(match.group(1))
    
    # Send payment to your Flask app
    payment_data = {
        'telegram_id': user_id,
        'username': username,
        'amount': amount,
        'message': message_text
    }
    
    try:
        await update.message.reply_text(f"🔄 Processing payment of {amount} tokens...")
        
        response = requests.post(
            f"{WEBAPP_URL}/api/payment/telegram",
            json=payment_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            await update.message.reply_text(
                f"✅ Payment successful!\n"
                f"Amount: {amount} tokens\n"
                f"New balance: {result.get('new_balance', 0)} tokens\n"
                f"Transaction ID: {result.get('payment_id', 'N/A')}"
            )
        else:
            error_msg = response.json().get('error', 'Unknown error')
            await update.message.reply_text(f"❌ Payment failed: {error_msg}")
            
    except requests.exceptions.ConnectionError:
        await update.message.reply_text(
            "❌ Cannot connect to payment server.\n"
            "Please make sure the website is running.\n"
            "Contact support if this continues."
        )
    except requests.exceptions.Timeout:
        await update.message.reply_text(
            "❌ Payment processing timed out.\n"
            "Please try again in a moment."
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

def main():
    """Start bot with proxy support for Turkmenistan"""
    
    # Try with common MTProto proxy servers
    proxy_servers = [
        # Correct MTProto proxy format
        "socks5://proxy.tg.org:1080",
        "socks5://149.154.175.10:1080",
        "socks5://149.154.175.5:1080",
        # HTTP proxy alternative
        "http://proxy.tg.org:8080",
    ]
    
    def create_application(proxy_url=None):
        application = Application.builder().token(BOT_TOKEN).build()
        if proxy_url:
            application = Application.builder().token(BOT_TOKEN).proxy_url(proxy_url).build()
        
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_payment))
        
        return application
    
    for i, proxy_url in enumerate(proxy_servers):
        try:
            print(f"Trying proxy {i+1}: {proxy_url}")
            application = create_application(proxy_url)
            
            print(f"✅ Telegram Payment Bot started with proxy {i+1}!")
            application.run_polling()
            break
            
        except Exception as e:
            print(f"❌ Proxy {i+1} failed: {e}")
            continue
    
    # If all proxies fail, try without proxy
    try:
        print("Trying without proxy...")
        application = create_application()
        
        print("✅ Telegram Payment Bot started without proxy!")
        application.run_polling()
        
    except Exception as e:
        print(f"❌ All connection attempts failed: {e}")
        print("\n🔧 Solutions:")
        print("1. Use a VPN to connect to Turkey/Russia, then run bot")
        print("2. Find working MTProto proxies online")
        print("3. Deploy bot to a server outside Turkmenistan")
        print("4. Use web interface: http://localhost:5000/test-payment")
        
        print("Please set up a proxy service and update the proxy_url in the code")

if __name__ == '__main__':
    main()
