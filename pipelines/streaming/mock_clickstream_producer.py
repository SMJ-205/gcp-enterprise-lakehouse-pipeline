import time
import json
import random
import datetime
import os
from google.cloud import pubsub_v1

# Setup service account path relative to workspace if running locally
SA_KEY_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../gcp-sa-key.json"))
if os.path.exists(SA_KEY_PATH):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SA_KEY_PATH

PROJECT_ID = "gcp-pde-project-505510"
TOPIC_ID = "clickstream-events"

def publish_mock_events(num_events=50):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)
    
    event_types = ["view_item", "add_to_cart", "click", "search", "checkout"]
    user_ids = [f"user_{random.randint(1000, 1100)}" for _ in range(20)]
    
    print(f"Publishing {num_events} clickstream events to topic {topic_path}...")
    
    for i in range(num_events):
        event = {
            "user_id": random.choice(user_ids),
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "event_type": random.choice(event_types),
            "session_id": f"sess_{random.randint(100000, 999999)}"
        }
        
        data = json.dumps(event).encode("utf-8")
        future = publisher.publish(topic_path, data)
        print(f"Published event {i+1}/{num_events}: {event['user_id']} - {event['event_type']} - Message ID: {future.result()}")
        
        # Micro-sleep to distribute timestamps slightly
        time.sleep(random.uniform(0.05, 0.2))

if __name__ == "__main__":
    publish_mock_events()
