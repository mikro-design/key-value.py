# Python Examples for Key-Value Store

This folder contains Python examples demonstrating how to use the key-value web service.

## Requirements

```bash
# Basic requirements
pip install requests

# For encryption examples
pip install cryptography

# For clipboard sync
pip install pyperclip

# For webhook receiver
pip install flask

# For Raspberry Pi DHT sensors (optional)
pip install adafruit-circuitpython-dht
```

## Examples

### 1. Basic Example (`basic_example.py`)

Demonstrates basic operations:
- Generate a memorable token
- Store JSON data
- Retrieve data
- Update data

**Usage:**
```bash
python basic_example.py
```

### 2. Encrypted Example (`encrypted_example.py`)

Shows client-side encryption for sensitive data:
- Encrypt data before sending to server
- Store encrypted payload
- Decrypt on retrieval
- Server cannot read your data

**Usage:**
```bash
python encrypted_example.py
```

### 3. IP Tracker (`ip_tracker.py`)

A practical service to track your external IP address:
- Detects your public IP automatically
- Stores with timestamp and history
- Monitor mode for continuous tracking
- Useful for dynamic IPs

**Usage:**

```bash
# Generate a token first
TOKEN="your-five-word-token"

# One-time IP update
python ip_tracker.py --token $TOKEN update

# Continuous monitoring (check every 5 minutes)
python ip_tracker.py --token $TOKEN monitor --interval 300

# Get stored IP data
python ip_tracker.py --token $TOKEN get
```

**Systemd Service Example:**

Create `/etc/systemd/system/ip-tracker.service`:

```ini
[Unit]
Description=IP Address Tracker
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/examples/python
ExecStart=/usr/bin/python3 ip_tracker.py --token your-token --url https://your-domain.com monitor --interval 300
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable ip-tracker
sudo systemctl start ip-tracker
sudo systemctl status ip-tracker
```

### 4. Clipboard Sync (`clipboard_sync.py`) ⭐

Sync clipboard content between devices - super useful for daily workflows!

**Features:**
- Copy text on one device, paste on another
- Monitor mode for automatic sync
- Cross-platform (Linux, macOS, Windows)
- Push or pull modes

**Usage:**

```bash
TOKEN="your-five-word-token"

# Push local clipboard to cloud
python clipboard_sync.py --token $TOKEN push

# Pull cloud clipboard to local
python clipboard_sync.py --token $TOKEN pull

# Auto-sync mode (push on local clipboard change)
python clipboard_sync.py --token $TOKEN monitor --interval 2

# Auto-pull mode (pull when cloud clipboard changes)
python clipboard_sync.py --token $TOKEN monitor --mode pull --interval 5

# Check status
python clipboard_sync.py --token $TOKEN status
```

**Workflow Example:**
```bash
# On computer A:
echo "Important command: docker ps -a" | xclip -selection c
python clipboard_sync.py --token $TOKEN push

# On computer B:
python clipboard_sync.py --token $TOKEN pull
# Now paste - the text is in your clipboard!
```

### 5. One-Time Secret (`one_time_secret.py`) ⭐

Share passwords and API keys securely - they self-destruct after being read once.

**Features:**
- Auto-delete after first read
- Optional password protection
- Expiration time (TTL)
- Client-side encryption

**Usage:**

```bash
# Create a one-time secret
python one_time_secret.py create "Database password: MySecretPass123"

# With password protection
python one_time_secret.py create "API Key: sk_live_123" --prompt-password

# With expiration (1 hour = 3600 seconds)
python one_time_secret.py create "Temp token" --ttl 3600

# Read a secret
python one_time_secret.py read your-five-word-token

# Read with password
python one_time_secret.py read your-five-word-token --prompt-password
```

**Real-world Example:**
```bash
# Share SSH private key temporarily
python one_time_secret.py create "$(cat ~/.ssh/id_rsa)" --password MyPass --ttl 1800

# Send token to colleague via Slack/email
# They read it once, then it's gone forever
```

### 6. Sensor Dashboard (`sensor_dashboard.py`) ⭐

Track IoT sensor data - perfect for Raspberry Pi projects!

**Features:**
- Log temperature, humidity, pressure
- Automatic statistics (min, max, avg)
- Alert thresholds
- DHT22/DHT11 sensor support
- Custom sensor commands

**Usage:**

```bash
TOKEN="your-five-word-token"

# Manual logging
python sensor_dashboard.py --token $TOKEN log --temp 23.5 --humidity 45.2

# View current readings
python sensor_dashboard.py --token $TOKEN view

# View statistics
python sensor_dashboard.py --token $TOKEN stats

# View history
python sensor_dashboard.py --token $TOKEN view --history 10

# Raspberry Pi - Monitor DHT22 sensor on GPIO pin 4
python sensor_dashboard.py --token $TOKEN monitor --dht-pin 4 --interval 300

# Custom sensor command (outputs JSON)
python sensor_dashboard.py --token $TOKEN monitor \
  --command "python read_my_sensor.py" --interval 60
```

**Custom Sensor Script Example:**

Create `read_my_sensor.py`:
```python
#!/usr/bin/env python3
import json
import random

# Read your actual sensor here
temperature = random.uniform(20, 25)
humidity = random.uniform(40, 60)

print(json.dumps({
    "temperature": temperature,
    "humidity": humidity
}))
```

### 7. Webhook Receiver (`webhook_receiver.py`) ⭐

Catch webhooks from GitHub, Stripe, etc. without deploying a server!

**Features:**
- Local webhook receiver
- Store and view payloads
- Works with any webhook provider
- Great for debugging

**Usage:**

```bash
TOKEN="your-five-word-token"

# Start webhook server
python webhook_receiver.py --token $TOKEN serve --port 5000

# Expose to internet with ngrok (in another terminal)
ngrok http 5000

# Configure your webhook provider to send to:
# https://your-ngrok-url/webhook/YOUR-TOKEN

# View received webhooks
python webhook_receiver.py --token $TOKEN list

# View specific webhook
python webhook_receiver.py --token $TOKEN view 0

# Send test webhook
python webhook_receiver.py --token $TOKEN test
```

**Example with GitHub:**
1. Start receiver: `python webhook_receiver.py --token $TOKEN serve`
2. Expose with ngrok: `ngrok http 5000`
3. Go to GitHub repo → Settings → Webhooks
4. Add webhook URL: `https://abc123.ngrok.io/webhook/YOUR-TOKEN`
5. Push to repo and see webhooks appear!

## Configuration

All examples default to `http://localhost:3000`. To use a different URL:

1. Edit `API_URL` in each file, or
2. Pass `--url` parameter (for ip_tracker.py)

**For production:**
```python
API_URL = "https://your-domain.com"
```

## Security Notes

- **Basic Example**: Data is stored unencrypted on the server
- **Encrypted Example**: Data is encrypted client-side; server never sees plaintext
- **IP Tracker**: Stores public IP (not sensitive), but you can combine with encryption
- **Clipboard Sync**: Clipboard content is stored as-is; use encryption for sensitive data
- **One-Time Secret**: Uses client-side encryption with password-based key derivation
- **Sensor Dashboard**: Sensor data typically not sensitive, stored unencrypted
- **Webhook Receiver**: Webhook payloads stored unencrypted; inspect before sharing tokens

## Common Issues

**Rate Limiting:**
- Free tier: 10 requests/minute per IP
- If you hit limits, wait and retry

**Connection Errors:**
- Ensure the API server is running
- Check the API_URL is correct
- Verify network connectivity

**Token Not Found:**
- Token must be stored before retrieval
- Tokens are case-sensitive
- Use exact 5-word token from generation
