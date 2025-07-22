from google.cloud import pubsub_v1
import json
import time
import random
from datetime import datetime, timedelta
import uuid

# -------- CONFIG --------
PROJECT_ID = "consummate-fold-466316-c3"
TOPIC_ID = "orders-stream"
NUM_MESSAGES = 500
INTERVAL = 0.5
four_months_days = 120
# ------------------------

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

products = ['P001', 'P002', 'P003', 'P004']
regions = ['us-west', 'us-east', 'europe', 'asia']

for i in range(NUM_MESSAGES):
    # Random timestamp between now and 4 months ago
    random_days_ago = random.randint(0, four_months_days)
    random_seconds_ago = random.randint(0, 86400)  # seconds in a day
    
    event_time = datetime.utcnow() - timedelta(days=random_days_ago, seconds=random_seconds_ago)
    
    order = {
        "order_id": str(uuid.uuid4()),
        "product_id": random.choice(products),
        "timestamp": event_time.isoformat(),
        "amount": round(random.uniform(10.0, 500.0), 2),
        "region": random.choice(regions)
    }

    data = json.dumps(order).encode("utf-8")
    future = publisher.publish(topic_path, data=data)
    print(f"Published message {i+1}: {order}")
    time.sleep(INTERVAL)

print("✅ Finished sending messages.")
