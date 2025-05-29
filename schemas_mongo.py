from pymongo import MongoClient
from genson import SchemaBuilder
import json
import os
from datetime import datetime, timezone

MONGO_URI = "mongodb+srv://trackademic_user:k7gi34Yk0eHmfS4S@cluster0.fo0dqxz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
MONGO_DB_NAME = "trackademic"
OUTPUT_DIR = "mongo_schemas"

def datetime_to_iso8601(dt):
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()

def convert_dates(obj):
    """
    Recursively convierte objetos datetime dentro de dicts/listas a strings ISO 8601
    """
    if isinstance(obj, dict):
        return {k: convert_dates(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_dates(i) for i in obj]
    elif isinstance(obj, datetime):
        return datetime_to_iso8601(obj)
    else:
        return obj

def main():
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB_NAME]

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    collections_to_process = [
        "evaluation_plans",
        "comments",
        "grades",
        "students"
        
    ]

    for collection_name in collections_to_process:
        print(f"Procesando colección: {collection_name}")
        collection = db[collection_name]

        builder = SchemaBuilder()
        cursor = collection.find().limit(100)

        for doc in cursor:
            doc.pop("_id", None)  # Quitar el _id para no incluirlo en el esquema
            doc = convert_dates(doc)  # Convertir datetime a string ISO8601
            builder.add_object(doc)

        schema = builder.to_schema()

        output_path = os.path.join(OUTPUT_DIR, f"{collection_name}_schema.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)

        print(f"Esquema guardado en: {output_path}\n")

    print("Todos los esquemas han sido generados correctamente.")

if __name__ == "__main__":
    main()
