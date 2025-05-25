# 知识增强

import sys

sys.path.append('/home/zhengy/ScienceDataAnalyze')
from mongo_helper import MongoHelper
import logging
from datetime import datetime
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from glm.glm4ApiEnglish import GLM4ClientEnglish
log_filename = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s: %(message)s',
                    handlers=[
                        logging.StreamHandler(),
                        logging.FileHandler(f'sci_pop_score_logfile_{log_filename}.log',encoding='utf-8')
                    ])


# 无明确含义

def popSci(key,index):
    logging.info(f"Starting thread for key {key} and index {index}")
    mongo = MongoHelper()
    client = mongo.client
    db = client['personalization']
    collectionName = f"MaPereduKnowledgeAgent_{index}"
    collections = db[collectionName]
    all_documents = list(collections.find())
    print(f"Number of documents: {len(all_documents)}")
    if len(all_documents) == 0:
        return
    batch_size = 1000  # 批量插入的大小
    batch = []  # 用于存储待插入的文档
    for index,document in tqdm(enumerate(all_documents)):
        try:
            updateKnowledge = document['updateKnowledge']
            abstract = document['abstract']
            original_id = document['original_id']
            new_document = {
                'original_id':original_id,
                'abstract':abstract,
                'updateKnowledge':updateKnowledge,
                'score':-1
            }
            logging.info(f"文章{original_id}处理完成，继续下一个.....")
        except Exception as e:
            logging.error(e)
            # print(index)
            # quit()
    logging.info(f"Finished thread for key {key} and index {index}")


def main():
    logging.info("start PopScience process")
    configKeys = [
        "5d402c5e8df649b9acbe23058d261336.5n7AkiLxzf51t5tZ",
        "99626758d48544d2822315c5e6eaf5ee.fuxIb0w9azCJtUNn",
        "799c6e24c32e4c7db26fe92442ba6c75.WePbYZMOmPc6kB0i",
        "cead652a24cd4de4aa9ee5ae9d8cd044.hAqjnmj8IWvaCMcx",
        "5c40f74a3eb341de90ca95a66ce55740.1kEZZD616pNCIUc5",
        "96cc3810ae9b43098f36b2754152f2a3.hbeFkwcJsWzlisrM"
    ]
    # popSci(configKeys[0],1)
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(popSci, key, index) for index, key in enumerate(configKeys, start=1)]
        for future in futures:
            future.result()  # 等待所有线程完成
    logging.info("end PopScience process")


if __name__ == '__main__':
    main()