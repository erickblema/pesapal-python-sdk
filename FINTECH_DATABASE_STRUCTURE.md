# Fintech-Grade Database Structure

## Overview

This payment system now uses a comprehensive, fintech-grade database structure with complete transaction tracking and audit trails.

## Database Collections

### 1. Payments Collection (`payments`)

**Purpose**: Main payment records with comprehensive tracking

**Fields**:
- `_id`: MongoDB ObjectId
- `order_id`: Unique order identifier (merchant reference)
- `amount`: Payment amount
- `currency`: Currency code (KES, TZS, UGX, RWF, USD)
- `description`: Payment description
- `status`: Current payment status
- `order_tracking_id`: Pesapal tracking ID
- `redirect_url`: Payment redirect URL
- `payment_method`: Payment method used
- `confirmation_code`: Confirmation code
- `customer`: Customer information
- `billing_address`: Billing address
- `merchant_id`: Merchant identifier
- `branch`: Store/branch name
- `fees`: Transaction fees
- `net_amount`: Net amount after fees
- `total_amount`: Total amount (amount + fees)
- `payment_provider`: Payment provider (PESAPAL)
- `provider_response`: Full provider response
- `callback_received`: Boolean - callback received flag
- `callback_received_at`: Timestamp when callback received
- `webhook_received`: Boolean - webhook received flag
- `webhook_received_at`: Timestamp when webhook received
- `last_status_check`: Last status check timestamp
- `status_history`: Array of status changes with timestamps
- `events`: Array of payment events
- `metadata`: Additional metadata
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### 2. Transactions Collection (`transactions`)

**Purpose**: Individual transaction records (separate from payments)

**Fields**:
- `_id`: MongoDB ObjectId
- `payment_id`: Reference to payment order_id
- `transaction_type`: PAYMENT, REFUND, CHARGEBACK, REVERSAL, FEE, SETTLEMENT
- `amount`: Transaction amount
- `currency`: Currency code
- `status`: Transaction status (PENDING, PROCESSING, COMPLETED, FAILED, etc.)
- `transaction_reference`: Pesapal tracking ID or other reference
- `payment_method`: Payment method used
- `payment_provider`: Payment provider (PESAPAL)
- `provider_transaction_id`: Provider's transaction ID
- `confirmation_code`: Confirmation code
- `fees`: Transaction fees
- `net_amount`: Net amount after fees
- `description`: Transaction description
- `metadata`: Additional metadata
- `initiated_by`: Who initiated (SYSTEM, USER, etc.)
- `processed_at`: When transaction was processed
- `settled_at`: When transaction was settled
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

## Payment Lifecycle Tracking

### Status History
Every status change is tracked with:
- `old_status`: Previous status
- `new_status`: New status
- `source`: Where change came from (CREATION, CALLBACK, WEBHOOK, MANUAL_CHECK)
- `reason`: Reason for change
- `metadata`: Additional context
- `timestamp`: When change occurred

### Event History
All events are tracked:
- `CREATED`: Payment created
- `SUBMITTED_TO_PESAPAL`: Submitted to Pesapal
- `CALLBACK_RECEIVED`: Callback received from Pesapal
- `WEBHOOK_RECEIVED`: Webhook received from Pesapal
- `STATUS_CHECKED`: Status checked from Pesapal
- `STATUS_UPDATED_VIA_WEBHOOK`: Status updated via webhook

## API Endpoints

### Payment Endpoints

1. **POST `/payments/`** - Create payment
   - Creates payment record
   - Creates transaction record
   - Tracks creation event

2. **GET `/payments/callback`** - Payment callback handler
   - Receives callback from Pesapal
   - Updates callback flags
   - Fetches fresh status
   - Returns comprehensive payment data with transactions

3. **GET `/payments/{order_id}`** - Get payment details
   - Returns complete payment information
   - Includes status history
   - Includes event history
   - Optional: include transactions

4. **GET `/payments/{order_id}/status`** - Check payment status
   - Fetches status from Pesapal
   - Updates transaction status
   - Returns status with history

5. **GET `/payments/{order_id}/transactions`** - Get transaction history
   - Returns all transactions for a payment
   - Includes payment, refunds, fees, etc.

6. **GET `/payments/status/transaction`** - Get transaction status by tracking ID
   - Uses Pesapal tracking ID
   - Returns status with history

## Example Payment Document

```json
{
  "_id": "690fb56aba1b44e85870105f",
  "order_id": "stri-3-4433dSDt-ng",
  "amount": "1000",
  "currency": "TZS",
  "description": "Payment description",
  "status": "200",
  "order_tracking_id": "09369ec3-04a2-4eca-8b8c-db1c25b29552",
  "payment_method": "Visa",
  "confirmation_code": "ABC123",
  "callback_received": true,
  "callback_received_at": "2025-11-09T02:10:00Z",
  "webhook_received": true,
  "webhook_received_at": "2025-11-09T02:10:05Z",
  "last_status_check": "2025-11-09T02:10:00Z",
  "status_history": [
    {
      "old_status": "PENDING",
      "new_status": "200",
      "source": "CREATION",
      "reason": "Submitted to Pesapal",
      "timestamp": "2025-11-09T02:09:00Z"
    }
  ],
  "events": [
    {
      "event_type": "CREATED",
      "status": "PENDING",
      "source": "CREATION",
      "timestamp": "2025-11-09T02:09:00Z"
    },
    {
      "event_type": "CALLBACK_RECEIVED",
      "status": "200",
      "source": "CALLBACK",
      "timestamp": "2025-11-09T02:10:00Z"
    }
  ],
  "created_at": "2025-11-09T02:09:00Z",
  "updated_at": "2025-11-09T02:10:00Z"
}
```

## Benefits

1. **Complete Audit Trail**: Every action is tracked with timestamps
2. **Status History**: See exactly when and why status changed
3. **Transaction Tracking**: Separate transaction records for reconciliation
4. **Callback/Webhook Tracking**: Know when each notification was received
5. **Provider Response Storage**: Full provider responses stored
6. **Professional Structure**: Fintech-grade database design
7. **Easy Reconciliation**: Transaction records make reconciliation simple
8. **Debugging**: Complete history makes debugging easy

## Usage

### View Complete Payment History

```bash
GET /payments/{order_id}?include_transactions=true
```

### View Transaction History

```bash
GET /payments/{order_id}/transactions
```

### View Callback Response

The callback endpoint now returns:
- Payment details
- Status history
- Event history
- Transaction history

This gives you a complete view of the payment lifecycle in one response.

