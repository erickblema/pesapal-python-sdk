"""Utility functions for Pesapal SDK."""

import hmac
import hashlib
import base64
from typing import Dict, Any


def generate_signature(data: Dict[str, Any], consumer_secret: str) -> str:
    """
    Generate HMAC-SHA256 signature for Pesapal API requests.
    
    Args:
        data: Dictionary of data to sign
        consumer_secret: Pesapal consumer secret
        
    Returns:
        Base64 encoded signature
    """
    # Sort keys and create query string
    sorted_keys = sorted(data.keys())
    query_string = "&".join([f"{key}={data[key]}" for key in sorted_keys])
    
    # Generate HMAC-SHA256
    signature = hmac.new(
        consumer_secret.encode("utf-8"),
        query_string.encode("utf-8"),
        hashlib.sha256
    ).digest()
    
    # Base64 encode
    return base64.b64encode(signature).decode("utf-8")


def verify_webhook_signature(
    data: Dict[str, Any],
    signature: str,
    consumer_secret: str
) -> bool:
    """
    Verify webhook signature from Pesapal.
    
    Args:
        data: Webhook data dictionary
        signature: Signature to verify
        consumer_secret: Pesapal consumer secret
        
    Returns:
        True if signature is valid, False otherwise
    """
    expected_signature = generate_signature(data, consumer_secret)
    return hmac.compare_digest(expected_signature, signature)

