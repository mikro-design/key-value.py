#!/usr/bin/env python3
"""
Basic Key-Value Store Example

Demonstrates basic usage of the key-value web service:
- Generate a token
- Store JSON data
- Retrieve the data
"""

import requests
import json
from typing import Dict, Any, Optional

# Configuration
API_URL = "http://localhost:3000"  # Change to your deployed URL


class KeyValueClient:
    """Simple client for the key-value store API."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')

    def generate_token(self) -> str:
        """Generate a new 5-word memorable token."""
        response = requests.get(f"{self.base_url}/api/generate")
        response.raise_for_status()
        data = response.json()
        return data['token']

    def store(self, token: str, data: Dict[Any, Any], ttl: Optional[int] = None) -> Dict:
        """
        Store JSON data with a token.

        Args:
            token: The 5-word token
            data: JSON-serializable data to store
            ttl: Optional time-to-live in seconds (max 30 days)

        Returns:
            Response data with success status and size
        """
        payload = {
            "token": token,
            "data": data
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
        Retrieve data for a token.

        Args:
            token: The 5-word token

        Returns:
            The stored data
        """
        response = requests.get(
            f"{self.base_url}/api/retrieve",
            params={"token": token}
        )
        response.raise_for_status()
        data = response.json()
        return data['data']


def main():
    """Demonstrate basic key-value store operations."""
    client = KeyValueClient(API_URL)

    # Step 1: Generate a token
    print("=== Generating Token ===")
    token = client.generate_token()
    print(f"Generated token: {token}")
    print(f"Remember this token! You'll need it to retrieve your data.\n")

    # Step 2: Store some data
    print("=== Storing Data ===")
    my_data = {
        "user": "alice",
        "settings": {
            "theme": "dark",
            "notifications": True
        },
        "scores": [95, 87, 92]
    }

    result = client.store(token, my_data)
    print(f"Store result: {json.dumps(result, indent=2)}\n")

    # Step 3: Retrieve the data
    print("=== Retrieving Data ===")
    retrieved = client.retrieve(token)
    print(f"Retrieved data: {json.dumps(retrieved, indent=2)}\n")

    # Verify data matches
    assert retrieved == my_data, "Data mismatch!"
    print("✓ Data successfully stored and retrieved!")

    # Step 4: Update the data
    print("\n=== Updating Data ===")
    my_data["settings"]["theme"] = "light"
    my_data["last_updated"] = "2025-10-13"

    result = client.store(token, my_data)
    print(f"Update result: {json.dumps(result, indent=2)}\n")

    # Retrieve updated data
    updated = client.retrieve(token)
    print(f"Updated data: {json.dumps(updated, indent=2)}\n")
    assert updated == my_data, "Updated data mismatch!"
    print("✓ Data successfully updated!")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        if e.response:
            print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"Error: {e}")
