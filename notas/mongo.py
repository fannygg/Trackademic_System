from pymongo import MongoClient
from django.conf import settings 

def get_collection(collection_name):
    client = MongoClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB_NAME]  # Aquí seleccionas la base de datos según el nombre que se mande
    collection = db[collection_name]  # Aquí seleccionas la colección según el nombre que se mande
    return collection
