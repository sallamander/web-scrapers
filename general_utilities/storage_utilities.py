from pymongo import MongoClient

def store_in_mongo(lst_of_dcts, db_name, collection_name, key=None): 
    """Store the list of dictionaries in Mongo

    Args: 
        lst_of_dicts: List of dictionaries to insert into Mongo. 
        db_name: String - database name
        collection_name: String - collection name
    """
    
    client = MongoClient()
    db = client[db_name]
    collection = db[collection_name]
    
    if key is not None: 
        store_in_mongo_by_key(lst_of_dcts, collection, key)
    else: 
        if len(lst_of_dcts) == 1: 
            collection.insert_one(lst_of_dcts[0])
        else: 
            collection.insert_many(lst_of_dcts)

def store_in_mongo_by_key(lst_of_dcts, mongo_client, key):
    '''
    Input: List, String, List
    Output: Data saved to Mongo
    '''

    for dct in lst_of_dcts: 
        key_value = dct[key]
        # Not the most efficient way to do this, but this allows it 
        # to be really general. 
        for k, v in dct.iteritems():
            mongo_client.update_one({key: key_value}, {'$set': {k :v}})
