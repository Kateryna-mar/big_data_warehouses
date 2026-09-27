import sys
import pymongo

client = pymongo.MongoClient('localhost', 27017)
db = client.store_db

while True:
    print("\n" + "="*50)
    print("Input collection (1 - Category, 2 - Product, 0 - Exit)")
    type_col_input = input().strip()
    
    if type_col_input == "0":
        print("Exit.")
        break
    
    if type_col_input not in ["1", "2"]:
        print("Error: Unknown collection!\n")
        continue

    type_col = int(type_col_input)

    if type_col == 1:
        collection = db.category
        print("\nInput action (1 - Insert, 2 - Update, 3 - Delete, 4 - Select)")
        type_act = int(input())

        if type_act == 1:
            new_category = {
                "name": input("\nInput name of category: "),
                "category_code": input("\nInput category code: "),
                "service": {
                    "name_of_service": input("\nInput name of service: "),
                    "price": int(input("\nInput service price: "))
                }
            }
            new_id = collection.insert_one(new_category).inserted_id
            print("Inserted new category !!!\n")
            print(collection.find_one({"_id": new_id}))

        elif type_act == 2:
            update_name = input("\nInput name for search: ")
            update_name_new = input("\nInput name for update: ")
            collection.update_one({"name": update_name}, {"$set": {"name": update_name_new}})
            print("Replaced name of category !!!\n")
            print(collection.find_one({"name": update_name_new}))

        elif type_act == 3:
            delete_name = input("\nInput name for delete: ")
            search_cat = collection.find_one({"name": delete_name})
            if search_cat:
                cat_code = search_cat["category_code"]
                print(cat_code)
                print("is in category_code")
                
                collection.delete_one({"name": delete_name})
                print("Deleted category !!!\n")
                
                rel_col = db.product
                res = rel_col.delete_many({"category_code": cat_code})
                print(f"Cascade deleted {res.deleted_count} products with category_code: {cat_code}")
                print(collection.find_one({"name": delete_name}))
            else:
                print("Category not found!")

        elif type_act == 4:
            print("All documents in collection category (sorted by name)\n")
            cursor = collection.find({}).sort("name", 1)
            for document in cursor:
                print(document)

    elif type_col == 2:
        collection = db.product
        print("\nInput action (1 - Insert, 2 - Update, 3 - Delete, 4 - Select)")
        type_act = int(input())

        if type_act == 1:
            new_prod = {
                "code": input("\nInput product code: "),
                "category_code": input("\nInput category code (link): "),
                "title": input("\nInput title of product: "),
                "price": int(input("\nInput price: "))
            }
            new_id = collection.insert_one(new_prod).inserted_id
            print("Inserted new product !!!\n")
            print(collection.find_one({"_id": new_id}))

        elif type_act == 2:
            update_code = input("\nInput product code for search: ")
            update_title_new = input("\nInput new title: ")
            collection.update_one({"code": update_code}, {"$set": {"title": update_title_new}})
            print("Replaced product title !!!\n")
            print(collection.find_one({"code": update_code}))

        elif type_act == 3:
            delete_code = input("\nInput product code for delete: ")
            collection.delete_one({"code": delete_code})
            print("Deleted !!!\n")
            print(collection.find_one({"code": delete_code}))

        elif type_act == 4:
            print("All documents in collection product (sorted by code)\n")
            cursor = collection.find({}).sort("code", 1)
            for document in cursor:
                print(document)