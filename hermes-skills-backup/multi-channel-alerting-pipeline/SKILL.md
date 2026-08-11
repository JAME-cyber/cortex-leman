---
name: multi-channel-alerting-pipeline
category: devops
description: Build multi-channel notification pipelines with threshold calibration, retry logic, and email integration. Supports Telegram, Discord, Email (HTML), and JSON export. Includes ProtonMail Bridge and Gmail SMTP setup guides.

---

# Multi-Channel Alerting Pipeline

## RÔLE

Système de notification multi-channel pour alertes automatisées. Construit des pipelines complets: data collection → analysis → scoring → alerting via Email, Telegram, Discord, JSON.

**Use Cases:**
- Veille technologique (ArXiv, RSS, APIs)
- Monitoring infrastructure
- Compliance alerts
- Social media tracking
- Any time-series data with threshold-based alerting

---

## ARCHITECTURE

```
Data Source (API/DB/File)
    ↓
Collection Script (batch/streaming)
    ↓
Processing (parse/transform/score)
    ↓
Threshold Check (calibrated on real data)
    ↓
Alert Generator (format per channel)
    ↓
Multi-Channel Dispatcher
    ├─→ Email (HTML responsive)
    ├─→ Telegram (Markdown)
    ├─→ Discord (Embeds)
    └─→ JSON (Grafana/Analytics)
```

---

## PATTERN: THRESHOLD CALIBRATION

### Problem
Arbitrary thresholds (e.g., "80% relevance") often result in 0 alerts or false positives.

### Solution: Calibrate on Production Data

```python
# Step 1: Collect production data
papers = get_all_papers()
relevances = [p['relevance_score'] for p in papers]

# Step 2: Calculate statistics
import numpy as np
max_relevance = max(relevances)
avg_relevance = np.mean(relevances)
percentile_90 = np.percentile(relevances, 90)

# Step 3: Set threshold based on data
# Instead of arbitrary 0.8 (80%), use top 10%
THRESHOLD = percentile_90  # e.g., 0.15 based on real data

# Step 4: Document rationale
# "Threshold: 0.15 (90th percentile, based on 65 production samples)"
```

### Benefits
- Based on actual data distribution
- Adapts to domain characteristics
- Prevents 0 alerts or alert fatigue
- Documentable for stakeholders

---

## PATTERN: RATE LIMITING WITH EXPONENTIAL BACKOFF

### Problem
External APIs (Semantic Scholar, Twitter, etc.) have rate limits. Naive retry = permanent failure.

### Solution: Exponential Backoff

```python
import time
import requests

def api_call_with_retry(url, max_retries=3, base_delay=5):
    """API call with exponential backoff for rate limiting"""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                # Rate limit - exponential backoff
                wait_time = base_delay * (2 ** attempt)  # 5s, 10s, 20s
                print(f"Rate limited. Waiting {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            elif response.status_code == 404:
                # Not found - don't retry
                return None
            else:
                print(f"HTTP {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 1s, 2s, 4s
                time.sleep(wait_time)
    
    return None
```

### Benefits
- Handles rate limits gracefully
- Prevents API blocking
- Configurable retries and delays
- Logs attempts for debugging

---

## PATTERN: MULTI-CHANNEL ALERTING

### Problem
Different channels require different formats and error handling. Hard-coded = brittle.

### Solution: Channel Abstraction

