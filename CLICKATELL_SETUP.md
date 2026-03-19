# Clickatell SMS Payment Setup Guide

## Step 1: Sign up for Clickatell
1. Go to https://www.clickatell.com
2. Create an account
3. Choose a plan (they have free trial options)
4. Get a virtual phone number (supports Azerbaijan numbers)

## Step 2: Configure Webhook
1. In Clickatell dashboard, go to "Settings" → "Webhooks"
2. Set webhook URL to: `https://your-app-url.com/api/payment/sms`
3. Choose "JSON" format
4. Enable "Incoming SMS" webhook

## Step 3: Update Payment Instructions
Update your payment instructions template with your Clickatell phone number:
- Edit `templates/payment_instructions.html`
- Replace "+994 XX XXX XX XX" with your actual Clickatell number

## Step 4: Test the Integration
1. Send an SMS to your Clickatell number with: "PAY 5"
2. Check if user balance is updated
3. Check Payment table for transaction record

## Clickatell Webhook Format
Your app will receive data like this:
```json
{
  "from_number": "+994501234567",
  "to_number": "+994707654321",
  "text": "PAY 5",
  "timestamp": "2023-12-01T12:00:00Z"
}
```

## Phone Number Format Support
The app automatically handles:
- +994501234567 → 994501234567
- 0501234567 → 994501234567
- 994501234567 → 994501234567

## SMS Message Format
Users should send: "PAY [amount]"
- "PAY 5" → Adds 5 tokens
- "PAY 10.5" → Adds 10.5 tokens
- Case insensitive: "pay 5" also works

## Troubleshooting
1. **Webhook not working**: Check your URL is publicly accessible
2. **User not found**: Ensure phone numbers match database format
3. **Amount not parsed**: Check SMS format matches "PAY [number]"

## Security Notes
- The webhook URL should be HTTPS
- Consider adding authentication tokens
- Monitor for duplicate transactions
