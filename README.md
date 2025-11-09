# Pesapal Payment SDK

FastAPI-based payment integration with Pesapal API 3.0, featuring complete transaction tracking and webhook handling.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Setup

Create a `.env` file in the project root:

```env
# MongoDB Configuration
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/?appName=Cluster0
MONGODB_DB_NAME=sdk_payments

# Pesapal API 3.0 Configuration
PESAPAL_CONSUMER_KEY=your_consumer_key_here
PESAPAL_CONSUMER_SECRET=your_consumer_secret_here
PESAPAL_SANDBOX=true
PESAPAL_CALLBACK_URL=https://your-domain.com/payments/callback
PESAPAL_IPN_URL=https://your-domain.com/webhooks/pesapal
PESAPAL_IPN_ID=your_ipn_notification_id_here
```

### 3. Get Pesapal Credentials

1. **Consumer Key & Secret:**
   - Log into Pesapal merchant dashboard
   - Go to Settings → API Credentials
   - Copy Consumer Key and Consumer Secret

2. **IPN Notification ID:**
   - Go to Settings → IPN (Instant Payment Notification)
   - Register your IPN URL: `https://your-domain.com/webhooks/pesapal`
   - Copy the IPN Notification ID
   - Add to `.env` as `PESAPAL_IPN_ID`

**Note:** IPN_ID is required for Pesapal API 3.0. For local testing, use ngrok to expose your server.

### 4. Run the Application

```bash
uvicorn main:app --reload
```

Access Swagger UI at: `http://localhost:8000/docs`

## API Endpoints

### Payment Endpoints

- **POST `/payments/`** - Create payment
  ```json
  {
    "order_id": "ORDER-123",
    "amount": 1000,
    "currency": "TZS",
    "description": "Payment description",
    "billing_address": {
      "email_address": "customer@example.com",
      "phone_number": "+255123456789",
      "country_code": "TZ",
      "first_name": "John",
      "middle_name": "",
      "last_name": "Doe",
      "line_1": "Street Address",
      "line_2": "",
      "city": "Dar es Salaam",
      "state": "",
      "postal_code": "",
      "zip_code": ""
    }
  }
  ```

- **GET `/payments/callback`** - Payment callback handler (called by Pesapal after payment)
  - Automatically fetches payment status
  - Returns complete payment data with transaction history

- **GET `/payments/{order_id}`** - Get payment details
  - Returns payment info, status history, event history
  - Add `?include_transactions=true` to include transaction history

- **GET `/payments/{order_id}/status`** - Check payment status
  - Fetches latest status from Pesapal
  - Updates transaction records

- **GET `/payments/{order_id}/transactions`** - Get transaction history
  - Returns all transactions for a payment

- **GET `/payments/status/transaction?orderTrackingId={id}`** - Get status by tracking ID

- **GET `/payments/`** - List payments (with optional status filter)

### Webhook Endpoints

- **POST `/webhooks/pesapal`** - IPN webhook handler
  - Receives payment notifications from Pesapal
  - Automatically fetches payment status
  - Returns IPN response format

## Database Structure

### Payments Collection

Stores main payment records with:
- Payment details (amount, currency, status)
- Tracking information (order_tracking_id, redirect_url)
- Status history (all status changes with timestamps)
- Event history (all payment events)
- Callback/webhook tracking (flags and timestamps)
- Provider responses (full Pesapal API responses)

### Transactions Collection

Stores individual transaction records:
- Transaction type (PAYMENT, REFUND, CHARGEBACK, etc.)
- Amount, fees, net amount
- Status (PENDING, PROCESSING, COMPLETED, etc.)
- Processing timestamps
- Links to payment via `payment_id`

### Status History

Every status change is tracked:
```json
{
  "old_status": "PENDING",
  "new_status": "200",
  "source": "CALLBACK",
  "reason": "Payment completed",
  "timestamp": "2025-11-09T02:10:00Z"
}
```

### Event History

All events are tracked:
- `CREATED` - Payment created
- `SUBMITTED_TO_PESAPAL` - Submitted to Pesapal
- `CALLBACK_RECEIVED` - Callback received
- `WEBHOOK_RECEIVED` - Webhook received
- `STATUS_CHECKED` - Status checked from Pesapal
- `STATUS_UPDATED_VIA_WEBHOOK` - Status updated via webhook

## Example Payment Flow

1. **Create Payment:**
   ```bash
   POST /payments/
   ```
   - Creates payment record
   - Creates transaction record
   - Returns redirect URL for customer

2. **Customer Completes Payment:**
   - Customer redirected to Pesapal
   - Completes payment
   - Pesapal redirects to callback URL

3. **Callback Received:**
   ```bash
   GET /payments/callback?OrderTrackingId=xxx&OrderMerchantReference=ORDER-123
   ```
   - Updates callback flags
   - Fetches fresh status from Pesapal
   - Updates transaction status
   - Returns complete payment data

4. **Webhook Received:**
   ```bash
   POST /webhooks/pesapal
   ```
   - Receives IPN notification
   - Fetches payment status
   - Updates payment and transaction records
   - Returns IPN response

## Response Format

### Payment Response
```json
{
  "_id": "690fb56aba1b44e85870105f",
  "order_id": "ORDER-123",
  "amount": "1000",
  "currency": "TZS",
  "status": "200",
  "OrderTrackingId": "09369ec3-04a2-4eca-8b8c-db1c25b29552",
  "redirect_url": "https://cybqa.pesapal.com/pesapaliframe/...",
  "payment_method": "Visa",
  "confirmation_code": "ABC123",
  "created_at": "2025-11-09T02:09:00Z",
  "updated_at": "2025-11-09T02:10:00Z"
}
```

### Callback Response
```json
{
  "message": "Payment callback received",
  "payment": { /* complete payment details */ },
  "status_history": [ /* all status changes */ ],
  "transactions": [ /* all transactions */ ],
  "events": [ /* all events */ ]
}
```

## Development

### Project Structure

```
.
├── main.py                 # FastAPI application entry point
├── app/
│   ├── config/            # Configuration settings
│   ├── database/          # MongoDB connection
│   ├── models/            # Data models (Payment, Transaction)
│   ├── repositories/      # Database operations
│   ├── routers/           # API routes
│   ├── schema/            # Pydantic schemas
│   └── services/          # Business logic
├── pesapal/               # Pesapal API client
└── requirements.txt       # Python dependencies
```

### Key Features

- Complete transaction tracking
- Status history with timestamps
- Event logging
- Callback and webhook handling
- Automatic status synchronization
- Transaction reconciliation support

## Testing

Use Swagger UI at `/docs` to test endpoints. For webhook testing, use ngrok to expose your local server:

```bash
ngrok http 8000
```

Then use the ngrok URL for your IPN URL in Pesapal dashboard.

## Notes

- IPN_ID is required for Pesapal API 3.0
- IPN URL must be publicly accessible
- Sandbox and Production use different credentials
- All timestamps are in UTC
- Status codes: "200" = completed, "PENDING" = pending, etc.
