
import sys

sys.path.append('/home/zhengy/ScienceDataAnalyze')
from datasets import load_dataset

# 假设数据集的文件路径是 'path/to/your/file.parquet'

import json
from mongo_helper import MongoHelper
import logging
from datetime import datetime
from tqdm import tqdm
log_filename = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s: %(message)s',
                    handlers=[
                        logging.StreamHandler(),
                        logging.FileHandler(f'sci_pop_score_logfile_{log_filename}.log',encoding='utf-8')
                    ])


def main():
    mongo = MongoHelper()
    client = mongo.client
    db = client['personalization']  # 只用一个数据库
    base_collection_name = 'ccnews'  # 集合名基础
    batch_size = 5000  # 每5000条数据一个新集合
    batch = []
    collection_counter = 1  # 集合编号，从1开始

    dataset = load_dataset('parquet', data_files='train-00000-of-00005.parquet')
    data = list(dataset['train'])
    logging.info("开始处理CCNews数据")

    for index, item in tqdm(enumerate(data)):
        title = item['title']
        abstract = item['text']
        new_document = {
            'title':title,
            'abstract': abstract
        }
        batch.append(new_document)

        # 如果当前批次大小达到5000，就切换集合并插入数据
        if len(batch) >= batch_size:

            collection_name = f"{base_collection_name}_{collection_counter}"  # 动态生成集合名称
            collection = db[collection_name]
            collection.insert_many(batch)
            logging.info(f"数据已插入集合: {collection_name}")
            # quit()
            # 清空批次并递增集合编号
            batch.clear()
            collection_counter += 1

    # 处理剩余数据（如果有的话）
    if batch:
        collection_name = f"{base_collection_name}_{collection_counter}"
        collection = db[collection_name]
        collection.insert_many(batch)
        logging.info(f"数据已插入集合: {collection_name}")

    logging.info("CCNews数据处理完成")

if __name__ == '__main__':
    main()