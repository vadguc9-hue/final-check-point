# FREE Telegram Payment Setup for Turkmenistan

## Step 1: Create Telegram Bot (5 minutes)
1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Choose a name: "Payment Bot"
4. Choose username: "YourShopPaymentBot" (must end in 'bot')
5. **Copy the bot token** (looks like: `1234567890:ABCDEF...`)

## Step 2: Update Bot Code
1. Edit `telegram_payment_bot.py`
2. Replace `YOUR_BOT_TOKEN_HERE` with your actual token
3. Replace `http://localhost:5000` with your app URL

## Step 3: Install Requirements
```bash
pip install python-telegram-bot requests
```

## Step 4: Start the Bot
```bash
python telegram_payment_bot.py
```

## Step 5: Update Your Website
1. Edit `templates/payment_instructions.html`
2. Replace `https://t.me/YOUR_BOT_USERNAME` with your bot link
3. Test the bot by sending "PAY 5"

## How It Works for Users:
1. User clicks "Start Payment Bot" button
2. User sends "PAY 5" to the bot
3. Bot automatically adds 5 tokens to their account
4. User can immediately use tokens to sell products or view contacts

## Benefits for Turkmenistan:
✅ **Completely FREE** - No SMS charges
✅ **Works worldwide** - No country restrictions  
✅ **Instant processing** - Real-time balance updates
✅ **Easy to use** - Just send a message
✅ **No phone number required** - Uses Telegram username

## Alternative Free Options:
1. **WhatsApp Business** - Free API for small volumes
2. **Email Payments** - Users send "PAY 5" via email
3. **Web Form** - Manual payment confirmation

## Security Tips:
- Keep your bot token secret
- Monitor for duplicate payments
- Use HTTPS for your webhook URL

## Support:
If you need help, check:
- Telegram Bot documentation
- Python-telegram-bot examples
- Your app logs for debugging
