"""Pesapal API constants and endpoints."""

# API Base URLs
# Sandbox: https://cybqa.pesapal.com/pesapalv3
# Production: https://pay.pesapal.com/v3
# Full URLs are constructed as: {BASE_URL}{ENDPOINT}
# Example: https://cybqa.pesapal.com/pesapalv3/api/Transactions/SubmitOrderRequest
PESAPAL_SANDBOX_BASE_URL = "https://cybqa.pesapal.com/pesapalv3"
PESAPAL_PRODUCTION_BASE_URL = "https://pay.pesapal.com/v3"

# API Endpoints
ENDPOINT_AUTH_TOKEN = "/api/Auth/RequestToken"  # OAuth token endpoint (required for API 3.0)
ENDPOINT_SUBMIT_ORDER = "/api/Transactions/SubmitOrderRequest"
ENDPOINT_GET_STATUS = "/api/Transactions/GetTransactionStatus"
ENDPOINT_IPN_REGISTER = "/api/URLSetup/RegisterIPN"
ENDPOINT_IPN_LIST = "/api/URLSetup/GetRegisteredNotificationUrl"  # Get list of registered IPNs
ENDPOINT_REFUND = "/api/Transactions/RefundOrder"  # Refund request endpoint
ENDPOINT_CANCEL_ORDER = "/api/Transactions/CancelOrder"  # Cancel order endpoint

# Payment Status Codes
STATUS_PENDING = "PENDING"
STATUS_COMPLETED = "COMPLETED"
STATUS_FAILED = "FAILED"
STATUS_INVALID = "INVALID"

# Supported Currencies
CURRENCY_KES = "KES"  # Kenyan Shilling
CURRENCY_TZS = "TZS"  # Tanzanian Shilling
CURRENCY_UGX = "UGX"  # Ugandan Shilling
CURRENCY_RWF = "RWF"  # Rwandan Franc
CURRENCY_USD = "USD"  # US Dollar

SUPPORTED_CURRENCIES = [CURRENCY_KES, CURRENCY_TZS, CURRENCY_UGX, CURRENCY_RWF, CURRENCY_USD]

# Payment Methods
PAYMENT_METHOD_MOBILE_MONEY = "MOBILE_MONEY"
PAYMENT_METHOD_CARD = "CARD"
PAYMENT_METHOD_BANK = "BANK"

SUPPORTED_PAYMENT_METHODS = [PAYMENT_METHOD_MOBILE_MONEY, PAYMENT_METHOD_CARD, PAYMENT_METHOD_BANK]