```python
import os
import smtplib
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class AlertChannel:
    """Base class for alert channels"""
    
    def __init__(self, config):
        self.config = config
        self.enabled = self._check_enabled()
    
    def _check_enabled(self):
        """Override to check if channel is configured"""
        return True
    
    def send(self, subject, body, data):
        """Override to implement sending logic"""
        raise NotImplementedError
    
    def format(self, subject, body, data):
        """Override to implement channel-specific formatting"""
        return body

class EmailChannel(AlertChannel):
    """HTML email notifications"""
    
    def _check_enabled(self):
        return bool(
            self.config.get('SMTP_USER') and 
            self.config.get('SMTP_PASSWORD')
        )
    
    def send(self, subject, body, data):
        """Send HTML email via SMTP"""
        msg = MIMEMultipart()
        msg['From'] = self.config['EMAIL_FROM']
        msg['To'] = self.config['EMAIL_TO']
        msg['Subject'] = f"[{self.config.get('APP_NAME', 'ALERT')}] {subject}"
        
        html_body = self.format(subject, body, data)
        msg.attach(MIMEText(html_body, 'html'))
        
        try:
            if self.config.get('SMTP_USE_TLS', False):
                server = smtplib.SMTP(self.config['SMTP_HOST'], self.config['SMTP_PORT'])
                server.starttls()
            else:
                server = smtplib.SMTP(self.config['SMTP_HOST'], self.config['SMTP_PORT'])
            
            server.login(self.config['SMTP_USER'], self.config['SMTP_PASSWORD'])
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            print(f"Email error: {e}")
            return False
    
    def format(self, subject, body, data):
        """Format as responsive HTML"""
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #667eea;">{subject}</h2>
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px;">
                {body}
            </div>
        </body>
        </html>
        """

class TelegramChannel(AlertChannel):
    """Markdown Telegram notifications"""
    
    def _check_enabled(self):
        return bool(
            self.config.get('TELEGRAM_BOT_TOKEN') and 
            self.config.get('TELEGRAM_CHAT_ID')
        )
    
    def send(self, subject, body, data):
        """Send Markdown message via Telegram Bot API"""
        url = f"https://api.telegram.org/bot{self.config['TELEGRAM_BOT_TOKEN']}/sendMessage"
        message = self.format(subject, body, data)
        
        try:
            response = requests.post(url, json={
                "chat_id": self.config['TELEGRAM_CHAT_ID'],
                "text": message,
                "parse_mode": "Markdown"
            }, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Telegram error: {e}")
            return False
    
    def format(self, subject, body, data):
        """Format as Markdown"""
        return f"🚨 *{subject}*\n\n{body}"

class DiscordChannel(AlertChannel):
    """Rich Discord embed notifications"""
    
    def _check_enabled(self):
        return bool(self.config.get('DISCORD_WEBHOOK_URL'))
    
    def send(self, subject, body, data):
        """Send embed via Discord webhook"""
        embed = {
            "title": subject,
            "description": body[:4096],  # Discord limit
            "color": 0xFF6B6B,
            "timestamp": datetime.now().isoformat(),
            "fields": []
        }
        
        # Add data fields
        for key, value in data.items()[:10]:
            embed["fields"].append({
                "name": str(key),
                "value": str(value)[:1024],  # Field value limit
                "inline": True
            })
        
        try:
            response = requests.post(
                self.config['DISCORD_WEBHOOK_URL'],
                json={"embeds": [embed]},
                timeout=10
            )
            return response.status_code in [200, 204]
        except Exception as e:
            print(f"Discord error: {e}")
            return False

class JSONChannel(AlertChannel):
    """JSON export for analytics/Grafana"""
    
    def send(self, subject, body, data):
        """Save to JSON file"""
        import json
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = f"{self.config.get('JSON_DIR', './alerts')}/alert_{timestamp}.json"
        
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump({
                    'subject': subject,
                    'body': body,
                    'data': data,
                    'timestamp': datetime.now().isoformat()
                }, f, indent=2)
            return True
        except Exception as e:
            print(f"JSON error: {e}")
            return False

class AlertDispatcher:
    """Multi-channel alert dispatcher"""
    
    def __init__(self, config):
        self.channels = [
            EmailChannel(config),
            TelegramChannel(config),
            DiscordChannel(config),
            JSONChannel(config)
        ]
    
    def dispatch(self, subject, body, data=None):
        """Send alert via all configured channels"""
        data = data or {}
        results = {}
        
        for channel in self.channels:
            if channel.enabled:
                success = channel.send(subject, body, data)
                results[channel.__class__.__name__] = success
                print(f"{'✅' if success else '❌'} {channel.__class__.__name__}")
            else:
                print(f"⏸️  {channel.__class__.__name__} (not configured)")
        
        return results

# Usage
config = {
    'APP_NAME': 'MyApp',
    'SMTP_HOST': 'smtp.gmail.com',
    'SMTP_PORT': '587',
    'SMTP_USER': 'user@gmail.com',
    'SMTP_PASSWORD': 'app_password',
    'EMAIL_FROM': 'user@gmail.com',
    'EMAIL_TO': 'recipient@example.com',
    'SMTP_USE_TLS': True,
    'TELEGRAM_BOT_TOKEN': os.environ.get('TELEGRAM_BOT_TOKEN'),
    'TELEGRAM_CHAT_ID': os.environ.get('TELEGRAM_CHAT_ID'),
    'DISCORD_WEBHOOK_URL': os.environ.get('DISCORD_WEBHOOK_URL'),
    'JSON_DIR': './alerts'
}

dispatcher = AlertDispatcher(config)
dispatcher.dispatch(
    "Alert Subject",
    "Alert body with details",
    {'metric': 123, 'threshold': 100}
)
```

