from mongo_helper import MongoHelper

def split_collection_into_parts(db, source_collection_name, target_collection_base_name, parts=5):
    source_collection = db[source_collection_name]
    total_documents = source_collection.count_documents({})
    documents_per_part = total_documents // parts
    remainder = total_documents % parts # 还多出多少个

    cursor = source_collection.find()
    for part in range(parts):
        target_collection_name = f"{target_collection_base_name}_{part + 1}"
        target_collection = db[target_collection_name]
        
        # 计算当前部分的文档数量
        current_part_size = documents_per_part + (1 if part < remainder else 0)
        
        # 批量插入当前部分的文档
        documents_to_insert = []
        for _ in range(current_part_size):
            try:
                doc = next(cursor)
                documents_to_insert.append(doc)
            except StopIteration:
                break
        
        if documents_to_insert:
            target_collection.insert_many(documents_to_insert)
            print(f"Inserted {len(documents_to_insert)} documents into {target_collection_name}")

def main():
    mongo = MongoHelper()
    client = mongo.client
    db = client['personalization']
    
    source_collection_name = "pereduAbstractEnglish"
    target_collection_base_name = "pereduAbstractEnglish_part"
    
    split_collection_into_parts(db, source_collection_name, target_collection_base_name)

if __name__ == '__main__':
    main()