from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')
database = client['example_database']

user_collection = database['users']