### Benefits
- Clean separation of concerns
- Easy to add new channels
- Graceful degradation (unconfigured channels skipped)
- Consistent error handling

---

## PATTERN: PROTONMAIL BRIDGE INTEGRATION

### Problem
ProtonMail requires Bridge for SMTP access. Bridge needs paid account + local setup.

### Solution: Fallback Strategy

```bash
# Check if ProtonMail Bridge is viable
if protonmail_account_is_free():
    # Fallback 1: Gmail SMTP
    configure_gmail_smtp()
elif protonmail_bridge_not_installed():
    # Provide detailed setup guide
    print_protonmail_bridge_installation_guide()
else:
    # Use ProtonMail Bridge
    configure_protonmail_bridge()
```

### ProtonMail Bridge Setup (Linux)

```bash
# 1. Download and install
wget https://proton.me/download/bridge/protonmail-bridge_3.13.0-1_amd64.deb
sudo dpkg -i protonmail-bridge_3.13.0-1_amd64.deb
sudo apt --fix-broken install -y

# 2. Configure with CLI
protonmail-bridge --cli
login your_email@protonmail.com
# Enter password + 2FA code
info  # Copy the "Bridge password"

# 3. Verify bridge is running
ps aux | grep protonmail-bridge
netstat -tlnp | grep 1025

# 4. Configure application
export SMTP_HOST="127.0.0.1"
export SMTP_PORT="1025"
export SMTP_USER="your_email@protonmail.com"
export SMTP_PASSWORD="BRIDGE_PASSWORD_FROM_STEP_2"
export EMAIL_FROM="your_email@protonmail.com"
export SMTP_USE_TLS="false"
```

### Critical Learnings

**ProtonMail Bridge Requirements:**
- ✅ Paid account required (ProtonMail Plus 5€/mois minimum)
- ✅ Local installation needed (CLI or GUI)
- ✅ Bridge runs on 127.0.0.1:1025 by default
- ❌ Free accounts get HTTP 422 error

**Troubleshooting:**
```bash
# Check if bridge is running
ps aux | grep protonmail-bridge

# Check if port is open
netstat -tlnp | grep 1025

# View bridge logs
journalctl -u protonmail-bridge -f

# Restart bridge
sudo systemctl restart protonmail-bridge
```

---

## FULL WORKFLOW EXAMPLE

### Complete ArXiv Research Alerting Pipeline

