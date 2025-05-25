import pymongo
from config import MONGO_URI


clusters={
    'gxh':{'uri':MONGO_URI}
}
class MongoHelper(object):
    def __init__(self,cluster_name='gxh'):
        self.uri = clusters[cluster_name]['uri']
        self.client = pymongo.MongoClient(self.uri)
    def exits(self):
        self.client.close()
    def save_(self,collection,data):
        db = self.client.get_default_database()
        collection = db[collection]
        collection.insert_many(data)

