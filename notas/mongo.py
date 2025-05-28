from pymongo import MongoClient

def get_collection(collection_name):
    client = MongoClient(settings.MONGO_URI)
    db = client["mi_basedatos"]
    collection = db[settings.MONGO_DB_NAME]  # Aquí seleccionas la colección según el nombre que se mande
    return collection
