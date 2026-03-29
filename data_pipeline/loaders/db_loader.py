import pandas as pd
from sqlalchemy import create_engine
from pymongo import MongoClient
import os

class DataLoader:
    def __init__(self, db_type="postgres"):
        self.db_type = db_type
        # In a real project, these should come from your config.py or .env file
        self.pg_url = "postgresql://username:password@localhost:5432/reddit_db"
        self.mongo_url = "mongodb://localhost:27017/"

    def load_to_postgres(self, csv_path, table_name):
        """Loads structured CSV data into a Postgres table."""
        try:
            df = pd.read_csv(csv_path)
            engine = create_engine(self.pg_url)
            
            # 'replace' will overwrite the table, 'append' will add to it
            df.to_sql(table_name, engine, if_exists='replace', index=False)
            print(f"✅ Successfully loaded {len(df)} rows to Postgres table: {table_name}")
        except Exception as e:
            print(f"❌ Postgres Load Error: {e}")

    def load_to_mongodb(self, csv_path, db_name, collection_name):
        """Loads CSV data as JSON documents into MongoDB."""
        try:
            df = pd.read_csv(csv_path)
            client = MongoClient(self.mongo_url)
            db = client[db_name]
            collection = db[collection_name]
            
            # Convert DataFrame to a list of dictionaries (JSON format)
            data_dict = df.to_dict(orient='records')
            
            collection.insert_many(data_dict)
            print(f"✅ Successfully loaded {len(data_dict)} documents to MongoDB: {collection_name}")
        except Exception as e:
            print(f"❌ MongoDB Load Error: {e}")

if __name__ == "__main__":
    loader = DataLoader()
    
    # Path to the data you just collected
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_file = os.path.join(BASE_DIR, "collectors", "reddit_data.csv")
    
    if os.path.exists(data_file):
        # Example 1: Load to MongoDB (Good for raw/unstructured data)
        loader.load_to_mongodb(data_file, "trend_db", "raw_reddit_posts")
        
        # Example 2: Load to Postgres (Good for cleaned/analyzed data)
        # loader.load_to_postgres(data_file, "cleaned_posts")
    else:
        print("Target CSV file not found. Run the collector first!")