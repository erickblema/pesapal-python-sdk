# Pesapal v3 API Compliance Check

## ✅ What's Correct

1. **SubmitOrderRequest Endpoint**
   - ✅ Base URLs correct (sandbox/production)
   - ✅ Authentication with Bearer token
   - ✅ Required fields: `id`, `currency`, `amount`, `description`, `callback_url`, `notification_id`
   - ✅ `billing_address` support

2. **IPN Webhook (POST)**
   - ✅ Handles JSON format correctly
   - ✅ Extracts `OrderTrackingId`, `OrderNotificationType`, `OrderMerchantReference`
   - ✅ Returns correct IPN response format
   - ✅ No mock data (uses actual Pesapal data)

3. **GetTransactionStatus**
   - ✅ Endpoint exists at `/payments/status/transaction`
   - ✅ Uses `orderTrackingId` parameter

## ❌ Missing/Incorrect

1. **SubmitOrderRequest Missing Parameters**
   - ❌ `redirect_mode` - in model but NOT sent to Pesapal API
   - ❌ `cancellation_url` - missing from model and not sent
   - ❌ `branch` - missing from model and not sent
   - ⚠️ `billing_address` - marked as optional in code, but doc says REQUIRED

2. **Response Format**
   - ❌ `error` field not in PaymentResponse model (doc shows it in response)

3. **Callback URL Handler**
   - ❌ No endpoint to handle callback URL
   - Should handle: `OrderTrackingId`, `OrderNotificationType` (CALLBACKURL), `OrderMerchantReference` as query parameters
   - Should call GetTransactionStatus after receiving callback

4. **IPN Webhook**
   - ❌ GET method removed (but doc says IPN can be GET or POST depending on registration)
   - Should support both GET and POST

5. **Automatic Status Check**
   - ⚠️ GetTransactionStatus should be called automatically after callback/IPN
   - Currently requires manual call

## 📋 Required Fixes

1. Add `redirect_mode`, `cancellation_url`, `branch` to PaymentRequest model
2. Send `redirect_mode` to Pesapal API (currently in model but not sent)
3. Create `/payments/callback` endpoint to handle callback URL
4. Add GET support back to IPN webhook (or make it configurable)
5. Automatically call GetTransactionStatus after callback/IPN
6. Add `error` field to PaymentResponse model
7. Make `billing_address` required (or document why it's optional)

