from pymongo import MongoClient

def store_in_mongo(lst_of_dcts, db_name, collection_name): 
    """Store the list of dictionaries in Mongo

    Args: 
        lst_of_dicts: List of dictionaries to insert into Mongo. 
        db_name: String - database name
        collection_name: String - collection name
    """
    
    client = MongoClient()
    db = client[db_name]
    collection = db[collection_name]
    
    if len(lst_of_dcts) == 1: 
        collection.insert_one(lst_of_dcts)
    else: 
        collection.insert_many(lst_of_dcts)
