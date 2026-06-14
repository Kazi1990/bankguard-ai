Import requests
import random
import time
import urllib3
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SPLUNK_HEC_URL = "https://prd-p-7syl8.splunkcloud.com:8088/services/collector/event"
SPLUNK_TOKEN = "83a75bbb-52a8-4952-89c8-99ade7d37f4e"

accounts = ["ACC001", "ACC002", "ACC003", "ACC004", "ACC005"]
locations = ["Dhaka", "Chittagong", "London", "Dubai", "Unknown"]

transaction_history = {}

def detect_fraud(account_id, amount, location, hour):
    reasons = []
    
    if amount > 15000:
        reasons.append("Large amount")
    
    if location in ["Dubai", "Unknown"]:
        reasons.append("Suspicious location")
    
    if hour >= 0 and hour <= 5:
        reasons.append("Unusual hour")
    
    history = transaction_history.get(account_id, [])
    recent = [t for t in history if time.time() - t < 300]
    if len(recent) >= 3:
        reasons.append("Rapid transactions")
    
    return "SUSPICIOUS" if reasons else "NORMAL", reasons

def send_to_splunk(data):
    headers = {"Authorization": f"Splunk {SPLUNK_TOKEN}"}
    try:
        response = requests.post(SPLUNK_HEC_URL, 
                                json={"event": data}, 
                                headers=headers, 
                                verify=False, 
                                timeout=10)
        return response.status_code
    except Exception as e:
        print(f"Error: {e}")
        return None

print("BankGuard AI - Starting real-time monitoring...")

while True:
    account_id = random.choice(accounts)
    amount = random.randint(500, 25000)
    location = random.choice(locations)
    hour = datetime.now().hour
    
    if account_id not in transaction_history:
        transaction_history[account_id] = []
    transaction_history[account_id].append(time.time())
    
    status, reasons = detect_fraud(account_id, amount, location, hour)
    
    transaction = {
        "account_id": account_id,
        "amount": amount,
        "location": location,
        "hour": hour,
        "status": status,
        "fraud_reasons": reasons,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    result = send_to_splunk(transaction)
    print(f"[{status}] Account: {account_id} | Amount: {amount} | Location: {location} | Reasons: {reasons} | HTTP: {result}")
    
    time.sleep(2)