```python
#!/usr/bin/env python3
"""
Multi-channel alerting pipeline for ArXiv research
"""

import sqlite3
import requests
from datetime import datetime, timedelta
from pathlib import Path

# 1. COLLECTION: Scan ArXiv
def scan_arxiv():
    """Scan ArXiv for papers in target domains"""
    domains = {
        'gdpr': 'ti:GDPR OR ti:privacy OR ti:compliance',
        'ai_act': 'ti:AI Act OR ti:AI regulation',
        'vision': 'ti:deepfake OR ti:document verification',
        'ocr': 'ti:OCR OR ti:document analysis'
    }
    
    all_papers = []
    for domain, query in domains.items():
        url = f"https://export.arxiv.org/api/query?search_query={query}&max_results=10"
        papers = parse_arxiv_xml(requests.get(url).text)
        all_papers.extend(papers)
    
    return all_papers

# 2. PROCESSING: Score relevance
def score_relevance(papers):
    """Score papers for Cortex Leman relevance (0-1)"""
    KEYWORDS = {
        'gdpr': ['RGPD', 'GDPR', 'privacy', 'compliance'],
        'ai_act': ['AI Act', 'AI regulation', 'AI governance'],
        'vision': ['deepfake', 'document verification'],
        'ocr': ['OCR', 'text recognition', 'document analysis']
    }
    
    for paper in papers:
        title_lower = paper['title'].lower()
        score = 0.0
        for domain, keywords in KEYWORDS.items():
            for kw in keywords:
                if kw.lower() in title_lower:
                    score += 0.05
        paper['relevance_score'] = min(score, 1.0)
    
    return papers

# 3. THRESHOLD CHECKING: Calibrated on real data
def get_alert_papers(papers, threshold=0.15):
    """Filter papers above threshold (calibrated on production data)"""
    return [p for p in papers if p['relevance_score'] >= threshold]

# 4. ALERT GENERATION: Multi-channel
def generate_alerts(papers, dispatcher):
    """Send alerts via all configured channels"""
    if not papers:
        print("✅ No papers to alert")
        return
    
    # Format alert
    subject = f"ArXiv Alert - {len(papers)} papers détectés"
    
    body_lines = [f"📊 **{len(papers)}** papers high relevance:\n"]
    for i, paper in enumerate(papers[:5], 1):
        body_lines.append(
            f"{i}. [{paper['relevance_score']:.2f}] {paper['title'][:60]}\n"
            f"   arXiv: {paper['arxiv_id']} | {paper['domain']}"
        )
    body = "\n".join(body_lines)
    
    # Dispatch to all channels
    data = {'papers': [{'title': p['title'], 'arxiv_id': p['arxiv_id']} for p in papers]}
    dispatcher.dispatch(subject, body, data)

# Main pipeline
def main():
    # Load config
    config = load_config_from_env()
    
    # Initialize dispatcher
    dispatcher = AlertDispatcher(config)
    
    # Run pipeline
    papers = scan_arxiv()
    papers = score_relevance(papers)
    alert_papers = get_alert_papers(papers, threshold=0.15)
    generate_alerts(alert_papers, dispatcher)

if __name__ == "__main__":
    main()
```

---

## PITFALLS TO AVOID

### 1. URL Encoding in API Requests

**Problem:** Spaces in query strings fail
```python
# WRONG - spaces not encoded
url = f"https://api.example.com/search?q=AI Act OR AI regulation"
```

**Solution:** Proper URL encoding
```python
# CORRECT - use urllib.parse.quote
from urllib.parse import quote
query = quote("AI Act OR AI regulation", safe='')
url = f"https://api.example.com/search?q={query}"
```

### 2. Import Scope Issues

**Problem:** `datetime` imported inside function, used outside
```python
def main():
    from datetime import datetime
    print(datetime.now())  # OK

# LATER IN CODE
print(datetime.now())  # NameError: name 'datetime' is not defined
```

**Solution:** Import at module level
```python
from datetime import datetime  # At top of file

def main():
    print(datetime.now())  # OK

# LATER IN CODE
print(datetime.now())  # OK
```

### 3. Missing JSON Import

**Problem:** `json` used but not imported
```python
# Inside function - json.dump() used
def save_report(data):
    with open('report.json', 'w') as f:
        json.dump(data, f, indent=2)  # NameError
```

**Solution:** Import at module level
```python
import json  # At top of file

def save_report(data):
    with open('report.json', 'w') as f:
        json.dump(data, f, indent=2)  # OK
```

### 4. Cron Job Environment Variables

**Problem:** Cron runs with minimal PATH, no env vars
```bash
# In script - assumes env vars are set
export SMTP_USER="user@example.com"
python3 script.py  # Works when run manually
```

**Solution:** Source env file in cron
```bash
# In crontab
0 6 * * * source ~/.hermes/skills/myproject/.env && python3 script.py
```

Or use absolute paths:
```python
# In Python - don't rely on PATH
import os
config_path = os.path.expanduser('~/.hermes/skills/myproject/.env')
# Load config from absolute path
```

