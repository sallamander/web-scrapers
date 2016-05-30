"""A module to help out with storing web scraping info. 

This module currently provides a couple of helper functions for storing scraping results in mongo. Only one is meant to be called directly - `store_in_mongo`. 
"""

from pymongo import MongoClient

def store_in_mongo(lst_of_dcts, db_name, collection_name, key=None): 
    """Store the list of dictionaries in Mongo. 

    Store the `lst_of_dcts` in Mongo, by an inputted `key` if passed in. 

    Args: 
    ----
        lst_of_dicts: list of dictionaries 
        db_name: str
        collection_name: str
        key (optional): str
            Key to use to line up the dictionaries with a particular document that
            may already exist in Mongo. 
    """
    
    client = MongoClient()
    db = client[db_name]
    collection = db[collection_name]
    
    if key is not None: 
        _store_in_mongo_by_key(lst_of_dcts, collection, key)
    else: 
        # Check if the length is one, in which case we need to use insert_one. 
        # Otherwise, make sure that it's not empty (i.e. the `elif` statement) 
        # below, and then insert many. If it's empty, don't do anything and close
        # the client. 
        if len(lst_of_dcts) == 1: 
            collection.insert_one(lst_of_dcts[0])
        elif lst_of_dcts: 
            collection.insert_many(lst_of_dcts)

    client.close()

def _store_in_mongo_by_key(lst_of_dcts, mongo_client, key):
    """Store the list of dictionaries in Mongo, by key. 

    This is a helper function to `store_in_mongo` that is used to line up each
    dictionary that is being inserted into Mongo with an already existent document
    in the Mongo collection. Use the inputted `key` parameter to do so. 

    Args: 
    ----
        lst_of_dcts: list of dictionaries
        mongo_client: MongoClient()
        key: str
    """ 

    for dct in lst_of_dcts: 
        key_value = dct[key]
        # Not the most efficient way, but this allows it to be really general. 
        for k, v in dct.items():
            res = mongo_client.find({key: key_value})
            mongo_client.update_one({key: key_value}, {'$set': {k :v}})
