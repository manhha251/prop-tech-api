import os
from dotenv import load_dotenv
import pymongo
from pymongo.errors import ConnectionFailure

load_dotenv()

connection_string = os.getenv('CONNECTION_STRING')
client = pymongo.MongoClient(connection_string)
print('Cluster connection successful')


def connect_database(database_name: str):
    try:
        return client[database_name]
    except ConnectionFailure as e:
        print("Connection Failed")
        return e


def get_collection(database_name: str, collection_name: str):
    db = connect_database(database_name)
    return db[collection_name]
