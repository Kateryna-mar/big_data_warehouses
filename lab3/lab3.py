import json
import pymongo
from pymongo import MongoClient
from pymongo.database import Database

DB_NAME = "hospital_db"
COLLECTION_NAME = "inpatient_charges"
JSON_FILE_PATH = "hospitals_mongodb.json"

def init_database() -> Database:
    client = MongoClient("mongodb://localhost:27017/")
    return client[DB_NAME]

def import_dataset(database: Database, filepath: str = JSON_FILE_PATH) -> None:
    collection = database.get_collection(COLLECTION_NAME)
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)
            collection.delete_many({})
            if isinstance(data, list):
                collection.insert_many(data)
            else:
                collection.insert_one(data)
        print(f">> Dani uspishno importovano. Dokumentiv: {collection.count_documents({})}")
    except FileNotFoundError:
        print(f"File {filepath} not found.")

def step1_count(database: Database) -> None:
    records = database.get_collection(COLLECTION_NAME)
    pipeline = [
        {"$group": {"_id": None, "total_count": {"$sum": 1}}}
    ]
    res = records.aggregate(pipeline)
    result = res.try_next() or {"total_count": 0}
    print(f">> Step 1 | Count: {result['total_count']}")

def step2_max_overall(database: Database) -> None:
    records = database.get_collection(COLLECTION_NAME)
    pipeline = [
        {
            "$group": {
                "_id": None,
                "maxCoveredCharges": {"$max": "$Average_Covered_Charges"}
            }
        }
    ]
    res = records.aggregate(pipeline)
    result = res.try_next() or {"maxCoveredCharges": 0}
    print(f">> Step 2 | Max Average_Covered_Charges: {result['maxCoveredCharges']}")

def step3_max_by_drg(database: Database) -> None:
    records = database.get_collection(COLLECTION_NAME)
    out_collection = "records_step3_max_drg"
    pipeline = [
        {
            "$group": {
                "_id": "$DRG_Definition",
                "maxCoveredCharges": {"$max": "$Average_Covered_Charges"}
            }
        },
        {
            "$sort": {"maxCoveredCharges": pymongo.DESCENDING}
        },
        {
            "$out": out_collection
        }
    ]
    records.aggregate(pipeline)
    print(f">> Step 3 | Done. Saved to '{out_collection}'.")
    for doc in database[out_collection].find().limit(5):
        print(f"   {doc['_id']} -> {doc['maxCoveredCharges']}")

def step4_max_by_drg_gt(database: Database, gt_val: float = 100000) -> None:
    records = database.get_collection(COLLECTION_NAME)
    out_collection = "records_step4_max_gt"
    pipeline = [
        {
            "$group": {
                "_id": "$DRG_Definition",
                "maxCoveredCharges": {"$max": "$Average_Covered_Charges"}
            }
        },
        {
            "$match": {"maxCoveredCharges": {"$gt": gt_val}}
        },
        {
            "$sort": {"maxCoveredCharges": pymongo.DESCENDING}
        },
        {
            "$out": out_collection
        }
    ]
    records.aggregate(pipeline)
    print(f">> Step 4 | Done (> {gt_val}). Saved to '{out_collection}'.")
    for doc in database[out_collection].find().limit(5):
        print(f"   {doc['_id']} -> {doc['maxCoveredCharges']}")

def step5_filter_input_and_output(database: Database, gt_val: float = 80000, input_lt: float = 150000) -> None:
    records = database.get_collection(COLLECTION_NAME)
    out_collection = "records_step5_final"
    pipeline = [
        {
            "$match": {"Average_Covered_Charges": {"$lt": input_lt}}
        },
        {
            "$group": {
                "_id": "$DRG_Definition",
                "maxCoveredCharges": {"$max": "$Average_Covered_Charges"}
            }
        },
        {
            "$match": {"maxCoveredCharges": {"$gt": gt_val}}
        },
        {
            "$sort": {"maxCoveredCharges": pymongo.DESCENDING}
        },
        {
            "$out": out_collection
        }
    ]
    records.aggregate(pipeline)
    print(f">> Step 5 | Done (< {input_lt} & > {gt_val}). Saved to '{out_collection}'.")
    for doc in database[out_collection].find().limit(5):
        print(f"   {doc['_id']} -> {doc['maxCoveredCharges']}")

if __name__ == "__main__":
    db = init_database()

    print("\n--- Start MongoDB Aggregations ---")
    step1_count(db)
    step2_max_overall(db)
    step3_max_by_drg(db)
    step4_max_by_drg_gt(db, gt_val=100000)
    step5_filter_input_and_output(db, gt_val=80000, input_lt=150000)