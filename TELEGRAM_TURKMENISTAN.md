# Telegram Setup Guide for Turkmenistan

## 🌐 Problem: Telegram is Blocked in Turkmenistan

The error you're seeing is because Telegram servers are blocked in Turkmenistan. You need to use a proxy to connect.

## 🔧 Solutions (Choose ONE):

### **Option 1: MTProto Proxy (Recommended)**
1. **Get a free MTProto proxy:**
   - Go to: https://mtproto.pro
   - Or search "free MTProto proxy" online
   - You'll get something like: `server:port secret`

2. **Update your bot code:**
   ```python
   # Replace in telegram_payment_bot.py line 110:
   proxy_url = "proxy://server:port?secret=YOUR_SECRET"
   ```

### **Option 2: SOCKS5 Proxy**
1. **Get a SOCKS5 proxy:**
   - Search "free SOCKS5 proxy list"
   - Example: `123.45.67.89:1080`

2. **Update your bot code:**
   ```python
   # Replace in telegram_payment_bot.py line 110:
   proxy_url = "socks5://123.45.67.89:1080"
   ```

### **Option 3: VPN (Easiest)**
1. **Install any VPN:**
   - NordVPN, ExpressVPN, or free VPN
   - Connect to a nearby country (Turkey, Russia)
   - Run your bot normally

### **Option 4: Use Web Interface (No Bot)**
1. **Use the web test interface I created:**
   - Go to: http://localhost:5000/test-payment
   - Test payments without Telegram bot
   - Later deploy to a server with internet access

## 🚀 Quick Test (No Proxy Needed):

1. **Use the web interface:**
   ```
   Open: http://localhost:5000/test-payment
   Enter your username
   Enter amount: 5
   Click "Test Payment"
   ```

2. **This will:**
   - Test your payment system
   - Update user balance
   - Work without Telegram

## 📱 For Production:

Once your app works, you have two options:

1. **Deploy to a server** outside Turkmenistan
2. **Use a proxy service** for Telegram access

## 🎯 Recommendation:

**Start with the web test interface** to verify your payment system works, then worry about Telegram proxy later.

**Try this now:**
1. Go to http://localhost:5000/test-payment
2. Enter your username and amount
3. Test the payment system

This will work immediately without any proxy!
