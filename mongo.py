import json
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv

load_dotenv()

def test_mongo_connection(mongo_uri, json_folder_path, DB_NAME):
    try:
        # Établit la connexion avec MongoDB
        client = MongoClient(mongo_uri)
        print("Connection successful!")
        
        json_files = [os.path.join(json_folder_path, f) for f in os.listdir(json_folder_path) 
                     if f.endswith('.json')]
        
        save_json_files_to_mongo(json_files, mongo_uri, DB_NAME)

    except Exception as e:
        print("Connection failed:", e)
        
#Convertit les fichiers JSON en documents MongoDB
def save_json_files_to_mongo(json_files, connection_string, DB_NAME):
    try:
        client = MongoClient(
            connection_string,
            server_api=ServerApi('1')
        )
        
        db = client[DB_NAME]
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                collection_name = os.path.splitext(os.path.basename(json_file))[0]
                collection = db[collection_name]
                
                if isinstance(data, list):
                    collection.insert_many(data)
                else:
                    collection.insert_one(data)
                    
                print(f"Successfully imported {json_file} into collection {collection_name}")
                
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON file {json_file}: {str(e)}")
                print(f"Error occurred at line {e.lineno}, column {e.colno}")
                
            except Exception as e:
                print(f"Error processing file {json_file}: {str(e)}")
                if 'bad auth' in str(e):
                    print("Authentication failed. Please check your MongoDB credentials.")
        
    except Exception as e:
        print(f"MongoDB connection error: {str(e)}")
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    mongo_uri = os.getenv("MONGO_URI")
    json_folder_path = 'json'  
    DB_NAME = os.getenv("DB_NAME")

    test_mongo_connection(mongo_uri, json_folder_path, DB_NAME)