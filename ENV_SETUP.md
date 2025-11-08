# Environment Variables Setup

## Required Environment Variables

Add these to your `.env` file:

```env
# MongoDB Configuration
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/?appName=Cluster0
MONGODB_DB_NAME=sdk_payments

# Pesapal API 3.0 Configuration
PESAPAL_CONSUMER_KEY=your_consumer_key_here
PESAPAL_CONSUMER_SECRET=your_consumer_secret_here
PESAPAL_SANDBOX=true
PESAPAL_CALLBACK_URL=https://payment-helper.onrender.com/payments/callback
PESAPAL_IPN_URL=https://payment-helper.onrender.com/webhooks/pesapal
PESAPAL_IPN_ID=your_ipn_notification_id_here
```

## How to Get Pesapal Credentials

1. **Consumer Key & Secret:**
   - Log into your Pesapal merchant dashboard
   - Go to Settings → API Credentials
   - Copy your Consumer Key and Consumer Secret

2. **IPN Notification ID (IPN_ID):**
   - Log into Pesapal dashboard
   - Go to Settings → IPN (Instant Payment Notification)
   - Register your IPN URL: `https://your-domain.com/webhooks/pesapal`
   - Copy the IPN Notification ID that Pesapal generates
   - Add it to `.env` as `PESAPAL_IPN_ID`

## Important Notes

- **IPN_ID is REQUIRED** for Pesapal API 3.0
- The IPN URL must be publicly accessible (not localhost)
- For local testing, use a service like ngrok to expose your local server
- Sandbox and Production use different credentials

## Example .env File

```env
# MongoDB
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/?appName=Cluster0
MONGODB_DB_NAME=payments-helper-db

# Pesapal (Sandbox)
PESAPAL_CONSUMER_KEY=qkio1BGGYgLgB6JvPm0XNVqD2u0tWBer
PESAPAL_CONSUMER_SECRET=your_secret_here
PESAPAL_SANDBOX=true
PESAPAL_CALLBACK_URL=https://payment-helper.onrender.com/payments/callback
PESAPAL_IPN_URL=https://payment-helper.onrender.com/webhooks/pesapal
PESAPAL_IPN_ID=abc123xyz-ipn-id-from-pesapal
```

