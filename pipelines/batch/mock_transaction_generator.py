import os
import random
import datetime
import pyarrow as pa
import pyarrow.parquet as pq
from google.cloud import storage

# Setup service account path relative to workspace if running locally
SA_KEY_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../gcp-sa-key.json"))
if os.path.exists(SA_KEY_PATH):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SA_KEY_PATH

PROJECT_ID = "gcp-pde-project-505510"
BUCKET_NAME = f"{PROJECT_ID}-bronze-lakehouse"

def generate_and_upload_transactions(num_transactions=100):
    user_ids = [f"user_{random.randint(1000, 1100)}" for _ in range(20)]
    merchant_ids = [f"merchant_{random.randint(500, 520)}" for _ in range(10)]
    payment_methods = ["credit_card", "debit_card", "e_wallet", "bank_transfer"]
    statuses = ["COMPLETED", "COMPLETED", "COMPLETED", "FAILED", "PENDING"]
    
    data = []
    base_time = datetime.datetime.utcnow() - datetime.timedelta(days=1)
    
    for i in range(num_transactions):
        tx_time = base_time + datetime.timedelta(minutes=random.randint(0, 1440))
        tx = {
            "transaction_id": f"tx_{random.randint(10000000, 99999999)}",
            "user_id": random.choice(user_ids),
            "merchant_id": random.choice(merchant_ids),
            "amount": float(round(random.uniform(5.0, 500.0), 2)),
            "payment_method": random.choice(payment_methods),
            "status": random.choice(statuses),
            "transaction_timestamp": tx_time
        }
        data.append(tx)
        
    # Convert list of dicts to PyArrow Table
    schema = pa.schema([
        ("transaction_id", pa.string()),
        ("user_id", pa.string()),
        ("merchant_id", pa.string()),
        ("amount", pa.float64()),
        ("payment_method", pa.string()),
        ("status", pa.string()),
        ("transaction_timestamp", pa.timestamp('us'))
    ])
    
    # Restructure lists for pyarrow
    columns = {field.name: [] for field in schema}
    for item in data:
        for field in schema:
            columns[field.name].append(item[field.name])
            
    table = pa.Table.from_pydict(columns, schema=schema)
    
    # Save local Parquet file temporarily
    local_file = f"transactions_{base_time.strftime('%Y%m%d')}.parquet"
    pq.write_table(table, local_file)
    print(f"Generated local parquet file: {local_file}")
    
    # Upload to GCS
    print(f"Uploading {local_file} to GCS bucket {BUCKET_NAME}...")
    try:
        client = storage.Client(project=PROJECT_ID)
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"transactions/{local_file}")
        blob.upload_from_filename(local_file)
        print(f"Successfully uploaded {local_file} to gs://{BUCKET_NAME}/transactions/{local_file}")
    except Exception as e:
        print(f"Error uploading file to GCS: {e}")
    finally:
        # Cleanup local file
        if os.path.exists(local_file):
            os.remove(local_file)
            print(f"Cleaned up local file {local_file}")

if __name__ == "__main__":
    generate_and_upload_transactions()
