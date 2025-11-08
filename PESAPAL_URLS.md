# Pesapal API Base URLs and Endpoints

## 🔗 Base URLs

### Sandbox (Testing Environment)
```
https://cybqa.pesapal.com/pesapalv3
```

### Production (Live Environment)
```
https://pay.pesapal.com/v3
```

## 📍 Full API Endpoints

### Sandbox Endpoints

1. **Submit Order Request**
   ```
   https://cybqa.pesapal.com/pesapalv3/api/Transactions/SubmitOrderRequest
   ```

2. **Get Transaction Status**
   ```
   https://cybqa.pesapal.com/pesapalv3/api/Transactions/GetTransactionStatus
   ```

3. **Register IPN**
   ```
   https://cybqa.pesapal.com/pesapalv3/api/URLSetup/RegisterIPN
   ```

### Production Endpoints

1. **Submit Order Request**
   ```
   https://pay.pesapal.com/v3/api/Transactions/SubmitOrderRequest
   ```

2. **Get Transaction Status**
   ```
   https://pay.pesapal.com/v3/api/Transactions/GetTransactionStatus
   ```

3. **Register IPN**
   ```
   https://pay.pesapal.com/v3/api/URLSetup/RegisterIPN
   ```

## 🔧 How URLs are Constructed

In the SDK, URLs are built as:
```python
url = f"{base_url}{endpoint}"
```

Where:
- `base_url` = `PESAPAL_SANDBOX_BASE_URL` or `PESAPAL_PRODUCTION_BASE_URL`
- `endpoint` = "/api/Transactions/SubmitOrderRequest" (etc.)

## 📝 Configuration

The base URL is selected based on the `sandbox` parameter when creating `PesapalClient`:

```python
client = PesapalClient(
    consumer_key="your_key",
    consumer_secret="your_secret",
    sandbox=True  # True = Sandbox, False = Production
)
```

## ✅ Verification

You can verify the base URL is being used correctly by checking:
- `pesapal/constants.py` - Contains the base URLs
- `pesapal/client.py` line 45 - Sets `self.base_url`
- `pesapal/client.py` line 91 - Constructs full URL: `f"{self.base_url}{endpoint}"`

## 🧪 Testing

To test with Swagger:
1. Start server: `uvicorn main:app --reload`
2. Open: `http://localhost:8000/docs`
3. Use the JSON payloads from `swagger_test_payloads.json`

