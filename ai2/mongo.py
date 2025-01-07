import pymongo
from pymongo import MongoClient
import os
import json
from datetime import datetime
from bson import ObjectId
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MongoDB connection URI
MONGO_URI = os.getenv("MONGO_URI")

def connect_to_mongodb(uri):
    client = MongoClient(uri)
    return client

def retrieve_data_from_mongodb(client, database_name, collection_name):
    db = client[database_name]
    collection = db[collection_name]
    
    # Retrieve data from the collection
    data = list(collection.find())
    
    return data

class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

def export_to_json(data, filename):
    # Create 'json' directory if it doesn't exist
    output_dir = 'json'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Write to JSON file using custom encoder
    output_path = os.path.join(output_dir, f'{filename}.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, cls=MongoJSONEncoder, ensure_ascii=False, indent=4)
    
    return output_path
    
    # Write to JSON file
    output_path = os.path.join(output_dir, f'{filename}.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    return output_path

if __name__ == "__main__":
    try:
        # Connect to MongoDB Atlas
        client = connect_to_mongodb(MONGO_URI)
        
        # Database and collection information
        database_name = "linkedin"
        collection_name = "comments_data_of_post_4"
        
        # Retrieve data from the specified collection
        data = retrieve_data_from_mongodb(client, database_name, collection_name)
        
        # Export data to JSON
        output_file = export_to_json(data, collection_name)
        print(f"Data exported successfully to: {output_file}")
        
    except Exception as e:
        print("An error occurred:", e)
    finally:
        client.close()