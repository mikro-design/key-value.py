#!/usr/bin/env python3
"""
Encrypted Key-Value Store Example

Demonstrates client-side encryption before storing sensitive data.
The server stores encrypted data and cannot read the contents.

Requirements:
    pip install requests cryptography
"""

import requests
import json
import base64
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2

# Configuration
API_URL = "http://localhost:3000"  # Change to your deployed URL


class EncryptedKeyValueClient:
    """Client with automatic encryption/decryption."""

    def __init__(self, base_url: str, password: str):
        """
        Initialize client with encryption password.

        Args:
            base_url: API base URL
            password: Password used to derive encryption key
        """
        self.base_url = base_url.rstrip('/')
        self.cipher = self._create_cipher(password)

    def _create_cipher(self, password: str) -> Fernet:
        """Create Fernet cipher from password."""
        # Use a fixed salt for deterministic key derivation
        # In production, store salt separately and retrieve it
        salt = b'keyvalue-store-salt-change-this!'

        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return Fernet(key)

    def generate_token(self) -> str:
        """Generate a new 5-word memorable token."""
        response = requests.get(f"{self.base_url}/api/generate")
        response.raise_for_status()
        data = response.json()
        return data['token']

    def _encrypt_data(self, data: Dict[Any, Any]) -> Dict[str, str]:
        """Encrypt data payload."""
        json_str = json.dumps(data)
        encrypted = self.cipher.encrypt(json_str.encode())
        return {
            "encrypted": True,
            "payload": base64.b64encode(encrypted).decode('utf-8')
        }

    def _decrypt_data(self, encrypted_data: Dict[str, str]) -> Dict[Any, Any]:
        """Decrypt data payload."""
        if not encrypted_data.get("encrypted"):
            raise ValueError("Data is not encrypted")

        payload = base64.b64decode(encrypted_data["payload"])
        decrypted = self.cipher.decrypt(payload)
        return json.loads(decrypted.decode())

    def store(self, token: str, data: Dict[Any, Any], ttl: Optional[int] = None) -> Dict:
        """
        Encrypt and store data.

        Args:
            token: The 5-word token
            data: JSON-serializable data to encrypt and store
            ttl: Optional time-to-live in seconds

        Returns:
            Response data with success status
        """
        encrypted_data = self._encrypt_data(data)

        payload = {
            "token": token,
            "data": encrypted_data
        }
        if ttl:
            payload["ttl"] = ttl

        response = requests.post(
            f"{self.base_url}/api/store",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()

    def retrieve(self, token: str) -> Dict[Any, Any]:
        """
        Retrieve and decrypt data.

        Args:
            token: The 5-word token

        Returns:
            The decrypted data
        """
        response = requests.get(
            f"{self.base_url}/api/retrieve",
            params={"token": token}
        )
        response.raise_for_status()
        data = response.json()

        return self._decrypt_data(data['data'])


def main():
    """Demonstrate encrypted key-value operations."""

    # Use a strong password for encryption
    password = "my-super-secret-password-123"  # Change this!

    client = EncryptedKeyValueClient(API_URL, password)

    # Step 1: Generate token
    print("=== Generating Token ===")
    token = client.generate_token()
    print(f"Generated token: {token}")
    print(f"Encryption password: {password}")
    print(f"Keep both safe!\n")

    # Step 2: Store sensitive data (will be encrypted automatically)
    print("=== Storing Encrypted Data ===")
    sensitive_data = {
        "api_key": "sk_live_1234567890abcdef",
        "database_url": "postgresql://user:pass@host:5432/db",
        "secrets": {
            "aws_access_key": "AKIAIOSFODNN7EXAMPLE",
            "aws_secret_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        },
        "credit_card": {
            "number": "4532-1234-5678-9010",
            "cvv": "123"
        }
    }

    result = client.store(token, sensitive_data)
    print(f"Store result: {json.dumps(result, indent=2)}")
    print("✓ Data encrypted and stored on server\n")

    # Step 3: Retrieve and decrypt
    print("=== Retrieving and Decrypting ===")
    retrieved = client.retrieve(token)
    print(f"Decrypted data: {json.dumps(retrieved, indent=2)}\n")

    # Verify
    assert retrieved == sensitive_data, "Data mismatch!"
    print("✓ Data successfully encrypted, stored, and decrypted!")

    # Step 4: Show what's actually stored on the server
    print("\n=== What the Server Sees ===")
    response = requests.get(
        f"{API_URL}/api/retrieve",
        params={"token": token}
    )
    server_data = response.json()['data']
    print(f"Encrypted payload on server:")
    print(f"  - encrypted: {server_data['encrypted']}")
    print(f"  - payload: {server_data['payload'][:80]}...")
    print("\n✓ Server cannot read your data without the password!")

    # Step 5: Wrong password fails
    print("\n=== Testing Wrong Password ===")
    try:
        wrong_client = EncryptedKeyValueClient(API_URL, "wrong-password")
        wrong_client.retrieve(token)
        print("✗ Should have failed!")
    except Exception as e:
        print(f"✓ Decryption failed as expected: {type(e).__name__}")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        if e.response:
            print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