---

## CRON JOB SETUP

### Daily Pipeline Schedule

```bash
# ~/.hermes/cron/myproject.cron
# Run full pipeline daily at 6 AM CET

# 1. Data collection (6:00 AM)
0 6 * * * source ~/.hermes/skills/myproject/.env && python3 ~/.hermes/skills/myproject/scripts/collect.py >> ~/.hermes/cron/logs/collect.log 2>&1

# 2. Analysis (6:30 AM)
30 6 * * * source ~/.hermes/skills/myproject/.env && python3 ~/.hermes/skills/myproject/scripts/analyze.py >> ~/.hermes/cron/logs/analyze.log 2>&1

# 3. Scoring (7:00 AM)
0 7 * * * source ~/.hermes/skills/myproject/.env && python3 ~/.hermes/skills/myproject/scripts/score.py >> ~/.hermes/cron/logs/score.log 2>&1

# 4. Alerting (7:30 AM)
30 7 * * * source ~/.hermes/skills/myproject/.env && python3 ~/.hermes/skills/myproject/scripts/alert.py >> ~/.hermes/cron/logs/alert.log 2>&1
```

### Activate Cron Job
```bash
# Install cron
crontab ~/.hermes/cron/myproject.cron

# Verify
crontab -l

# Test manually
python3 ~/.hermes/skills/myproject/scripts/alert.py
```

---

## TESTING CHECKLIST

Before production deployment:

- [ ] **Collection**: Data fetched correctly from API/DB
- [ ] **Processing**: Parse errors handled, invalid data skipped
- [ ] **Scoring**: Relevance scores in expected range (0-1)
- [ ] **Thresholds**: Calibrated on production data
- [ ] **Email**: SMTP connection successful, test email received
- [ ] **Telegram**: Bot token valid, message sent
- [ ] **Discord**: Webhook URL valid, embed received
- [ ] **JSON**: File saved to correct directory
- [ ] **Cron**: Jobs scheduled, logs directory exists
- [ ] **Env vars**: All required variables set
- [ ] **Error handling**: Failures logged, pipeline continues

---

## INTEGRATION PATTERNS

### With Existing Systems

```python
# Example: Integrate with Cortex Leman agents
class CortexLemanAlertDispatcher(AlertDispatcher):
    """Extend with Cortex Leman specific logic"""
    
    def dispatch(self, subject, body, data):
        # Send to standard channels
        super().dispatch(subject, body, data)
        
        # Additional: Alert specific agents
        if 'compliance' in subject.lower():
            alert_agent('Le Gardien des Normes', subject, body)
        elif 'vision' in subject.lower():
            alert_agent('L\'Oeil de Cortex', subject, body)
```

### With Monitoring Systems

```python
# Example: Forward to Prometheus/Promtail
class PrometheusChannel(AlertChannel):
    """Send alerts to Prometheus Alertmanager"""
    
    def send(self, subject, body, data):
        url = f"{self.config['PROMETHEUS_URL']}/api/v1/alerts"
        alert = {
            "labels": {
                "alertname": subject,
                "severity": data.get('severity', 'warning')
            },
            "annotations": {
                "description": body
            }
        }
        
        response = requests.post(url, json=[alert], timeout=10)
        return response.status_code == 200
```

---

## REFERENCE IMPLEMENTATION

Full working implementation available in:
- `~/.hermes/skills/data-science/l-oeil-de-cortex/scripts/alert_papers.py`
- `~/.hermes/skills/data-science/l-oeil-de-cortex/config/notification_config.sh`
- `~/.hermes/skills/data-science/l-oeil-de-cortex/docs/PROTONMAIL_BRIDGE_SETUP.md`

**Key Files:**
- `alert_papers.py` (23KB) - Multi-channel dispatcher + HTML email formatter
- `notification_config.sh` - Template for Telegram, Discord, Email config
- `PROTONMAIL_BRIDGE_SETUP.md` - Comprehensive ProtonMail Bridge guide

---

**Multi-Channel Alerting = Production-Ready Notifications for Any Data Pipeline**

*Calibrate thresholds, handle rate limits, dispatch gracefully. Alert fatigue solved.*
